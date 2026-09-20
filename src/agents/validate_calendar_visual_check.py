from __future__ import annotations

from pathlib import Path
import pandas as pd

DEFAULT_OUTPUT_DIR = Path('outputs/2026_27_readiness_03Sep/calendar_visual_check')


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description='Validate MAP current APD scenario calendar visual check outputs.')
    parser.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    out = args.output_dir
    html_path = out / 'MAP_Calendar_Visual_Check_2026_27.html'
    events_path = out / 'MAP_Calendar_Visual_Check_Events.csv'
    summary_path = out / 'MAP_Calendar_Visual_Check_Summary_By_Area_Stage.csv'
    changes_path = out / 'MAP_Calendar_Visual_Check_APD_Proposed_Submission_Changes.csv'

    print('CURRENT APD SCENARIO CALENDAR VALIDATION')
    print('=' * 55)
    for p in [html_path, events_path, summary_path, changes_path]:
        print(f'{p.name}: {"FOUND" if p.exists() else "MISSING"}')
    if not events_path.exists():
        print('\nCannot validate without events CSV.')
        return

    events = pd.read_csv(events_path, dtype=str).fillna('')
    print('\nEvents CSV')
    print(f'Rows: {len(events)}')
    print(f'Columns: {list(events.columns)}')

    required = [
        'source_row', 'view', 'date_iso', 'date_label', 'event_type', 'event_short',
        'date_source', 'area', 'stage', 'programme_stage_key', 'programme_stage_source',
        'module_code', 'assessment_code', 'assessment_title', 'original_submission_date',
        'apd_proposed_submission_date', 'same_day_submission_pressure', 'near_date_submission_pressure'
    ]
    missing = [c for c in required if c not in events.columns]
    print(f'Missing required columns: {missing if missing else "None"}')

    parsed = pd.to_datetime(events['date_iso'], errors='coerce') if 'date_iso' in events.columns else pd.Series(dtype='datetime64[ns]')
    print(f'Invalid date_iso values: {int(parsed.isna().sum())}')

    print('\nViews:')
    print(events['view'].value_counts().to_string())
    print('\nEvent types:')
    print(events['event_type'].value_counts().to_string())
    print('\nDate sources:')
    print(events['date_source'].value_counts().to_string())

    if 'programme_stage_source' in events.columns:
        print('\nProgramme/stage mapping sources:')
        print(events['programme_stage_source'].value_counts().to_string())

    current_sub = events[
        (events['view'] == 'Current APD scenario')
        & (events['event_type'] == 'Submission')
        & (events['area'] != 'Other / unmapped')
    ]
    print(f'\nCurrent scenario submission events excluding Other/unmapped: {len(current_sub)}')
    print(f'Unique current-scenario submission assessments: {current_sub["assessment_code"].nunique()}')
    print(f'APD proposed submission events: {(current_sub["date_source"] == "APD proposed date").sum()}')
    print(f'Same-day pressure markers: {(current_sub["same_day_submission_pressure"] == "Yes").sum()}')
    print(f'Near-date pressure markers: {(current_sub["near_date_submission_pressure"] == "Yes").sum()}')

    other_sub = events[
        (events['view'] == 'Current APD scenario')
        & (events['event_type'] == 'Submission')
        & (events['area'] == 'Other / unmapped')
    ]
    print(f'Other/unmapped current-scenario submission events: {len(other_sub)}')
    if not other_sub.empty:
        print('Other/unmapped modules:')
        print(other_sub[['module_code', 'assessment_code', 'assessment_title']].drop_duplicates().to_string(index=False))

    print('\nTargeted checks:')
    targets = [
        ('ECS1001', 'EEE/CE', 'Stage 1'),
        ('CSC2059', 'EEE/CE', 'Stage 2'),
        ('ELE3045', 'EEE/CE', 'Stage 3'),
    ]
    for module, area, stage in targets:
        hit = current_sub[
            (current_sub['module_code'] == module)
            & (current_sub['area'] == area)
            & (current_sub['stage'] == stage)
        ]
        status = 'PASS' if not hit.empty else 'FAIL'
        print(f'{status}: {module} in {area} {stage}: {hit["assessment_code"].nunique()} unique submission assessment(s)')
        if not hit.empty:
            print(hit[['module_code', 'assessment_code', 'assessment_title', 'date_label', 'date_source', 'programme_stage_key', 'programme_stage_source']].drop_duplicates().to_string(index=False))

    if summary_path.exists():
        summary = pd.read_csv(summary_path, dtype=str).fillna('')
        print(f'\nSummary file rows: {len(summary)}')
        print(summary.to_string(index=False))

    if changes_path.exists():
        changes = pd.read_csv(changes_path, dtype=str).fillna('')
        print(f'\nAPD proposed changes rows: {len(changes)}')
        if not changes.empty:
            print(changes.head(50).to_string(index=False))
            # Light warning for likely typo dates outside core 2026/27 teaching year.
            if 'APD proposed submission' in changes.columns:
                parsed_changes = pd.to_datetime(changes['APD proposed submission'], dayfirst=True, errors='coerce')
                suspicious = changes[(parsed_changes < pd.Timestamp('2026-07-01')) | (parsed_changes > pd.Timestamp('2027-08-31'))]
                print(f'\nSuspicious APD proposed submission dates outside 2026/27 window: {len(suspicious)}')
                if len(suspicious):
                    print(suspicious.to_string(index=False))

    if html_path.exists():
        html = html_path.read_text(encoding='utf-8', errors='replace')
        print('\nHTML checks')
        print(f'Contains APD scenario title: {"Static Interim APD Scenario" in html or "Current APD scenario" in html}')
        print(f'Contains mapping fallback text: {"programme-module mapping fallback" in html.lower() or "mapping fallback" in html.lower()}')
        print(f'Contains dropdown/select menus: {"<select" in html.lower()}')
        print(f'HTML contains ECS1001: {"ECS1001" in html}')
        print(f'HTML contains CSC2059: {"CSC2059" in html}')
        print(f'HTML contains ELE3045: {"ELE3045" in html}')

    print('\nVALIDATION COMPLETE')


if __name__ == '__main__':
    main()
