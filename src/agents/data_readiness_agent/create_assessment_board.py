"""
MAP Assessment Board Agent v0.1

Purpose:
Creates a first one-look assessment board from the clean MAP assessment data.

Outputs:
- all_assessments_by_submission_date.csv
- same_day_assessment_pressure.csv
- near_date_assessment_pressure.csv
- feedback_20wd_warnings.csv

This is a quick MVP board before the full Programme-Cohort Mapping Agent.
"""

from pathlib import Path
from datetime import datetime
import csv
from collections import defaultdict


def find_project_root():
    """
    Finds the project root by walking upwards until it finds the main
    project folders: data, outputs and src.
    This avoids path errors if this script is accidentally placed one folder deeper.
    """
    current = Path(__file__).resolve().parent

    for parent in [current] + list(current.parents):
        if (parent / "data").exists() and (parent / "outputs").exists() and (parent / "src").exists():
            return parent

    raise RuntimeError("Could not find project root. Please check the folder structure.")


ROOT = find_project_root()

INPUT_FOLDER = ROOT / "outputs" / "2026_27_readiness_03Sep"
OUTPUT_FOLDER = ROOT / "outputs" / "2026_27_readiness_03Sep" / "assessment_board"
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

CLEAN_ASSESSMENTS = INPUT_FOLDER / "clean_assessments.csv"
READINESS_ISSUES = INPUT_FOLDER / "readiness_issues.csv"


def read_csv(path):
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fieldnames=None):
    rows = list(rows)

    if fieldnames is None:
        fieldnames = []
        for row in rows:
            for key in row.keys():
                if key not in fieldnames:
                    fieldnames.append(key)

    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def parse_iso_date(value):
    value = "" if value is None else str(value).strip()
    if value == "":
        return None

    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def to_float(value):
    value = "" if value is None else str(value).strip()
    if value == "":
        return 0.0

    try:
        return float(value)
    except ValueError:
        return 0.0


print("Loading clean assessment data...")

assessments = read_csv(CLEAN_ASSESSMENTS)
issues = read_csv(READINESS_ISSUES)

print(f"Clean assessment rows: {len(assessments)}")
print(f"Readiness issues: {len(issues)}")


# ---------------------------------------------------------------------
# Keep only summative, non-formal-exam, calendar-relevant assessments
# ---------------------------------------------------------------------

calendar_assessments = []

for row in assessments:
    is_summative = str(row.get("Is Summative", "")).lower() == "true"
    is_formal_exam = str(row.get("Is Formal Examination", "")).lower() == "true"
    include_calendar = str(row.get("Include in EEECS Calendar", "")).lower() == "true"

    submission_date = parse_iso_date(row.get("Predicted Submission Date", ""))

    if is_summative and not is_formal_exam and include_calendar and submission_date is not None:
        calendar_assessments.append(row)

print(f"Calendar-relevant non-exam assessments: {len(calendar_assessments)}")


# ---------------------------------------------------------------------
# Output 1: all assessments by submission date
# ---------------------------------------------------------------------

all_by_date = sorted(
    calendar_assessments,
    key=lambda r: (
        parse_iso_date(r.get("Predicted Submission Date", "")),
        r.get("Module Code", ""),
        r.get("Assessment Code", "")
    )
)

write_csv(
    OUTPUT_FOLDER / "all_assessments_by_submission_date.csv",
    all_by_date
)


# ---------------------------------------------------------------------
# Output 2: same-day assessment pressure
# ---------------------------------------------------------------------

by_date = defaultdict(list)

for row in calendar_assessments:
    submission_date = row.get("Predicted Submission Date", "")
    by_date[submission_date].append(row)

same_day_rows = []

for submission_date, rows in sorted(by_date.items()):
    if len(rows) <= 1:
        continue

    total_weight = sum(to_float(r.get("Assessment Weight", "")) for r in rows)
    module_codes = sorted(set(r.get("Module Code", "") for r in rows))

    same_day_rows.append({
        "Submission Date": submission_date,
        "Number of Assessments": len(rows),
        "Total Weighting": round(total_weight, 2),
        "Modules": "; ".join(module_codes),
        "Assessment Codes": "; ".join(r.get("Assessment Code", "") for r in rows),
        "Assessment Titles": "; ".join(r.get("Assessment Title", "") for r in rows),
        "Indicative Severity": "High" if len(rows) >= 3 or total_weight >= 80 else "Warning",
        "Note": "This is a general board only. Programme/stage mapping is needed to confirm shared-cohort conflict."
    })

write_csv(
    OUTPUT_FOLDER / "same_day_assessment_pressure.csv",
    same_day_rows
)


# ---------------------------------------------------------------------
# Output 3: near-date assessment pressure, within 1 or 2 calendar days
# ---------------------------------------------------------------------

near_date_rows = []

sorted_rows = sorted(
    calendar_assessments,
    key=lambda r: parse_iso_date(r.get("Predicted Submission Date", ""))
)

for i in range(len(sorted_rows)):
    a = sorted_rows[i]
    date_a = parse_iso_date(a.get("Predicted Submission Date", ""))

    for j in range(i + 1, len(sorted_rows)):
        b = sorted_rows[j]
        date_b = parse_iso_date(b.get("Predicted Submission Date", ""))

        if date_a is None or date_b is None:
            continue

        gap = (date_b - date_a).days

        if gap > 2:
            break

        if gap < 0:
            continue

        # Avoid comparing assessments from the same module for this general board
        if a.get("Module Code", "") == b.get("Module Code", ""):
            continue

        weight_a = to_float(a.get("Assessment Weight", ""))
        weight_b = to_float(b.get("Assessment Weight", ""))
        combined_weight = weight_a + weight_b

        severity = "Warning"
        if gap == 0:
            severity = "High"
        elif gap == 1 and combined_weight >= 50:
            severity = "High"
        elif gap == 2 and combined_weight >= 70:
            severity = "Warning"

        near_date_rows.append({
            "Date Gap": gap,
            "Indicative Severity": severity,
            "Submission Date A": a.get("Predicted Submission Date", ""),
            "Submission Date B": b.get("Predicted Submission Date", ""),
            "Module A": a.get("Module Code", ""),
            "Assessment A": a.get("Assessment Code", ""),
            "Title A": a.get("Assessment Title", ""),
            "Weight A": a.get("Assessment Weight", ""),
            "Module B": b.get("Module Code", ""),
            "Assessment B": b.get("Assessment Code", ""),
            "Title B": b.get("Assessment Title", ""),
            "Weight B": b.get("Assessment Weight", ""),
            "Combined Weight": round(combined_weight, 2),
            "Note": "This is an indicative general clash. Programme/stage mapping is required before APD action."
        })

write_csv(
    OUTPUT_FOLDER / "near_date_assessment_pressure.csv",
    near_date_rows
)


# ---------------------------------------------------------------------
# Output 4: feedback warnings
# ---------------------------------------------------------------------

feedback_warnings = [
    row for row in issues
    if row.get("Rule ID") == "DR-011"
]

write_csv(
    OUTPUT_FOLDER / "feedback_20wd_warnings.csv",
    feedback_warnings
)


# ---------------------------------------------------------------------
# Run summary
# ---------------------------------------------------------------------

print("\nMAP Assessment Board Agent completed.")
print("=" * 60)
print(f"All calendar-relevant assessments: {len(all_by_date)}")
print(f"Same-day pressure dates: {len(same_day_rows)}")
print(f"Near-date pressure pairs: {len(near_date_rows)}")
print(f"Feedback >20 working days warnings: {len(feedback_warnings)}")
print(f"Output folder: {OUTPUT_FOLDER}")

print("\nFiles created:")
print("- all_assessments_by_submission_date.csv")
print("- same_day_assessment_pressure.csv")
print("- near_date_assessment_pressure.csv")
print("- feedback_20wd_warnings.csv")