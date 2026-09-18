# MAP Calendar Visual Check Agent

## Purpose

The calendar visual check agent provides an interim visual checking layer for the MAP deconfliction workflow.

It was added after APDs raised that row-based review alone makes it difficult to visualise assessment pressure, especially where resolving one assessment clash may create another same-day or near-date pressure point elsewhere in the programme/stage calendar.

The agent is not intended to replace the APD working workbook or the final EEECS assessment calendar. It provides a temporary, static visual aid for checking the current APD scenario.

## Rationale

The MAP deconfliction workbook is useful for structured review, but it is difficult to mentally visualise the impact of date changes from rows alone.

The visual check agent addresses this by converting the current APD working workbook into a static HTML calendar view. This allows APDs and the Director of Education to see how release, submission and feedback dates are distributed across programme/stage cohorts.

The immediate use case is to help answer the question:

> If the APD-proposed changes currently entered in the workbook were applied, would the assessment spread improve, or might new same-day or near-date pressure points be created?

## Input

The agent reads the latest local APD working workbook from the deconfliction output folder.

Expected workbook:

```text
outputs/2026_27_readiness_03Sep/deconfliction_cases/MAP_Assessment_Deconfliction_Working_2026_27_FIXED_UK_DATES.xlsx
```

Expected worksheet:

```text
Assessment_Plan_Working
```

The agent uses the following fields where available:

- original MAP-submitted release, submission and feedback dates;
- APD-proposed release, submission and feedback dates;
- module code, assessment code, assessment title and assessment type;
- programme/stage exposure;
- APD owner;
- MAP case type, severity and triggered rules;
- APD review status, APD decision, module-owner confirmation and comments.

## Date logic

The agent creates an interim current-scenario view.

For each release, submission and feedback event:

```text
Use APD-proposed date if entered;
otherwise use the original MAP-submitted date.
```

The agent does not infer final dates, approve changes, or overwrite the MAP workbook.

## Event types

Each assessment can generate up to three calendar events:

```text
[R] Release
[S] Submission
[F] Feedback
```

Submission dates are the primary deconfliction focus, but release and feedback dates are included to support wider QA checking.

## Programme/stage views

The static HTML output separates views by programme area and stage.

Examples include:

```text
CS/SE Stage 1
CS/SE Stage 2
CS/SE Stage 3
CS/SE Stage 4

EEE/CE Stage 1
EEE/CE Stage 2
EEE/CE Stage 3
EEE/CE Stage 4

CIT Stage 1
CIT Stage 2
CIT Stage 3

BIT Stage 1
BIT Stage 2
BIT Stage 3

Data Science Stage 1
Data Science Stage 2
Data Science Stage 3
```

Stage 3 and Stage 4 are intentionally kept separate because assessment exposure differs by stage.

## Output

The agent creates local files in:

```text
outputs/2026_27_readiness_03Sep/calendar_visual_check/
```

Typical outputs are:

```text
MAP_Calendar_Visual_Check_2026_27.html
MAP_Calendar_Visual_Check_Events.csv
MAP_Calendar_Visual_Check_Summary_By_Area_Stage.csv
MAP_Calendar_Visual_Check_APD_Proposed_Submission_Changes.csv
```

These files are operational outputs and should not be committed to GitHub.

## Static HTML design

Version 0.3 uses a static HTML design with no dropdown filters or dynamic JavaScript menus. This was chosen because the first interactive prototype caused browser/filtering issues in the urgent APD review context.

The static version provides:

- a clear title and warning that the output is not the final calendar;
- jump links to programme/stage sections;
- month-by-month calendar views;
- submission calendars by programme/stage;
- original and APD-proposed date information;
- visual markers for APD-proposed dates;
- markers for same-day and near-date submission pressure;
- summary tables for APD checking.

## De-duplication logic

Some assessments appear across multiple programmes or pathways because they affect more than one cohort. This is expected.

For the calendar display, duplicate pathway-level rows are collapsed within each programme/stage/date/assessment view so that the same assessment is not repeated unnecessarily within the same programme/stage calendar.

The same assessment may still correctly appear in more than one programme/stage view where it affects multiple cohorts.

## Interpretation

The generated HTML should be interpreted as an interim visual checking aid only.

It should not be used as:

- the final EEECS assessment calendar;
- a direct replacement for the APD working workbook;
- an approval mechanism;
- an automatic date-change system.

The APD working workbook remains the authoritative place for recording APD decisions and module-owner confirmation.

## Current implementation status

The implemented v0.3 agent successfully generates a static visual calendar from the current APD working workbook and creates summary outputs for local validation.

The current local run generated:

- static HTML visual checker;
- event-level CSV;
- programme/stage summary CSV;
- APD-proposed submission-date change CSV.

The output is suitable for interim visual checking once manually reviewed against known cases.
