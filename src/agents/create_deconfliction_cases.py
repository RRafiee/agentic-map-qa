"""
MAP Deconfliction Case Builder v0.5

Purpose:
Creates APD-ready MAP deconfliction outputs from mapped cohort outputs.

Inputs:
- outputs/2026_27_readiness_03Sep/programme_cohort_mapping/cohort_same_day_pressure.csv
- outputs/2026_27_readiness_03Sep/programme_cohort_mapping/cohort_near_date_pressure.csv
- outputs/2026_27_readiness_03Sep/programme_cohort_mapping/affected_cohort_assessments.csv
- outputs/2026_27_readiness_03Sep/programme_cohort_mapping/unmapped_calendar_modules.csv
- outputs/2026_27_readiness_03Sep/readiness_issues.csv
- outputs/2026_27_readiness_03Sep/clean_assessments.csv

Outputs:
- MAP_Deconfliction_Cases_Draft.csv
- MAP_Feedback_Timing_Warnings.csv
- MAP_Calendar_Rule_Warnings.csv
- MAP_Unmapped_Calendar_Modules.csv
- MAP_Assessment_Only_Manual_Cases.csv
- MAP_APD_Review_Pack.csv
- apd_review_packs/*.csv

This is deterministic.
It does not use Gemini.
It does not approve, change, or publish dates.

v0.5 update:
- APD-facing and human-facing output dates are formatted as British DD/MM/YYYY.
- Internal date processing remains date-object based / ISO-safe.
- Suggested alternative dates are constrained so they are not earlier than the latest
  predicted release date of the assessment(s) involved in the case.
"""

from pathlib import Path
from datetime import datetime, timedelta, date
from collections import defaultdict
import csv
import re


# ---------------------------------------------------------------------
# Find project root safely
# ---------------------------------------------------------------------

def find_project_root():
    current = Path(__file__).resolve().parent

    for parent in [current] + list(current.parents):
        if (parent / "data").exists() and (parent / "outputs").exists() and (parent / "src").exists():
            return parent

    raise RuntimeError("Could not find project root.")


ROOT = find_project_root()

BASE = ROOT / "outputs" / "2026_27_readiness_03Sep"
MAPPING_OUTPUT = BASE / "programme_cohort_mapping"
CASE_OUTPUT = BASE / "deconfliction_cases"
APD_PACK_OUTPUT = CASE_OUTPUT / "apd_review_packs"

CASE_OUTPUT.mkdir(parents=True, exist_ok=True)
APD_PACK_OUTPUT.mkdir(parents=True, exist_ok=True)

# Remove stale APD-specific CSV files from previous runs.
# This prevents old routing files, such as a previous Dr_Joseph_Dexter.csv,
# from remaining in the folder after APD responsibility changes.
for old_file in APD_PACK_OUTPUT.glob("*.csv"):
    old_file.unlink()

SAME_DAY_FILE = MAPPING_OUTPUT / "cohort_same_day_pressure.csv"
NEAR_DATE_FILE = MAPPING_OUTPUT / "cohort_near_date_pressure.csv"
AFFECTED_FILE = MAPPING_OUTPUT / "affected_cohort_assessments.csv"
UNMAPPED_FILE = MAPPING_OUTPUT / "unmapped_calendar_modules.csv"
READINESS_ISSUES_FILE = BASE / "readiness_issues.csv"
CLEAN_ASSESSMENTS_FILE = BASE / "clean_assessments.csv"

ACADEMIC_YEAR = "2026/27"


# ---------------------------------------------------------------------
# Calendar rules for 2026/27
# ---------------------------------------------------------------------

# Independent Study Weeks: no assessment submissions / class tests.
INDEPENDENT_STUDY_RANGES = [
    (date(2026, 10, 26), date(2026, 11, 1)),   # S1 W06
    (date(2027, 2, 8), date(2027, 2, 14)),     # S2 independent study week / W17
]

# QUB closure periods shown on the EEECS calendar.
QUB_CLOSURE_RANGES = [
    (date(2026, 12, 23), date(2027, 1, 1)),    # Christmas closure
    (date(2027, 3, 26), date(2027, 4, 2)),     # Easter closure
]

# Formal assessment period: do not suggest alternative coursework/class-test dates here.
FORMAL_ASSESSMENT_RANGES = [
    (date(2027, 5, 3), date(2027, 5, 30)),
]

# Normal windows for suggested alternatives.
SEMESTER_WINDOWS = [
    ("Semester 1", date(2026, 9, 21), date(2026, 12, 20)),
    ("Semester 2", date(2027, 1, 18), date(2027, 5, 2)),
]

SPECIAL_AVOID_DATES = {
    date(2027, 3, 17): "St Patrick's Day",
}

ASSESSMENT_ONLY_MODULES = {
    "CSC1034",
}


# ---------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------

def read_csv(path):
    if not path.exists():
        print(f"Warning: missing file: {path}")
        return []

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


def clean(value):
    return "" if value is None else str(value).replace("\ufeff", "").strip()


def yes(value):
    return clean(value).lower() in {"yes", "y", "true", "1", "checked"}


def parse_date(value):
    """
    Parses internal ISO dates and UK-facing DD/MM/YYYY dates.

    Internal agent files normally use YYYY-MM-DD.
    APD-facing outputs use DD/MM/YYYY.
    """
    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    value = clean(value)
    if value == "":
        return None

    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass

    return None


def format_date_uk(value):
    """
    Converts a date object or date string into British format DD/MM/YYYY.

    Keeps non-date operational text unchanged, for example:
    '14/12/2026 AM/PM separation'.
    """
    if value is None:
        return ""

    if isinstance(value, datetime):
        return value.date().strftime("%d/%m/%Y")

    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")

    value = clean(value)
    if value == "":
        return ""

    parsed = parse_date(value)
    if parsed:
        return parsed.strftime("%d/%m/%Y")

    return value


def date_to_text(value):
    """
    Human-facing date text for APD outputs.
    """
    return format_date_uk(value)


def sort_date_key(value):
    parsed = parse_date(value)
    if parsed:
        return parsed.isoformat()
    return clean(value)


def to_float(value):
    value = clean(value).replace("%", "").replace(",", "")
    if value == "":
        return 0.0

    try:
        return float(value)
    except ValueError:
        return 0.0


def normalise_case_part(*parts):
    return "|".join(clean(p).upper() for p in parts if clean(p))


def safe_filename(value):
    value = clean(value)
    value = re.sub(r"[^A-Za-z0-9]+", "_", value)
    value = value.strip("_")
    return value or "Unassigned"


def date_in_ranges(target_date, ranges):
    if target_date is None:
        return False

    for start, end in ranges:
        if start <= target_date <= end:
            return True

    return False


def semester_window_for(target_date):
    if target_date is None:
        return None

    for name, start, end in SEMESTER_WINDOWS:
        if start <= target_date <= end:
            return (name, start, end)

    return None


def blocked_reasons_for_date(target_date, for_alternative=True):
    reasons = []

    if target_date is None:
        return ["Invalid or missing date"]

    if target_date.weekday() >= 5:
        reasons.append("Weekend")

    if date_in_ranges(target_date, INDEPENDENT_STUDY_RANGES):
        reasons.append("Independent Study Week")

    if date_in_ranges(target_date, QUB_CLOSURE_RANGES):
        reasons.append("QUB closure period")

    if target_date in SPECIAL_AVOID_DATES:
        reasons.append(SPECIAL_AVOID_DATES[target_date])

    if for_alternative and date_in_ranges(target_date, FORMAL_ASSESSMENT_RANGES):
        reasons.append("Formal Assessment Period")

    return reasons


def apd_owner_from_programme_stage(programme_stage_key):
    key = clean(programme_stage_key).upper()

    if key in {
        "BSC-CS-L1", "MENG-CS-L1",
        "BENG-SE-L1", "MENG-SE-L1"
    }:
        return "Dr Leo Galway"

    if key in {
        "BSC-CS-L2", "MENG-CS-L2",
        "BENG-SE-L2", "MENG-SE-L2"
    }:
        return "Dr Darryl Stewart"

    if key in {
        "BSC-CS-L3", "MENG-CS-L3", "MENG-CS-L4",
        "BENG-SE-L3", "MENG-SE-L3", "MENG-SE-L4"
    }:
        return "Mr John Busch"

    if key in {
        "BENG-EEE-L1", "BENG-EEE-L2",
        "MENG-EEE-L1", "MENG-EEE-L2",
        "BENG-CE-L1", "BENG-CE-L2",
        "MENG-CE-L1", "MENG-CE-L2"
    }:
        return "Dr Ayesha Khalid"

    if key in {
        "BENG-EEE-L3", "MENG-EEE-L3", "MENG-EEE-L4",
        "BENG-CE-L3", "MENG-CE-L3", "MENG-CE-L4"
    }:
        return "Dr Maarten van Walstijn"

    if key.startswith("BSC-CIT") or key.startswith("BSC-BIT"):
        return "Ms Angela Allen"

    # Data Science
    if key.startswith("BSC-DS"):
        return "Dr Neil Anderson"

    return ""


def apd_owner_from_module_code(module_code):
    """
    Fallback only, used where no mapped cohort/APD is available.
    """
    code = clean(module_code).upper()
    match = re.search(r"([A-Z]{3})(\d)", code)

    if not match:
        return ""

    prefix = match.group(1)
    level_digit = match.group(2)

    if prefix == "CSC":
        if level_digit == "1":
            return "Dr Leo Galway"
        if level_digit == "2":
            return "Dr Darryl Stewart"
        if level_digit in {"3", "4"}:
            return "Mr John Busch"

    if prefix in {"ELE", "ECS", "MEE"}:
        if level_digit in {"1", "2"}:
            return "Dr Ayesha Khalid"
        if level_digit in {"3", "4"}:
            return "Dr Maarten van Walstijn"

    return ""


def make_pair_case_id(programme_stage_key, rule, assessment_a, assessment_b):
    ordered = sorted([clean(assessment_a), clean(assessment_b)])
    return normalise_case_part(
        ACADEMIC_YEAR,
        programme_stage_key,
        rule,
        ordered[0],
        ordered[1]
    ).replace("/", "-")


def make_cluster_case_id(programme_stage_key, rule, submission_date, modules):
    return normalise_case_part(
        ACADEMIC_YEAR,
        programme_stage_key,
        rule,
        submission_date,
        modules
    ).replace("/", "-")


def make_simple_case_id(section, module_code, assessment_code):
    return normalise_case_part(
        ACADEMIC_YEAR,
        section,
        module_code,
        assessment_code
    ).replace("/", "-")


def suggested_action(severity, certainty, rule, special_note=""):
    severity = clean(severity)
    certainty = clean(certainty)
    rule = clean(rule)

    if special_note:
        return special_note

    # Calendar rules must be handled before generic severity rules.
    # Otherwise a CAL-003 QUB-closure case could receive a generic
    # "shared-cohort clash" message, which is misleading.
    if rule == "CAL-001":
        return (
            "APD/module-owner review required. The date falls in Independent Study Week, "
            "which should normally be avoided for assessment submissions/class tests."
        )

    if rule == "CAL-002":
        return (
            "APD/module-owner review required. The date falls on a weekend and should "
            "normally be moved to a suitable working day."
        )

    if rule == "CAL-003":
        return (
            "Immediate APD/module-owner review required. The date falls within a QUB closure "
            "period and should normally be moved to a valid working day."
        )

    if rule.startswith("CAL-"):
        return (
            "APD/module-owner review required because the date falls in a blocked or "
            "discouraged calendar period."
        )

    if rule == "DR-011":
        return (
            "QA/APD review of feedback timing; confirm whether feedback can be returned "
            "within 20 working days or whether a justification is needed."
        )

    if severity == "Critical" and certainty == "Definite":
        return "Immediate APD review; module-owner follow-up likely required."

    if severity == "Critical":
        return (
            "APD review required; confirm whether this is a real shared-cohort clash "
            "or an acceptable exception."
        )

    if severity == "High":
        return "APD sense-check required; consider whether one assessment date should move."

    return "Review if time allows; may be acceptable depending on cohort exposure and assessment type."

def build_cohort_date_lookup(affected_rows):
    lookup = defaultdict(lambda: defaultdict(list))

    for row in affected_rows:
        programme_stage_key = clean(row.get("Programme Stage Key", ""))
        submission_date = parse_date(row.get("Predicted Submission Date", ""))

        if programme_stage_key and submission_date:
            lookup[programme_stage_key][submission_date].append(row)

    return lookup


def build_assessment_lookup(clean_assessments):
    lookup = {}

    for row in clean_assessments:
        assessment_code = clean(row.get("Assessment Code", ""))

        if assessment_code:
            lookup[assessment_code] = row

    return lookup


def latest_release_date_for_assessments(assessment_codes, assessment_lookup):
    """
    Returns the latest predicted release date for the assessment code(s) involved
    in a case.

    This is used to prevent suggested alternative submission/class-test dates
    from being earlier than the assessment release date. For pair/cluster cases,
    using the latest release date is safest because the system does not decide
    which module should move.
    """
    release_dates = []

    for assessment_code in assessment_codes:
        assessment = assessment_lookup.get(clean(assessment_code), {})
        release_date = parse_date(assessment.get("Predicted Release Date", ""))

        if release_date is not None:
            release_dates.append(release_date)

    if not release_dates:
        return None

    return max(release_dates)


def build_module_and_assessment_apd_lookups(affected_rows):
    module_to_apds = defaultdict(set)
    module_to_cohorts = defaultdict(set)
    assessment_to_apds = defaultdict(set)
    assessment_to_cohorts = defaultdict(set)

    for row in affected_rows:
        module_code = clean(row.get("Module Code", ""))
        assessment_code = clean(row.get("Assessment Code", ""))
        programme_stage_key = clean(row.get("Programme Stage Key", ""))
        apd = apd_owner_from_programme_stage(programme_stage_key)

        if module_code and apd:
            module_to_apds[module_code].add(apd)

        if module_code and programme_stage_key:
            module_to_cohorts[module_code].add(programme_stage_key)

        if assessment_code and apd:
            assessment_to_apds[assessment_code].add(apd)

        if assessment_code and programme_stage_key:
            assessment_to_cohorts[assessment_code].add(programme_stage_key)

    return module_to_apds, module_to_cohorts, assessment_to_apds, assessment_to_cohorts


def join_sorted(values):
    cleaned = sorted(set(clean(v) for v in values if clean(v)))
    return "; ".join(cleaned)


def generate_candidate_dates(anchor_dates):
    """
    Generates candidate dates near the current assessment date.
    We prefer nearby dates, but allow up to roughly two weeks either side.
    """
    anchor_dates = sorted(set(d for d in anchor_dates if d is not None))
    seen = set()

    offsets = (
        list(range(-7, 0)) +
        list(range(1, 8)) +
        list(range(-14, -7)) +
        list(range(8, 15))
    )

    for anchor in anchor_dates:
        for offset in offsets:
            candidate = anchor + timedelta(days=offset)

            if candidate not in seen:
                seen.add(candidate)
                yield candidate


def suggest_alternative_dates_for_cohorts(
    cohort_keys,
    original_dates,
    cohort_date_lookup,
    earliest_allowed_date=None,
    max_suggestions=3,
):
    """
    Suggests alternative working dates.

    Rules:
    - same semester where possible
    - no weekends
    - no Independent Study Week
    - no QUB closure dates
    - no Formal Assessment Period
    - no date earlier than the latest predicted release date of the involved assessment(s)
    - avoid dates already used by the same affected cohort(s)
    - prefer dates more than 2 days away from other known assessments
    """
    cohort_keys = [clean(x) for x in cohort_keys if clean(x)]
    original_dates = sorted(set(d for d in original_dates if d is not None))

    if not original_dates:
        return []

    earliest_allowed_date = parse_date(earliest_allowed_date)

    main_anchor = original_dates[0]
    semester_window = semester_window_for(main_anchor)

    occupied_dates = set()

    for cohort_key in cohort_keys:
        occupied_dates.update(cohort_date_lookup.get(cohort_key, {}).keys())

    original_date_set = set(original_dates)

    strict_suggestions = []
    relaxed_suggestions = []

    for candidate in generate_candidate_dates(original_dates):
        if semester_window is not None:
            _, start, end = semester_window

            if not (start <= candidate <= end):
                continue

        if earliest_allowed_date is not None and candidate < earliest_allowed_date:
            continue

        blocked_reasons = blocked_reasons_for_date(candidate, for_alternative=True)
        if blocked_reasons:
            continue

        if candidate in original_date_set:
            continue

        if candidate in occupied_dates:
            continue

        other_occupied_dates = [d for d in occupied_dates if d not in original_date_set]
        nearest_gap = min(
            [abs((candidate - d).days) for d in other_occupied_dates],
            default=999
        )

        if nearest_gap > 2:
            strict_suggestions.append({
                "date": format_date_uk(candidate),
                "rationale": "Nearby working day in the same semester; on/after the relevant assessment release date; not in Independent Study Week, weekend, QUB closure or Formal Assessment Period; no known same-cohort assessment within 2 days."
            })
        else:
            relaxed_suggestions.append({
                "date": format_date_uk(candidate),
                "rationale": "Nearby working day in the same semester and on/after the relevant assessment release date with no known same-day cohort clash; however, APD should sense-check near-date workload."
            })

        if len(strict_suggestions) >= max_suggestions:
            break

    suggestions = strict_suggestions[:max_suggestions]

    if len(suggestions) < max_suggestions:
        needed = max_suggestions - len(suggestions)
        suggestions.extend(relaxed_suggestions[:needed])

    return suggestions[:max_suggestions]


def add_alternative_date_fields(case, suggestions):
    for i in range(1, 4):
        if i <= len(suggestions):
            case[f"Suggested Alternative Date {i}"] = suggestions[i - 1].get("date", "")
            case[f"Alternative Date {i} Rationale"] = suggestions[i - 1].get("rationale", "")
        else:
            case[f"Suggested Alternative Date {i}"] = ""
            case[f"Alternative Date {i} Rationale"] = ""


def is_csc1025_csc1026_hla_case(modules, dates):
    modules = {clean(m).upper() for m in modules if clean(m)}
    dates = {d for d in dates if d is not None}

    return (
        {"CSC1025", "CSC1026"}.issubset(modules)
        and date(2026, 12, 14) in dates
    )


def split_modules(modules_text):
    return [clean(x).upper() for x in clean(modules_text).split(";") if clean(x)]


def split_semicolon_values(values_text):
    return [clean(x) for x in clean(values_text).split(";") if clean(x)]


def severity_order_value(severity):
    order = {
        "Critical": 1,
        "High": 2,
        "Warning": 3,
        "Advisory": 4,
        "Exception": 5,
    }
    return order.get(clean(severity), 99)


# ---------------------------------------------------------------------
# Load input files
# ---------------------------------------------------------------------

print("Loading deconfliction inputs...")

same_day_rows = read_csv(SAME_DAY_FILE)
near_date_rows = read_csv(NEAR_DATE_FILE)
affected_rows = read_csv(AFFECTED_FILE)
unmapped_input_rows = read_csv(UNMAPPED_FILE)
readiness_issues = read_csv(READINESS_ISSUES_FILE)
clean_assessments = read_csv(CLEAN_ASSESSMENTS_FILE)

print(f"Same-day rows: {len(same_day_rows)}")
print(f"Near-date rows: {len(near_date_rows)}")
print(f"Affected cohort assessment rows: {len(affected_rows)}")
print(f"Unmapped calendar module rows: {len(unmapped_input_rows)}")
print(f"Readiness issue rows: {len(readiness_issues)}")
print(f"Clean assessment rows: {len(clean_assessments)}")


cohort_date_lookup = build_cohort_date_lookup(affected_rows)
assessment_lookup = build_assessment_lookup(clean_assessments)

module_to_apds, module_to_cohorts, assessment_to_apds, assessment_to_cohorts = (
    build_module_and_assessment_apd_lookups(affected_rows)
)

created_on = datetime.now().isoformat(timespec="seconds")


# ---------------------------------------------------------------------
# Build main deconfliction cases
# ---------------------------------------------------------------------

deconfliction_cases = []
seen_case_ids = set()


# Same-day cluster cases
for row in same_day_rows:
    programme_stage_key = clean(row.get("Programme Stage Key", ""))
    submission_date_text = clean(row.get("Submission Date", ""))
    submission_date = parse_date(submission_date_text)
    modules_text = clean(row.get("Modules", ""))
    modules = split_modules(modules_text)
    rule = clean(row.get("Rule Triggered", "C-001"))
    severity = clean(row.get("Indicative Severity", "Critical"))
    certainty = clean(row.get("Conflict Certainty Summary", "Definite or Potential - check assessment pair details"))

    case_id = make_cluster_case_id(programme_stage_key, rule, submission_date_text, modules_text)

    if case_id in seen_case_ids:
        continue

    seen_case_ids.add(case_id)

    hla_special = is_csc1025_csc1026_hla_case(modules, [submission_date])

    if hla_special:
        recommended_action = (
            "Known HLA operational constraint: CSC1025 and CSC1026 are both on Monday 14 December 2026. "
            "Date movement may not be appropriate because HLA students attend on Mondays. "
            "Recommended resolution is same-day time separation, for example one assessment in the morning and one in the afternoon, "
            "subject to lab availability and reasonable-adjustment requirements."
        )
        suggestions = [
            {
                "date": "14/12/2026 AM/PM separation",
                "rationale": "HLA-specific operational resolution: keep the Monday date but separate the two assessment times sufficiently."
            }
        ]
    else:
        recommended_action = suggested_action(severity, certainty, rule)
        assessment_codes = split_semicolon_values(row.get("Assessment Codes", ""))
        earliest_allowed_date = latest_release_date_for_assessments(
            assessment_codes,
            assessment_lookup,
        )
        suggestions = suggest_alternative_dates_for_cohorts(
            [programme_stage_key],
            [submission_date],
            cohort_date_lookup,
            earliest_allowed_date=earliest_allowed_date,
        )

    case = {
        "Pack Section": "Date deconfliction",
        "Case ID": case_id,
        "Academic Year": ACADEMIC_YEAR,
        "Case Source": "Conflict Detection Agent",
        "Case Type": "Same-day assessment cluster",
        "Programme Stage Key": programme_stage_key,
        "APD Owner": apd_owner_from_programme_stage(programme_stage_key),
        "Rule Triggered": rule,
        "Severity": severity,
        "Conflict Certainty": certainty,
        "Date Gap": "0",
        "Submission Date A": format_date_uk(submission_date),
        "Submission Date B": format_date_uk(submission_date),
        "Module A": modules_text,
        "Assessment A": clean(row.get("Assessment Codes", "")),
        "Title A": clean(row.get("Assessment Titles", "")),
        "Weight A": clean(row.get("Total Weighting", "")),
        "Module B": "",
        "Assessment B": "",
        "Title B": "",
        "Weight B": "",
        "Combined Weight": clean(row.get("Total Weighting", "")),
        "Evidence Summary": clean(row.get("Evidence Summary", "")),
        "Recommended Action": recommended_action,
        "Suggested Module to Move": "APD/module owners to decide",
        "Review Status": "Awaiting APD Review",
        "APD Decision": "",
        "APD Comments": "",
        "Final Agreed Action": "",
        "Calendar Ready": "No",
        "Created On": created_on,
    }

    add_alternative_date_fields(case, suggestions)
    deconfliction_cases.append(case)


# Near-date pair cases
for row in near_date_rows:
    rule = clean(row.get("Rule Triggered", ""))
    gap = clean(row.get("Date Gap", ""))

    # Same-day cases are already represented as cluster cases above.
    if rule == "C-001" or gap == "0":
        continue

    programme_stage_key = clean(row.get("Programme Stage Key", ""))
    assessment_a = clean(row.get("Assessment A", ""))
    assessment_b = clean(row.get("Assessment B", ""))

    case_id = make_pair_case_id(programme_stage_key, rule, assessment_a, assessment_b)

    if case_id in seen_case_ids:
        continue

    seen_case_ids.add(case_id)

    severity = clean(row.get("Indicative Severity", ""))
    certainty = clean(row.get("Conflict Certainty", ""))
    date_a = parse_date(row.get("Submission Date A", ""))
    date_b = parse_date(row.get("Submission Date B", ""))

    modules = [
        clean(row.get("Module A", "")).upper(),
        clean(row.get("Module B", "")).upper(),
    ]

    hla_special = is_csc1025_csc1026_hla_case(modules, [date_a, date_b])

    if hla_special:
        recommended_action = (
            "Known HLA operational constraint: CSC1025 and CSC1026 are both on Monday 14 December 2026. "
            "Date movement may not be appropriate. Recommended resolution is same-day time separation, "
            "subject to lab availability and reasonable-adjustment requirements."
        )
        suggestions = [
            {
                "date": "14/12/2026 AM/PM separation",
                "rationale": "HLA-specific operational resolution: keep the Monday date but separate the two assessment times sufficiently."
            }
        ]
    else:
        recommended_action = suggested_action(severity, certainty, rule)
        earliest_allowed_date = latest_release_date_for_assessments(
            [assessment_a, assessment_b],
            assessment_lookup,
        )
        suggestions = suggest_alternative_dates_for_cohorts(
            [programme_stage_key],
            [date_a, date_b],
            cohort_date_lookup,
            earliest_allowed_date=earliest_allowed_date,
        )

    case = {
        "Pack Section": "Date deconfliction",
        "Case ID": case_id,
        "Academic Year": ACADEMIC_YEAR,
        "Case Source": "Conflict Detection Agent",
        "Case Type": "Near-date assessment pair",
        "Programme Stage Key": programme_stage_key,
        "APD Owner": apd_owner_from_programme_stage(programme_stage_key),
        "Rule Triggered": rule,
        "Severity": severity,
        "Conflict Certainty": certainty,
        "Date Gap": gap,
        "Submission Date A": format_date_uk(date_a),
        "Submission Date B": format_date_uk(date_b),
        "Module A": clean(row.get("Module A", "")),
        "Assessment A": assessment_a,
        "Title A": clean(row.get("Title A", "")),
        "Weight A": clean(row.get("Weight A", "")),
        "Module B": clean(row.get("Module B", "")),
        "Assessment B": assessment_b,
        "Title B": clean(row.get("Title B", "")),
        "Weight B": clean(row.get("Weight B", "")),
        "Combined Weight": clean(row.get("Combined Weight", "")),
        "Evidence Summary": clean(row.get("Evidence Summary", "")),
        "Recommended Action": recommended_action,
        "Suggested Module to Move": "APD/module owners to decide",
        "Review Status": "Awaiting APD Review",
        "APD Decision": "",
        "APD Comments": "",
        "Final Agreed Action": "",
        "Calendar Ready": "No",
        "Created On": created_on,
    }

    add_alternative_date_fields(case, suggestions)
    deconfliction_cases.append(case)


# ---------------------------------------------------------------------
# Build feedback timing warning file
# ---------------------------------------------------------------------

feedback_warning_rows = []

for issue in readiness_issues:
    if clean(issue.get("Rule ID", "")) != "DR-011":
        continue

    module_code = clean(issue.get("Module Code", "")).upper()
    assessment_code = clean(issue.get("Assessment Code", ""))
    assessment = assessment_lookup.get(assessment_code, {})

    apds = module_to_apds.get(module_code, set())
    if not apds:
        fallback_apd = apd_owner_from_module_code(module_code)
        if fallback_apd:
            apds.add(fallback_apd)

    row = {
        "Pack Section": "Feedback timing warning",
        "Case ID": make_simple_case_id("FEEDBACK", module_code, assessment_code),
        "Academic Year": ACADEMIC_YEAR,
        "Case Source": "Data Readiness Agent",
        "Case Type": "Feedback timing warning",
        "Programme Stage Key": join_sorted(module_to_cohorts.get(module_code, set())),
        "APD Owner": join_sorted(apds),
        "Rule Triggered": "DR-011",
        "Severity": clean(issue.get("Severity", "Warning")),
        "Conflict Certainty": "Not a date-clash case",
        "Date Gap": "",
        "Submission Date A": format_date_uk(assessment.get("Predicted Submission Date", "")),
        "Submission Date B": "",
        "Module A": module_code,
        "Assessment A": assessment_code,
        "Title A": clean(assessment.get("Assessment Title", "")),
        "Weight A": clean(assessment.get("Assessment Weight", "")),
        "Module B": "",
        "Assessment B": "",
        "Title B": "",
        "Weight B": "",
        "Combined Weight": "",
        "Evidence Summary": clean(issue.get("Message", "")),
        "Recommended Action": suggested_action("Warning", "Not a date-clash case", "DR-011"),
        "Suggested Module to Move": "Not applicable",
        "Review Status": "QA/APD Review",
        "APD Decision": "",
        "APD Comments": "",
        "Final Agreed Action": "",
        "Calendar Ready": "No",
        "Created On": created_on,
    }

    add_alternative_date_fields(row, [])
    feedback_warning_rows.append(row)


# ---------------------------------------------------------------------
# Build calendar rule warnings
# ---------------------------------------------------------------------

calendar_warning_rows = []
seen_calendar_assessments = set()

for assessment in clean_assessments:
    assessment_code = clean(assessment.get("Assessment Code", ""))

    if assessment_code in seen_calendar_assessments:
        continue

    seen_calendar_assessments.add(assessment_code)

    module_code = clean(assessment.get("Module Code", "")).upper()
    is_summative = yes(assessment.get("Is Summative", ""))
    is_formal_exam = yes(assessment.get("Is Formal Examination", ""))
    include_calendar = yes(assessment.get("Include in EEECS Calendar", ""))
    submission_date = parse_date(assessment.get("Predicted Submission Date", ""))

    if not (is_summative and not is_formal_exam and include_calendar and submission_date is not None):
        continue

    reasons = blocked_reasons_for_date(submission_date, for_alternative=False)

    # For actual submitted dates, do not flag formal assessment period here.
    reasons = [r for r in reasons if r != "Formal Assessment Period"]

    if not reasons:
        continue

    if "QUB closure period" in reasons:
        rule = "CAL-003"
        severity = "Critical"
    elif "Independent Study Week" in reasons:
        rule = "CAL-001"
        severity = "High"
    elif "Weekend" in reasons:
        rule = "CAL-002"
        severity = "Warning"
    else:
        rule = "CAL-004"
        severity = "Warning"

    cohort_keys = assessment_to_cohorts.get(assessment_code, set())
    apds = assessment_to_apds.get(assessment_code, set())

    if not apds:
        fallback_apd = apd_owner_from_module_code(module_code)
        if fallback_apd:
            apds.add(fallback_apd)

    earliest_allowed_date = latest_release_date_for_assessments(
        [assessment_code],
        assessment_lookup,
    )

    suggestions = suggest_alternative_dates_for_cohorts(
        cohort_keys,
        [submission_date],
        cohort_date_lookup,
        earliest_allowed_date=earliest_allowed_date,
    )

    row = {
        "Pack Section": "Calendar rule warning",
        "Case ID": make_simple_case_id("CALENDAR", module_code, assessment_code),
        "Academic Year": ACADEMIC_YEAR,
        "Case Source": "Calendar Rule Check",
        "Case Type": "Calendar rule warning",
        "Programme Stage Key": join_sorted(cohort_keys),
        "APD Owner": join_sorted(apds),
        "Rule Triggered": rule,
        "Severity": severity,
        "Conflict Certainty": "Calendar rule issue",
        "Date Gap": "",
        "Submission Date A": format_date_uk(submission_date),
        "Submission Date B": "",
        "Module A": module_code,
        "Assessment A": assessment_code,
        "Title A": clean(assessment.get("Assessment Title", "")),
        "Weight A": clean(assessment.get("Assessment Weight", "")),
        "Module B": "",
        "Assessment B": "",
        "Title B": "",
        "Weight B": "",
        "Combined Weight": "",
        "Evidence Summary": f"Predicted submission/class-test date falls on: {'; '.join(reasons)}.",
        "Recommended Action": suggested_action(severity, "Calendar rule issue", rule),
        "Suggested Module to Move": module_code,
        "Review Status": "Awaiting APD Review",
        "APD Decision": "",
        "APD Comments": "",
        "Final Agreed Action": "",
        "Calendar Ready": "No",
        "Created On": created_on,
    }

    add_alternative_date_fields(row, suggestions)
    calendar_warning_rows.append(row)


# ---------------------------------------------------------------------
# Build unmapped and assessment-only manual case files
# ---------------------------------------------------------------------

unmapped_rows = []
assessment_only_rows = []

for row in unmapped_input_rows:
    module_code = clean(row.get("Module Code", "")).upper()
    assessment_code = clean(row.get("Example Assessment Code", ""))

    if module_code in ASSESSMENT_ONLY_MODULES:
        manual_row = {
            "Case ID": make_simple_case_id("ASSESSMENT-ONLY", module_code, assessment_code),
            "Academic Year": ACADEMIC_YEAR,
            "Case Type": "Assessment-only / manual review",
            "Module Code": module_code,
            "Example Assessment Code": assessment_code,
            "Example Assessment Title": clean(row.get("Example Assessment Title", "")),
            "APD Owner": apd_owner_from_module_code(module_code),
            "Reason": "Assessment-only/AO module. Keep separate from normal current-cohort deconfliction to avoid false Level 1 clashes.",
            "Recommended Action": "Manual QA/APD review only. Do not add to normal L1 programme-stage mapping unless a specific AO cohort rule is approved.",
            "Review Status": "Manual Review",
            "Created On": created_on,
        }
        assessment_only_rows.append(manual_row)
    else:
        unmapped_row = {
            "Case ID": make_simple_case_id("UNMAPPED", module_code, assessment_code),
            "Academic Year": ACADEMIC_YEAR,
            "Case Type": "Unmapped calendar module",
            "Module Code": module_code,
            "Example Assessment Code": assessment_code,
            "Example Assessment Title": clean(row.get("Example Assessment Title", "")),
            "APD Owner": apd_owner_from_module_code(module_code),
            "Reason": clean(row.get("Reason", "")),
            "Recommended Action": "QA/APD to confirm whether this is a service, external, special-case, assessment-only, or missing mapping item.",
            "Review Status": "QA Review",
            "Created On": created_on,
        }
        unmapped_rows.append(unmapped_row)


# ---------------------------------------------------------------------
# Sort outputs
# ---------------------------------------------------------------------

deconfliction_cases = sorted(
    deconfliction_cases,
    key=lambda r: (
        severity_order_value(r.get("Severity", "")),
        r.get("APD Owner", ""),
        r.get("Programme Stage Key", ""),
        sort_date_key(r.get("Submission Date A", "")),
        r.get("Module A", ""),
    )
)

feedback_warning_rows = sorted(
    feedback_warning_rows,
    key=lambda r: (
        r.get("APD Owner", ""),
        r.get("Module A", ""),
        r.get("Assessment A", ""),
    )
)

calendar_warning_rows = sorted(
    calendar_warning_rows,
    key=lambda r: (
        severity_order_value(r.get("Severity", "")),
        r.get("APD Owner", ""),
        sort_date_key(r.get("Submission Date A", "")),
        r.get("Module A", ""),
    )
)

unmapped_rows = sorted(unmapped_rows, key=lambda r: r.get("Module Code", ""))
assessment_only_rows = sorted(assessment_only_rows, key=lambda r: r.get("Module Code", ""))


# ---------------------------------------------------------------------
# Build combined APD review pack
# ---------------------------------------------------------------------

apd_review_pack_rows = []
apd_review_pack_rows.extend(deconfliction_cases)
apd_review_pack_rows.extend(calendar_warning_rows)
apd_review_pack_rows.extend(feedback_warning_rows)

apd_review_pack_rows = sorted(
    apd_review_pack_rows,
    key=lambda r: (
        r.get("APD Owner", ""),
        severity_order_value(r.get("Severity", "")),
        r.get("Programme Stage Key", ""),
        sort_date_key(r.get("Submission Date A", "")),
        r.get("Module A", ""),
    )
)


# ---------------------------------------------------------------------
# Write outputs
# ---------------------------------------------------------------------

write_csv(CASE_OUTPUT / "MAP_Deconfliction_Cases_Draft.csv", deconfliction_cases)
write_csv(CASE_OUTPUT / "MAP_Feedback_Timing_Warnings.csv", feedback_warning_rows)
write_csv(CASE_OUTPUT / "MAP_Calendar_Rule_Warnings.csv", calendar_warning_rows)
write_csv(CASE_OUTPUT / "MAP_Unmapped_Calendar_Modules.csv", unmapped_rows)
write_csv(CASE_OUTPUT / "MAP_Assessment_Only_Manual_Cases.csv", assessment_only_rows)
write_csv(CASE_OUTPUT / "MAP_APD_Review_Pack.csv", apd_review_pack_rows)


# APD-specific packs
rows_by_apd = defaultdict(list)

for row in apd_review_pack_rows:
    apd_field = clean(row.get("APD Owner", ""))

    if not apd_field:
        rows_by_apd["Unassigned_QA_Review"].append(row)
        continue

    for apd in [clean(x) for x in apd_field.split(";") if clean(x)]:
        rows_by_apd[apd].append(row)

for apd, rows in rows_by_apd.items():
    write_csv(APD_PACK_OUTPUT / f"{safe_filename(apd)}.csv", rows)


# ---------------------------------------------------------------------
# Print summary
# ---------------------------------------------------------------------

print("\nMAP Deconfliction Case Builder completed.")
print("=" * 60)
print(f"Main deconfliction cases: {len(deconfliction_cases)}")
print(f"Calendar rule warnings: {len(calendar_warning_rows)}")
print(f"Feedback timing warnings: {len(feedback_warning_rows)}")
print(f"Unmapped calendar modules: {len(unmapped_rows)}")
print(f"Assessment-only/manual cases: {len(assessment_only_rows)}")
print(f"Combined APD review pack rows: {len(apd_review_pack_rows)}")
print(f"APD-specific files created: {len(rows_by_apd)}")
print(f"Output folder: {CASE_OUTPUT}")

print("\nMain deconfliction cases by severity:")
counts = defaultdict(int)
for case in deconfliction_cases:
    counts[case.get("Severity", "")] += 1

for severity, count in sorted(counts.items(), key=lambda x: severity_order_value(x[0])):
    print(f"- {severity}: {count}")

print("\nCalendar warnings by rule:")
calendar_counts = defaultdict(int)
for row in calendar_warning_rows:
    calendar_counts[row.get("Rule Triggered", "")] += 1

for rule, count in sorted(calendar_counts.items()):
    print(f"- {rule}: {count}")

print("\nFiles created:")
print("- MAP_Deconfliction_Cases_Draft.csv")
print("- MAP_Feedback_Timing_Warnings.csv")
print("- MAP_Calendar_Rule_Warnings.csv")
print("- MAP_Unmapped_Calendar_Modules.csv")
print("- MAP_Assessment_Only_Manual_Cases.csv")
print("- MAP_APD_Review_Pack.csv")
print("- apd_review_packs/*.csv")