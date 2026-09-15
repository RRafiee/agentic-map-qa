from pathlib import Path
from datetime import datetime, date
import csv
import re


def find_project_root():
    current = Path(__file__).resolve().parent

    for parent in [current] + list(current.parents):
        if (parent / "data").exists() and (parent / "outputs").exists() and (parent / "src").exists():
            return parent

    raise RuntimeError("Could not find project root.")


ROOT = find_project_root()
BASE = ROOT / "outputs" / "2026_27_readiness_03Sep"
CASE_OUTPUT = BASE / "deconfliction_cases"
APD_PACK_OUTPUT = CASE_OUTPUT / "apd_review_packs"

CLEAN_ASSESSMENTS_FILE = BASE / "clean_assessments.csv"
APD_REVIEW_PACK_FILE = CASE_OUTPUT / "MAP_APD_Review_Pack.csv"


INDEPENDENT_STUDY_RANGES = [
    (date(2026, 10, 26), date(2026, 11, 1)),
    (date(2027, 2, 8), date(2027, 2, 14)),
]

QUB_CLOSURE_RANGES = [
    (date(2026, 12, 23), date(2027, 1, 1)),
    (date(2027, 3, 26), date(2027, 4, 2)),
]

FORMAL_ASSESSMENT_RANGES = [
    (date(2027, 5, 3), date(2027, 5, 30)),
]


def read_csv(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean(value):
    return "" if value is None else str(value).strip()


def parse_date(value):
    value = clean(value)

    if not value:
        return None

    # Ignore operational text such as "14/12/2026 AM/PM separation"
    if "AM/PM" in value.upper():
        return None

    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass

    return None


def date_in_ranges(target_date, ranges):
    if target_date is None:
        return False

    for start, end in ranges:
        if start <= target_date <= end:
            return True

    return False


def extract_assessment_codes(row):
    text = "; ".join([
        clean(row.get("Assessment A", "")),
        clean(row.get("Assessment B", "")),
    ])

    return sorted(set(re.findall(r"[A-Z]{3}\d{4}_\d{4}_\d+", text)))


def latest_release_date_for_codes(codes, assessment_lookup):
    dates = []

    for code in codes:
        row = assessment_lookup.get(code, {})
        release_date = parse_date(row.get("Predicted Release Date", ""))

        if release_date:
            dates.append(release_date)

    return max(dates) if dates else None


clean_assessments = read_csv(CLEAN_ASSESSMENTS_FILE)
apd_rows = read_csv(APD_REVIEW_PACK_FILE)

assessment_lookup = {
    clean(row.get("Assessment Code", "")): row
    for row in clean_assessments
    if clean(row.get("Assessment Code", ""))
}

date_format_issues = []
before_release_issues = []
blocked_date_issues = []
stale_joseph_files = []

for row in apd_rows:
    case_id = clean(row.get("Case ID", ""))
    codes = extract_assessment_codes(row)
    latest_release = latest_release_date_for_codes(codes, assessment_lookup)

    for col in [
        "Submission Date A",
        "Submission Date B",
        "Suggested Alternative Date 1",
        "Suggested Alternative Date 2",
        "Suggested Alternative Date 3",
    ]:
        value = clean(row.get(col, ""))

        if not value:
            continue

        if "AM/PM" in value.upper():
            continue

        parsed = parse_date(value)

        if parsed is None:
            date_format_issues.append((case_id, col, value))
            continue

        # Check visible format is UK DD/MM/YYYY
        if not re.fullmatch(r"\d{2}/\d{2}/\d{4}", value):
            date_format_issues.append((case_id, col, value))

        # Only alternative dates need release-date and blocked-date checks
        if col.startswith("Suggested Alternative Date"):
            if latest_release and parsed < latest_release:
                before_release_issues.append(
                    (case_id, col, value, latest_release.strftime("%d/%m/%Y"))
                )

            if parsed.weekday() >= 5:
                blocked_date_issues.append((case_id, col, value, "Weekend"))

            if date_in_ranges(parsed, INDEPENDENT_STUDY_RANGES):
                blocked_date_issues.append((case_id, col, value, "Independent Study Week"))

            if date_in_ranges(parsed, QUB_CLOSURE_RANGES):
                blocked_date_issues.append((case_id, col, value, "QUB closure period"))

            if date_in_ranges(parsed, FORMAL_ASSESSMENT_RANGES):
                blocked_date_issues.append((case_id, col, value, "Formal Assessment Period"))


for file in APD_PACK_OUTPUT.glob("*.csv"):
    if "Joseph" in file.name:
        stale_joseph_files.append(file.name)


print("=" * 80)
print("MAP DECONFLICTION OUTPUT VALIDATION")
print("=" * 80)

print(f"APD review pack rows checked: {len(apd_rows)}")
print(f"Assessment lookup rows: {len(assessment_lookup)}")
print(f"Date format issues: {len(date_format_issues)}")
print(f"Alternative dates before release date: {len(before_release_issues)}")
print(f"Blocked alternative date issues: {len(blocked_date_issues)}")
print(f"Stale Joseph APD files: {len(stale_joseph_files)}")

if date_format_issues:
    print("\nDate format issues - first 20")
    for item in date_format_issues[:20]:
        print(item)

if before_release_issues:
    print("\nAlternative dates before release - first 20")
    for item in before_release_issues[:20]:
        print(item)

if blocked_date_issues:
    print("\nBlocked alternative date issues - first 20")
    for item in blocked_date_issues[:20]:
        print(item)

if stale_joseph_files:
    print("\nStale Joseph files")
    for item in stale_joseph_files:
        print(item)

print("\nExpected clean result:")
print("- Date format issues: 0")
print("- Alternative dates before release date: 0")
print("- Blocked alternative date issues: 0")
print("- Stale Joseph APD files: 0")