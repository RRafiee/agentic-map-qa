"""
MAP Intake and Data Readiness Agent v0.2

Purpose:
Reads raw Microsoft List exports for the MAP system and produces:
- clean assessment data
- readiness issues
- module-level readiness status
- weighting totals
- date checks
- run log

This agent performs deterministic checks only.
It does not use Gemini.
It does not change source records.

Important date logic:
- Microsoft Lists CSV export is currently interpreted as US-style dates: M/D/YYYY.
- Release date and submission date are allowed to be the same day.
- Submission date and feedback date are allowed to be the same day.
- Feedback beyond 20 working days is flagged as a Warning, not a Critical issue.
"""

from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import csv
import re



# ---------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[3]

INPUT_FOLDER = ROOT / "data" / "raw" / "2026_27_snapshot_03Sep"
OUTPUT_FOLDER = ROOT / "outputs" / "2026_27_readiness_03Sep"
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

FILES = {
    "module_catalogue": "module_catalogue_raw.csv",
    "module_plans": "module_plans_raw.csv",
    "assessments": "assessments_raw.csv",
    "programme_module_mapping": "programme_module_mapping_raw.csv",
}

ACADEMIC_YEAR = "2026/27"


# ---------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------

def read_csv(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows, fieldnames=None):
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


def clean_text(value):
    if value is None:
        return ""
    return str(value).strip()


def is_blank(value):
    return clean_text(value) == ""


def normalise_yes_no(value):
    value = clean_text(value).lower()
    return value in {"yes", "y", "true", "1", "checked"}


def extract_module_code(value):
    """
    Extracts module codes such as CSC1023, ELE2041, ECS8055.
    """
    value = clean_text(value).upper()
    match = re.search(r"\b[A-Z]{3}\d{4}\b", value)
    return match.group(0) if match else ""


def parse_number(value):
    value = clean_text(value)
    if value == "":
        return None

    value = value.replace("%", "").replace(",", "").strip()

    try:
        return float(value)
    except ValueError:
        return None


def parse_int(value):
    number = parse_number(value)
    if number is None:
        return None
    return int(number)


def parse_date(value):
    """
    Parses SharePoint/Microsoft Lists CSV dates.

    The current export appears to use US-style dates:
    M/D/YYYY, for example:
    - 12/18/2026 = 18 December 2026
    - 4/30/2027 = 30 April 2027

    Equality is allowed:
    - release date can equal submission date
    - submission date can equal feedback date
    """
    value = clean_text(value)
    if value == "":
        return None

    value = value.replace("Z", "").strip()

    # Handle ISO datetime such as 2026-12-18T00:00:00
    if "T" in value:
        value = value.split("T")[0].strip()

    # Handle values with time, such as 12/18/2026 12:00 AM
    if " " in value:
        value = value.split(" ")[0].strip()

    formats = [
        "%m/%d/%Y",   # Microsoft Lists export format
        "%m/%d/%y",
        "%Y-%m-%d",
        "%d/%m/%Y",   # fallback only
        "%d-%m-%Y",
        "%d/%m/%y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass

    return None


def days_between(date_a, date_b):
    if date_a is None or date_b is None:
        return None
    return (date_b - date_a).days


def working_days_between(start_date, end_date):
    """
    Counts working days between submission and feedback dates.
    Weekends are excluded.
    Bank holidays are not included in this MVP version.

    Example:
    Submission Monday, feedback next Monday = 5 working days.
    """
    if start_date is None or end_date is None:
        return None

    if end_date < start_date:
        return None

    count = 0
    current = start_date

    while current < end_date:
        current = current + timedelta(days=1)
        if current.weekday() < 5:  # Monday=0, Friday=4
            count += 1

    return count


def add_issue(
    issues,
    module_code,
    assessment_code,
    rule_id,
    severity,
    issue_type,
    message,
    source="Data Readiness Agent",
):
    issues.append({
        "Academic Year": ACADEMIC_YEAR,
        "Module Code": module_code,
        "Assessment Code": assessment_code,
        "Rule ID": rule_id,
        "Severity": severity,
        "Issue Type": issue_type,
        "Message": message,
        "Source": source,
    })


# ---------------------------------------------------------------------
# Load files
# ---------------------------------------------------------------------

print("Loading MAP data exports...")

module_catalogue = read_csv(INPUT_FOLDER / FILES["module_catalogue"])
module_plans = read_csv(INPUT_FOLDER / FILES["module_plans"])
assessments = read_csv(INPUT_FOLDER / FILES["assessments"])

print(f"Module catalogue rows: {len(module_catalogue)}")
print(f"Module plan rows: {len(module_plans)}")
print(f"Assessment rows: {len(assessments)}")


# ---------------------------------------------------------------------
# Prepare lookup dictionaries
# ---------------------------------------------------------------------

catalogue_by_code = {}
catalogue_codes = set()

for row in module_catalogue:
    code = extract_module_code(row.get("Module Code", ""))
    if code:
        catalogue_codes.add(code)
        catalogue_by_code[code] = row


plan_ref_to_module_code = {}
plans_by_module = defaultdict(list)

for row in module_plans:
    plan_ref = clean_text(row.get("Plan Reference", ""))
    module_value = clean_text(row.get("Module", ""))
    module_code = extract_module_code(module_value)

    if plan_ref:
        plan_ref_to_module_code[plan_ref] = module_code

    if module_code:
        plans_by_module[module_code].append(row)


# ---------------------------------------------------------------------
# Run readiness checks
# ---------------------------------------------------------------------

issues = []
clean_assessments = []
date_checks = []
weighting_by_module = defaultdict(float)
summative_count_by_module = defaultdict(int)

# DR-001: duplicate module plans
for module_code, rows in plans_by_module.items():
    if len(rows) > 1:
        add_issue(
            issues,
            module_code,
            "",
            "DR-001",
            "Critical",
            "Duplicate module plan",
            f"{len(rows)} MAP plan records found for module {module_code}."
        )

# DR-002: module plan exists in catalogue
for module_code in plans_by_module.keys():
    if module_code not in catalogue_codes:
        add_issue(
            issues,
            module_code,
            "",
            "DR-002",
            "Critical",
            "Module not in catalogue",
            f"Module {module_code} appears in Module Plans but was not found in the Module Catalogue."
        )


for row in assessments:
    assessment_code = clean_text(row.get("Assessment Code", ""))
    module_plan_ref = clean_text(row.get("Module Plan", ""))

    module_code = ""

    # Try to find module code from Module Plan lookup
    if module_plan_ref in plan_ref_to_module_code:
        module_code = plan_ref_to_module_code[module_plan_ref]

    # Fallback: extract module code from Assessment Code
    if not module_code:
        module_code = extract_module_code(assessment_code)

    assessment_title = clean_text(row.get("Assessment Title", ""))
    assessment_type = clean_text(row.get("Assessment Type", ""))
    assessment_weight_raw = row.get("Assessment Weight", "")
    assessment_weight = parse_number(assessment_weight_raw)

    is_summative = normalise_yes_no(row.get("Is Summative", ""))
    is_formal_exam = normalise_yes_no(row.get("Is Formal Examination", ""))

    include_calendar_raw = clean_text(row.get("Include in EEECS Calendar", ""))
    include_calendar = normalise_yes_no(include_calendar_raw)

    release_date_raw = clean_text(row.get("Predicted Release Date", ""))
    submission_date_raw = clean_text(row.get("Predicted Submission Date", ""))
    feedback_date_raw = clean_text(row.get("Predicted Feedback Date", ""))

    release_date = parse_date(release_date_raw)
    submission_date = parse_date(submission_date_raw)
    feedback_date = parse_date(feedback_date_raw)

    submission_to_feedback_working_days = working_days_between(submission_date, feedback_date)

    if is_summative:
        summative_count_by_module[module_code] += 1

    # DR-002: assessment module exists in catalogue
    if module_code and module_code not in catalogue_codes:
        add_issue(
            issues,
            module_code,
            assessment_code,
            "DR-002",
            "Critical",
            "Assessment module not in catalogue",
            f"Assessment {assessment_code} appears to belong to {module_code}, but this module was not found in the Module Catalogue."
        )

    if not module_code:
        add_issue(
            issues,
            "",
            assessment_code,
            "DR-002",
            "Critical",
            "Missing module code",
            f"Could not identify module code for assessment {assessment_code}."
        )

    # Only summative assessments are readiness-checked for MAP calendar/deconfliction
    if is_summative:

        # DR-003: assessment type present
        if is_blank(assessment_type):
            add_issue(
                issues,
                module_code,
                assessment_code,
                "DR-003",
                "Critical",
                "Missing assessment type",
                "Assessment type is blank for a summative assessment."
            )

        # DR-004: assessment weight present
        if assessment_weight is None:
            add_issue(
                issues,
                module_code,
                assessment_code,
                "DR-004",
                "Critical",
                "Missing or invalid assessment weight",
                f"Assessment weight is missing or invalid: '{assessment_weight_raw}'."
            )
        else:
            weighting_by_module[module_code] += assessment_weight

        # Formal exams are excluded from coursework-style release/submission/feedback checks
        if not is_formal_exam:

            # DR-006: release date must be present for non-formal-exam summative assessments
            if release_date is None:
                add_issue(
                    issues,
                    module_code,
                    assessment_code,
                    "DR-006",
                    "Critical",
                    "Missing or invalid release date",
                    f"Predicted release date is missing or invalid: '{release_date_raw}'."
                )

            # DR-006: submission date must be present for non-formal-exam summative assessments
            if submission_date is None:
                add_issue(
                    issues,
                    module_code,
                    assessment_code,
                    "DR-006",
                    "Critical",
                    "Missing or invalid submission date",
                    f"Predicted submission date is missing or invalid: '{submission_date_raw}'."
                )

            # DR-008: feedback date must be present for non-formal-exam summative assessments
            if feedback_date is None:
                add_issue(
                    issues,
                    module_code,
                    assessment_code,
                    "DR-008",
                    "Critical",
                    "Missing predicted feedback date",
                    "Predicted feedback date is missing for a non-formal-exam summative assessment."
                )

            # DR-006: release <= submission
            # Same-day release and submission is allowed.
            if release_date is not None and submission_date is not None:
                if release_date > submission_date:
                    add_issue(
                        issues,
                        module_code,
                        assessment_code,
                        "DR-006",
                        "Critical",
                        "Invalid date sequence",
                        "Predicted release date is after predicted submission date."
                    )

            # DR-007: submission <= feedback
            # Same-day submission and feedback is allowed.
            if submission_date is not None and feedback_date is not None:
                if submission_date > feedback_date:
                    add_issue(
                        issues,
                        module_code,
                        assessment_code,
                        "DR-007",
                        "Critical",
                        "Invalid feedback sequence",
                        "Predicted feedback date is before predicted submission date."
                    )

            # DR-011: feedback within 20 working days
            # This is a Warning for MVP, because some cases may need academic/contextual review.
            if submission_date is not None and feedback_date is not None:
                if submission_to_feedback_working_days is not None and submission_to_feedback_working_days > 20:
                    add_issue(
                        issues,
                        module_code,
                        assessment_code,
                        "DR-011",
                        "Warning",
                        "Feedback exceeds 20 working days",
                        f"Predicted feedback is {submission_to_feedback_working_days} working days after submission, which exceeds the 20-working-day expectation."
                    )

        # DR-009: calendar inclusion clear
        if include_calendar_raw == "":
            add_issue(
                issues,
                module_code,
                assessment_code,
                "DR-009",
                "Warning",
                "Calendar inclusion unclear",
                "Include in EEECS Calendar is blank."
            )

    date_checks.append({
        "Academic Year": ACADEMIC_YEAR,
        "Module Code": module_code,
        "Assessment Code": assessment_code,
        "Assessment Title": assessment_title,
        "Assessment Type": assessment_type,
        "Is Summative": is_summative,
        "Is Formal Examination": is_formal_exam,
        "Include in EEECS Calendar": include_calendar,
        "Predicted Release Date Raw": release_date_raw,
        "Predicted Submission Date Raw": submission_date_raw,
        "Predicted Feedback Date Raw": feedback_date_raw,
        "Parsed Release Date": release_date.isoformat() if release_date else "",
        "Parsed Submission Date": submission_date.isoformat() if submission_date else "",
        "Parsed Feedback Date": feedback_date.isoformat() if feedback_date else "",
        "Release to Submission Calendar Days": days_between(release_date, submission_date),
        "Submission to Feedback Calendar Days": days_between(submission_date, feedback_date),
        "Submission to Feedback Working Days": submission_to_feedback_working_days,
    })

    clean_assessments.append({
        "Academic Year": ACADEMIC_YEAR,
        "Module Code": module_code,
        "Assessment Code": assessment_code,
        "Assessment Number": clean_text(row.get("Assessment Number", "")),
        "Assessment Title": assessment_title,
        "Assessment Type": assessment_type,
        "Assessment Weight": assessment_weight if assessment_weight is not None else "",
        "Assessment Mode": clean_text(row.get("Assessment Mode", "")),
        "Is Summative": is_summative,
        "Is Formal Examination": is_formal_exam,
        "Include in EEECS Calendar": include_calendar,
        "Assessment Lead": clean_text(row.get("Assessment Lead", "")),
        "Assessment Period": clean_text(row.get("Assessment Period", "")),
        "Predicted Release Date": release_date.isoformat() if release_date else "",
        "Predicted Submission Date": submission_date.isoformat() if submission_date else "",
        "Predicted Feedback Date": feedback_date.isoformat() if feedback_date else "",
        "Submission to Feedback Working Days": submission_to_feedback_working_days,
        "Original Module Plan": module_plan_ref,
    })


# ---------------------------------------------------------------------
# DR-005: Weighting total checks
# ---------------------------------------------------------------------

weighting_totals = []

for module_code, total_weight in sorted(weighting_by_module.items()):
    cat_row = catalogue_by_code.get(module_code, {})
    cats = parse_number(cat_row.get("CATS", ""))

    status = "OK"

    if abs(total_weight - 100.0) <= 0.01:
        status = "OK"
    elif cats == 0 and abs(total_weight - 0.0) <= 0.01:
        status = "Approved exception / 0-CATS"
        add_issue(
            issues,
            module_code,
            "",
            "DR-005",
            "Exception",
            "Approved 0-CATS/pass-fail exception",
            f"Module {module_code} has 0 CATS and total assessment weighting of 0%."
        )
    else:
        status = "Issue"
        add_issue(
            issues,
            module_code,
            "",
            "DR-005",
            "Critical",
            "Assessment weighting total not 100%",
            f"Summative assessment weights total {round(total_weight, 2)}%, not 100%."
        )

    weighting_totals.append({
        "Academic Year": ACADEMIC_YEAR,
        "Module Code": module_code,
        "Total Assessment Weight": round(total_weight, 2),
        "CATS": cats if cats is not None else "",
        "Status": status,
    })


# ---------------------------------------------------------------------
# DR-010: Assessment count check
# ---------------------------------------------------------------------

for module_code, plan_rows in plans_by_module.items():
    # If duplicate plans exist, avoid confusing the count check
    if len(plan_rows) != 1:
        continue

    plan_row = plan_rows[0]
    expected_count = parse_int(plan_row.get("Number of Summative Assessments", ""))
    actual_count = summative_count_by_module.get(module_code, 0)

    if expected_count is not None and expected_count != actual_count:
        add_issue(
            issues,
            module_code,
            "",
            "DR-010",
            "Warning",
            "Assessment count mismatch",
            f"Module plan declares {expected_count} summative assessments, but {actual_count} summative assessment records were found."
        )


# ---------------------------------------------------------------------
# Module readiness status
# ---------------------------------------------------------------------

severity_rank = {
    "Critical": 4,
    "Warning": 2,
    "Exception": 1,
}

issues_by_module = defaultdict(list)

for issue in issues:
    module_code = issue.get("Module Code", "")
    if module_code:
        issues_by_module[module_code].append(issue)


module_status_rows = []

all_modules_to_report = sorted(
    set(catalogue_codes) |
    set(plans_by_module.keys()) |
    set(weighting_by_module.keys())
)

for module_code in all_modules_to_report:
    module_issues = issues_by_module.get(module_code, [])

    worst = 0
    for issue in module_issues:
        worst = max(worst, severity_rank.get(issue.get("Severity", ""), 0))

    if worst >= 4:
        status = "Critical issue"
    elif worst >= 2:
        status = "Ready with warning"
    elif worst >= 1:
        status = "Approved exception"
    else:
        status = "Ready"

    module_status_rows.append({
        "Academic Year": ACADEMIC_YEAR,
        "Module Code": module_code,
        "Module Title": clean_text(catalogue_by_code.get(module_code, {}).get("Module Title", "")),
        "Readiness Status": status,
        "Issue Count": len(module_issues),
        "Critical Issues": sum(1 for x in module_issues if x.get("Severity") == "Critical"),
        "Warnings": sum(1 for x in module_issues if x.get("Severity") == "Warning"),
        "Exceptions": sum(1 for x in module_issues if x.get("Severity") == "Exception"),
    })


# ---------------------------------------------------------------------
# Run log
# ---------------------------------------------------------------------

issue_counts = Counter(issue["Severity"] for issue in issues)

run_log = [{
    "Run ID": f"DR-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
    "Academic Year": ACADEMIC_YEAR,
    "Agent Name": "MAP Intake and Data Readiness Agent",
    "Run Timestamp": datetime.now().isoformat(timespec="seconds"),
    "Input Folder": str(INPUT_FOLDER),
    "Output Folder": str(OUTPUT_FOLDER),
    "Module Catalogue Rows": len(module_catalogue),
    "Module Plan Rows": len(module_plans),
    "Assessment Rows": len(assessments),
    "Clean Assessment Rows": len(clean_assessments),
    "Total Issues": len(issues),
    "Critical Issues": issue_counts.get("Critical", 0),
    "Warnings": issue_counts.get("Warning", 0),
    "Exceptions": issue_counts.get("Exception", 0),
    "Status": "Completed",
}]


# ---------------------------------------------------------------------
# Write outputs
# ---------------------------------------------------------------------

write_csv(OUTPUT_FOLDER / "clean_assessments.csv", clean_assessments)
write_csv(OUTPUT_FOLDER / "readiness_issues.csv", issues)
write_csv(OUTPUT_FOLDER / "module_readiness_status.csv", module_status_rows)
write_csv(OUTPUT_FOLDER / "weighting_totals.csv", weighting_totals)
write_csv(OUTPUT_FOLDER / "date_checks.csv", date_checks)
write_csv(OUTPUT_FOLDER / "run_log.csv", run_log)


# ---------------------------------------------------------------------
# Print summary
# ---------------------------------------------------------------------

print("\nMAP Data Readiness Agent completed.")
print("=" * 60)
print(f"Clean assessment rows: {len(clean_assessments)}")
print(f"Total issues: {len(issues)}")
print(f"Critical issues: {issue_counts.get('Critical', 0)}")
print(f"Warnings: {issue_counts.get('Warning', 0)}")
print(f"Exceptions: {issue_counts.get('Exception', 0)}")
print(f"Output folder: {OUTPUT_FOLDER}")

print("\nFiles created:")
print("- clean_assessments.csv")
print("- readiness_issues.csv")
print("- module_readiness_status.csv")
print("- weighting_totals.csv")
print("- date_checks.csv")
print("- run_log.csv")