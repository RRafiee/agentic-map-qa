# MAP Assessments Validation

**Project:** Agentic MAP-QA  
**Related issue:** #17  
**Document version:** 0.1  
**Status:** Initial validation completed  

## 1. Purpose

This document records the initial validation of the `MAP_Assessments` Microsoft List.

The validation focused on whether the List can represent assessment components as structured records linked to an annual module plan in `MAP_Module_Plans`.

The test also checked whether the List can support both assessment planning and later QA monitoring of feedback timeliness.

## 2. Validation scope

The validation used one annual module plan selected from `MAP_Module_Plans`.

The module plan was used only to test the structure and behaviour of the `MAP_Assessments` List. No identifiable operational records are included in this public documentation.

The validation focused on:

- one assessment component per row;
- linkage to one annual module plan;
- assessment number, title, type, mode and weighting;
- predicted assessment dates;
- actual monitoring date fields;
- representation of formal examinations;
- EEECS calendar inclusion;
- total assessment weighting.

## 3. Assessment records created

Two assessment records were created for one annual module plan.

The combined assessment weighting was confirmed as `100%`.

This confirms that the List can represent multiple assessment components linked to one module plan and that their weights can be checked against the expected module total.

## 4. Coursework or locally managed assessment test

A locally managed assessment record was created successfully.

The test confirmed that:

- the assessment could be linked to the correct module plan;
- an assessment number could be recorded;
- an assessment title could be entered;
- an assessment type could be selected;
- the assessment weight could be entered as a percentage;
- the assessment mode could be selected;
- predicted release, submission and feedback dates could be recorded;
- actual release, submission and feedback dates could remain blank;
- the record could be included in the EEECS assessment calendar.

This supports the planned use of `MAP_Assessments` for collecting structured coursework assessment information before the academic year begins.

## 5. Formal examination or centrally managed assessment test

A formal examination or centrally managed assessment record was tested using the formal-examination fields.

The test confirmed that:

- the assessment could be represented as a normal assessment record;
- the assessment weighting could contribute to the module total;
- `Is Formal Examination` could be set to `Yes`;
- `Include in EEECS Calendar` could be set to `No`;
- predicted coursework dates could be left blank;
- actual monitoring dates could be left blank.

This confirms that formal examinations can be represented consistently without requiring locally controlled coursework dates.

## 6. Date-field validation

The six assessment date fields are:

- `Predicted Release Date`
- `Predicted Submission Date`
- `Predicted Feedback Date`
- `Actual Release Date`
- `Actual Submission Date`
- `Actual Feedback Date`

All six date fields were confirmed as optional at List level.

This is necessary because formal examinations and centrally managed assessments may not have locally controlled release, submission or feedback dates.

For locally managed coursework, predicted dates should normally be completed. Conditional enforcement of this rule will be handled later through Power Apps, Power Automate or the deterministic QA validation layer.

## 7. Feedback-monitoring readiness

The validation confirmed that actual monitoring dates can remain blank at the planning stage.

The following fields will be completed later during the academic year:

- `Actual Release Date`
- `Actual Submission Date`
- `Actual Feedback Date`

`Actual Feedback Date` will later be compared with:

1. the predicted feedback date;
2. the feedback due date calculated from the actual submission date.

The intended QA rule is:

- `Actual Submission Date + 20 working days = Feedback Due Date`

The feedback status can then be classified as:

- `On time`
- `Late`
- `Missing`
- `Not yet due`

This logic has not yet been automated.

## 8. Weighting validation

The two assessment records linked to the test module plan were checked manually.

The combined assessment weighting was `100%`.

This confirms that the List structure supports module-level weighting validation.

Automatic validation of total weighting has not yet been implemented. This will be handled later by deterministic validation code, Power Automate or the agentic QA layer.

## 9. Calendar inclusion validation

The validation confirmed that local coursework and formal examinations can be separated for calendar purposes.

The intended rule is:

- locally managed coursework or tests: `Include in EEECS Calendar = Yes`;
- formal examinations or centrally managed exams: `Include in EEECS Calendar = No`.

This distinction allows the full assessment structure to be retained for weighting validation while excluding centrally managed examination dates from the local EEECS coursework calendar.

## 10. Data protection

The public GitHub repository must not include:

- real staff names;
- staff email addresses;
- identifiable module records;
- exported Microsoft Lists data containing operational details;
- screenshots showing personal or institutional information;
- private Microsoft Lists or SharePoint links.

This validation document records only the structure, test outcomes and anonymised findings.

Operational records remain within the institutional Microsoft 365 environment.

## 11. Current limitations

The current validation identified the following limitations:

1. Total assessment weighting is checked manually.
2. Assessment count is checked manually against the declared number in `MAP_Module_Plans`.
3. Date-order validation has not yet been automated.
4. Conditional date requirements for coursework are not yet enforced.
5. Formal-examination date fields are not yet automatically hidden.
6. Feedback due dates are not yet calculated.
7. Feedback timeliness status is not yet derived.
8. Export compatibility with the target Assessment Pivot workbook has not yet been tested.

## 12. Next steps

1. Add a small number of additional representative assessment records.
2. Export `MAP_Assessments` to Excel.
3. Compare the exported structure with the target Assessment Pivot workbook.
4. Define deterministic validation rules for assessment count, weighting and date order.
5. Define feedback-monitoring logic using actual submission and feedback dates.
6. Design the future Power Apps form for conditional field display and validation.
7. Prepare the assessment data structure for deterministic and agent-based deconfliction.