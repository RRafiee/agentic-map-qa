# Original Assessment Calendar Agent

## Purpose

The original assessment calendar agent generates a static visual calendar of the original MAP-submitted assessment dates.

It is intended to provide a baseline view of the non-exam assessment calendar before APD deconfliction changes are applied.

This allows comparison between:

- the original MAP-submitted assessment pattern;
- the current APD scenario calendar;
- the final confirmed assessment calendar.

## Input

The agent reads the local APD working workbook and uses only the original MAP-submitted dates.

Expected worksheet:

```text
Assessment_Plan_Working
```

The agent uses:

- original predicted release date;
- original predicted submission date;
- original predicted feedback date;
- module code;
- assessment code;
- assessment title;
- assessment type;
- assessment weight;
- programme/stage exposure;
- EEECS calendar inclusion flag;
- formal examination flag.

## Scope

The agent includes non-exam assessments only.

Formal examination rows are excluded where the formal-exam indicator is available.

The agent does not apply:

- APD-proposed dates;
- review-stage changes;
- deconflicted dates;
- final calendar dates.

## Date logic

For each assessment, the agent uses only the original MAP-submitted dates:

```text
Original predicted release date
Original predicted submission date
Original predicted feedback date
```

Each assessment can generate up to three calendar events:

```text
[R] Release
[S] Submission
[F] Feedback
```

## Output

The agent creates local-only outputs under:

```text
outputs/2026_27_readiness_03Sep/original_calendar_check/
```

Typical outputs are:

```text
MAP_Original_Assessment_Calendar_2026_27.html
MAP_Original_Assessment_Calendar_Events.csv
MAP_Original_Assessment_Calendar_Summary_By_Area_Stage.csv
```

These files are operational outputs and should not be committed to GitHub.

## Validation

The validator checks that:

- the HTML, event CSV and summary CSV are present;
- all dates parse correctly;
- no APD-related columns are present;
- no APD-proposed wording appears in the HTML;
- no exam-like assessment rows are included;
- programme/stage labels are clear;
- static HTML is generated without dropdown menus.

The latest validation confirmed:

- 741 calendar event rows;
- 247 release events;
- 247 submission events;
- 247 feedback events;
- 0 invalid dates;
- 0 exam-like assessment rows;
- no APD-related columns;
- no APD-proposed wording in the HTML.

## Interpretation

This calendar is a baseline visualisation of the original module-owner submitted MAP dates.

It is not:

- the APD scenario calendar;
- the final EEECS assessment calendar;
- an approval mechanism;
- a deconfliction decision tool.

It should be used alongside the APD scenario calendar to compare the original submitted pattern with the partially deconflicted or final assessment pattern.
