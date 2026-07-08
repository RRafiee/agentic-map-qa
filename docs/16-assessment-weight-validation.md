# Assessment-Weight Validation Before Module Plan Submission

**Project:** Agentic MAP-QA  
**Related issue:** #29  
**Document version:** 0.1  
**Status:** Design rule defined  

## 1. Purpose

This document defines how MAP-QA should validate assessment weights before a module plan is submitted for QA review.

The purpose of this rule is to reduce assessment-planning errors by checking that summative assessment components normally total 100% of the module mark.

This document also records the current Microsoft Lists limitation and explains why final enforcement should be implemented through a submission gate rather than through a simple single-column validation rule.

## 2. Core validation rule

For each module plan, the total weighting of all summative assessment components should normally equal **100%**.

Before a module plan is submitted, the system should check all assessment records linked to that module plan and calculate the total assessment weight.

Example of a valid assessment structure:

| Assessment | Weight |
|---|---:|
| Coursework 1 | 30 |
| Coursework 2 | 20 |
| Formal Examination | 50 |
| **Total** | **100** |

This should be accepted because the summative assessment weights total 100%.

Example of an invalid assessment structure:

| Assessment | Weight |
|---|---:|
| Coursework 1 | 40 |
| Coursework 2 | 40 |
| **Total** | **80** |

This should not be accepted for submission because the total summative assessment weight is not 100%.

## 3. Scope of the rule

The rule applies to each annual module plan.

The validation should be calculated using all linked assessment records where:

| Field | Required condition |
|---|---|
| Module Plan | Matches the module plan being submitted |
| Is Summative | Yes |
| Assessment Weight | Present |

The rule should not calculate across the whole assessment List. It must calculate per module plan.

## 4. Formal examinations

Formal examinations should be included in the total summative assessment weight.

However, formal examinations should not appear in the local EEECS coursework calendar because they are normally managed through the formal examination process rather than the local coursework-calendar process.

Expected logic for a formal examination:

| Field | Expected value |
|---|---|
| Assessment Type | Formal Examination |
| Is Summative | Yes |
| Is Formal Examination | Yes |
| Include in EEECS Calendar | No |
| Predicted Release Date | Not required |
| Predicted Submission Date | Not required |
| Predicted Feedback Date | Not required |
| Predicted Date Status | Not required |
| Calendar Inclusion Status | Correct - exam excluded |

This means a formal examination can contribute to the module mark while being excluded from local coursework-calendar planning.

## 5. Non-exam assessments

For non-exam summative assessments, predicted dates should normally be required.

Expected logic for non-exam summative assessments:

| Field | Expected value |
|---|---|
| Is Summative | Yes |
| Is Formal Examination | No |
| Include in EEECS Calendar | Yes |
| Predicted Release Date | Required |
| Predicted Submission Date | Required |
| Predicted Feedback Date | Required |
| Predicted Date Status | Complete |
| Calendar Inclusion Status | Correct - included |

Examples include:

- coursework;
- projects;
- class tests;
- reports;
- portfolios;
- presentations;
- practical assessments;
- laboratory assessments.

## 6. 0-CATS and non-credit exceptions

Some module records may have 0 CATS or may represent exceptional non-credit-bearing activity.

These cases should be treated as exceptions rather than normal credit-bearing modules.

For 0-CATS or non-credit cases, an assessment-weight total of 0 may be valid if the module is explicitly marked as a 0-CATS or non-credit case.

Example:

| Field | Example value |
|---|---|
| Module CATS | 0 |
| Assessment Type | Report |
| Assessment Weight | 0 |
| Exception status | Allowed |

The final workflow should avoid blocking valid 0-CATS or non-credit records, but these records should remain visible to QA reviewers.

Recommended handling:

| Condition | Recommended action |
|---|---|
| CATS = 0 and total assessment weight = 0 | Allow submission as an exception |
| CATS = 0 and total assessment weight is not 0 | Flag for QA review |
| CATS > 0 and total assessment weight = 100 | Allow submission |
| CATS > 0 and total assessment weight is not 100 | Block submission |

## 7. Current Microsoft Lists limitation

The current Microsoft Lists pilot can store assessment weights and display them for review.

However, a simple Microsoft Lists column cannot reliably enforce the total assessment-weight rule across multiple linked assessment records.

This is because the rule depends on aggregating several assessment rows linked to the same module plan.

The required calculation is:

`Sum of assessment weights for all summative assessments linked to one module plan`

This is a cross-record validation rule, not a simple single-row validation rule.

For example, the system must know that the following three records belong to the same module plan:

| Module Plan | Assessment | Weight |
|---|---|---:|
| 2026-27_PILOT102 | Pilot Coursework 1 | 30 |
| 2026-27_PILOT102 | Pilot Coursework 2 | 20 |
| 2026-27_PILOT102 | Formal Exam | 50 |

It must then calculate:

`30 + 20 + 50 = 100`

A standard single-row Microsoft Lists validation rule is not sufficient for this kind of linked-record aggregation.

## 8. Current pilot workaround

In the current pilot, assessment weights are checked manually using the assessment-weighting review view.

The pilot can support manual QA checking by displaying:

- module plan;
- assessment number;
- assessment title;
- assessment type;
- assessment weight;
- summative status;
- formal examination status;
- calendar inclusion status.

This allows QA reviewers to identify whether each module plan appears to total 100%.

However, this is only a review aid. It does not yet prevent an invalid module plan from being submitted.

## 9. Recommended future enforcement

The final workflow should enforce the assessment-weight rule using Power Apps, Power Automate or equivalent deterministic validation logic.

Recommended logic:

1. Identify the module plan being submitted.
2. Find all assessment records linked to that module plan.
3. Keep assessment records where `Is Summative = Yes`.
4. Sum the `Assessment Weight` values.
5. Read the module CATS value from the linked module catalogue record.
6. If CATS is greater than 0, require the total summative weight to equal 100.
7. If CATS equals 0, allow a total summative weight of 0 as an exception.
8. If the total is invalid, prevent submission.
9. Show a clear message to the module owner.
10. Keep the module plan in Draft or Returned for revision status until the issue is corrected.

## 10. Suggested validation outcomes

| Scenario | Expected result |
|---|---|
| CATS > 0 and total summative weight = 100 | Pass |
| CATS > 0 and total summative weight < 100 | Block submission |
| CATS > 0 and total summative weight > 100 | Block submission |
| CATS = 0 and total summative weight = 0 | Pass as exception |
| CATS = 0 and total summative weight > 0 | Flag for QA review |
| No linked assessment records | Block submission |
| Missing assessment weight | Block submission |
| Non-numeric assessment weight | Block submission |
| Formal examination included in total | Pass if overall total is valid |
| Formal examination excluded from EEECS calendar | Pass |
| Formal examination included in EEECS calendar | Block or flag before submission |

## 11. Suggested user-facing messages

If the total assessment weight is too low:

> The total summative assessment weight for this module is currently below 100%. Please update the assessment components so that the total is 100% before submitting the module plan.

If the total assessment weight is too high:

> The total summative assessment weight for this module is currently above 100%. Please update the assessment components so that the total is 100% before submitting the module plan.

If no assessment records exist:

> No assessment records are linked to this module plan. Please add the summative assessment components before submitting the module plan.

If an assessment weight is missing:

> One or more summative assessment components does not have an assessment weight. Please complete all assessment weights before submitting the module plan.

If the module is a valid 0-CATS exception:

> This module is recorded as 0 CATS. A total assessment weight of 0% is allowed as an exceptional non-credit case.

If a 0-CATS module has a non-zero assessment weight:

> This module is recorded as 0 CATS but has a non-zero assessment weight. Please check whether this is correct or request QA review.

## 12. Submission-gate requirement

The module plan should not be allowed to move from `Draft` to `Submitted` unless the assessment-weight validation rule has passed.

Recommended submission gate:

| Condition | Submission allowed? |
|---|---|
| CATS > 0 and summative weight total = 100 | Yes |
| CATS > 0 and summative weight total is not 100 | No |
| CATS = 0 and summative weight total = 0 | Yes |
| CATS = 0 and summative weight total is not 0 | Requires QA review |
| Missing assessment records | No |
| Missing assessment weights | No |

The submission gate should run when the module owner attempts to submit the module plan for QA review.

## 13. Relationship to other validation rules

Assessment-weight validation should work alongside other MAP-QA validation rules.

Before submission, the system should also check that:

- non-exam assessments have predicted release, submission and feedback dates;
- formal examinations are excluded from the EEECS coursework calendar;
- formal examinations are marked consistently;
- assessment numbers are present;
- assessment titles are present;
- assessment types are present;
- assessment periods are present;
- module owner declaration is completed.

Together, these checks form the basis of the MAP-QA submission gate.

## 14. Implementation options

### Option A: Manual QA review

This is the current pilot approach.

Advantages:

- simple to implement;
- works with standard Microsoft Lists views;
- useful during early prototyping.

Limitations:

- does not block invalid submissions;
- depends on manual checking;
- may not scale well across many modules.

### Option B: Power Automate calculation

Power Automate could calculate the total assessment weight for each module plan and write the result back to the module plan record.

Possible module-plan-level fields:

| Field | Purpose |
|---|---|
| Total Summative Weight | Stores the calculated total |
| Weighting Status | Stores Pass, Warning or Fail |
| Weighting Check Notes | Stores any QA notes |

Advantages:

- creates a visible module-plan-level status;
- supports automated checking;
- can be used in QA dashboards.

Limitations:

- may not provide immediate form-level feedback;
- flow timing and trigger behaviour must be tested;
- additional maintenance is required.

### Option C: Power Apps submission gate

Power Apps could check the linked assessment records when the user clicks Submit.

Advantages:

- provides immediate feedback to the module owner;
- can prevent submission before data quality issues reach QA;
- can combine assessment-weight validation with other checks.

Limitations:

- requires Power Apps configuration;
- requires testing of edge cases;
- requires maintenance if the data model changes.

### Recommended approach

The recommended final approach is to use Power Apps for the submission gate and Power Automate for background calculation or status updates if needed.

## 15. Acceptance criteria

This document satisfies Issue #29 by defining that:

- summative assessment weights should normally total 100%;
- formal examinations are included in the summative assessment total;
- formal examinations are excluded from the local EEECS coursework calendar;
- 0-CATS and non-credit-bearing cases are treated as exceptions;
- Microsoft Lists alone cannot reliably enforce this as a cross-record rule;
- the current pilot workaround is manual QA checking;
- the recommended final solution is a submission gate using Power Apps, Power Automate or deterministic validation logic;
- suggested validation outcomes and user-facing messages are recorded.

## 16. Data protection

This document contains only structural design rules.

It does not include:

- operational module data;
- staff names;
- student data;
- email addresses;
- screenshots;
- private SharePoint links;
- identifiable assessment records.

## 17. Next steps

1. Define how total assessment weight should be stored or displayed at module-plan level.
2. Decide whether Power Apps or Power Automate should calculate the total.
3. Define the exact user-facing error messages.
4. Test the rule using the existing representative pilot records.
5. Add the rule to the final MAP-QA submission workflow.
