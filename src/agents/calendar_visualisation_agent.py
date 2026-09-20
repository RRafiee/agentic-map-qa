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
DEFAULT_OUTPUT_DIR = Path("outputs/2026_27_readiness_03Sep/calendar_visual_check")
DEFAULT_MAPPING_INPUT = Path("data/raw/2026_27_snapshot_03Sep/programme_module_mapping_raw.csv")
SHEET_NAME = "Assessment_Plan_Working"

EVENT_TYPES = ["Release", "Submission", "Feedback"]
EVENT_ORDER = {"Submission": 0, "Release": 1, "Feedback": 2}
AREA_ORDER = ["CS/SE", "EEE/CE", "CIT", "BIT", "Data Science"]
STAGE_ORDER = ["Stage 1", "Stage 2", "Stage 3", "Stage 4"]


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


def find_col(df: pd.DataFrame, aliases: list[str], required: bool = False) -> str | None:
    norm_to_original = {normalise_header(c).lower(): c for c in df.columns}
    for alias in aliases:
        key = normalise_header(alias).lower()
        if key in norm_to_original:
            return norm_to_original[key]
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
        return ["Unmapped"]
    parts = [p.strip() for p in re.split(r"[;,\n]+", value) if p.strip()]
    return parts or ["Unmapped"]


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


def choose_current_date(original: date | None, proposed: date | None, decision: str) -> tuple[date | None, str]:
    # Proposed dates are shown as the current APD scenario unless APD decision explicitly says no date change.
    decision_l = decision.lower()
    if proposed and "no date change" not in decision_l:
        return proposed, "APD proposed date"
    return original, "Original submitted date"


def combine_unique(values: list[Any]) -> str:
    seen: list[str] = []
    for value in values:
        for part in re.split(r"[;\n]+", clean_text(value)):
            part = part.strip()
            if part and part not in seen:
                seen.append(part)
    return "; ".join(seen)


def is_truthy_value(value: Any) -> bool:
    value = clean_text(value).lower()
    return value in {"true", "yes", "1", "y"}


def load_programme_mapping(mapping_path: Path) -> dict[str, list[str]]:
    """Load module -> cohort-stage keys from the programme-module mapping file.

    This is used as a fallback when the APD working workbook has a blank
    Programme Stage Key(s) value. The fallback prevents normal, unflagged
    assessments from disappearing from the current scenario visualisation.
    """
    if not mapping_path.exists():
        print(f"Programme-module mapping fallback file not found: {mapping_path}")
        return {}

    mapping_df = pd.read_csv(mapping_path, dtype=str).fillna("")
    mapping_df.columns = [normalise_header(c) for c in mapping_df.columns]

    module_col = find_col(mapping_df, ["Module Code", "ModuleCode", "Module"], required=True)
    cohort_col = find_col(mapping_df, ["Cohort Key", "Programme Stage Key", "Programme Stage"], required=True)
    include_col = find_col(mapping_df, ["Include in Deconfliction", "Include", "Active"] )
    active_col = find_col(mapping_df, ["Active"] )

    mapping: dict[str, list[str]] = defaultdict(list)
    for _, row in mapping_df.iterrows():
        module_code = get_value(row, module_col).upper()
        cohort_key = get_value(row, cohort_col)
        if not module_code or not cohort_key:
            continue
        if active_col and not is_truthy_value(get_value(row, active_col)):
            continue
        if include_col and include_col != active_col and not is_truthy_value(get_value(row, include_col)):
            continue
        if cohort_key not in mapping[module_code]:
            mapping[module_code].append(cohort_key)

    print(f"Programme-module mapping fallback file: {mapping_path}")
    print(f"Programme-module mapping fallback modules loaded: {len(mapping)}")
    return dict(mapping)


def programme_keys_for_row(row: pd.Series, cols: dict[str, str | None], module_code: str, mapping_by_module: dict[str, list[str]]) -> tuple[list[str], str]:
    workbook_value = get_value(row, cols.get("programme_stage"))
    if workbook_value:
        return split_stage_keys(workbook_value), "Workbook Programme Stage Key(s)"
    fallback_keys = mapping_by_module.get(module_code.upper(), [])
    if fallback_keys:
        return fallback_keys, "Programme-module mapping fallback"
    return ["Unmapped"], "Unmapped"


def build_events(df: pd.DataFrame, mapping_by_module: dict[str, list[str]]) -> list[dict[str, Any]]:
    cols = {
        "academic_year": find_col(df, ["Academic Year"]),
        "module_code": find_col(df, ["Module Code", "ModuleCode", "Module"], required=True),
        "module_title": find_col(df, ["Module Title", "Module Title(s)", "Title"]),
        "assessment_number": find_col(df, ["Assessment Number", "Assessment #"]),
        "assessment_code": find_col(df, ["Assessment Code", "Assignment Code"], required=True),
        "assessment_title": find_col(df, ["Assessment Title", "Assignment Title"], required=True),
        "assessment_type": find_col(df, ["Assessment Type", "Type"]),
        "assessment_weight": find_col(df, ["Assessment Weight", "Weight"]),
        "assessment_period": find_col(df, ["Assessment Period", "Period"]),
        "include_calendar": find_col(df, ["Include in EEECS Calendar", "Include in Calendar"]),
        "formal_exam": find_col(df, ["Is Formal Examination", "Formal Examination", "Is Formal Exam"]),
        "original_release": find_col(df, ["Predicted Release Date", "Original Predicted Release Date", "Original Release Date"], required=True),
        "original_submission": find_col(df, ["Predicted Submission Date", "Original Predicted Submission Date", "Original Submission Date"], required=True),
        "original_feedback": find_col(df, ["Predicted Feedback Date", "Original Predicted Feedback Date", "Original Feedback Date"], required=True),
        "apd_release": find_col(df, ["APD Proposed Release Date", "Proposed Release Date"]),
        "apd_submission": find_col(df, ["APD Proposed Submission Date", "Proposed Submission Date"]),
        "apd_feedback": find_col(df, ["APD Proposed Feedback Date", "Proposed Feedback Date"]),
        "programme_stage": find_col(df, ["Programme Stage Key(s)", "Programme Stage Key", "Cohort Key", "Programme Stage"]),
        "apd_owner": find_col(df, ["APD Owner(s)", "APD Owner", "APD"]),
        "case_id": find_col(df, ["MAP Case ID(s)", "MAP Case ID", "Case ID"]),
        "pack_sections": find_col(df, ["MAP Pack Section(s)", "Review Area(s)"]),
        "case_types": find_col(df, ["MAP Case Type(s)", "Issue Type(s)", "Case Type"]),
        "severity": find_col(df, ["Highest Severity", "Severity"]),
        "rules": find_col(df, ["Rule Triggered", "Rule(s) Triggered", "Triggered Rules"]),
        "review_status": find_col(df, ["APD Review Status", "Review Status"]),
        "decision": find_col(df, ["APD Decision", "Decision"]),
        "owner_confirmed": find_col(df, ["Module Owner Confirmed", "Owner Confirmed"]),
        "comments": find_col(df, ["APD Comments / Justification", "APD Comments", "Comments / Justification", "Comments"]),
    }

    print("Column mapping used:")
    for k, v in cols.items():
        print(f"  {k}: {v}")

    raw_events: list[dict[str, Any]] = []

    for idx, row in df.iterrows():
        if not is_truthy_calendar_flag(get_value(row, cols["include_calendar"])):
            continue
        if is_truthy_value(get_value(row, cols["formal_exam"])):
            continue

        original_dates = {
            "Release": parse_date(get_value(row, cols["original_release"])),
            "Submission": parse_date(get_value(row, cols["original_submission"])),
            "Feedback": parse_date(get_value(row, cols["original_feedback"])),
        }
        proposed_dates = {
            "Release": parse_date(get_value(row, cols["apd_release"])),
            "Submission": parse_date(get_value(row, cols["apd_submission"])),
            "Feedback": parse_date(get_value(row, cols["apd_feedback"])),
        }

        module_code = get_value(row, cols["module_code"]).upper()
        assessment_code = get_value(row, cols["assessment_code"])
        decision = get_value(row, cols["decision"])
        programme_keys, programme_stage_source = programme_keys_for_row(row, cols, module_code, mapping_by_module)

        for programme_stage_key in programme_keys:
            area = area_from_key(programme_stage_key)
            stage = stage_from_key(programme_stage_key, fallback=get_value(row, cols["assessment_period"]))

            for event_type in EVENT_TYPES:
                original_date = original_dates[event_type]
                proposed_date = proposed_dates[event_type]
                current_date, current_source = choose_current_date(original_date, proposed_date, decision)

                for view_name, event_date, date_source in [
                    ("Original MAP dates", original_date, "Original submitted date"),
                    ("Current APD scenario", current_date, current_source),
                ]:
                    if not event_date:
                        continue
                    raw_events.append(
                        {
                            "source_row": str(int(idx) + 2),
                            "view": view_name,
                            "date_iso": event_date.isoformat(),
                            "date_label": fmt_date(event_date),
                            "event_type": event_type,
                            "event_short": event_type[0],
                            "date_source": date_source,
                            "area": area,
                            "stage": stage,
                            "programme_stage_key": programme_stage_key,
                            "programme_stage_source": programme_stage_source,
                            "academic_year": get_value(row, cols["academic_year"]),
                            "module_code": module_code,
                            "module_title": get_value(row, cols["module_title"]),
                            "assessment_number": get_value(row, cols["assessment_number"]),
                            "assessment_code": assessment_code,
                            "assessment_title": get_value(row, cols["assessment_title"]),
                            "assessment_type": get_value(row, cols["assessment_type"]),
                            "assessment_weight": get_value(row, cols["assessment_weight"]),
                            "assessment_period": get_value(row, cols["assessment_period"]),
                            "original_release_date": fmt_date(original_dates["Release"]),
                            "original_submission_date": fmt_date(original_dates["Submission"]),
                            "original_feedback_date": fmt_date(original_dates["Feedback"]),
                            "apd_proposed_release_date": fmt_date(proposed_dates["Release"]),
                            "apd_proposed_submission_date": fmt_date(proposed_dates["Submission"]),
                            "apd_proposed_feedback_date": fmt_date(proposed_dates["Feedback"]),
                            "apd_owner": get_value(row, cols["apd_owner"]),
                            "case_id": get_value(row, cols["case_id"]),
                            "pack_sections": get_value(row, cols["pack_sections"]),
                            "case_types": get_value(row, cols["case_types"]),
                            "severity": get_value(row, cols["severity"]),
                            "rules": get_value(row, cols["rules"]),
                            "review_status": get_value(row, cols["review_status"]),
                            "apd_decision": decision,
                            "module_owner_confirmed": get_value(row, cols["owner_confirmed"]),
                            "comments": get_value(row, cols["comments"]),
                            "same_day_submission_pressure": "No",
                            "near_date_submission_pressure": "No",
                        }
                    )

    collapsed = collapse_events_for_display(raw_events)
    mark_pressure(collapsed)
    return collapsed


def collapse_events_for_display(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for e in events:
        key = (e["view"], e["area"], e["stage"], e["event_type"], e["date_iso"], e["assessment_code"])
        grouped[key].append(e)

    collapsed: list[dict[str, Any]] = []
    combine_fields = [
        "source_row", "programme_stage_key", "apd_owner", "case_id",
        "pack_sections", "case_types", "rules", "comments"
    ]
    for rows in grouped.values():
        base = dict(rows[0])
        for field in combine_fields:
            base[field] = combine_unique([r.get(field, "") for r in rows])
        base["display_row_count"] = str(len(rows))
        collapsed.append(base)

    return sorted(
        collapsed,
        key=lambda e: (
            e["view"], e["area"], e["stage"], e["date_iso"],
            EVENT_ORDER.get(e["event_type"], 99), e["module_code"]
        )
    )


def mark_pressure(events: list[dict[str, Any]]) -> None:
    current_submissions = [e for e in events if e["view"] == "Current APD scenario" and e["event_type"] == "Submission"]
    by_group_date: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    by_group: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)

    for e in current_submissions:
        if e["area"] == "Other / unmapped":
            continue
        by_group_date[(e["area"], e["stage"], e["date_iso"])].append(e)
        by_group[(e["area"], e["stage"])].append(e)

    for rows in by_group_date.values():
        if len({r["assessment_code"] for r in rows}) > 1:
            for r in rows:
                r["same_day_submission_pressure"] = "Yes"

    for rows in by_group.values():
        rows_sorted = sorted(rows, key=lambda x: x["date_iso"])
        for i, a in enumerate(rows_sorted):
            da = datetime.fromisoformat(a["date_iso"]).date()
            for b in rows_sorted[i + 1:]:
                db = datetime.fromisoformat(b["date_iso"]).date()
                diff = (db - da).days
                if diff > 2:
                    break
                if a["assessment_code"] != b["assessment_code"]:
                    a["near_date_submission_pressure"] = "Yes"
                    b["near_date_submission_pressure"] = "Yes"


def area_stage_sort_key(item: tuple[str, str]) -> tuple[int, int, str, str]:
    area, stage = item
    area_rank = AREA_ORDER.index(area) if area in AREA_ORDER else 999
    stage_rank = STAGE_ORDER.index(stage) if stage in STAGE_ORDER else 999
    return (area_rank, stage_rank, area, stage)


def event_title(e: dict[str, Any]) -> str:
    lines = [
        f"Module: {e['module_code']} {e.get('module_title','')}",
        f"Assessment: {e.get('assessment_code','')} — {e.get('assessment_title','')}",
        f"Event: {e['event_type']}",
        f"Date shown: {e['date_label']}",
        f"Date source: {e['date_source']}",
        f"Original release: {e.get('original_release_date','')}",
        f"Original submission: {e.get('original_submission_date','')}",
        f"Original feedback: {e.get('original_feedback_date','')}",
        f"APD proposed release: {e.get('apd_proposed_release_date','')}",
        f"APD proposed submission: {e.get('apd_proposed_submission_date','')}",
        f"APD proposed feedback: {e.get('apd_proposed_feedback_date','')}",
        f"Programme/stage key(s): {e.get('programme_stage_key','')}",
        f"APD owner: {e.get('apd_owner','')}",
        f"Severity: {e.get('severity','')}",
        f"Issue type: {e.get('case_types','')}",
        f"Review status: {e.get('review_status','')}",
        f"Decision: {e.get('apd_decision','')}",
    ]
    return "\n".join(lines)


def event_html(e: dict[str, Any]) -> str:
    proposed = e.get("date_source") == "APD proposed date"
    pressure = e.get("event_type") == "Submission" and (
        e.get("same_day_submission_pressure") == "Yes" or e.get("near_date_submission_pressure") == "Yes"
    )
    classes = ["event", e["event_type"], "apd" if proposed else "orig"]
    if pressure:
        classes.append("pressure")
    label = f"[{html.escape(e['event_short'])}] {html.escape(e['module_code'])}"
    if proposed:
        label += " <span class='tag'>APD</span>"
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


def render_area_stage_section(events: list[dict[str, Any]], area: str, stage: str, view: str, event_filter: str | None = None) -> str:
    section_events = [
        e for e in events
        if e["view"] == view and e["area"] == area and e["stage"] == stage
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

    pressure_count = sum(
        1 for e in section_events
        if e["event_type"] == "Submission" and (e["same_day_submission_pressure"] == "Yes" or e["near_date_submission_pressure"] == "Yes")
    )
    apd_count = sum(1 for e in section_events if e["date_source"] == "APD proposed date")
    anchor = f"{area}-{stage}-{view}-{event_filter or 'all'}".lower().replace("/", "-").replace(" ", "-")
    title_extra = "submission dates" if event_filter == "Submission" else "release, submission and feedback dates"

    out = [
        f"<section id='{html.escape(anchor)}' class='section'>",
        f"<h2>{html.escape(area)} — {html.escape(stage)} <span class='subtitle'>({html.escape(title_extra)})</span></h2>",
        f"<p class='small'>Visible events: {len(section_events)}; APD proposed-date events: {apd_count}; submission pressure markers: {pressure_count}. Hover over an event to see original and APD proposed dates.</p>",
    ]
    for year, month in months:
        out.append(month_grid([e for e in section_events if e["date_iso"].startswith(f"{year}-{month:02d}")], year, month))
    out.append("</section>")
    return "".join(out)


def make_summary_table(events: list[dict[str, Any]]) -> pd.DataFrame:
    current_sub = [e for e in events if e["view"] == "Current APD scenario" and e["event_type"] == "Submission" and e["area"] != "Other / unmapped"]
    if not current_sub:
        return pd.DataFrame()
    rows = []
    for (area, stage), group in defaultdict(list).items():
        pass
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for e in current_sub:
        groups[(e["area"], e["stage"])].append(e)
    for area, stage in sorted(groups, key=area_stage_sort_key):
        group = groups[(area, stage)]
        rows.append({
            "area": area,
            "stage": stage,
            "submission_events": len(group),
            "unique_assessments": len({e["assessment_code"] for e in group}),
            "apd_proposed_submission_events": sum(1 for e in group if e["date_source"] == "APD proposed date"),
            "same_day_markers": sum(1 for e in group if e["same_day_submission_pressure"] == "Yes"),
            "near_date_markers": sum(1 for e in group if e["near_date_submission_pressure"] == "Yes"),
        })
    return pd.DataFrame(rows)


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


def make_changed_dates_table(events: list[dict[str, Any]]) -> pd.DataFrame:
    submissions = [
        e for e in events
        if e["view"] == "Current APD scenario"
        and e["event_type"] == "Submission"
        and e["date_source"] == "APD proposed date"
        and e["area"] != "Other / unmapped"
    ]
    rows = []
    seen = set()
    for e in submissions:
        key = (e["area"], e["stage"], e["assessment_code"], e["date_iso"])
        if key in seen:
            continue
        seen.add(key)
        rows.append({
            "Area": e["area"],
            "Stage": e["stage"],
            "Module": e["module_code"],
            "Assessment": e["assessment_title"],
            "Original submission": e["original_submission_date"],
            "APD proposed submission": e["apd_proposed_submission_date"],
            "Review status": e["review_status"],
            "APD decision": e["apd_decision"],
            "Same-day pressure": e["same_day_submission_pressure"],
            "Near-date pressure": e["near_date_submission_pressure"],
        })
    return pd.DataFrame(rows).sort_values(["Area", "Stage", "APD proposed submission", "Module"]) if rows else pd.DataFrame()


def make_static_html(events: list[dict[str, Any]], summary_df: pd.DataFrame, changed_df: pd.DataFrame) -> str:
    generated = datetime.now().strftime("%d/%m/%Y %H:%M")
    groups = sorted({(e["area"], e["stage"]) for e in events if e["area"] != "Other / unmapped"}, key=area_stage_sort_key)

    nav_links = []
    for area, stage in groups:
        anchor = f"{area}-{stage}-current-apd-scenario-submission".lower().replace("/", "-").replace(" ", "-")
        nav_links.append(f"<a href='#{html.escape(anchor)}'>{html.escape(area)} {html.escape(stage)}</a>")

    submission_sections = [render_area_stage_section(events, area, stage, "Current APD scenario", "Submission") for area, stage in groups]
    all_event_sections = [render_area_stage_section(events, area, stage, "Current APD scenario", None) for area, stage in groups]

    css = """
body { font-family: Arial, sans-serif; margin: 24px; background: #f8fafc; color: #111827; }
h1 { margin-bottom: 4px; }
.note { background: #fff7ed; border: 1px solid #fed7aa; padding: 12px 14px; border-radius: 8px; margin: 14px 0; }
.nav { background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px; margin: 14px 0; position: sticky; top: 0; z-index: 5; }
.nav a { display: inline-block; margin: 3px 5px 3px 0; padding: 5px 8px; background: #e5e7eb; border-radius: 999px; color: #111827; text-decoration: none; font-size: 13px; }
.legend { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0; font-size: 13px; }
.pill, .tag { padding: 3px 7px; border-radius: 999px; background: #e5e7eb; font-size: 11px; }
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
.event { font-size: 11px; margin: 2px 0; padding: 3px 4px; border-radius: 5px; line-height: 1.2; cursor: default; }
.Release { background: #dbeafe; }
.Submission { background: #fecaca; font-weight: bold; }
.Feedback { background: #dcfce7; }
.apd { border-left: 4px solid #7c3aed; }
.orig { border-left: 4px solid #6b7280; }
.pressure { outline: 2px solid #ef4444; }
table { border-collapse: collapse; width: 100%; background: white; margin: 10px 0 18px; }
th, td { border: 1px solid #e5e7eb; padding: 6px; font-size: 12px; text-align: left; vertical-align: top; }
th { background: #f3f4f6; }
hr { border: none; border-top: 1px solid #e5e7eb; margin: 28px 0; }
"""

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>MAP Calendar Visual Check — Static Interim APD Scenario</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>{css}</style>
</head>
<body>
<h1>MAP Calendar Visual Check — Static Interim APD Scenario</h1>
<div class="small">Generated: {html.escape(generated)}</div>
<div class="note">
  <strong>Important:</strong> This is an interim visual checking view generated from the current APD working workbook. It shows the current APD scenario: APD proposed dates where entered, otherwise original submitted MAP dates. It is not the final EEECS assessment calendar.<br>
  Programme-stage views use the workbook Programme Stage Key(s) where present, and the programme-module mapping fallback where the workbook field is blank.
</div>
<div class="legend">
  <span class="pill">[R] Release</span>
  <span class="pill">[S] Submission</span>
  <span class="pill">[F] Feedback</span>
  <span class="pill">Purple edge = APD proposed date</span>
  <span class="pill">Grey edge = original submitted date</span>
  <span class="pill">Red outline = possible same-day/near-date submission pressure</span>
</div>
<div class="nav"><strong>Jump to submission calendar:</strong><br>{''.join(nav_links)}</div>
<h2>Current submission pressure summary</h2>
<p class="small">This summary excludes Other/unmapped rows. Duplicate pathway rows are collapsed for visual display.</p>
{df_to_html_table(summary_df)}
<h2>APD proposed submission-date changes currently visible in the scenario</h2>
<p class="small">These are proposed/pending scenario dates, not final confirmed calendar dates.</p>
{df_to_html_table(changed_df, max_rows=100)}
<hr>
<h1>Submission calendars by programme/stage</h1>
<p class="small">These are the main views for checking student workload and possible clashes.</p>
{''.join(submission_sections)}
<hr>
<h1>All event calendars by programme/stage</h1>
<p class="small">These show release, submission and feedback events together. Use this as a wider QA overview; submission events remain the main deconfliction focus.</p>
{''.join(all_event_sections)}
</body>
</html>"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Create static interim MAP calendar visual check HTML.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to latest APD working workbook")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Output folder")
    parser.add_argument("--mapping-input", type=Path, default=DEFAULT_MAPPING_INPUT, help="Programme-module mapping CSV used as fallback for blank Programme Stage Key(s)")
    args = parser.parse_args()

    input_path = args.input
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    if not input_path.exists():
        raise FileNotFoundError(f"Input workbook not found: {input_path}")

    df = pd.read_excel(input_path, sheet_name=SHEET_NAME, dtype=str)
    df.columns = [normalise_header(c) for c in df.columns]
    mapping_by_module = load_programme_mapping(args.mapping_input)

    events = build_events(df, mapping_by_module)
    events_df = pd.DataFrame(events)
    summary_df = make_summary_table(events)
    changed_df = make_changed_dates_table(events)

    csv_path = output_dir / "MAP_Calendar_Visual_Check_Events.csv"
    summary_path = output_dir / "MAP_Calendar_Visual_Check_Summary_By_Area_Stage.csv"
    changed_path = output_dir / "MAP_Calendar_Visual_Check_APD_Proposed_Submission_Changes.csv"
    html_path = output_dir / "MAP_Calendar_Visual_Check_2026_27.html"

    events_df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    summary_df.to_csv(summary_path, index=False, encoding="utf-8-sig")
    changed_df.to_csv(changed_path, index=False, encoding="utf-8-sig")
    html_path.write_text(make_static_html(events, summary_df, changed_df), encoding="utf-8")

    current = events_df[events_df["view"] == "Current APD scenario"] if not events_df.empty else events_df
    submissions = current[(current["event_type"] == "Submission") & (current["area"] != "Other / unmapped")] if not current.empty else current

    print("\nCreated static calendar visual check outputs:")
    print(f"  HTML:    {html_path}")
    print(f"  Events:  {csv_path}")
    print(f"  Summary: {summary_path}")
    print(f"  Changes: {changed_path}")
    print("\nSummary:")
    print(f"  Calendar display events generated: {len(events_df)}")
    print(f"  Current scenario submission display events, excluding Other/unmapped: {len(submissions)}")
    if not submissions.empty:
        print(f"  Same-day submission pressure markers: {(submissions['same_day_submission_pressure'] == 'Yes').sum()}")
        print(f"  Near-date submission pressure markers: {(submissions['near_date_submission_pressure'] == 'Yes').sum()}")
        print(f"  APD proposed submission events: {(submissions['date_source'] == 'APD proposed date').sum()}")
    if not events_df.empty and "programme_stage_source" in events_df.columns:
        print("  Programme/stage mapping sources:")
        for source, count in events_df["programme_stage_source"].value_counts().items():
            print(f"    {source}: {count}")
        unmapped_modules = sorted(events_df.loc[events_df["programme_stage_source"] == "Unmapped", "module_code"].dropna().unique())
        if unmapped_modules:
            print(f"  Unmapped module codes after fallback: {', '.join(unmapped_modules)}")
    print("\nNote: v0.4 is static HTML with programme-module mapping fallback for blank Programme Stage Key(s).")


if __name__ == "__main__":
    main()
