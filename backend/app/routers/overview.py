from collections import defaultdict
from typing import Dict, List

from fastapi import APIRouter, Depends

from ..deps import get_firebase_manager
from ..firebase_manager import FirebaseManager
from ..schemas import OverviewResponse
from .auth_helpers import handle_firebase_error

router = APIRouter(prefix="/overview", tags=["overview"])


@router.get("/", response_model=OverviewResponse)
def get_overview(fm: FirebaseManager = Depends(get_firebase_manager)):
    try:
        files = fm.get_all_result_files()
    except Exception as e:
        handle_firebase_error(e)

    dept_stats: Dict[str, dict] = defaultdict(
        lambda: {"total": 0, "passed": 0, "sgpa_sum": 0, "sgpa_count": 0, "files": 0}
    )
    year_stats: Dict[str, dict] = defaultdict(lambda: {"total": 0, "passed": 0})

    total_students = 0
    total_passed = 0
    total_sgpa_sum = 0
    total_sgpa_count = 0

    for f in files:
        dept = f.get("department", "Uncategorized")
        year = f.get("year", "Unknown")
        summary = f.get("summary", {}) or {}
        count = f.get("total_students", 0)
        passed = summary.get("passed_students", 0)
        avg_sgpa = summary.get("average_sgpa", 0)

        total_students += count
        total_passed += passed
        if count > 0:
            total_sgpa_sum += avg_sgpa * count
            total_sgpa_count += count

        dept_stats[dept]["total"] += count
        dept_stats[dept]["passed"] += passed
        if count > 0:
            dept_stats[dept]["sgpa_sum"] += avg_sgpa * count
            dept_stats[dept]["sgpa_count"] += count
        year_stats[year]["total"] += count
        year_stats[year]["passed"] += passed

    overall_pass_rate = (total_passed / total_students * 100) if total_students else 0
    overall_avg_sgpa = (total_sgpa_sum / total_sgpa_count) if total_sgpa_count else 0

    department_stats = []
    for d, stats in dept_stats.items():
        pass_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] else 0
        avg = (stats["sgpa_sum"] / stats["sgpa_count"]) if stats["sgpa_count"] else 0
        department_stats.append({
            "department": d,
            "pass_rate": round(pass_rate, 1),
            "avg_sgpa": round(avg, 2),
            "students": stats["total"],
        })

    year_stats_list = []
    for y, stats in year_stats.items():
        pass_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] else 0
        year_stats_list.append({
            "year": y,
            "pass_rate": round(pass_rate, 1),
            "students": stats["total"],
        })

    year_order = {"FE": 1, "SE": 2, "TE": 3, "BE": 4}
    year_stats_list.sort(key=lambda x: year_order.get(x["year"], 5))

    return OverviewResponse(
        total_students=total_students,
        overall_pass_rate=round(overall_pass_rate, 1),
        overall_avg_sgpa=round(overall_avg_sgpa, 2),
        exams_analyzed=len(files),
        department_stats=department_stats,
        year_stats=year_stats_list,
    )
