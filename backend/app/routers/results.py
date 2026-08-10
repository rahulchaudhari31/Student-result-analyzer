import io
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from ..analyzer import AdvancedResultAnalyzer
from ..deps import get_firebase_manager
from ..firebase_manager import FirebaseManager
from ..schemas import AnalysisResponse, MessageResponse, SaveResultRequest
from .auth_helpers import handle_firebase_error

router = APIRouter(prefix="/results", tags=["results"])


def _build_analysis_response(analyzer: AdvancedResultAnalyzer) -> dict:
    return {
        "students": analyzer.students_data,
        "summary": analyzer.get_result_summary(),
        "top_students": analyzer.get_top_students(50),
        "failed_students": analyzer.get_failed_students(),
        "subject_grade_summary": analyzer.get_subject_grade_summary(),
        "grade_distribution": analyzer.get_grade_distribution(),
        "batch_statistics": analyzer.get_batch_statistics(),
        "pdf_type": analyzer.pdf_type,
    }


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_pdf(file: UploadFile = File(...)):
    """Parse an uploaded marksheet PDF and return full analysis payload."""
    try:
        content = await file.read()
    except Exception as e:
        handle_firebase_error(e)

    analyzer = AdvancedResultAnalyzer()
    try:
        text = analyzer.extract_text_from_pdf(io.BytesIO(content))
        if not text:
            raise ValueError("Could not extract any text from the PDF.")
        students = analyzer.parse_comprehensive_data(text)
        if not students:
            raise ValueError("No student data could be extracted. Please check the PDF format.")
    except Exception as e:
        handle_firebase_error(e)

    return _build_analysis_response(analyzer)


@router.post("/save", response_model=MessageResponse)
def save_result(
    request: SaveResultRequest,
    fm: FirebaseManager = Depends(get_firebase_manager),
):
    try:
        doc_id = fm.save_result_data(
            request.file_name,
            request.exam_tag,
            request.department,
            request.year,
            request.students_data,
            request.uploaded_by,
            request.summary,
        )
        if not doc_id:
            raise ValueError("Failed to save result data to Firestore.")
        return MessageResponse(message=doc_id)
    except Exception as e:
        handle_firebase_error(e)


@router.get("/")
def list_results(fm: FirebaseManager = Depends(get_firebase_manager)):
    try:
        return fm.get_all_result_files()
    except Exception as e:
        handle_firebase_error(e)


@router.get("/{result_id}")
def get_result(result_id: str, fm: FirebaseManager = Depends(get_firebase_manager)):
    try:
        files = fm.get_all_result_files()
        for f in files:
            if f.get("id") == result_id:
                return f
        raise HTTPException(status_code=404, detail="Result file not found.")
    except Exception as e:
        handle_firebase_error(e)
