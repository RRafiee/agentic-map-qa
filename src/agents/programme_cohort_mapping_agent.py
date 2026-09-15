"""
MAP Programme-Cohort Mapping Agent v0.2

Purpose:
Expands clean MAP assessment records into affected programme-stage cohort records
using MAP_Programme_Module_Mapping.

This is the bridge between assessment dates and real deconfliction.

Inputs:
- outputs/2026_27_readiness_03Sep/clean_assessments.csv
- data/raw/2026_27_snapshot_03Sep/programme_module_mapping_raw.csv

Outputs:
- affected_cohort_assessments.csv
- unmapped_calendar_modules.csv
- cohort_assessments_by_date.csv
- cohort_same_day_pressure.csv
- cohort_near_date_pressure.csv

Important v0.2 changes:
- Runs across all active programme/module mappings, not only BSc CS.
- Carries Selection Minimum and Selection Maximum into the cohort output.
- Does not automatically exclude optional modules in the same option group.
  It excludes them only where the group maximum is 1.
- Handles mutually exclusive SSD / NONSSD route groups more safely.
"""

from pathlib import Path
from datetime import datetime
from collections import defaultdict
from itertools import combinations
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

READINESS_OUTPUT = ROOT / "outputs" / "2026_27_readiness_03Sep"
RAW_INPUT = ROOT / "data" / "raw" / "2026_27_snapshot_03Sep"

OUTPUT_FOLDER = READINESS_OUTPUT / "programme_cohort_mapping"
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

CLEAN_ASSESSMENTS = READINESS_OUTPUT / "clean_assessments.csv"
MAPPING_FILE = RAW_INPUT / "programme_module_mapping_raw.csv"

ACADEMIC_YEAR = "2026/27"


# ---------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------

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


def clean(value):
    return "" if value is None else str(value).replace("\ufeff", "").strip()


def yes(value):
    return clean(value).lower() in {"yes", "y", "true", "1", "checked"}


def parse_date(value):
    value = clean(value)
    if value == "":
        return None

    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def to_float(value):
    value = clean(value)
    if value == "":
        return 0.0

    value = value.replace("%", "").replace(",", "").strip()

    try:
        return float(value)
    except ValueError:
        return 0.0


def to_int(value, default=0):
    value = clean(value)
    if value == "":
        return default

    try:
        return int(float(value))
    except ValueError:
        return default


def requirement_priority(requirement_type):
    rt = clean(requirement_type).lower()

    if rt in {"core", "compulsory", "mandatory"}:
        return "High"

    if rt == "optional":
        return "Medium"

    if rt == "conditional":
        return "Medium"

    if rt in {"placement", "external", "into"}:
        return "Low"

    return "Unknown"


def group_tokens(group_id):
    """
    Splits selection group IDs into useful route tokens.
    Example:
    MENG-CS-L1-NONSSD -> {"MENG", "CS", "L1", "NONSSD"}
    """
    group_id = clean(group_id).upper()
    if not group_id:
        return set()

    return set(x for x in re.split(r"[-_/\\s]+", group_id) if x)


def mutually_exclusive_route_groups(group_a, group_b):
    """
    Handles known mutually exclusive route groups without hard-coding a programme.

    Example:
    SSD and NONSSD are mutually exclusive.
    """
    tokens_a = group_tokens(group_a)
    tokens_b = group_tokens(group_b)

    if "SSD" in tokens_a and "NONSSD" in tokens_b:
        return True

    if "NONSSD" in tokens_a and "SSD" in tokens_b:
        return True

    return False


def overlap_certainty(
    requirement_a,
    requirement_b,
    group_a,
    group_b,
    selection_max_a,
    selection_max_b,
):
    """
    Estimates whether two mapped assessments can affect the same student.

    Key rule:
    Optional modules in the same option group are excluded only where the
    selection maximum is 1. If students can choose 2, 3, 4, etc. from the group,
    then two modules in the same option group can still overlap for a student.
    """
    ra = clean(requirement_a).lower()
    rb = clean(requirement_b).lower()
    ga = clean(group_a)
    gb = clean(group_b)

    max_a = to_int(selection_max_a, default=0)
    max_b = to_int(selection_max_b, default=0)

    core_types = {"core", "compulsory", "mandatory"}

    if mutually_exclusive_route_groups(ga, gb):
        return "Excluded - mutually exclusive route groups"

    if ra in core_types and rb in core_types:
        return "Definite"

    if ra == "optional" and rb == "optional":
        if ga and gb and ga == gb:
            if max_a == 1 and max_b == 1:
                return "Excluded - same option group with maximum 1"
            return "Potential - same option group allows multiple choices"

        return "Potential - different option groups"

    if ra in core_types and rb == "optional":
        return "Potential"

    if rb in core_types and ra == "optional":
        return "Potential"

    if "conditional" in {ra, rb}:
        return "Conditional"

    return "Unknown"


def severity_for_same_day(pair_certainties, total_weight, module_count):
    if any(x == "Definite" for x in pair_certainties):
        return "Critical"

    if any(x.startswith("Potential") for x in pair_certainties):
        if total_weight >= 50 or module_count >= 3:
            return "High"
        return "Warning"

    if any(x == "Conditional" for x in pair_certainties):
        return "Warning"

    return "Warning"


# ---------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------

print("Loading clean assessments and programme-module mapping...")

assessments = read_csv(CLEAN_ASSESSMENTS)
mappings = read_csv(MAPPING_FILE)

print(f"Clean assessment rows: {len(assessments)}")
print(f"Programme-module mapping rows: {len(mappings)}")


# ---------------------------------------------------------------------
# Prepare active mapping lookup
# ---------------------------------------------------------------------

mapping_by_module = defaultdict(list)

for row in mappings:
    academic_year = clean(row.get("Academic Year", ""))
    module_code = clean(row.get("Module Code", "") or row.get("ModuleCode", "")).upper()
    active = yes(row.get("Active", ""))
    include = yes(row.get("Include in Deconfliction", ""))

    if academic_year == ACADEMIC_YEAR and module_code and active and include:
        mapping_by_module[module_code].append(row)


mapped_module_codes = set(mapping_by_module.keys())


# ---------------------------------------------------------------------
# Expand assessments into affected cohort assessments
# ---------------------------------------------------------------------

affected_rows = []
unmapped_modules = {}

for assessment in assessments:
    module_code = clean(assessment.get("Module Code", "")).upper()

    is_summative = clean(assessment.get("Is Summative", "")).lower() == "true"
    is_formal_exam = clean(assessment.get("Is Formal Examination", "")).lower() == "true"
    include_calendar = clean(assessment.get("Include in EEECS Calendar", "")).lower() == "true"

    submission_date = parse_date(assessment.get("Predicted Submission Date", ""))

    # For this deconfliction MVP, focus on summative, non-formal-exam,
    # calendar-relevant assessments with a valid submission/class-test date.
    if not (is_summative and not is_formal_exam and include_calendar and submission_date is not None):
        continue

    module_mappings = mapping_by_module.get(module_code, [])

    if not module_mappings:
        unmapped_modules[module_code] = {
            "Academic Year": ACADEMIC_YEAR,
            "Module Code": module_code,
            "Example Assessment Code": clean(assessment.get("Assessment Code", "")),
            "Example Assessment Title": clean(assessment.get("Assessment Title", "")),
            "Reason": "No active Include-in-Deconfliction mapping found for this module. This may include assessment-only, service, external, or special-case modules.",
        }
        continue

    for mapping in module_mappings:
        programme_key = clean(mapping.get("Programme Key", ""))
        pathway_code = clean(mapping.get("Pathway Code", ""))
        pathway_name = clean(mapping.get("Pathway Name", ""))
        stage = clean(mapping.get("Stage", ""))
        cohort_key = clean(mapping.get("Cohort Key", ""))
        requirement_type = clean(mapping.get("Requirement Type", ""))
        selection_group_id = clean(mapping.get("Selection Group ID", ""))
        selection_minimum = clean(mapping.get("Selection Minimum", ""))
        selection_maximum = clean(mapping.get("Selection Maximum", ""))
        route_condition = clean(mapping.get("Route Condition", ""))
        delivery_period = clean(mapping.get("Delivery Period", ""))

        programme_stage_key = cohort_key
        if not programme_stage_key:
            programme_stage_key = f"{programme_key}-{stage}"

        affected_rows.append({
            "Academic Year": ACADEMIC_YEAR,
            "Programme Key": programme_key,
            "Pathway Code": pathway_code,
            "Pathway Name": pathway_name,
            "Stage": stage,
            "Programme Stage Key": programme_stage_key,
            "Cohort Key": cohort_key,
            "Module Code": module_code,
            "Module Title": clean(mapping.get("Module Title", "")),
            "Requirement Type": requirement_type,
            "Selection Group ID": selection_group_id,
            "Selection Minimum": selection_minimum,
            "Selection Maximum": selection_maximum,
            "Route Condition": route_condition,
            "Mapping Delivery Period": delivery_period,
            "Deconfliction Priority": requirement_priority(requirement_type),
            "Assessment Code": clean(assessment.get("Assessment Code", "")),
            "Assessment Number": clean(assessment.get("Assessment Number", "")),
            "Assessment Title": clean(assessment.get("Assessment Title", "")),
            "Assessment Type": clean(assessment.get("Assessment Type", "")),
            "Assessment Weight": clean(assessment.get("Assessment Weight", "")),
            "Assessment Mode": clean(assessment.get("Assessment Mode", "")),
            "Assessment Period": clean(assessment.get("Assessment Period", "")),
            "Predicted Release Date": clean(assessment.get("Predicted Release Date", "")),
            "Predicted Submission Date": clean(assessment.get("Predicted Submission Date", "")),
            "Predicted Feedback Date": clean(assessment.get("Predicted Feedback Date", "")),
            "Submission to Feedback Working Days": clean(assessment.get("Submission to Feedback Working Days", "")),
        })


# ---------------------------------------------------------------------
# Board 1: cohort assessments by date
# ---------------------------------------------------------------------

cohort_assessments_by_date = sorted(
    affected_rows,
    key=lambda r: (
        r.get("Programme Stage Key", ""),
        parse_date(r.get("Predicted Submission Date", "")) or datetime.max.date(),
        r.get("Module Code", ""),
        r.get("Assessment Code", "")
    )
)


# ---------------------------------------------------------------------
# Board 2: same-day pressure within same programme-stage cohort
# ---------------------------------------------------------------------

by_cohort_date = defaultdict(list)

for row in affected_rows:
    key = (
        row.get("Programme Stage Key", ""),
        row.get("Predicted Submission Date", "")
    )
    by_cohort_date[key].append(row)

same_day_rows = []

for (programme_stage_key, submission_date), rows in sorted(by_cohort_date.items()):
    modules = sorted(set(r.get("Module Code", "") for r in rows))

    if len(modules) <= 1:
        continue

    relevant_pair_certainties = []

    for a, b in combinations(rows, 2):
        if a.get("Module Code", "") == b.get("Module Code", ""):
            continue

        overlap = overlap_certainty(
            a.get("Requirement Type", ""),
            b.get("Requirement Type", ""),
            a.get("Selection Group ID", ""),
            b.get("Selection Group ID", ""),
            a.get("Selection Maximum", ""),
            b.get("Selection Maximum", ""),
        )

        if not overlap.startswith("Excluded"):
            relevant_pair_certainties.append(overlap)

    if not relevant_pair_certainties:
        continue

    total_weight = sum(to_float(r.get("Assessment Weight", "")) for r in rows)
    severity = severity_for_same_day(
        relevant_pair_certainties,
        total_weight,
        len(modules),
    )

    same_day_rows.append({
        "Academic Year": ACADEMIC_YEAR,
        "Programme Stage Key": programme_stage_key,
        "Submission Date": submission_date,
        "Number of Assessment Records": len(rows),
        "Number of Distinct Modules": len(modules),
        "Total Weighting": round(total_weight, 2),
        "Modules": "; ".join(modules),
        "Assessment Codes": "; ".join(r.get("Assessment Code", "") for r in rows),
        "Requirement Types": "; ".join(sorted(set(r.get("Requirement Type", "") for r in rows))),
        "Conflict Certainty Summary": "; ".join(sorted(set(relevant_pair_certainties))),
        "Indicative Severity": severity,
        "Rule Triggered": "C-001",
        "Evidence Summary": "Two or more mapped modules have assessment submissions on the same date for the same programme-stage cohort."
    })


# ---------------------------------------------------------------------
# Board 3: near-date pressure within same programme-stage cohort
# ---------------------------------------------------------------------

by_cohort = defaultdict(list)

for row in affected_rows:
    by_cohort[row.get("Programme Stage Key", "")].append(row)

near_date_rows = []

for programme_stage_key, rows in sorted(by_cohort.items()):
    rows_sorted = sorted(
        rows,
        key=lambda r: parse_date(r.get("Predicted Submission Date", "")) or datetime.max.date()
    )

    for i in range(len(rows_sorted)):
        a = rows_sorted[i]
        date_a = parse_date(a.get("Predicted Submission Date", ""))

        for j in range(i + 1, len(rows_sorted)):
            b = rows_sorted[j]
            date_b = parse_date(b.get("Predicted Submission Date", ""))

            if date_a is None or date_b is None:
                continue

            gap = (date_b - date_a).days

            if gap > 2:
                break

            if gap < 0:
                continue

            if a.get("Module Code", "") == b.get("Module Code", ""):
                continue

            overlap = overlap_certainty(
                a.get("Requirement Type", ""),
                b.get("Requirement Type", ""),
                a.get("Selection Group ID", ""),
                b.get("Selection Group ID", ""),
                a.get("Selection Maximum", ""),
                b.get("Selection Maximum", ""),
            )

            if overlap.startswith("Excluded"):
                continue

            weight_a = to_float(a.get("Assessment Weight", ""))
            weight_b = to_float(b.get("Assessment Weight", ""))
            combined_weight = weight_a + weight_b

            if gap == 0:
                rule = "C-001"
                severity = "Critical" if overlap == "Definite" else "High"
            elif gap == 1:
                rule = "C-002"
                severity = "High" if combined_weight >= 50 else "Warning"
            else:
                rule = "C-003"
                severity = "Warning"

            near_date_rows.append({
                "Academic Year": ACADEMIC_YEAR,
                "Programme Stage Key": programme_stage_key,
                "Pathway Name": a.get("Pathway Name", ""),
                "Stage": a.get("Stage", ""),
                "Date Gap": gap,
                "Rule Triggered": rule,
                "Indicative Severity": severity,
                "Conflict Certainty": overlap,
                "Submission Date A": a.get("Predicted Submission Date", ""),
                "Module A": a.get("Module Code", ""),
                "Assessment A": a.get("Assessment Code", ""),
                "Title A": a.get("Assessment Title", ""),
                "Requirement A": a.get("Requirement Type", ""),
                "Selection Group A": a.get("Selection Group ID", ""),
                "Selection Max A": a.get("Selection Maximum", ""),
                "Weight A": a.get("Assessment Weight", ""),
                "Submission Date B": b.get("Predicted Submission Date", ""),
                "Module B": b.get("Module Code", ""),
                "Assessment B": b.get("Assessment Code", ""),
                "Title B": b.get("Assessment Title", ""),
                "Requirement B": b.get("Requirement Type", ""),
                "Selection Group B": b.get("Selection Group ID", ""),
                "Selection Max B": b.get("Selection Maximum", ""),
                "Weight B": b.get("Assessment Weight", ""),
                "Combined Weight": round(combined_weight, 2),
                "Evidence Summary": "Mapped assessments are due within 0-2 calendar days for the same programme-stage cohort."
            })


# ---------------------------------------------------------------------
# Write outputs
# ---------------------------------------------------------------------

write_csv(OUTPUT_FOLDER / "affected_cohort_assessments.csv", affected_rows)
write_csv(OUTPUT_FOLDER / "unmapped_calendar_modules.csv", unmapped_modules.values())
write_csv(OUTPUT_FOLDER / "cohort_assessments_by_date.csv", cohort_assessments_by_date)
write_csv(OUTPUT_FOLDER / "cohort_same_day_pressure.csv", same_day_rows)
write_csv(OUTPUT_FOLDER / "cohort_near_date_pressure.csv", near_date_rows)


# ---------------------------------------------------------------------
# Print summary
# ---------------------------------------------------------------------

print("\nMAP Programme-Cohort Mapping Agent completed.")
print("=" * 60)
print(f"Mapped module codes available: {len(mapped_module_codes)}")
print(f"Affected cohort assessment rows: {len(affected_rows)}")
print(f"Unmapped calendar module codes: {len(unmapped_modules)}")
print(f"Cohort same-day pressure cases: {len(same_day_rows)}")
print(f"Cohort near-date pressure cases: {len(near_date_rows)}")
print(f"Output folder: {OUTPUT_FOLDER}")

print("\nFiles created:")
print("- affected_cohort_assessments.csv")
print("- unmapped_calendar_modules.csv")
print("- cohort_assessments_by_date.csv")
print("- cohort_same_day_pressure.csv")
print("- cohort_near_date_pressure.csv")