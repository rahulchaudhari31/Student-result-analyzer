from typing import Dict, List

from fastapi import APIRouter, Depends

from ..analyzer import AdvancedResultAnalyzer
from ..deps import get_firebase_manager
from ..firebase_manager import FirebaseManager
from ..schemas import StudentHistoryResponse
from .auth_helpers import handle_firebase_error

router = APIRouter(prefix="/students", tags=["students"])


@router.get("/identifiers")
def get_identifiers(fm: FirebaseManager = Depends(get_firebase_manager)) -> Dict[str, str]:
    try:
        return fm.get_all_student_identifiers()
    except Exception as e:
        handle_firebase_error(e)


@router.get("/history", response_model=StudentHistoryResponse)
def get_history(prn: str, fm: FirebaseManager = Depends(get_firebase_manager)):
    try:
        history = fm.get_student_history(prn)
        if not history:
            raise ValueError("Profile not found.")
        student = history[0]

        analyzer = AdvancedResultAnalyzer()

        failed_subjects_list = []
        for result in student.get("Results", []):
            for sub in result.get("Subjects", []):
                grade = str(sub.get("Grade", "")).upper()
                if grade in ["F", "FF", "FAIL"]:
                    failed_subjects_list.append({
                        "Exam": result.get("Exam"),
                        "Subject": sub.get("Course Name", "Unknown"),
                        "Grade": grade,
                    })

        # Results need date-sortable string for prediction helper
        history_payload = {"Results": student.get("Results", [])}
        predicted = analyzer.predict_next_sgpa(history_payload)

        return StudentHistoryResponse(
            name=student.get("Name", "Unknown"),
            prn=student.get("PRN", prn),
            mother=student.get("Mother"),
            results=student.get("Results", []),
            predicted_next_sgpa=predicted,
            failed_subjects=failed_subjects_list,
        )
    except Exception as e:
        handle_firebase_error(e)
