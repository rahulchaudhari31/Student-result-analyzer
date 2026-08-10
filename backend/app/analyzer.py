import re
from collections import defaultdict
from typing import Dict, List, Optional

import numpy as np
import PyPDF2
from sklearn.linear_model import LinearRegression


class AdvancedResultAnalyzer:
    def __init__(self):
        self.students_data: List[Dict] = []
        self.raw_text = ""
        self.pdf_type = "unknown"
        self.valid_grades = {'O', 'A+', 'A', 'B+', 'B', 'C', 'P', 'F', 'FF', 'AB', 'IC', 'ABS', 'PP'}

    def extract_text_from_pdf(self, uploaded_file) -> Optional[str]:
        """Extract raw text from a PDF file-like object."""
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- PAGE {page_num + 1} ---\n"
                    text += page_text
            self.raw_text = text
            return text
        except Exception as e:
            raise ValueError(f"Error reading PDF: {str(e)}") from e

    def clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = text.replace('|', 'I')
        text = text.replace('®', '').replace('©', '').replace('#', '')
        text = text.replace('$', '').replace('@', '').replace('%', '')
        return text

    def detect_pdf_type(self, text: str) -> str:
        if re.search(r'B\.E\.', text, re.IGNORECASE):
            return "be"
        elif re.search(r'T\.E\.', text, re.IGNORECASE):
            return "te"
        elif re.search(r'THIRD YEAR', text, re.IGNORECASE):
            return "te"
        elif re.search(r'SEM\.:?\s*7', text, re.IGNORECASE):
            return "be"
        elif re.search(r'SEM\.:?\s*[5-6]', text, re.IGNORECASE):
            return "te"
        return "unknown"

    def extract_grade(self, token: str) -> Optional[str]:
        token = token.strip().rstrip('.,;')
        return token if token in self.valid_grades else None

    def parse_subjects_from_block(self, block: str) -> List[Dict]:
        subjects = []
        lines = block.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            codes = re.findall(r'\b(\d{6})\b', line)
            if not codes:
                continue

            tokens = line.split()
            for code in codes:
                try:
                    code_idx = tokens.index(code)
                except ValueError:
                    continue

                grade = None
                grade_idx = -1
                for i, tok in enumerate(tokens[code_idx + 1:], start=code_idx + 1):
                    potential_grade = self.extract_grade(tok)
                    if potential_grade:
                        grade = potential_grade
                        grade_idx = i
                        break

                if not grade:
                    continue

                name_tokens = []
                for t in tokens[code_idx + 1:grade_idx]:
                    if re.match(r'^\d+$', t) or re.match(r'^\d+/\d+$', t):
                        continue
                    name_tokens.append(t)

                course_name = ' '.join(name_tokens).strip()
                if not course_name:
                    course_name = code

                course_name = re.sub(r'[^\w\s]', '', course_name)

                subjects.append({
                    'Course Code': code,
                    'Course Name': course_name,
                    'Grade': grade
                })
        return subjects

    def parse_comprehensive_data(self, text: str) -> List[Dict]:
        self.pdf_type = self.detect_pdf_type(text)
        students = []
        text = self.clean_text(text)

        blocks = re.split(r'(?=SEAT NO\.?\s*:)', text)

        for block in blocks:
            if "SEAT NO.:" not in block:
                continue

            try:
                student = self.extract_common_fields(block)
                if not student:
                    continue

                student['Subjects'] = self.parse_subjects_from_block(block)

                student['Passed Subjects'] = sum(
                    1 for sub in student['Subjects']
                    if sub['Grade'] not in ['F', 'FF', 'AB', 'IC', 'ABS']
                )
                student['Total Subjects'] = len(student['Subjects'])

                has_failing = any(
                    sub['Grade'] in ['F', 'FF', 'AB', 'IC'] for sub in student['Subjects']
                )
                if student.get('Has Valid SGPA', False) and not has_failing:
                    student['Result Status'] = 'Pass'
                else:
                    student['Result Status'] = 'Fail'

                if not any(s.get('Seat No') == student['Seat No'] for s in students):
                    students.append(student)
            except Exception:
                continue

        self.students_data = students
        return students

    def extract_common_fields(self, block: str) -> Optional[Dict]:
        student = {}

        seat_match = re.search(r'SEAT NO\.?\s*:?\s*([A-Z0-9]+)', block, re.IGNORECASE)
        if not seat_match:
            return None
        student['Seat No'] = seat_match.group(1)

        name_match = re.search(r'NAME\s*:?\s*([A-Z\s]+?)(?=\s+(?:MOTHER|PRN|COURSE|$))', block, re.IGNORECASE)
        student['Name'] = name_match.group(1).strip() if name_match else "Unknown"

        mother_match = re.search(r'MOTHER\s*:?\s*([A-Z\s]+?)(?=\s+(?:PRN|COURSE|$))', block, re.IGNORECASE)
        student['Mother Name'] = mother_match.group(1).strip() if mother_match else "Unknown"

        prn_match = re.search(r'PRN\s*:?\s*([A-Z0-9]+)', block, re.IGNORECASE)
        student['PRN'] = prn_match.group(1).strip() if prn_match else "Unknown"

        sgpa_patterns = [
            r'SGPA1?\s*:?\s*([\d.]+|--|FF)',
            r'THIRD YEAR SGPA\s*:?\s*([\d.]+|--|FF)',
            r'FOURTH YEAR SGPA\s*:?\s*([\d.]+|--|FF)',
            r'SEM\.?:?\s*\d+.*?SGPA\s*:?\s*([\d.]+|--|FF)',
            r'SGPA\s*:?\s*([\d.]+|--|FF)',
            r'([\d.]+),?\s*TOTAL CREDITS',
            r'([\d.]+)\s*SGPA',
            r'SPGAP?\s*:?\s*([\d.]+|--|FF)',
        ]

        sgpa_raw = "0.0"
        for pattern in sgpa_patterns:
            sgpa_match = re.search(pattern, block, re.IGNORECASE)
            if sgpa_match:
                sgpa_raw = sgpa_match.group(1)
                break

        if sgpa_raw in ['--', 'FF', 'AB', 'IC', '']:
            sgpa = 0.0
        else:
            try:
                sgpa_clean = re.sub(r'[^\d.]', '', sgpa_raw)
                sgpa = float(sgpa_clean) if sgpa_clean else 0.0
            except Exception:
                sgpa = 0.0

        student['SGPA'] = sgpa
        student['SGPA_Raw'] = sgpa_raw
        student['Has Valid SGPA'] = sgpa > 0

        credits_match = re.search(r'TOTAL CREDITS EARNED\s*:?\s*(\d+)', block, re.IGNORECASE)
        student['Credits'] = int(credits_match.group(1)) if credits_match else 0

        return student

    def get_result_summary(self) -> Dict:
        if not self.students_data:
            return {}

        total = len(self.students_data)
        passed = sum(1 for s in self.students_data if s['Result Status'] == 'Pass')
        valid_sgpa_students = [s for s in self.students_data if s.get('Has Valid SGPA')]

        avg_sgpa = 0
        if valid_sgpa_students:
            avg_sgpa = sum(s['SGPA'] for s in valid_sgpa_students) / len(valid_sgpa_students)

        return {
            'total_students': total,
            'passed_students': passed,
            'failed_students': total - passed,
            'average_sgpa': round(avg_sgpa, 2),
            'pass_percentage': round((passed / total * 100) if total > 0 else 0, 1)
        }

    def get_top_students(self, n: int = 10) -> List[Dict]:
        valid = [s for s in self.students_data if s.get('Has Valid SGPA')]
        return sorted(valid, key=lambda x: x['SGPA'], reverse=True)[:n]

    def get_failed_students(self) -> List[Dict]:
        return [s for s in self.students_data if s['Result Status'] == 'Fail']

    def predict_next_sgpa(self, student_history: Dict) -> Optional[float]:
        results = student_history.get('Results', [])
        if len(results) < 2:
            return None

        sorted_results = sorted(results, key=lambda x: x.get('Date', ''))

        X = np.array([i for i in range(len(sorted_results))]).reshape(-1, 1)
        Y = np.array([float(r.get('SGPA', 0.0)) for r in sorted_results])

        try:
            model = LinearRegression()
            model.fit(X, Y)
            next_index = len(results)
            prediction = model.predict([[next_index]])
            return round(max(0.0, min(10.0, prediction[0])), 2)
        except Exception:
            return None

    def get_subject_grade_summary(self) -> List[Dict]:
        if not self.students_data:
            return []

        subject_grades = defaultdict(lambda: defaultdict(int))
        course_code_to_name = {}

        for student in self.students_data:
            for subject in student.get('Subjects', []):
                course_code = subject.get('Course Code')
                course_name = subject.get('Course Name', 'Unknown Subject')
                grade = subject.get('Grade', 'N/A')

                if course_code and grade and grade not in ['IC', 'ABS', 'N/A']:
                    course_code_to_name[course_code] = course_name

                    if grade == 'FF':
                        grade = 'F'

                    subject_grades[course_code]['Total Students'] += 1
                    subject_grades[course_code][grade] += 1

        summary_list = []
        for code, data in subject_grades.items():
            total = data.pop('Total Students')
            row = {
                'Course Code': code,
                'Course Name': course_code_to_name.get(code, code),
                'Total Students': total
            }

            grades = ['O', 'A+', 'A', 'B+', 'B', 'C', 'P', 'F']
            for g in grades:
                row[g] = data.get(g, 0)

            failures = row.get('F', 0)
            row['Failure Rate (%)'] = round((failures / total) * 100, 1) if total > 0 else 0

            summary_list.append(row)

        summary_list.sort(key=lambda x: x['Course Code'])
        return summary_list

    def get_grade_distribution(self) -> Dict:
        grade_counts = defaultdict(int)

        for student in self.students_data:
            for subject in student.get('Subjects', []):
                grade = subject.get('Grade', 'N/A')
                if grade not in ['IC', 'ABS', 'N/A']:
                    if grade == 'FF':
                        grade = 'F'
                    grade_counts[grade] += 1

        return dict(grade_counts)

    def get_batch_statistics(self) -> Dict:
        if not self.students_data:
            return {}

        sgpa_values = [s['SGPA'] for s in self.students_data if s.get('Has Valid SGPA')]

        stats = {
            'total_students': len(self.students_data),
            'students_with_sgpa': len(sgpa_values),
            'sgpa_stats': {}
        }

        if sgpa_values:
            stats['sgpa_stats'] = {
                'min': min(sgpa_values),
                'max': max(sgpa_values),
                'mean': float(np.mean(sgpa_values)),
                'median': float(np.median(sgpa_values)),
                'std': float(np.std(sgpa_values)),
                'p90': float(np.percentile(sgpa_values, 90)),
                'p10': float(np.percentile(sgpa_values, 10)),
            }

        return stats

    def search_students(self, search_term: str) -> List[Dict]:
        search_term = search_term.lower().strip()
        results = []

        for student in self.students_data:
            if (search_term in student.get('Name', '').lower() or
                    search_term in student.get('PRN', '').lower() or
                    search_term in student.get('Seat No', '').lower()):
                results.append(student)

        return results
