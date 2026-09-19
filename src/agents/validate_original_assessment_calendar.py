from pathlib import Path
import pandas as pd

base = Path("outputs/2026_27_readiness_03Sep/original_calendar_check")
html_path = base / "MAP_Original_Assessment_Calendar_2026_27.html"
events_path = base / "MAP_Original_Assessment_Calendar_Events.csv"
summary_path = base / "MAP_Original_Assessment_Calendar_Summary_By_Area_Stage.csv"

print("\nORIGINAL ASSESSMENT CALENDAR VALIDATION")
print("=" * 55)

for path in [html_path, events_path, summary_path]:
    print(f"{path.name}: {'FOUND' if path.exists() else 'MISSING'}")

if not events_path.exists():
    raise FileNotFoundError(events_path)

events = pd.read_csv(events_path, dtype=str).fillna("")
print("\nEvents CSV")
print("Rows:", len(events))
print("Columns:", list(events.columns))

required_cols = [
    "view", "date_iso", "date_label", "event_type", "date_source",
    "area", "stage", "programme_stage_key", "module_code", "assessment_code",
    "assessment_title", "assessment_type", "original_release_date",
    "original_submission_date", "original_feedback_date",
]
missing_cols = [c for c in required_cols if c not in events.columns]
print("Missing required columns:", missing_cols if missing_cols else "None")
if missing_cols:
    raise SystemExit("Stopping: missing required columns.")

invalid_dates = pd.to_datetime(events["date_iso"], errors="coerce").isna().sum()
print("Invalid date_iso values:", invalid_dates)

print("\nViews:")
print(events["view"].value_counts(dropna=False).to_string())

print("\nEvent types:")
print(events["event_type"].value_counts(dropna=False).to_string())

print("\nDate sources:")
print(events["date_source"].value_counts(dropna=False).to_string())

apd_columns_present = [c for c in events.columns if "apd" in c.lower()]
print("\nAPD-related columns present:", apd_columns_present if apd_columns_present else "None")

exam_like = events[events["assessment_type"].str.contains("exam", case=False, na=False)]
print("Exam-like assessment type rows in output:", len(exam_like))
if len(exam_like) > 0:
    print(exam_like[["module_code", "assessment_code", "assessment_type"]].drop_duplicates().head(20).to_string(index=False))

combined_stage = events[events["stage"].str.contains("/", regex=False, na=False)]
print("Combined/unclear stage labels:", len(combined_stage))

submissions = events[(events["event_type"] == "Submission") & (events["area"] != "Other / unmapped")].copy()
print("\nOriginal submission events excluding Other/unmapped:", len(submissions))
print("Unique submission assessments:", submissions["assessment_code"].nunique())

summary = (
    submissions
    .groupby(["area", "stage"], dropna=False)
    .agg(
        submission_events=("assessment_code", "count"),
        unique_assessments=("assessment_code", pd.Series.nunique),
    )
    .reset_index()
    .sort_values(["area", "stage"])
)
print("\nSubmission summary by area/stage:")
print(summary.to_string(index=False))

if summary_path.exists():
    summary_file = pd.read_csv(summary_path, dtype=str).fillna("")
    print("\nSummary file rows:", len(summary_file))
    print(summary_file.to_string(index=False))

if html_path.exists():
    html = html_path.read_text(encoding="utf-8", errors="ignore")
    print("\nHTML checks")
    print("Contains original title:", "MAP Original Assessment Calendar" in html)
    apd_wording_present = any(term in html for term in ["APD-proposed", "APD proposed", "APD Proposed"])
    print("Contains APD-proposed wording:", apd_wording_present)
    print("Contains final-calendar warning:", "not the final EEECS assessment calendar" in html)
    print("Contains dropdown/select menus:", "<select" in html.lower())

print("\nVALIDATION COMPLETE")
