# MAP Assessments Prototype

**Project:** Agentic MAP-QA  
**Related issue:** #15  
**Document version:** 0.1  
**Status:** Initial prototype implemented  

## 1. Purpose

This document records the initial implementation of the `MAP_Assessments` Microsoft List.

The List stores one structured record for each assessment component linked to an annual module plan in `MAP_Module_Plans`.

The design supports both:

- assessment planning before the academic year begins;
- monitoring of actual release, submission and feedback dates during the academic year.

## 2. Relationship with module plans

Each assessment record is linked to one annual module plan through the `Module Plan` lookup field.

The lookup uses the unique `Plan Reference` from `MAP_Module_Plans`.

Example:

```text
2026-27_CSC1037
```

This ensures that assessment records are linked to the correct module and academic year.

## 3. Core implemented columns

| Column | Type | Required | Configuration |
|---|---|---:|---|
| Module Plan | Lookup | Yes | Links to `Plan Reference` in `MAP_Module_Plans` |
| Assessment Number | Number | Yes | Whole number; minimum 1 |
| Assessment Title | Single line of text | Yes | Free-text assessment title |
| Assessment Type | Choice | Yes | Controlled assessment category |
| Assessment Weight | Number | Yes | Percentage value from 0 to 100 |
| Assessment Mode | Choice | Yes | Individual, Group or Mixed |
| Is Summative | Yes/No | Yes | Default value: Yes |
| Is Formal Examination | Yes/No | Yes | Default value: No |
| Include in EEECS Calendar | Yes/No | Yes | Default value: Yes |
| Feedback Monitoring Notes | Multiple lines of text | No | Optional monitoring notes |

## 4. Assessment type values

The controlled `Assessment Type` values are:

- `Coursework / Assignment`
- `Project`
- `Class Test`
- `Practical Test`
- `Laboratory Assessment`
- `Presentation / Oral / Demonstration`
- `Portfolio`
- `Report`
- `Formal Examination`
- `Other`

The `Assessment Title` field should be used to record the specific title, sequence, topic or local naming convention.

For example:

| Assessment Title | Assessment Type |
|---|---|
| Python Programming Assessment | Coursework / Assignment |
| Class Test 1 | Class Test |
| Practical Programming Test 1 | Practical Test |
| Final Theory Examination | Formal Examination |

## 5. Assessment mode values

The controlled `Assessment Mode` values are:

- `Individual`
- `Group`
- `Mixed`

This separates the assessment format from whether students complete it individually or as a group.

## 6. Predicted date fields

The planning date fields are:

| Column | Purpose |
|---|---|
| Predicted Release Date | Planned date on which the assessment brief will be released |
| Predicted Submission Date | Planned student submission deadline |
| Predicted Feedback Date | Planned date on which feedback will be available |

All predicted date fields are configured as:

- Date only;
- not required;
- initially blank.

They are not required at List level because formal examinations may not have locally controlled coursework release, submission or feedback dates.

## 7. Actual date fields

The monitoring date fields are:

| Column | Purpose |
|---|---|
| Actual Release Date | Actual date on which the assessment brief was released |
| Actual Submission Date | Final submission deadline that applied to students |
| Actual Feedback Date | Actual date on which feedback was made available |

All actual date fields are configured as:

- Date only;
- not required;
- initially blank.

The actual date fields will be completed during the academic year.

`Actual Feedback Date` is particularly important because it will later support evaluation of whether feedback was provided within the required feedback period.

## 8. Feedback monitoring logic

The intended QA logic is:

```text
Actual Submission Date + 20 working days = Feedback Due Date
```

Then:

```text
Actual Feedback Date on or before Feedback Due Date = On time
Actual Feedback Date after Feedback Due Date = Late
```

This calculation should not be implemented as a simple 20-calendar-day calculation because weekends and institutional closure days must be excluded.

The calculation will later be handled by Power Automate, Python validation code or the agentic QA layer.

## 9. Formal examination representation

Formal examinations are represented as normal assessment records, but with specific values.

Example:

| Field | Value |
|---|---|
| Assessment Title | Formal Examination |
| Assessment Type | Formal Examination |
| Assessment Mode | Individual |
| Is Summative | Yes |
| Is Formal Examination | Yes |
| Include in EEECS Calendar | No |
| Predicted Release Date | Blank |
| Predicted Submission Date | Blank |
| Predicted Feedback Date | Blank |
| Actual Release Date | Blank |
| Actual Submission Date | Blank |
| Actual Feedback Date | Blank |

This ensures that examination weightings contribute to the module total while centrally managed examination dates are not confused with coursework dates.

## 10. Coursework representation

Coursework, tests, projects and other locally managed assessments should normally use:

| Field | Typical value |
|---|---|
| Is Summative | Yes |
| Is Formal Examination | No |
| Include in EEECS Calendar | Yes |
| Predicted Release Date | Completed where applicable |
| Predicted Submission Date | Completed where applicable |
| Predicted Feedback Date | Completed where applicable |
| Actual dates | Initially blank |

Actual dates will be updated later during monitoring.

## 11. Validation requirements

The prototype supports later validation of:

- one assessment component per row;
- assessment numbers within each module plan;
- total assessment weightings equalling 100%;
- predicted release date before predicted submission date;
- predicted submission date before predicted feedback date;
- actual feedback date against the 20-working-day requirement;
- actual feedback date against the predicted feedback date;
- exclusion of formal examinations from the local EEECS coursework calendar.

## 12. Initial implementation outcome

The `MAP_Assessments` List has been created with structured fields for:

- module-plan linkage;
- assessment identity;
- assessment type and mode;
- weighting;
- summative and formal-examination flags;
- EEECS calendar inclusion;
- predicted dates;
- actual monitoring dates;
- feedback monitoring notes.

A key design correction was made during implementation: all six date fields were set as optional so that formal examinations can be saved without locally controlled coursework dates.

## 13. Data protection

The public GitHub repository must not include:

- staff names;
- staff email addresses;
- identifiable module records;
- exported Microsoft Lists data containing operational information;
- screenshots showing personal or institutional details;
- private Microsoft Lists or SharePoint links.

Public documentation records only the structure, configuration and anonymised implementation outcomes.

## 14. Current limitations

The current prototype has the following limitations:

1. Conditional date requirements are not yet enforced.
2. Coursework date fields are optional at List level to allow formal examinations.
3. Formal-examination date fields are not yet automatically hidden.
4. Feedback due dates are not yet calculated.
5. Feedback timeliness status is not yet derived.
6. Assessment weighting totals are not yet automatically checked.
7. Workflow permissions and monitoring reminders are not yet implemented.

## 15. Next steps

1. Add representative assessment records for one module plan.
2. Test coursework records with predicted dates.
3. Test a formal-examination record with blank dates.
4. Confirm that assessment weightings total 100%.
5. Export the List and compare the structure with the target Assessment Pivot workbook.
6. Design calculated or derived QA fields for feedback monitoring.
7. Evaluate Power Apps for conditional display and required-field logic.
8. Prepare the assessment records for deterministic validation and agent-based deconfliction.