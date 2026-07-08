# Formal Examination Handling Logic

**Project:** Agentic MAP-QA  
**Related issue:** #34  
**Document version:** 0.1  
**Status:** Design rule defined  

## 1. Purpose

This document defines how MAP-QA should handle formal examination records consistently across the assessment workflow.

Formal examinations need special handling because they are summative assessments and contribute to the total module mark, but they should not be treated in the same way as local coursework assessments.

In particular, formal examinations should:

- be included in summative assessment weighting;
- be excluded from the local EEECS coursework calendar;
- not require predicted release, submission or feedback dates;
- be clearly identifiable in assessment records;
- be handled automatically in the final staff-facing workflow.

## 2. Core rule

If an assessment is a formal examination, the system should treat it as a summative assessment that contributes to the module mark but is excluded from local coursework-calendar planning.

The required logic is:

| Field | Required value |
|---|---|
| Assessment Type | Formal Examination |
| Is Summative | Yes |
| Is Formal Examination | Yes |
| Include in EEECS Calendar | No |
| Assessment Period | Not applicable |
| Predicted Release Date | Blank / not required |
| Predicted Submission Date | Blank / not required |
| Predicted Feedback Date | Blank / not required |
| Predicted Date Status | Not required |
| Calendar Inclusion Status | Correct - exam excluded |

## 3. Why formal examinations need separate handling

Formal examinations are different from coursework, projects, reports, class tests, portfolios and other local assessment components.

They are normally managed through the formal examination process rather than through the local EEECS coursework calendar.

Therefore, they should not require the same local planning fields as coursework assessments.

The key distinction is:

| Assessment category | Included in total weighting? | Included in EEECS coursework calendar? | Predicted dates required? |
|---|---:|---:|---:|
| Coursework / project / report | Yes | Yes | Yes |
| Formal examination | Yes | No | No |

This distinction prevents formal examinations from appearing incorrectly in local coursework planning while still ensuring that their weighting is included in the full module assessment structure.

## 4. Relationship with assessment-weight validation

Formal examinations must be included in total summative assessment-weight validation.

Example valid structure:

| Assessment | Type | Weight |
|---|---|---:|
| Coursework 1 | Coursework / Assignment | 30 |
| Coursework 2 | Coursework / Assignment | 20 |
| Formal Exam | Formal Examination | 50 |
| **Total** |  | **100** |

This structure should pass assessment-weight validation because the formal examination contributes 50% to the total module mark.

Formal examinations should not be removed from the weighting calculation simply because they are excluded from the local coursework calendar.

## 5. Relationship with calendar-inclusion checking

Formal examinations should be excluded from the EEECS coursework calendar.

The expected calendar-inclusion rule is:

| Scenario | Expected Calendar Inclusion Status |
|---|---|
| Formal examination + Include in EEECS Calendar = No | Correct - exam excluded |
| Formal examination + Include in EEECS Calendar = Yes | Check - formal exam included in calendar |
| Non-exam assessment + Include in EEECS Calendar = Yes | Correct - included |
| Non-exam assessment + Include in EEECS Calendar = No | Check - non-exam excluded from calendar |

During pilot testing, this rule correctly identified a formal examination record that had accidentally been included in the EEECS calendar. The record was corrected by setting `Include in EEECS Calendar` to `No`.

## 6. Relationship with predicted-date checking

Formal examinations should not require predicted release, submission or feedback dates.

The expected predicted-date rule is:

| Scenario | Expected Predicted Date Status |
|---|---|
| Formal examination with blank predicted dates | Not required |
| Formal examination with completed predicted dates | Not required |
| Non-exam assessment with all predicted dates completed | Complete |
| Non-exam assessment with one or more missing predicted dates | Missing predicted dates |

This prevents the system from incorrectly flagging formal examinations as incomplete simply because local coursework dates are not entered.

## 7. Current pilot implementation

In the Microsoft Lists pilot, formal examination handling is supported using the following fields:

| Field | Purpose |
|---|---|
| Assessment Type | Identifies formal examinations using the choice `Formal Examination` |
| Is Formal Examination | Explicit Yes/No flag for formal examination logic |
| Include in EEECS Calendar | Controls whether the assessment appears in local calendar planning |
| Predicted Date Status | Flags whether predicted dates are required or complete |
| Calendar Inclusion Status | Flags whether calendar inclusion is correct |

The current pilot uses calculated helper columns to flag issues.

These helper columns support QA review, but they do not yet prevent users from saving inconsistent records.

## 8. Current calculated-status logic

The pilot uses `Predicted Date Status` to distinguish between formal examination and non-exam assessment records.

Expected logic:

| Condition | Status |
|---|---|
| Assessment is a formal examination | Not required |
| Non-exam assessment has missing predicted dates | Missing predicted dates |
| Non-exam assessment has all predicted dates | Complete |

The pilot also uses `Calendar Inclusion Status` to distinguish correct and incorrect calendar handling.

Expected logic:

| Condition | Status |
|---|---|
| Formal exam excluded from calendar | Correct - exam excluded |
| Formal exam included in calendar | Check - formal exam included in calendar |
| Non-exam included in calendar | Correct - included |
| Non-exam excluded from calendar | Check - non-exam excluded from calendar |

## 9. Inconsistent formal examination records

The final workflow should detect inconsistent formal examination records.

Examples of inconsistent records:

| Problem | Example |
|---|---|
| Assessment Type says Formal Examination but Is Formal Examination is No | Type = Formal Examination, flag unticked |
| Is Formal Examination is Yes but Assessment Type is not Formal Examination | Type = Coursework, flag ticked |
| Formal examination included in EEECS calendar | Include in EEECS Calendar = Yes |
| Formal examination has Assessment Period set to Semester 1 or Semester 2 | Assessment Period not set to Not applicable |
| Formal examination is not summative | Is Summative = No |
| Formal examination excluded from weighting calculation | Weight not included in total |

These inconsistencies should be blocked or flagged before module-plan submission.

## 10. Recommended final automation

In the final staff-facing workflow, Power Apps should automate formal examination handling.

Recommended behaviour:

When a user selects:

```text
Assessment Type = Formal Examination
```

the system should automatically set:

```text
Is Summative = Yes
Is Formal Examination = Yes
Include in EEECS Calendar = No
Assessment Period = Not applicable
Predicted Release Date = blank / not required
Predicted Submission Date = blank / not required
Predicted Feedback Date = blank / not required
```

The user should not need to remember all of these linked rules manually.

## 11. Recommended Power Apps behaviour

Suggested Power Apps behaviour:

| User action | System response |
|---|---|
| User selects Formal Examination | Auto-set formal exam fields |
| User changes from Formal Examination to another type | Re-enable predicted-date fields |
| User tries to include formal exam in EEECS calendar | Block or show warning |
| User tries to submit inconsistent formal exam record | Block submission |
| User leaves predicted dates blank for formal exam | Allow |
| User leaves predicted dates blank for non-exam | Block submission |

This would reduce module-owner error and make the form easier to use.

## 12. Suggested user-facing messages

If a formal examination is incorrectly included in the EEECS calendar:

> Formal examinations should not be included in the EEECS coursework calendar. Please set Include in EEECS Calendar to No.

If the formal examination flag is inconsistent with the assessment type:

> This assessment is marked inconsistently. If the assessment type is Formal Examination, the formal examination flag should also be set to Yes.

If a formal examination is marked as non-summative:

> Formal examinations should normally be recorded as summative assessments because they contribute to the module mark.

If a non-exam assessment has missing predicted dates:

> Predicted release, submission and feedback dates are required for non-exam assessments before the module plan can be submitted.

## 13. Submission-gate requirement

The module plan should not be allowed to move from `Draft` to `Submitted` if formal examination records are inconsistent.

Recommended submission gate:

| Condition | Submission allowed? |
|---|---|
| Formal examination has correct field values | Yes |
| Formal examination included in EEECS calendar | No |
| Formal examination not marked as formal examination | No |
| Formal examination not marked as summative | No |
| Formal examination has blank predicted dates | Yes |
| Non-exam assessment has blank predicted dates | No |

The submission gate should run together with other MAP-QA checks, including assessment-weight validation and predicted-date validation.

## 14. Recommended status fields

The following status fields are useful for QA review:

| Status field | Purpose |
|---|---|
| Predicted Date Status | Checks whether predicted dates are required or complete |
| Calendar Inclusion Status | Checks whether assessment-calendar inclusion is correct |
| Formal Examination Consistency Status | Checks whether formal examination fields are internally consistent |
| Submission Readiness Status | Combines key checks before submission |

A future enhancement could add a dedicated `Formal Examination Consistency Status` field.

Possible values:

| Status | Meaning |
|---|---|
| Correct - formal exam | Formal examination fields are consistent |
| Correct - non-exam | Non-exam assessment fields are consistent |
| Check - formal exam inconsistency | Assessment type and formal exam flag do not match |
| Check - calendar inconsistency | Formal exam is included in EEECS calendar |
| Check - summative inconsistency | Formal exam is not marked as summative |

## 15. Data protection

This document contains only structural design rules and anonymised pilot examples.

It does not include:

- operational module data;
- staff names;
- student data;
- email addresses;
- screenshots;
- private SharePoint links;
- identifiable assessment records.

## 16. Acceptance criteria

This document satisfies Issue #34 by defining that:

- formal examinations are summative assessment records;
- formal examinations are included in assessment-weight validation;
- formal examinations are excluded from the EEECS coursework calendar;
- formal examinations do not require predicted release, submission or feedback dates;
- inconsistent formal examination records should be flagged or blocked;
- Power Apps should automate the linked field values in the final staff-facing workflow;
- no operational or identifiable data is committed.

## 17. Next steps

1. Decide whether to add a dedicated `Formal Examination Consistency Status` helper column in the pilot.
2. Define the Power Apps rule for automatically setting formal examination fields.
3. Test the rule using the existing representative pilot records.
4. Add formal examination handling to the final MAP-QA submission gate.
5. Confirm compatibility with assessment-weight validation and calendar-export logic.