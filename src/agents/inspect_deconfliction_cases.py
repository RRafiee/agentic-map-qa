from pathlib import Path
from collections import Counter, defaultdict
import csv


def find_project_root():
    current = Path(__file__).resolve().parent

    for parent in [current] + list(current.parents):
        if (parent / "data").exists() and (parent / "outputs").exists() and (parent / "src").exists():
            return parent

    raise RuntimeError("Could not find project root.")


ROOT = find_project_root()
CASE_OUTPUT = ROOT / "outputs" / "2026_27_readiness_03Sep" / "deconfliction_cases"

FILES = {
    "main": CASE_OUTPUT / "MAP_Deconfliction_Cases_Draft.csv",
    "calendar": CASE_OUTPUT / "MAP_Calendar_Rule_Warnings.csv",
    "feedback": CASE_OUTPUT / "MAP_Feedback_Timing_Warnings.csv",
    "unmapped": CASE_OUTPUT / "MAP_Unmapped_Calendar_Modules.csv",
    "ao": CASE_OUTPUT / "MAP_Assessment_Only_Manual_Cases.csv",
    "apd": CASE_OUTPUT / "MAP_APD_Review_Pack.csv",
}


def read_csv(path):
    if not path.exists():
        print(f"Missing file: {path}")
        return []

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean(value):
    return "" if value is None else str(value).strip()


def print_counter(title, counter):
    print("\n" + title)
    print("-" * len(title))

    if not counter:
        print("  None")
        return

    for key, count in counter.most_common():
        print(f"  {key or '[blank]'}: {count}")


def print_first_cases(title, rows, limit=20):
    print("\n" + title)
    print("-" * len(title))

    if not rows:
        print("  None")
        return

    for i, row in enumerate(rows[:limit], start=1):
        print(f"\n{i}. {clean(row.get('Severity'))} | {clean(row.get('APD Owner'))} | {clean(row.get('Programme Stage Key'))}")
        print(f"   Type: {clean(row.get('Case Type'))}")
        print(f"   Rule: {clean(row.get('Rule Triggered'))}")
        print(f"   Date A: {clean(row.get('Submission Date A'))}")
        print(f"   Date B: {clean(row.get('Submission Date B'))}")
        print(f"   Module A: {clean(row.get('Module A'))}")
        print(f"   Module B: {clean(row.get('Module B'))}")
        print(f"   Assessment A: {clean(row.get('Assessment A'))}")
        print(f"   Assessment B: {clean(row.get('Assessment B'))}")
        print(f"   Suggested 1: {clean(row.get('Suggested Alternative Date 1'))}")
        print(f"   Action: {clean(row.get('Recommended Action'))}")


main_rows = read_csv(FILES["main"])
calendar_rows = read_csv(FILES["calendar"])
feedback_rows = read_csv(FILES["feedback"])
unmapped_rows = read_csv(FILES["unmapped"])
ao_rows = read_csv(FILES["ao"])
apd_rows = read_csv(FILES["apd"])

print("=" * 80)
print("MAP DECONFLICTION OUTPUT INSPECTION")
print("=" * 80)

print(f"Main deconfliction cases: {len(main_rows)}")
print(f"Calendar rule warnings: {len(calendar_rows)}")
print(f"Feedback timing warnings: {len(feedback_rows)}")
print(f"Unmapped calendar modules: {len(unmapped_rows)}")
print(f"Assessment-only/manual cases: {len(ao_rows)}")
print(f"Combined APD review pack rows: {len(apd_rows)}")

print_counter("Main cases by severity", Counter(clean(r.get("Severity")) for r in main_rows))
print_counter("Main cases by APD", Counter(clean(r.get("APD Owner")) for r in main_rows))
print_counter("Main cases by programme/stage", Counter(clean(r.get("Programme Stage Key")) for r in main_rows))
print_counter("Main cases by rule", Counter(clean(r.get("Rule Triggered")) for r in main_rows))

print_counter("Calendar warnings by rule", Counter(clean(r.get("Rule Triggered")) for r in calendar_rows))
print_counter("Calendar warnings by APD", Counter(clean(r.get("APD Owner")) for r in calendar_rows))

print_counter("Feedback warnings by APD", Counter(clean(r.get("APD Owner")) for r in feedback_rows))

critical_main = [r for r in main_rows if clean(r.get("Severity")) == "Critical"]
high_main = [r for r in main_rows if clean(r.get("Severity")) == "High"]
critical_calendar = [r for r in calendar_rows if clean(r.get("Severity")) == "Critical"]
study_week_calendar = [r for r in calendar_rows if clean(r.get("Rule Triggered")) == "CAL-001"]

print_first_cases("Critical main deconfliction cases", critical_main, limit=20)
print_first_cases("High main deconfliction cases - first 20", high_main, limit=20)
print_first_cases("Critical calendar warnings", critical_calendar, limit=20)
print_first_cases("Independent Study Week warnings", study_week_calendar, limit=20)

print("\nUnmapped calendar modules")
print("-------------------------")
for row in unmapped_rows:
    print(f"  {clean(row.get('Module Code'))}: {clean(row.get('Example Assessment Code'))} | {clean(row.get('Reason'))}")

print("\nAssessment-only/manual cases")
print("----------------------------")
for row in ao_rows:
    print(f"  {clean(row.get('Module Code'))}: {clean(row.get('Example Assessment Code'))} | {clean(row.get('Reason'))}")