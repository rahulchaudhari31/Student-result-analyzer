const PROD_API_URL = 'https://new-result-analysis-system.onrender.com'

export const API_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? '' : PROD_API_URL)

export const GRADES = ['O', 'A+', 'A', 'B+', 'B', 'C', 'P', 'F']

export const GRADE_COLORS = {
  O: '#27ae60',
  'A+': '#2ecc71',
  A: '#58d68d',
  'B+': '#3498db',
  B: '#5dade2',
  C: '#aed6f1',
  P: '#bdc3c7',
  F: '#ef4444',
}

export const GRADE_POINTS = {
  O: 10,
  'A+': 9,
  A: 8,
  'B+': 7,
  B: 6,
  C: 5,
  P: 4,
  F: 3,
  FF: 3,
  AB: 2,
  ABS: 2,
  IC: 2,
}

export const DEPARTMENTS = [
  'Computer',
  'IT',
  'Mechanical',
  'Civil',
  'Electrical',
  'AIDS',
  'E&TC',
  'General Science',
]

export const YEARS = ['FE', 'SE', 'TE', 'BE']
