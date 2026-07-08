# Module-Plan Submission Readiness Gate

**Project:** Agentic MAP-QA  
**Related issue:** #36  
**Document version:** 0.1  
**Status:** Design rule defined  

## 1. Purpose

This document defines the overall submission-readiness gate for MAP-QA.

The submission-readiness gate determines whether a module plan can move from:

`Draft`

to:

`Submitted`

The purpose is to ensure that module assessment plans are sufficiently complete, internally consistent and ready for QA review before they are formally submitted.

## 2. Rationale

The pilot has defined several separate validation rules:

- predicted-date checking;
- calendar-inclusion checking;
- assessment-weight validation;
- automatic Plan Reference generation;
- formal examination handling;
- module owner declaration.

These rules need to be combined into one clear submission-readiness check.

The submission gate should prevent incomplete or inconsistent module plans from reaching QA review.

## 3. Core submission rule

A module plan should only be allowed to move to `Submitted` when all required submission checks have passed.

The core rule is:

| Requirement | Required before submission? |
|---|---:|
| Plan Reference exists and is valid | Yes |
| Module plan has linked assessment records | Yes |
| Assessment weights are valid | Yes |
| Non-exam assessments have predicted dates | Yes |
| Formal examinations are handled consistently | Yes |
| Calendar inclusion is correct | Yes |
| Module owner declaration is completed | Yes |
| Required module-plan fields are completed | Yes |

If any blocking condition fails, the module plan should remain in `Draft` or be moved to `Returned for revision`.

## 4. Required module-plan checks

Before submission, the module plan should contain all required module-plan-level information.

Required checks:

| Check | Blocking? |
|---|---:|
| Academic Year is completed | Yes |
| Module is selected | Yes |
| Plan Reference is present | Yes |
| Plan Reference is unique | Yes |
| Confirmed Module Owners are completed | Yes |
| Coordinating Module Owner is completed | Yes |
| Number of Summative Assessments is completed | Yes |
| Student Support and Office Hours is completed | Yes |
| Owner Declaration is completed | Yes |

The module plan should not be submitted if any of these required fields are missing.

## 5. Plan Reference readiness

The Plan Reference should be automatically generated and should match the selected academic year and module code.

Required logic:

| Condition | Submission result |
|---|---|
| Plan Reference is present | Pass |
| Plan Reference is missing | Block |
| Plan Reference does not match Academic Year and Module Code | Block |
| Duplicate Plan Reference exists | Block |

Example valid Plan Reference:

`2026-27_PILOT101`

This supports reliable lookup relationships between the Module Plans List and the Assessments List.

## 6. Assessment-record readiness

Each module plan should have at least one linked assessment record before submission.

Required logic:

| Condition | Submission result |
|---|---|
| At least one linked assessment record exists | Pass |
| No linked assessment records exist | Block |
| Assessment Number is missing | Block |
| Assessment Title is missing | Block |
| Assessment Type is missing | Block |
| Assessment Weight is missing | Block |
| Assessment Period is missing | Block |

The system should check the assessment records linked to the specific module plan being submitted.

## 7. Assessment-weight readiness

Assessment weights should normally total 100% for credit-bearing modules.

Required logic:

| Condition | Submission result |
|---|---|
| CATS > 0 and total summative weight = 100 | Pass |
| CATS > 0 and total summative weight is less than 100 | Block |
| CATS > 0 and total summative weight is greater than 100 | Block |
| CATS = 0 and total summative weight = 0 | Pass as exception |
| CATS = 0 and total summative weight is not 0 | Warning or QA review |
| Missing assessment weight | Block |
| No summative assessment records | Block unless approved exception |

Formal examinations must be included in the total summative assessment weight.

## 8. Predicted-date readiness

Non-exam assessments should have predicted release, submission and feedback dates before submission.

Required logic:

| Assessment case | Required result |
|---|---|
| Non-exam assessment with all predicted dates | Pass |
| Non-exam assessment with missing predicted release date | Block |
| Non-exam assessment with missing predicted submission date | Block |
| Non-exam assessment with missing predicted feedback date | Block |
| Formal examination with blank predicted dates | Pass |
| Formal examination with completed predicted dates | Pass, but dates are not required |

Expected status values:

| Predicted Date Status | Meaning | Submission result |
|---|---|---|
| Complete | Non-exam predicted dates are complete | Pass |
| Not required | Formal examination dates are not required | Pass |
| Missing predicted dates | One or more required dates are missing | Block |

## 9. Calendar-inclusion readiness

Formal examinations should be excluded from the local EEECS coursework calendar.

Non-exam assessments should normally be included in the local EEECS coursework calendar.

Required logic:

| Calendar Inclusion Status | Meaning | Submission result |
|---|---|---|
| Correct - exam excluded | Formal examination correctly excluded | Pass |
| Correct - included | Non-exam assessment correctly included | Pass |
| Check - formal exam included in calendar | Formal examination incorrectly included | Block |
| Check - non-exam excluded from calendar | Non-exam assessment excluded | Warning or block depending on QA policy |

The final workflow should normally block formal examinations that are incorrectly included in the EEECS coursework calendar.

## 10. Formal examination readiness

Formal examination records should be internally consistent.

Required logic:

| Condition | Submission result |
|---|---|
| Assessment Type = Formal Examination | Must align with formal-exam fields |
| Is Summative = Yes | Required |
| Is Formal Examination = Yes | Required |
| Include in EEECS Calendar = No | Required |
| Assessment Period = Not applicable | Required |
| Predicted dates are blank or ignored | Allowed |
| Formal exam weight included in total weighting | Required |

Inconsistent formal examination records should block submission.

Examples of blocking inconsistencies:

| Inconsistency | Submission result |
|---|---|
| Formal Examination type but Is Formal Examination = No | Block |
| Is Formal Examination = Yes but Assessment Type is not Formal Examination | Block |
| Formal examination included in EEECS calendar | Block |
| Formal examination not marked as summative | Block |
| Formal examination excluded from total assessment weighting | Block |

## 11. Module owner declaration

The module owner declaration should be completed before submission.

Required logic:

| Condition | Submission result |
|---|---|
| Owner Declaration = Yes | Pass |
| Owner Declaration = No | Block |

The declaration confirms that the module owner has reviewed the plan and is ready to submit it for QA review.

## 12. Warning-only conditions

Some conditions may not need to block submission but should be visible to QA reviewers.

Possible warning-only conditions:

| Condition | Recommended status |
|---|---|
| Confirmed Moderator is blank | Warning, depending on QA policy |
| Moderator Discussion Status = Discussion pending | Warning |
| Assessment Count Justification is blank when assessment count is high | Warning or block depending on policy |
| CATS = 0 and assessment weight = 0 | Exception warning |
| Non-exam assessment excluded from calendar | Warning or block depending on policy |

These warnings should be clearly visible in the submission-readiness status.

## 13. Blocking conditions

The following should normally block submission:

| Blocking condition |
|---|
| Missing or duplicate Plan Reference |
| Missing module selection |
| Missing coordinating module owner |
| Missing confirmed module owner |
| Missing linked assessment records |
| Missing assessment type |
| Missing assessment weight |
| Invalid assessment-weight total |
| Missing predicted dates for non-exam assessments |
| Formal examination incorrectly included in EEECS calendar |
| Formal examination fields are inconsistent |
| Owner Declaration is not completed |

Blocking conditions should keep the module plan in `Draft`.

## 14. Suggested submission-readiness statuses

The final workflow could use a combined status field.

Suggested field name:

`Submission Readiness Status`

Suggested values:

| Status | Meaning |
|---|---|
| Ready to submit | All required checks have passed |
| Blocked - missing module-plan fields | Required module-plan fields are missing |
| Blocked - missing assessment records | No linked assessment records exist |
| Blocked - invalid assessment weighting | Total summative assessment weight is invalid |
| Blocked - missing predicted dates | Non-exam assessment dates are incomplete |
| Blocked - formal exam inconsistency | Formal examination logic is inconsistent |
| Blocked - calendar inconsistency | Calendar inclusion logic is incorrect |
| Warning - QA review recommended | Non-blocking issue should be reviewed |
| Submitted | Module plan has been submitted for QA review |

## 15. Suggested user-facing messages

If assessment weighting is invalid:

> The total summative assessment weight for this module is not valid. Please ensure that the total is 100% before submitting the module plan.

If assessment records are missing:

> No assessment records are linked to this module plan. Please add the assessment components before submitting.

If non-exam predicted dates are missing:

> Predicted release, submission and feedback dates are required for all non-exam assessments before submission.

If a formal examination is incorrectly included in the calendar:

> Formal examinations should not be included in the EEECS coursework calendar. Please set Include in EEECS Calendar to No.

If the module owner declaration is missing:

> Please confirm the module owner declaration before submitting this module plan for QA review.

If all checks pass:

> This module plan is ready to submit for QA review.

## 16. Recommended implementation approach

The recommended final approach is to implement the submission-readiness gate through Power Apps.

Power Apps should run the readiness checks when the module owner clicks Submit.

Recommended behaviour:

1. User completes module plan.
2. User adds linked assessment records.
3. User clicks Submit.
4. Power Apps runs all required checks.
5. If all blocking checks pass, the plan moves to Submitted.
6. If any blocking check fails, the plan remains in Draft.
7. The user sees clear messages explaining what must be corrected.

Power Automate may be used for background checks, status updates or QA notifications, but the user-facing submission gate should preferably be handled in Power Apps.

## 17. Relationship to previous design documents

This submission-readiness gate brings together the rules defined in earlier design documents.

| Design area | Relationship to submission gate |
|---|---|
| Assessment-weight validation | Blocks submission if total weighting is invalid |
| Automatic Plan Reference generation | Ensures module plan has a stable unique identifier |
| Formal examination handling | Ensures formal exams are treated consistently |
| Predicted-date checking | Ensures coursework dates are complete |
| Calendar-inclusion checking | Ensures formal exams are excluded from local coursework calendar |
| Module owner declaration | Confirms readiness for QA review |

The submission-readiness gate is therefore the combined decision layer above the individual checks.

## 18. Data protection

This document contains only structural design rules and anonymised pilot examples.

It does not include:

- operational module data;
- staff names;
- student data;
- email addresses;
- screenshots;
- private SharePoint links;
- identifiable assessment records.

## 19. Acceptance criteria

This document satisfies Issue #36 by defining that:

- submission-readiness requirements are documented;
- the Draft-to-Submitted transition logic is defined;
- assessment-weight validation is included;
- predicted-date validation is included;
- formal examination handling is included;
- calendar-inclusion checking is included;
- module owner declaration is included;
- blocking and warning conditions are listed;
- suggested user-facing messages are provided;
- Power Apps is recommended for the final user-facing submission gate;
- no operational or identifiable data is committed.

## 20. Next steps

1. Decide which warning-only conditions should become blocking conditions.
2. Define the exact Power Apps submission button logic.
3. Define whether a module-plan-level `Submission Readiness Status` field should be added.
4. Test the submission gate using representative pilot records.
5. Add the submission-readiness rule to the final MAP-QA workflow.