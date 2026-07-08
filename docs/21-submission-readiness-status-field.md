# Submission Readiness Status Field

**Project:** Agentic MAP-QA  
**Related issue:** #40  
**Document version:** 0.1  
**Status:** Design rule defined  

## 1. Purpose

This document defines a module-plan-level `Submission Readiness Status` field for MAP-QA.

The purpose of this field is to provide a clear summary of whether a module plan is ready to submit, blocked, or requires QA review.

The field should help both module owners and QA reviewers understand the current validation state of a module plan without needing to manually inspect every linked assessment record.

## 2. Rationale

The MAP-QA workflow now includes several validation checks:

- assessment-weight validation;
- predicted-date validation;
- calendar-inclusion validation;
- formal examination handling;
- automatic Plan Reference generation;
- module owner declaration;
- linked assessment-record completeness.

These checks are distributed across module-plan-level and assessment-level data.

A single module-plan-level readiness status helps summarise the combined result.

## 3. Recommended field name

The recommended field name is:

`Submission Readiness Status`

This field should be stored in the module plan List.

Recommended List:

`MAP_Module_Plans_Pilot_2026_27`

In the final workflow, the equivalent production module plan List should contain the same field.

## 4. Recommended field type

Recommended type:

| Setting | Recommended value |
|---|---|
| Column type | Choice |
| Required | No during early pilot; Yes in final workflow if automated |
| Allow multiple selections | No |
| Default value | Not checked |
| Editable by module owners | No, preferably hidden or read-only |
| Updated by | Power Apps or Power Automate |

The field should not normally be manually edited by module owners.

It should be updated by validation logic when the module owner checks or submits the module plan.

## 5. Recommended status values

The recommended status values are:

| Status value | Meaning |
|---|---|
| Not checked | Validation has not yet been run |
| Ready to submit | All blocking checks have passed |
| Blocked - missing module-plan fields | Required module-plan fields are missing |
| Blocked - missing assessment records | No linked assessment records exist |
| Blocked - incomplete assessment records | One or more assessment records has missing required fields |
| Blocked - invalid assessment weighting | Assessment weights do not meet the required rule |
| Blocked - missing predicted dates | Non-exam assessment predicted dates are incomplete |
| Blocked - formal exam inconsistency | Formal examination records are internally inconsistent |
| Blocked - calendar inconsistency | Calendar inclusion logic is incorrect |
| Blocked - declaration missing | Module owner declaration has not been completed |
| Warning - QA review recommended | No blocking issue, but QA should review a warning |
| Submitted - validation passed | Module plan has been submitted after passing validation |

These values should be reviewed during implementation to avoid unnecessary duplication with the existing `Submission Status` field.

## 6. Relationship with Submission Status

`Submission Readiness Status` and `Submission Status` should serve different purposes.

| Field | Purpose |
|---|---|
| Submission Status | Tracks workflow stage, such as Draft, Submitted, Returned for revision, Resubmitted or Approved |
| Submission Readiness Status | Tracks whether validation checks pass, fail or require review |

Example:

| Submission Status | Submission Readiness Status | Meaning |
|---|---|---|
| Draft | Not checked | Plan is being prepared and validation has not been run |
| Draft | Blocked - invalid assessment weighting | Plan cannot yet be submitted |
| Draft | Ready to submit | Plan is complete and can be submitted |
| Submitted | Submitted - validation passed | Plan has passed validation and was submitted |
| Returned for revision | Blocked - missing predicted dates | QA has returned the plan and validation issue remains |
| Approved | Submitted - validation passed | Plan passed validation and was approved after QA review |

The readiness field should support the workflow status, not replace it.

## 7. Blocking statuses

The following statuses indicate that the module plan should not be submitted:

| Status | Blocking reason |
|---|---|
| Blocked - missing module-plan fields | Required module-plan information is incomplete |
| Blocked - missing assessment records | No linked assessments exist |
| Blocked - incomplete assessment records | One or more assessment records is incomplete |
| Blocked - invalid assessment weighting | Summative assessment weights do not meet the required rule |
| Blocked - missing predicted dates | Non-exam predicted dates are missing |
| Blocked - formal exam inconsistency | Formal examination logic is inconsistent |
| Blocked - calendar inconsistency | Calendar inclusion logic is incorrect |
| Blocked - declaration missing | Owner declaration has not been completed |

If any blocking status is present, the module plan should remain in `Draft`.

## 8. Warning statuses

The following status should indicate that submission may be possible but QA review is recommended:

| Status | Meaning |
|---|---|
| Warning - QA review recommended | A non-blocking issue exists and should be reviewed |

Examples of warning-only conditions may include:

- 0-CATS module with valid 0% assessment weight;
- moderator discussion still pending;
- confirmed moderator not yet assigned;
- non-exam assessment excluded from the local calendar by exception;
- unusually high number of summative assessments with incomplete justification.

The final implementation should decide which warnings remain warning-only and which should become blocking conditions.

## 9. Ready and submitted statuses

The readiness field should clearly show when a module plan is ready to submit.

| Status | Meaning |
|---|---|
| Ready to submit | All blocking checks have passed, but the plan has not yet been submitted |
| Submitted - validation passed | The plan passed validation and the Submit action was completed |

The `Ready to submit` status is useful before the user clicks Submit.

The `Submitted - validation passed` status is useful after successful submission.

## 10. Relationship with linked assessment records

The readiness status depends on linked assessment records.

The system should validate only assessment records linked to the current module plan.

The readiness field should summarise results from checks such as:

| Assessment-level check | Possible readiness status |
|---|---|
| No assessment records linked | Blocked - missing assessment records |
| Missing assessment title, type, number or weight | Blocked - incomplete assessment records |
| Assessment weights total below or above 100 | Blocked - invalid assessment weighting |
| Non-exam predicted dates missing | Blocked - missing predicted dates |
| Formal exam included in calendar | Blocked - calendar inconsistency |
| Formal exam fields inconsistent | Blocked - formal exam inconsistency |

The readiness status therefore acts as a module-plan-level summary of linked assessment-record validation.

## 11. Relationship with assessment-weight validation

Assessment-weight validation should update the readiness status when the total summative weight is invalid.

Recommended logic:

| Condition | Readiness result |
|---|---|
| CATS > 0 and total summative weight = 100 | Pass |
| CATS > 0 and total summative weight is not 100 | Blocked - invalid assessment weighting |
| CATS = 0 and total summative weight = 0 | Warning - QA review recommended or Ready to submit as exception |
| CATS = 0 and total summative weight is not 0 | Warning - QA review recommended or Blocked - invalid assessment weighting |

The final policy should decide whether 0-CATS exceptions are warning-only or require explicit QA approval.

## 12. Relationship with predicted-date validation

Predicted-date validation should update the readiness status when non-exam assessment dates are incomplete.

Recommended logic:

| Condition | Readiness result |
|---|---|
| All non-exam assessments have predicted dates | Pass |
| One or more non-exam assessments has missing predicted dates | Blocked - missing predicted dates |
| Formal examination has blank predicted dates | Pass |

Formal examinations should not cause a missing predicted-date block.

## 13. Relationship with formal examination handling

Formal examination checks should update the readiness status when records are inconsistent.

Recommended logic:

| Condition | Readiness result |
|---|---|
| Formal examination fields are consistent | Pass |
| Assessment Type = Formal Examination but Is Formal Examination = No | Blocked - formal exam inconsistency |
| Is Formal Examination = Yes but Assessment Type is not Formal Examination | Blocked - formal exam inconsistency |
| Formal examination is not summative | Blocked - formal exam inconsistency |
| Formal examination Assessment Period is not Not applicable | Blocked - formal exam inconsistency |

Formal examinations should also be included in assessment-weight validation.

## 14. Relationship with calendar-inclusion validation

Calendar-inclusion checks should update the readiness status when assessment records are incorrectly included or excluded from the local calendar.

Recommended logic:

| Condition | Readiness result |
|---|---|
| Formal examination excluded from EEECS calendar | Pass |
| Formal examination included in EEECS calendar | Blocked - calendar inconsistency |
| Non-exam assessment included in EEECS calendar | Pass |
| Non-exam assessment excluded from EEECS calendar | Warning - QA review recommended or Blocked - calendar inconsistency |

The final policy should decide whether non-exam exclusion is always blocking or can be allowed as a QA-reviewed exception.

## 15. Relationship with module owner declaration

The module owner declaration should be completed before submission.

Recommended logic:

| Condition | Readiness result |
|---|---|
| Owner Declaration = Yes | Pass |
| Owner Declaration = No | Blocked - declaration missing |

The readiness status should make it clear when the only remaining issue is the missing declaration.

## 16. Priority order for status selection

A single status field can only show one value at a time.

If several validation problems exist, the system should use a priority order.

Recommended priority:

| Priority | Status |
|---:|---|
| 1 | Blocked - missing module-plan fields |
| 2 | Blocked - missing assessment records |
| 3 | Blocked - incomplete assessment records |
| 4 | Blocked - formal exam inconsistency |
| 5 | Blocked - calendar inconsistency |
| 6 | Blocked - missing predicted dates |
| 7 | Blocked - invalid assessment weighting |
| 8 | Blocked - declaration missing |
| 9 | Warning - QA review recommended |
| 10 | Ready to submit |
| 11 | Submitted - validation passed |

This means the system should display the most fundamental blocking issue first.

A separate notes or error-summary field may be needed to show all detected issues.

## 17. Recommended supporting field

A single status field is useful, but it may not provide enough detail when multiple issues exist.

A supporting field is recommended.

Suggested field name:

`Submission Readiness Notes`

Recommended type:

| Setting | Recommended value |
|---|---|
| Column type | Multiple lines of text |
| Required | No |
| Edited by module owners | No |
| Updated by | Power Apps or Power Automate |

Example notes:

| Readiness status | Example note |
|---|---|
| Blocked - missing predicted dates | Assessment 2 is missing predicted feedback date |
| Blocked - invalid assessment weighting | Total summative weight is 80%, expected 100% |
| Blocked - calendar inconsistency | Formal exam is currently included in EEECS calendar |
| Warning - QA review recommended | Module is 0 CATS and has 0% assessment weight |

This supporting field would help module owners correct problems more efficiently.

## 18. Recommended Power Apps behaviour

Power Apps should update the `Submission Readiness Status` when the user clicks:

- Check readiness;
- Save draft;
- Submit.

Recommended behaviour:

| User action | System behaviour |
|---|---|
| User saves draft | Optionally update readiness status |
| User clicks Check readiness | Run checks and update readiness status |
| User clicks Submit | Run checks and block or submit |
| Checks fail | Set relevant blocked status |
| Checks pass with warning | Set warning status and show message |
| Checks pass | Set Ready to submit or Submitted - validation passed |

The status should always reflect the latest validation result.

## 19. Recommended Power Automate behaviour

Power Automate could also update the readiness status in the background.

Possible triggers:

| Trigger | Purpose |
|---|---|
| Module plan created or modified | Recalculate readiness after plan changes |
| Assessment record created or modified | Recalculate readiness for linked module plan |
| Assessment record deleted | Recalculate readiness for linked module plan |
| Submission Status changed | Confirm readiness status is aligned |

Power Automate may be useful for keeping dashboards up to date.

However, the user-facing submission gate should preferably run in Power Apps so that the module owner receives immediate feedback.

## 20. Dashboard use

The `Submission Readiness Status` field would support QA review dashboards.

Example dashboard groupings:

| Dashboard group | Purpose |
|---|---|
| Ready to submit | Plans ready for module-owner submission |
| Submitted - validation passed | Plans awaiting QA review |
| Blocked statuses | Plans needing correction |
| Warning - QA review recommended | Plans requiring QA attention |
| Not checked | Plans not yet validated |

This would help QA reviewers identify where action is needed.

## 21. Suggested views

Suggested Microsoft Lists views:

| View name | Purpose |
|---|---|
| Submission readiness overview | Shows all module plans grouped by readiness status |
| Blocked module plans | Shows only plans with blocked statuses |
| Ready to submit | Shows plans ready for submission |
| Warning / QA review | Shows plans with warning status |
| Submitted for QA | Shows plans submitted after validation |

These views would support operational monitoring without exposing unnecessary detail.

## 22. Data protection

This document contains only structural design rules and anonymised pilot examples.

It does not include:

- operational module data;
- staff names;
- student data;
- email addresses;
- screenshots;
- private SharePoint links;
- identifiable assessment records.

## 23. Acceptance criteria

This document satisfies Issue #40 by defining that:

- the purpose of `Submission Readiness Status` is documented;
- recommended status values are defined;
- blocking and warning statuses are separated;
- the relationship with linked assessment records is explained;
- the relationship with assessment-weight validation is explained;
- the relationship with predicted-date validation is explained;
- the relationship with formal examination handling is explained;
- the relationship with calendar-inclusion validation is explained;
- the relationship with module owner declaration is explained;
- Power Apps and Power Automate update options are documented;
- dashboard use is explained;
- no operational or identifiable data is committed.

## 24. Next steps

1. Decide whether to add `Submission Readiness Status` to the pilot module plan List.
2. Decide whether to add `Submission Readiness Notes`.
3. Define whether readiness should update on Save, Check readiness, Submit or all three.
4. Test status updates using representative pilot records.
5. Add the status field to future QA dashboard views.