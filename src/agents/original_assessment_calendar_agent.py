from __future__ import annotations

import argparse
import html
import re
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd

DEFAULT_INPUT = Path(
    "outputs/2026_27_readiness_03Sep/deconfliction_cases/"
    "MAP_Assessment_Deconfliction_Working_2026_27_FIXED_UK_DATES.xlsx"
)
DEFAULT_OUTPUT_DIR = Path("outputs/2026_27_readiness_03Sep/original_calendar_check")
DEFAULT_MAPPING_CANDIDATES = [
    Path("data/raw/2026_27_snapshot_03Sep/programme_module_mapping_raw.csv"),
    Path("data/raw/programme_module_mapping_raw.csv"),
    Path("programme_module_mapping_raw.csv"),
    Path("MAP_Programme_Module_Mapping_Raw.csv"),
]
SHEET_NAME = "Assessment_Plan_Working"

EVENT_TYPES = ["Release", "Submission", "Feedback"]
EVENT_ORDER = {"Submission": 0, "Release": 1, "Feedback": 2}
AREA_ORDER = ["CS/SE", "EEE/CE", "CIT", "BIT", "Data Science", "Other / unmapped"]
STAGE_ORDER = ["Stage 1", "Stage 2", "Stage 3", "Stage 4", "Stage unknown"]


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    return str(value).replace("\xa0", " ").strip()


def normalise_header(value: Any) -> str:
    return re.sub(r"\s+", " ", clean_text(value)).strip()


def find_col(df: pd.DataFrame, aliases: list[str], required: bool = False, *, partial: bool = True) -> str | None:
    norm_to_original = {normalise_header(c).lower(): c for c in df.columns}
    for alias in aliases:
        key = normalise_header(alias).lower()
        if key in norm_to_original:
            return norm_to_original[key]
    if partial:
        for col in df.columns:
            col_norm = normalise_header(col).lower()
            for alias in aliases:
                alias_norm = normalise_header(alias).lower()
                if alias_norm and alias_norm in col_norm:
                    return col
    if required:
        available = "\n".join(f"- {c}" for c in df.columns)
        raise KeyError(
            f"Required column not found. Tried aliases: {aliases}\n\nAvailable columns:\n{available}"
        )
    return None


def get_value(row: pd.Series, col: str | None) -> str:
    if not col:
        return ""
    return clean_text(row.get(col, ""))


def parse_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    s = clean_text(value)
    if not s or s.lower() in {"nan", "none", "nat", "not applicable", "not required"}:
        return None
    s0 = s.split()[0]
    formats = ["%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"]
    for fmt in formats:
        try:
            return datetime.strptime(s0, fmt).date()
        except ValueError:
            pass
    parsed = pd.to_datetime(s, dayfirst=True, errors="coerce")
    if pd.notna(parsed):
        return parsed.date()
    parsed = pd.to_datetime(s, dayfirst=False, errors="coerce")
    if pd.notna(parsed):
        return parsed.date()
    return None


def fmt_date(d: date | None) -> str:
    return d.strftime("%d/%m/%Y") if d else ""


def split_stage_keys(value: str) -> list[str]:
    value = clean_text(value)
    if not value:
        return []
    parts = [p.strip() for p in re.split(r"[;,\n]+", value) if p.strip()]
    return parts


def area_from_key(stage_key: str) -> str:
    key = stage_key.upper()
    if "BSC-DS" in key:
        return "Data Science"
    if "BSC-CIT" in key:
        return "CIT"
    if "BSC-BIT" in key:
        return "BIT"
    if any(x in key for x in ["BSC-CS", "MENG-CS", "BENG-SE", "MENG-SE"]):
        return "CS/SE"
    if any(x in key for x in ["BENG-EEE", "MENG-EEE", "BENG-CE", "MENG-CE"]):
        return "EEE/CE"
    return "Other / unmapped"


def stage_from_key(stage_key: str, fallback: str = "") -> str:
    key = stage_key.upper()
    match = re.search(r"\bL([1-4])\b", key)
    if match:
        return f"Stage {match.group(1)}"
    match = re.search(r"LEVEL\s*([1-4])", key)
    if match:
        return f"Stage {match.group(1)}"
    match = re.search(r"STAGE\s*([1-4])", fallback.upper())
    if match:
        return f"Stage {match.group(1)}"
    match = re.search(r"\b([1-4])\b", fallback)
    if match:
        return f"Stage {match.group(1)}"
    return "Stage unknown"


def is_truthy_calendar_flag(value: str) -> bool:
    value = clean_text(value).lower()
    if not value:
        return True
    return value not in {"false", "no", "0", "n"}


def is_formal_exam(row: pd.Series, formal_exam_col: str | None, assessment_type_col: str | None) -> bool:
    formal_flag = get_value(row, formal_exam_col).lower()
    if formal_flag in {"true", "yes", "1", "y"}:
        return True
    assessment_type = get_value(row, assessment_type_col).lower()
    exam_terms = ["formal examination", "formal exam", "written exam", "examination", "exam"]
    return any(term in assessment_type for term in exam_terms)


def combine_unique(values: list[Any]) -> str:
    seen: list[str] = []
    for value in values:
        for part in re.split(r"[;\n]+", clean_text(value)):
            part = part.strip()
            if part and part not in seen:
                seen.append(part)
    return "; ".join(seen)


def resolve_mapping_path(user_mapping: Path | None = None) -> Path | None:
    if user_mapping:
        return user_mapping if user_mapping.exists() else None
    for candidate in DEFAULT_MAPPING_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def load_mapping_lookup(mapping_path: Path | None) -> tuple[dict[str, list[str]], dict[str, str], pd.DataFrame]:
    """Return module -> cohort keys and module -> title lookup from programme-module mapping."""
    if mapping_path is None:
        return {}, {}, pd.DataFrame()

    mapping_df = pd.read_csv(mapping_path, dtype=str).fillna("")
    mapping_df.columns = [normalise_header(c) for c in mapping_df.columns]

    module_col = find_col(mapping_df, ["Module Code", "ModuleCode", "Module"], required=True)
    cohort_col = find_col(mapping_df, ["Cohort Key", "Programme Stage Key", "Programme Stage"], required=True)
    title_col = find_col(mapping_df, ["Module Title", "Module Name", "Title"], partial=False)
    active_col = find_col(mapping_df, ["Active"])
    include_col = find_col(mapping_df, ["Include in Deconfliction", "Include in Calendar", "Include"])

    # Keep active, deconfliction-included rows where the columns exist.
    if active_col:
        mapping_df = mapping_df[mapping_df[active_col].map(is_truthy_calendar_flag)]
    if include_col:
        mapping_df = mapping_df[mapping_df[include_col].map(is_truthy_calendar_flag)]

    lookup: dict[str, list[str]] = defaultdict(list)
    title_lookup: dict[str, str] = {}
    for _, row in mapping_df.iterrows():
        module = clean_text(row.get(module_col, "")).upper()
        cohort = clean_text(row.get(cohort_col, ""))
        if not module or not cohort:
            continue
        if cohort not in lookup[module]:
            lookup[module].append(cohort)
        if title_col and module not in title_lookup:
            title_lookup[module] = clean_text(row.get(title_col, ""))

    return dict(lookup), title_lookup, mapping_df


def determine_programme_keys(
    workbook_keys_raw: str,
    module_code: str,
    mapping_lookup: dict[str, list[str]],
) -> tuple[list[str], str]:
    workbook_keys = split_stage_keys(workbook_keys_raw)
    if workbook_keys:
        return workbook_keys, "Workbook Programme Stage Key(s)"
    mapped_keys = mapping_lookup.get(module_code.upper(), [])
    if mapped_keys:
        return mapped_keys, "Programme-module mapping fallback"
    return ["Unmapped"], "Unmapped"


def build_original_events(
    df: pd.DataFrame,
    mapping_lookup: dict[str, list[str]] | None = None,
    module_title_lookup: dict[str, str] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    mapping_lookup = mapping_lookup or {}
    module_title_lookup = module_title_lookup or {}

    cols = {
        "academic_year": find_col(df, ["Academic Year"]),
        "module_code": find_col(df, ["Module Code", "ModuleCode", "Module"], required=True),
        # Partial=False prevents accidental mapping of Assessment Title to Module Title.
        "module_title": find_col(df, ["Module Title", "Module Title(s)"], partial=False),
        "assessment_number": find_col(df, ["Assessment Number", "Assessment #"]),
        "assessment_code": find_col(df, ["Assessment Code", "Assignment Code"], required=True),
        "assessment_title": find_col(df, ["Assessment Title", "Assignment Title"], required=True),
        "assessment_type": find_col(df, ["Assessment Type", "Type"]),
        "assessment_weight": find_col(df, ["Assessment Weight", "Weight"]),
        "assessment_period": find_col(df, ["Assessment Period", "Period"]),
        "include_calendar": find_col(df, ["Include in EEECS Calendar", "Include in Calendar"]),
        "formal_exam": find_col(df, ["Is Formal Examination", "Formal Examination", "Formal Exam", "Is Exam"]),
        "original_release": find_col(df, ["Original Predicted Release Date", "Predicted Release Date", "Original Release Date"], required=True),
        "original_submission": find_col(df, ["Original Predicted Submission Date", "Predicted Submission Date", "Original Submission Date"], required=True),
        "original_feedback": find_col(df, ["Original Predicted Feedback Date", "Predicted Feedback Date", "Original Feedback Date"], required=True),
        "programme_stage": find_col(df, ["Programme Stage Key(s)", "Programme Stage Key", "Cohort Key", "Programme Stage"]),
    }

    print("Column mapping used:")
    for k, v in cols.items():
        print(f"  {k}: {v}")

    raw_events: list[dict[str, Any]] = []
    skipped_exam = 0
    skipped_not_calendar = 0
    rows_by_mapping_source: dict[str, set[str]] = defaultdict(set)
    unmapped_modules: set[str] = set()

    for idx, row in df.iterrows():
        if not is_truthy_calendar_flag(get_value(row, cols["include_calendar"])):
            skipped_not_calendar += 1
            continue
        if is_formal_exam(row, cols["formal_exam"], cols["assessment_type"]):
            skipped_exam += 1
            continue

        dates = {
            "Release": parse_date(get_value(row, cols["original_release"])),
            "Submission": parse_date(get_value(row, cols["original_submission"])),
            "Feedback": parse_date(get_value(row, cols["original_feedback"])),
        }

        module_code = get_value(row, cols["module_code"]).upper()
        assessment_code = get_value(row, cols["assessment_code"])
        module_title = get_value(row, cols["module_title"]) or module_title_lookup.get(module_code, "")
        programme_keys, mapping_source = determine_programme_keys(
            get_value(row, cols["programme_stage"]),
            module_code,
            mapping_lookup,
        )
        rows_by_mapping_source[mapping_source].add(assessment_code)
        if mapping_source == "Unmapped":
            unmapped_modules.add(module_code)

        for programme_stage_key in programme_keys:
            area = area_from_key(programme_stage_key)
            stage = stage_from_key(programme_stage_key, fallback=get_value(row, cols["assessment_period"]))

            for event_type in EVENT_TYPES:
                event_date = dates[event_type]
                if not event_date:
                    continue
                raw_events.append(
                    {
                        "source_row": str(int(idx) + 2),
                        "view": "Original MAP submission",
                        "date_iso": event_date.isoformat(),
                        "date_label": fmt_date(event_date),
                        "event_type": event_type,
                        "event_short": event_type[0],
                        "date_source": "Original submitted date",
                        "area": area,
                        "stage": stage,
                        "programme_stage_key": programme_stage_key,
                        "programme_stage_source": mapping_source,
                        "academic_year": get_value(row, cols["academic_year"]),
                        "module_code": module_code,
                        "module_title": module_title,
                        "assessment_number": get_value(row, cols["assessment_number"]),
                        "assessment_code": assessment_code,
                        "assessment_title": get_value(row, cols["assessment_title"]),
                        "assessment_type": get_value(row, cols["assessment_type"]),
                        "assessment_weight": get_value(row, cols["assessment_weight"]),
                        "assessment_period": get_value(row, cols["assessment_period"]),
                        "original_release_date": fmt_date(dates["Release"]),
                        "original_submission_date": fmt_date(dates["Submission"]),
                        "original_feedback_date": fmt_date(dates["Feedback"]),
                    }
                )

    collapsed = collapse_events_for_display(raw_events)
    stats = {
        "skipped_not_calendar": skipped_not_calendar,
        "skipped_exam": skipped_exam,
        "rows_by_mapping_source": {k: len(v) for k, v in rows_by_mapping_source.items()},
        "unmapped_modules": sorted(unmapped_modules),
    }
    return collapsed, stats


def collapse_events_for_display(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for e in events:
        key = (e["area"], e["stage"], e["event_type"], e["date_iso"], e["assessment_code"])
        grouped[key].append(e)

    collapsed: list[dict[str, Any]] = []
    combine_fields = ["source_row", "programme_stage_key", "programme_stage_source"]
    for rows in grouped.values():
        base = dict(rows[0])
        for field in combine_fields:
            base[field] = combine_unique([r.get(field, "") for r in rows])
        base["display_row_count"] = str(len(rows))
        collapsed.append(base)

    return sorted(
        collapsed,
        key=lambda e: (
            area_stage_sort_key((e["area"], e["stage"])),
            e["date_iso"],
            EVENT_ORDER.get(e["event_type"], 99),
            e["module_code"],
            e.get("assessment_code", ""),
        ),
    )


def area_stage_sort_key(item: tuple[str, str]) -> tuple[int, int, str, str]:
    area, stage = item
    area_rank = AREA_ORDER.index(area) if area in AREA_ORDER else 999
    stage_rank = STAGE_ORDER.index(stage) if stage in STAGE_ORDER else 999
    return (area_rank, stage_rank, area, stage)


def event_title(e: dict[str, Any]) -> str:
    lines = [
        f"Module: {e['module_code']} {e.get('module_title','')}",
        f"Assessment: {e.get('assessment_code','')} — {e.get('assessment_title','')}",
        f"Type/weight: {e.get('assessment_type','')} / {e.get('assessment_weight','')}",
        f"Event: {e['event_type']}",
        f"Original submitted date shown: {e['date_label']}",
        f"Original release: {e.get('original_release_date','')}",
        f"Original submission: {e.get('original_submission_date','')}",
        f"Original feedback: {e.get('original_feedback_date','')}",
        f"Programme/stage key(s): {e.get('programme_stage_key','')}",
        f"Programme/stage source: {e.get('programme_stage_source','')}",
        f"Source row(s): {e.get('source_row','')}",
    ]
    return "\n".join(lines)


def event_html(e: dict[str, Any]) -> str:
    classes = ["event", e["event_type"]]
    label = f"[{html.escape(e['event_short'])}] {html.escape(e['module_code'])}"
    title = html.escape(event_title(e), quote=True)
    return f"<div class='{' '.join(classes)}' title=\"{title}\">{label}</div>"


def month_grid(events: list[dict[str, Any]], year: int, month: int) -> str:
    by_date: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for e in events:
        by_date[e["date_iso"]].append(e)

    month_name = datetime(year, month, 1).strftime("%B %Y")
    dows = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    out = [f"<div class='month'><h3>{html.escape(month_name)}</h3><div class='grid'>"]
    out.extend(f"<div class='dow'>{d}</div>" for d in dows)

    first = date(year, month, 1)
    for _ in range(first.weekday()):
        out.append("<div class='day empty'></div>")

    if month == 12:
        days_in_month = 31
    else:
        days_in_month = (date(year + (1 if month == 12 else 0), 1 if month == 12 else month + 1, 1) - first).days

    for day in range(1, days_in_month + 1):
        iso = date(year, month, day).isoformat()
        evs = sorted(
            by_date.get(iso, []),
            key=lambda x: (EVENT_ORDER.get(x["event_type"], 99), x["module_code"], x.get("assessment_code", "")),
        )
        out.append(f"<div class='day'><div class='date'>{day}</div>{''.join(event_html(e) for e in evs)}</div>")

    out.append("</div></div>")
    return "".join(out)


def render_area_stage_section(events: list[dict[str, Any]], area: str, stage: str, event_filter: str | None = None) -> str:
    section_events = [
        e for e in events
        if e["area"] == area and e["stage"] == stage
        and (event_filter is None or e["event_type"] == event_filter)
    ]
    if not section_events:
        return ""

    dates = [datetime.fromisoformat(e["date_iso"]).date() for e in section_events]
    ym_start = (min(dates).year, min(dates).month)
    ym_end = (max(dates).year, max(dates).month)
    months: list[tuple[int, int]] = []
    y, m = ym_start
    while y < ym_end[0] or (y == ym_end[0] and m <= ym_end[1]):
        months.append((y, m))
        m += 1
        if m == 13:
            y += 1
            m = 1

    anchor = f"{area}-{stage}-{'submission' if event_filter == 'Submission' else 'all'}".lower().replace("/", "-").replace(" ", "-")
    title_extra = "submission dates" if event_filter == "Submission" else "release, submission and feedback dates"

    out = [
        f"<section id='{html.escape(anchor)}' class='section'>",
        f"<h2>{html.escape(area)} — {html.escape(stage)} <span class='subtitle'>({html.escape(title_extra)})</span></h2>",
        f"<p class='small'>Visible events: {len(section_events)}. Hover over an event to see the original submitted release, submission and feedback dates, plus the programme/stage mapping source.</p>",
    ]
    for year, month in months:
        out.append(month_grid([e for e in section_events if e["date_iso"].startswith(f"{year}-{month:02d}")], year, month))
    out.append("</section>")
    return "".join(out)


def make_summary_table(events: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for e in events:
        if e["area"] == "Other / unmapped":
            continue
        groups[(e["area"], e["stage"])].append(e)
    for area, stage in sorted(groups, key=area_stage_sort_key):
        group = groups[(area, stage)]
        submissions = [e for e in group if e["event_type"] == "Submission"]
        rows.append({
            "area": area,
            "stage": stage,
            "release_events": sum(1 for e in group if e["event_type"] == "Release"),
            "submission_events": len(submissions),
            "feedback_events": sum(1 for e in group if e["event_type"] == "Feedback"),
            "unique_submission_assessments": len({e["assessment_code"] for e in submissions}),
        })
    return pd.DataFrame(rows)


def make_mapping_source_summary(events: list[dict[str, Any]]) -> pd.DataFrame:
    if not events:
        return pd.DataFrame(columns=["programme_stage_source", "submission_events", "unique_submission_assessments"])
    df = pd.DataFrame(events)
    submissions = df[df["event_type"] == "Submission"].copy()
    return (
        submissions.groupby("programme_stage_source", dropna=False)
        .agg(
            submission_events=("assessment_code", "count"),
            unique_submission_assessments=("assessment_code", pd.Series.nunique),
        )
        .reset_index()
        .sort_values("programme_stage_source")
    )


def df_to_html_table(df: pd.DataFrame, max_rows: int | None = None) -> str:
    if df.empty:
        return "<p class='small'>No rows.</p>"
    use_df = df.head(max_rows) if max_rows else df
    out = ["<table><thead><tr>"]
    for col in use_df.columns:
        out.append(f"<th>{html.escape(str(col))}</th>")
    out.append("</tr></thead><tbody>")
    for _, row in use_df.iterrows():
        out.append("<tr>")
        for col in use_df.columns:
            out.append(f"<td>{html.escape(clean_text(row[col]))}</td>")
        out.append("</tr>")
    out.append("</tbody></table>")
    if max_rows and len(df) > max_rows:
        out.append(f"<p class='small'>Showing first {max_rows} of {len(df)} rows.</p>")
    return "".join(out)


def make_static_html(events: list[dict[str, Any]], summary_df: pd.DataFrame, mapping_source_df: pd.DataFrame) -> str:
    generated = datetime.now().strftime("%d/%m/%Y %H:%M")
    groups = sorted({(e["area"], e["stage"]) for e in events if e["area"] != "Other / unmapped"}, key=area_stage_sort_key)
    other_groups = sorted({(e["area"], e["stage"]) for e in events if e["area"] == "Other / unmapped"}, key=area_stage_sort_key)

    nav_links = []
    for area, stage in groups:
        anchor = f"{area}-{stage}-submission".lower().replace("/", "-").replace(" ", "-")
        nav_links.append(f"<a href='#{html.escape(anchor)}'>{html.escape(area)} {html.escape(stage)}</a>")

    submission_sections = [render_area_stage_section(events, area, stage, "Submission") for area, stage in groups]
    all_event_sections = [render_area_stage_section(events, area, stage, None) for area, stage in groups]
    other_sections = [render_area_stage_section(events, area, stage, None) for area, stage in other_groups]

    css = """
body { font-family: Arial, sans-serif; margin: 24px; background: #f8fafc; color: #111827; }
h1 { margin-bottom: 4px; }
.note { background: #eff6ff; border: 1px solid #bfdbfe; padding: 12px 14px; border-radius: 8px; margin: 14px 0; }
.warn { background: #fff7ed; border: 1px solid #fed7aa; padding: 12px 14px; border-radius: 8px; margin: 14px 0; }
.nav { background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px; margin: 14px 0; position: sticky; top: 0; z-index: 5; }
.nav a { display: inline-block; margin: 3px 5px 3px 0; padding: 5px 8px; background: #e5e7eb; border-radius: 999px; color: #111827; text-decoration: none; font-size: 13px; }
.legend { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0; font-size: 13px; }
.pill { padding: 3px 7px; border-radius: 999px; background: #e5e7eb; font-size: 11px; }
.section { margin: 22px 0 36px; }
.subtitle { font-weight: normal; color: #6b7280; font-size: 14px; }
.small { font-size: 12px; color: #6b7280; }
.month { background: white; border: 1px solid #e5e7eb; border-radius: 8px; margin: 12px 0; overflow: hidden; }
.month h3 { text-align: center; font-size: 16px; margin: 0; padding: 8px; background: #f3f4f6; }
.grid { display: grid; grid-template-columns: repeat(7, 1fr); }
.dow { font-weight: bold; text-align: center; padding: 7px; background: #f9fafb; border-bottom: 1px solid #e5e7eb; font-size: 12px; }
.day { min-height: 92px; border-right: 1px solid #e5e7eb; border-bottom: 1px solid #e5e7eb; padding: 5px; background: white; }
.day:nth-child(7n) { border-right: none; }
.empty { background: #f3f4f6; }
.date { font-weight: bold; font-size: 12px; color: #374151; margin-bottom: 3px; }
.event { font-size: 11px; margin: 2px 0; padding: 3px 4px; border-radius: 5px; line-height: 1.2; cursor: default; border-left: 4px solid #6b7280; }
.Release { background: #dbeafe; }
.Submission { background: #fecaca; font-weight: bold; }
.Feedback { background: #dcfce7; }
table { border-collapse: collapse; width: 100%; background: white; margin: 10px 0 18px; }
th, td { border: 1px solid #e5e7eb; padding: 6px; font-size: 12px; text-align: left; vertical-align: top; }
th { background: #f3f4f6; }
hr { border: none; border-top: 1px solid #e5e7eb; margin: 28px 0; }
"""

    other_block = ""
    if other_sections:
        other_block = (
            "<hr><h1>Unmapped/manual-check events</h1>"
            "<div class='warn'><strong>Note:</strong> These rows could not be assigned to a normal programme/stage view. "
            "They should be checked against the programme-module mapping before sharing more widely.</div>"
            + "".join(other_sections)
        )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>MAP Original Assessment Calendar — Module Owner Submitted Dates</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>{css}</style>
</head>
<body>
<h1>MAP Original Assessment Calendar — Module Owner Submitted Dates</h1>
<div class="small">Generated: {html.escape(generated)}</div>
<div class="note">
  <strong>Important:</strong> This is a visualisation of the original MAP-submitted non-exam assessment dates. It does not apply review-stage or deconflicted date changes and it is not the final EEECS assessment calendar.
</div>
<div class="note">
  Programme/stage views are taken from the APD workbook where available. If that field is blank, the agent uses the programme-module mapping file as a fallback, so baseline modules such as ECS1001 are included in their correct programme/stage views.
</div>
<div class="legend">
  <span class="pill">[R] Release</span>
  <span class="pill">[S] Submission</span>
  <span class="pill">[F] Feedback</span>
  <span class="pill">Grey edge = original submitted date</span>
</div>
<div class="nav"><strong>Jump to submission calendar:</strong><br>{''.join(nav_links)}</div>
<h2>Original submission calendar summary</h2>
<p class="small">This summary excludes Other/unmapped rows. Duplicate pathway rows are collapsed for visual display.</p>
{df_to_html_table(summary_df)}
<h2>Programme/stage mapping source summary</h2>
<p class="small">This shows whether programme/stage placement came directly from the APD workbook or from the programme-module mapping fallback.</p>
{df_to_html_table(mapping_source_df)}
<hr>
<h1>Submission calendars by programme/stage</h1>
<p class="small">These show the original module-owner submitted submission dates only.</p>
{''.join(submission_sections)}
<hr>
<h1>All event calendars by programme/stage</h1>
<p class="small">These show original release, submission and feedback events together.</p>
{''.join(all_event_sections)}
{other_block}
</body>
</html>"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Create static original MAP-submitted assessment calendar HTML.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to APD working workbook or workbook containing original MAP dates")
    parser.add_argument("--mapping", type=Path, default=None, help="Path to programme-module mapping CSV. If omitted, common repo locations are searched.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Output folder")
    args = parser.parse_args()

    input_path = args.input
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    if not input_path.exists():
        raise FileNotFoundError(f"Input workbook not found: {input_path}")

    mapping_path = resolve_mapping_path(args.mapping)
    if mapping_path:
        print(f"Programme-module mapping fallback file: {mapping_path}")
    else:
        print("Programme-module mapping fallback file: NOT FOUND. Blank Programme Stage Key(s) rows may remain unmapped.")
    mapping_lookup, module_title_lookup, mapping_df = load_mapping_lookup(mapping_path)
    print(f"Programme-module mapping fallback modules loaded: {len(mapping_lookup)}")

    df = pd.read_excel(input_path, sheet_name=SHEET_NAME, dtype=str)
    df.columns = [normalise_header(c) for c in df.columns]

    events, stats = build_original_events(df, mapping_lookup, module_title_lookup)
    events_df = pd.DataFrame(events)
    summary_df = make_summary_table(events)
    mapping_source_df = make_mapping_source_summary(events)

    events_path = output_dir / "MAP_Original_Assessment_Calendar_Events.csv"
    summary_path = output_dir / "MAP_Original_Assessment_Calendar_Summary_By_Area_Stage.csv"
    html_path = output_dir / "MAP_Original_Assessment_Calendar_2026_27.html"

    events_df.to_csv(events_path, index=False, encoding="utf-8-sig")
    summary_df.to_csv(summary_path, index=False, encoding="utf-8-sig")
    html_path.write_text(make_static_html(events, summary_df, mapping_source_df), encoding="utf-8")

    submissions = events_df[(events_df["event_type"] == "Submission") & (events_df["area"] != "Other / unmapped")] if not events_df.empty else events_df
    other_submissions = events_df[(events_df["event_type"] == "Submission") & (events_df["area"] == "Other / unmapped")] if not events_df.empty else events_df

    print(f"Skipped rows not included in EEECS calendar: {stats['skipped_not_calendar']}")
    print(f"Skipped formal-exam rows: {stats['skipped_exam']}")
    print("Assessment rows by programme/stage source:")
    for source, count in sorted(stats["rows_by_mapping_source"].items()):
        print(f"  {source}: {count}")
    print(f"Unmapped module codes after fallback: {', '.join(stats['unmapped_modules']) if stats['unmapped_modules'] else 'None'}")

    print("\nCreated original assessment calendar outputs:")
    print(f"  HTML:    {html_path}")
    print(f"  Events:  {events_path}")
    print(f"  Summary: {summary_path}")
    print("\nSummary:")
    print(f"  Calendar display events generated: {len(events_df)}")
    print(f"  Original submission display events, excluding Other/unmapped: {len(submissions)}")
    print(f"  Other/unmapped submission display events after fallback: {len(other_submissions)}")
    print("\nNote: this is original MAP-submitted non-exam assessment calendar only. It does not apply review-stage or deconflicted date changes.")

if __name__ == "__main__":
    main()
