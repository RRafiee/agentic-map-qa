# Power Apps Submit Button Logic

**Project:** Agentic MAP-QA  
**Related issue:** #38  
**Document version:** 0.1  
**Status:** Design logic defined  

## 1. Purpose

This document defines the logic that should run when a module owner clicks the Submit button in the final MAP-QA Power Apps workflow.

The purpose of the Submit button is not only to change the module plan status from `Draft` to `Submitted`, but also to check that the module plan and its linked assessment records are complete, internally consistent and ready for QA review.

## 2. Relationship to the submission-readiness gate

This document translates the module-plan submission-readiness gate into practical Power Apps button behaviour.

The submission-readiness gate defines what must be true before a module plan can be submitted.

The Submit button logic defines how those checks should be executed in the staff-facing form.

The Submit button should only update `Submission Status` to `Submitted` when all blocking checks have passed.

## 3. Core button behaviour

When the user clicks Submit, the system should:

1. Save the latest form data.
2. Identify the current module plan.
3. Load all assessment records linked to that module plan.
4. Run module-plan-level checks.
5. Run assessment-record-level checks.
6. Run assessment-weight validation.
7. Run predicted-date validation.
8. Run formal-examination consistency validation.
9. Run calendar-inclusion validation.
10. Run module-owner declaration validation.
11. If any blocking check fails, keep the module plan in `Draft`.
12. If all blocking checks pass, update the module plan to `Submitted`.
13. Show a clear success or error message to the user.

## 4. Required data sources

The Submit button logic will need to read from the following Lists:

| List | Purpose |
|---|---|
| `MAP_Module_Catalogue_Pilot_2026_27` | Stores module catalogue and CATS values |
| `MAP_Module_Plans_Pilot_2026_27` | Stores annual module plan records |
| `MAP_Assessments_Pilot_2026_27` | Stores assessment component records |

In the final workflow, equivalent production Lists should be used.

## 5. Required current record

The Submit button should operate on the current module plan record only.

The current module plan should be identified using its item ID or equivalent stable internal identifier.

The logic should not rely only on display text, because display values can be edited or duplicated if not properly controlled.

## 6. Linked assessment loading

The Submit button should load all assessment records linked to the current module plan.

Required filter:

| Field | Required value |
|---|---|
| Assessment Module Plan lookup | Current module plan |

The logic should only validate assessment records belonging to the current module plan.

It should not calculate assessment-weight totals across the whole assessment List.

## 7. Execution order

The recommended execution order is:

| Step | Check type |
|---:|---|
| 1 | Confirm module-plan record exists |
| 2 | Save or validate current form input |
| 3 | Validate required module-plan fields |
| 4 | Validate Plan Reference |
| 5 | Load linked assessment records |
| 6 | Validate presence of assessment records |
| 7 | Validate required assessment fields |
| 8 | Validate formal examination consistency |
| 9 | Validate predicted dates |
| 10 | Validate calendar inclusion |
| 11 | Validate assessment-weight total |
| 12 | Validate module owner declaration |
| 13 | Update status to Submitted if all checks pass |
| 14 | Show success message |

This order helps the user see the most fundamental missing information first.

## 8. Module-plan-level checks

The Submit button should check that the following module-plan fields are complete.

| Field | Blocking if missing? |
|---|---:|
| Academic Year | Yes |
| Module | Yes |
| Plan Reference | Yes |
| Confirmed Module Owners | Yes |
| Coordinating Module Owner | Yes |
| Number of Summative Assessments | Yes |
| Student Support and Office Hours | Yes |
| Owner Declaration | Yes |

If any required field is missing, submission should be blocked.

Suggested message:

> Please complete all required module-plan fields before submitting this module plan for QA review.

## 9. Plan Reference checks

The Submit button should confirm that the Plan Reference is present, valid and unique.

Required checks:

| Check | Blocking? |
|---|---:|
| Plan Reference is present | Yes |
| Plan Reference matches Academic Year and Module Code | Yes |
| No duplicate Plan Reference exists | Yes |

Expected format:

`AcademicYear_ModuleCode`

Example:

`2026-27_PILOT101`

Suggested duplicate message:

> A module plan already exists for this module and academic year. Please check the existing plan instead of creating a duplicate.

Suggested mismatch message:

> The Plan Reference does not match the selected academic year and module. Please refresh or regenerate the Plan Reference before submitting.

## 10. Assessment-record presence check

A module plan should normally have at least one linked assessment record before submission.

Required logic:

| Condition | Result |
|---|---|
| One or more linked assessment records exist | Pass |
| No linked assessment records exist | Block |

Suggested message:

> No assessment records are linked to this module plan. Please add the assessment components before submitting.

## 11. Required assessment-field checks

For each linked assessment record, the Submit button should check that core assessment fields are complete.

Required fields:

| Field | Blocking if missing? |
|---|---:|
| Assessment Number | Yes |
| Assessment Title | Yes |
| Assessment Type | Yes |
| Assessment Weight | Yes |
| Assessment Mode | Yes |
| Is Summative | Yes |
| Is Formal Examination | Yes |
| Include in EEECS Calendar | Yes |
| Assessment Period | Yes |

Suggested message:

> One or more linked assessment records has missing required information. Please complete all assessment details before submitting.

## 12. Formal examination consistency checks

The Submit button should check whether any formal examination record is internally inconsistent.

Required formal examination values:

| Field | Required value |
|---|---|
| Assessment Type | Formal Examination |
| Is Summative | Yes |
| Is Formal Examination | Yes |
| Include in EEECS Calendar | No |
| Assessment Period | Not applicable |
| Predicted Release Date | Not required |
| Predicted Submission Date | Not required |
| Predicted Feedback Date | Not required |

Blocking inconsistencies:

| Inconsistency | Result |
|---|---|
| Assessment Type = Formal Examination but Is Formal Examination = No | Block |
| Is Formal Examination = Yes but Assessment Type is not Formal Examination | Block |
| Formal examination included in EEECS Calendar | Block |
| Formal examination not marked as summative | Block |
| Formal examination has Assessment Period other than Not applicable | Block |

Suggested message:

> One or more formal examination records is inconsistent. Formal examinations must be marked as summative, excluded from the EEECS coursework calendar and set to Assessment Period = Not applicable.

## 13. Predicted-date validation

The Submit button should require predicted dates for non-exam assessments.

Required logic:

| Assessment case | Submission result |
|---|---|
| Non-exam assessment with all predicted dates completed | Pass |
| Non-exam assessment missing predicted release date | Block |
| Non-exam assessment missing predicted submission date | Block |
| Non-exam assessment missing predicted feedback date | Block |
| Formal examination with blank predicted dates | Pass |
| Formal examination with completed predicted dates | Pass |

Suggested message:

> Predicted release, submission and feedback dates are required for all non-exam assessments before submission.

## 14. Calendar-inclusion validation

The Submit button should check that calendar inclusion is consistent.

Required logic:

| Assessment case | Expected calendar value | Submission result |
|---|---|---|
| Formal examination | Include in EEECS Calendar = No | Pass |
| Formal examination | Include in EEECS Calendar = Yes | Block |
| Non-exam assessment | Include in EEECS Calendar = Yes | Pass |
| Non-exam assessment | Include in EEECS Calendar = No | Warning or block depending on QA policy |

Recommended approach:

- block formal examinations that are incorrectly included in the EEECS coursework calendar;
- flag non-exam assessments that are excluded from the calendar;
- decide later whether non-exam exclusion should always block submission.

Suggested message for formal examination error:

> Formal examinations should not be included in the EEECS coursework calendar. Please set Include in EEECS Calendar to No.

Suggested message for non-exam warning:

> One or more non-exam assessments is excluded from the EEECS coursework calendar. Please check whether this is intentional.

## 15. Assessment-weight validation

The Submit button should calculate the total summative assessment weight for the current module plan.

Required logic:

1. Load linked assessment records for the current module plan.
2. Keep records where `Is Summative = Yes`.
3. Sum `Assessment Weight`.
4. Read the CATS value for the linked module.
5. Apply the weight-validation rule.

Validation outcomes:

| Condition | Submission result |
|---|---|
| CATS > 0 and total summative weight = 100 | Pass |
| CATS > 0 and total summative weight < 100 | Block |
| CATS > 0 and total summative weight > 100 | Block |
| CATS = 0 and total summative weight = 0 | Pass as exception |
| CATS = 0 and total summative weight is not 0 | Warning or QA review |
| Missing assessment weight | Block |
| No summative assessment records | Block unless approved exception |

Suggested message if total is not 100:

> The total summative assessment weight for this module is not valid. Please ensure that the total is 100% before submitting the module plan.

Suggested message for 0-CATS exception:

> This module is recorded as 0 CATS. A total assessment weight of 0% is allowed as an exceptional non-credit case.

## 16. Module owner declaration check

The Submit button should check that the module owner declaration has been completed.

Required logic:

| Condition | Submission result |
|---|---|
| Owner Declaration = Yes | Pass |
| Owner Declaration = No | Block |

Suggested message:

> Please confirm the module owner declaration before submitting this module plan for QA review.

## 17. Failure behaviour

If one or more blocking checks fail, the Submit button should:

1. Keep `Submission Status` as `Draft`.
2. Display a clear error message.
3. Highlight or list the failed checks.
4. Avoid creating duplicate module plan records.
5. Avoid partially submitting the module plan.
6. Allow the user to correct the issues and try again.

Recommended failure status:

`Blocked - action required`

The workflow should avoid silent failure. The user should always know why submission did not proceed.

## 18. Success behaviour

If all blocking checks pass, the Submit button should:

1. Save the module plan.
2. Update `Submission Status` to `Submitted`.
3. Record the submission timestamp if a field is available.
4. Record the submitting user if a field is available.
5. Show a success message.
6. Optionally notify the QA reviewer or coordinator.

Suggested success message:

> This module plan has been submitted for QA review.

## 19. Suggested combined readiness status

A future field could store the result of the latest submission-readiness check.

Suggested field name:

`Submission Readiness Status`

Suggested values:

| Status | Meaning |
|---|---|
| Ready to submit | All required checks have passed |
| Blocked - missing module-plan fields | Required module-plan fields are missing |
| Blocked - missing assessment records | No linked assessment records exist |
| Blocked - invalid assessment weighting | Assessment-weight total is invalid |
| Blocked - missing predicted dates | Non-exam predicted dates are incomplete |
| Blocked - formal exam inconsistency | Formal examination logic is inconsistent |
| Blocked - calendar inconsistency | Calendar inclusion is inconsistent |
| Warning - QA review recommended | Non-blocking warning exists |
| Submitted | Module plan has been submitted |

This field would support QA dashboards and troubleshooting.

## 20. Suggested Power Apps pseudo-logic

The final Power Apps formula should be implemented and tested in the actual app environment.

At design level, the Submit button should follow this structure:

1. Set a variable for the current module plan.
2. Load linked assessment records into a collection.
3. Calculate the total summative assessment weight.
4. Build a list of blocking errors.
5. Build a list of warnings.
6. If blocking errors exist, show the errors and do not submit.
7. If no blocking errors exist, patch the module plan status to `Submitted`.
8. Show a success notification.

Illustrative pseudo-logic:

`If blocking error count is greater than 0, show error message and keep Draft status. Otherwise, update Submission Status to Submitted.`

This document intentionally avoids committing production Power Apps formula code because the exact syntax will depend on the final control names, List names and data-source configuration.

## 21. Recommended error-display approach

The final form should display errors in a way that is useful to module owners.

Recommended approach:

| Error type | Display method |
|---|---|
| Single simple error | Notification banner |
| Multiple errors | Error summary panel |
| Assessment-specific error | Link or reference to assessment record |
| Warning | Warning panel or amber status |
| Successful submission | Success banner |

The error summary should use plain language and should avoid technical field names where possible.

## 22. Testing scenarios

The Submit button logic should be tested using representative records.

Recommended test cases:

| Test case | Expected result |
|---|---|
| Complete module plan with valid coursework assessments | Submit succeeds |
| Module plan with no assessment records | Submission blocked |
| Module plan with assessment weights totalling 80 | Submission blocked |
| Module plan with assessment weights totalling 120 | Submission blocked |
| Module plan with formal exam included in calendar | Submission blocked |
| Module plan with non-exam assessment missing predicted dates | Submission blocked |
| Module plan with valid formal exam and coursework | Submit succeeds |
| 0-CATS module with 0 assessment weight | Submit succeeds as exception |
| Missing Owner Declaration | Submission blocked |
| Duplicate Plan Reference | Submission blocked |

## 23. Data protection

This document contains only structural design rules and anonymised pilot examples.

It does not include:

- operational module data;
- staff names;
- student data;
- email addresses;
- screenshots;
- private SharePoint links;
- identifiable assessment records.

## 24. Acceptance criteria

This document satisfies Issue #38 by defining that:

- Submit button behaviour is documented;
- checks are listed in execution order;
- module-plan-level checks are defined;
- assessment-record-level checks are defined;
- assessment-weight validation is included;
- predicted-date validation is included;
- formal examination consistency checking is included;
- calendar-inclusion checking is included;
- owner declaration checking is included;
- failure and success behaviour are defined;
- suggested user-facing messages are provided;
- Power Apps is identified as the preferred implementation route;
- no operational or identifiable data is committed.

## 25. Next steps

1. Define the exact Power Apps control names and data-source names.
2. Prototype the Submit button using representative pilot records.
3. Decide whether warnings should block submission or remain QA-review flags.
4. Add a module-plan-level `Submission Readiness Status` field if required.
5. Test the logic with complete, incomplete and inconsistent module plans.
6. Confirm whether QA notifications should be triggered after successful submission.