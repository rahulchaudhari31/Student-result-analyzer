from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=1)
    role: str = Field(..., pattern="^(teacher|student)$")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    uid: str
    email: str
    name: str
    role: str
    token: str


class MessageResponse(BaseModel):
    message: str


class SaveResultRequest(BaseModel):
    file_name: str
    exam_tag: str
    department: str
    year: str
    students_data: List[Dict[str, Any]]
    summary: Dict[str, Any]


class StudentHistoryResponse(BaseModel):
    name: str
    prn: str
    mother: Optional[str] = None
    results: List[Dict[str, Any]]
    predicted_next_sgpa: Optional[float] = None
    failed_subjects: List[Dict[str, Any]]


class AnalysisResponse(BaseModel):
    students: List[Dict[str, Any]]
    summary: Dict[str, Any]
    top_students: List[Dict[str, Any]]
    failed_students: List[Dict[str, Any]]
    subject_grade_summary: List[Dict[str, Any]]
    grade_distribution: Dict[str, int]
    batch_statistics: Dict[str, Any]
    pdf_type: str


class OverviewResponse(BaseModel):
    total_students: int
    overall_pass_rate: float
    overall_avg_sgpa: float
    exams_analyzed: int
    department_stats: List[Dict[str, Any]]
    year_stats: List[Dict[str, Any]]
