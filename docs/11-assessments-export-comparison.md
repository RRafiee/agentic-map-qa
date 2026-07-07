# MAP Assessments Export Comparison

**Project:** Agentic MAP-QA  
**Related issue:** #19  
**Document version:** 0.1  
**Status:** Initial export comparison completed  

## 1. Purpose

This document records the initial comparison between the exported `MAP_Assessments` Microsoft List and the target Assessment Pivot structure.

The purpose of this comparison is to check whether assessment-level data collected through Microsoft Lists can support the final MAP output required for assessment planning, calendar preparation and QA monitoring.

The comparison identifies fields that are already present, fields that need to be derived, and fields that may need to be added or transformed before creating a clean pilot version.

## 2. Export source

The comparison used a private CSV export from the `MAP_Assessments` Microsoft List.

The export file is not included in the public GitHub repository because it may contain operational module information.

The public repository records only the structural comparison and anonymised findings.

## 3. Validation context

The exported List contained assessment records linked to one annual module plan.

The test confirmed that:

- multiple assessment records can be linked to one module plan;
- one assessment component is represented by one row;
- assessment weights can be checked against the expected module total;
- predicted and actual date fields are exported as structured fields;
- formal examinations can be represented without coursework dates;
- actual feedback monitoring fields are available for later semester tracking.

## 4. Overall comparison result

The exported `MAP_Assessments` structure is broadly compatible with the target Assessment Pivot model.

The most important design principle is working correctly:

- one assessment component is stored as one row.

However, the exported Microsoft Lists data is not yet a final Assessment Pivot output. Some target fields will need to be derived by joining `MAP_Assessments` with `MAP_Module_Plans` and `MAP_Module_Catalogue`, or generated during an export and transformation step.

## 5. Field mapping

| Target Assessment Pivot field | Current source field or derivation | Status |
|---|---|---|
| Module Code | Derived from `Module Plan` or joined from `MAP_Module_Plans` / `MAP_Module_Catalogue` | Needs export transformation |
| Module Title | Joined from `MAP_Module_Catalogue` through the module plan | Needs export transformation |
| Module Owner | Joined from `MAP_Module_Plans` using `Confirmed Module Owners` | Needs export transformation |
| Academic Year Code | Derived from `Academic Year` or `Plan Reference` | Needs export transformation |
| Assignment Code | Generated from module code, academic year and assessment number | Not yet generated |
| Assessment Number | `Assessment Number` | Present |
| Assessment Title | `Assessment Title` | Present |
| Assessment Type | `Assessment Type` | Present |
| Assessment Weight | `Assessment Weight` | Present |
| Predicted Release Date | `Predicted Release Date` | Present |
| Predicted Submission Date | `Predicted Submission Date` | Present |
| Predicted Feedback Date | `Predicted Feedback Date` | Present |
| Actual Release Date | `Actual Release Date` | Present |
| Actual Submission Date | `Actual Submission Date` | Present |
| Actual Feedback Date | `Actual Feedback Date` | Present |
| Notes | `Feedback Monitoring Notes` | Present but monitoring-specific |
| Calendar Inclusion | `Include in EEECS Calendar` | Present as operational field |
| Formal Examination Flag | `Is Formal Examination` | Present as operational field |
| Summative Flag | `Is Summative` | Present as operational field |

## 6. Fields already working well

The following fields are already suitable for the assessment-level structure:

- `Module Plan`
- `Assessment Number`
- `Assessment Title`
- `Assessment Type`
- `Assessment Weight`
- `Assessment Mode`
- `Is Summative`
- `Is Formal Examination`
- `Include in EEECS Calendar`
- `Predicted Release Date`
- `Predicted Submission Date`
- `Predicted Feedback Date`
- `Actual Release Date`
- `Actual Submission Date`
- `Actual Feedback Date`
- `Feedback Monitoring Notes`

These fields support both assessment planning and later QA monitoring.

## 7. Formal examination handling

The comparison confirmed that formal examinations should be retained as assessment records.

The correct representation is:

| Field | Expected value |
|---|---|
| Assessment Type | `Formal Examination` |
| Is Summative | `Yes` |
| Is Formal Examination | `Yes` |
| Include in EEECS Calendar | `No` |
| Predicted dates | Blank |
| Actual dates | Blank |

This allows formal examinations to contribute to the total module weighting while excluding them from the local EEECS coursework calendar.

A key correction was made during testing: a formal examination should remain summative. It should not be excluded from the summative assessment structure simply because it is excluded from the coursework calendar.

## 8. Date-field handling

The six date fields are:

- `Predicted Release Date`
- `Predicted Submission Date`
- `Predicted Feedback Date`
- `Actual Release Date`
- `Actual Submission Date`
- `Actual Feedback Date`

All six date fields must remain optional at Microsoft List level.

This is required because formal examinations and centrally managed assessments may not have locally controlled coursework release, submission or feedback dates.

For coursework and locally managed assessments, predicted dates should normally be completed. This conditional requirement should be enforced later through Power Apps, Power Automate or deterministic validation code.

## 9. Feedback monitoring readiness

The export includes `Actual Feedback Date`, which is essential for later QA monitoring.

The intended feedback-monitoring logic is:

- use `Actual Submission Date` as the reference deadline;
- calculate the feedback due date using 20 working days;
- compare `Actual Feedback Date` with the calculated due date;
- compare `Actual Feedback Date` with `Predicted Feedback Date`.

The feedback status can later be classified as:

- `On time`
- `Late`
- `Missing`
- `Not yet due`

This logic is not yet implemented in Microsoft Lists.

## 10. Fields requiring derivation or transformation

The direct CSV export does not yet provide all fields required by the target Assessment Pivot workbook.

The following fields should be produced through an export or transformation layer:

| Required output field | Proposed derivation |
|---|---|
| Module Code | Extract from `Plan Reference` or join from catalogue |
| Module Title | Join from `MAP_Module_Catalogue` |
| Module Owner | Join from `MAP_Module_Plans` |
| Academic Year Code | Derive from `Academic Year` or `Plan Reference` |
| Assignment Code | Generate from module code, academic year and assessment number |
| Planning Notes | Add as a separate field if needed |
| Feedback Status | Derive from actual submission and feedback dates |
| Feedback Due Date | Calculate from actual submission date plus 20 working days |

The preferred approach is to keep the Microsoft Lists structure relational and produce the final Assessment Pivot format through a controlled export or transformation process.

## 11. Recommended changes before the clean pilot version

Before creating the clean pilot version, the following actions are recommended:

1. Keep all six date fields optional at Microsoft List level.
2. Ensure formal examinations are recorded as summative assessments.
3. Keep formal examinations excluded from the EEECS coursework calendar.
4. Retain `Actual Feedback Date` for later feedback-timeliness monitoring.
5. Decide whether a separate `Planning Notes` field is needed in addition to `Feedback Monitoring Notes`.
6. Define how `Assignment Code` will be generated.
7. Define the export-layer mapping from relational Lists to the target Assessment Pivot structure.
8. Avoid adding too many duplicated lookup fields directly into `MAP_Assessments`.
9. Use transformation logic to join module, plan and assessment data cleanly.
10. Test the export again after adding more representative assessment records.

## 12. Data protection

The public GitHub repository must not include:

- exported Microsoft Lists files containing operational data;
- staff names;
- staff email addresses;
- identifiable module records;
- private SharePoint or Microsoft Lists links;
- screenshots containing personal or institutional information.

Only anonymised comparison findings and structural design decisions are documented in the repository.

## 13. Current limitations

The current comparison identified the following limitations:

1. The direct export does not yet include all target Assessment Pivot fields.
2. Module code, title and owner require joins or derivation.
3. Assignment codes are not yet generated.
4. Feedback due dates are not yet calculated.
5. Feedback timeliness status is not yet derived.
6. Working-day calculations are not yet implemented.
7. Export compatibility has been tested only on a small number of records.
8. The clean pilot version has not yet been created in the final intended location.

## 14. Conclusion

The `MAP_Assessments` export is structurally suitable as the foundation for the target Assessment Pivot output.

The core design is correct because each assessment is represented by one structured row, predicted and actual date fields are available, and formal examinations can be handled consistently.

The next major requirement is an export or transformation layer that combines data from:

- `MAP_Module_Catalogue`
- `MAP_Module_Plans`
- `MAP_Assessments`

This layer will generate the final Assessment Pivot-compatible output.

## 15. Next steps

1. Add more representative assessment records.
2. Define the export-layer field mapping formally.
3. Create a clean pilot version of the Lists in the appropriate SharePoint location.
4. Test the clean pilot with a small number of trusted users.
5. Design deterministic validation rules for weighting, assessment count and date order.
6. Design feedback-monitoring calculations using 20 working days.
7. Prepare the data structure for later deterministic and agent-based deconfliction.
