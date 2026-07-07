# Conditional Predicted-Date Validation

**Project:** Agentic MAP-QA  
**Related issue:** #23  
**Document version:** 0.1  
**Status:** Prototype validation completed  

## 1. Purpose

This document records the conditional validation rule used in the `MAP_Assessments` Microsoft List to require predicted dates for non-exam assessments.

The purpose of the rule is to ensure that module owners complete the key planning dates needed for assessment calendar preparation and QA monitoring, while still allowing formal examinations to be recorded without local coursework dates.

## 2. Design problem

The assessment planning workflow needs three predicted dates for coursework and locally managed assessments:

- predicted release date;
- predicted submission date;
- predicted feedback date.

These dates are essential for:

- assessment calendar planning;
- checking assessment bunching;
- checking feedback timing;
- supporting later comparison between predicted and actual delivery;
- enabling deterministic and agent-based QA checks.

However, these fields cannot be marked as globally required at Microsoft List level because formal examinations and centrally managed assessments may not have locally controlled coursework release, submission or feedback dates.

## 3. Design decision

The three predicted date fields should remain technically optional at List-column level.

However, the staff-facing workflow should enforce the following conditional rule:

- if `Is Formal Examination` is `No`, then predicted release, submission and feedback dates must be completed;
- if `Is Formal Examination` is `Yes`, then the predicted date fields may remain blank.

This gives the workflow both flexibility and data quality.

## 4. Microsoft Lists validation rule

The following validation formula was tested successfully in the prototype `MAP_Assessments` List:

```text
=IF([Is Formal Examination]=TRUE,TRUE,AND(NOT(ISBLANK([Predicted Release Date])),NOT(ISBLANK([Predicted Submission Date])),NOT(ISBLANK([Predicted Feedback Date]))))
```

The validation message used was:

```text
For non-exam assessments, please complete the predicted release date, predicted submission date and predicted feedback date. Formal examinations may leave these dates blank.
```

## 5. Validation behaviour

The rule implements the following behaviour:

| Scenario | Expected behaviour |
|---|---|
| Non-exam assessment with missing predicted dates | Save is blocked |
| Non-exam assessment with all predicted dates completed | Save is accepted |
| Formal examination with blank predicted dates | Save is accepted |

This behaviour was tested successfully in the prototype List.

## 6. Test scenario 1: non-exam assessment with missing dates

A non-exam assessment was tested with at least one missing predicted date.

The record was configured as:

| Field | Value |
|---|---|
| Is Formal Examination | No |
| Predicted Release Date | Missing |
| Predicted Submission Date | Missing or incomplete |
| Predicted Feedback Date | Missing or incomplete |

Expected result:

- the record should not save.

Observed result:

- the validation rule blocked the record from being saved.

## 7. Test scenario 2: non-exam assessment with completed dates

A non-exam assessment was tested with all three predicted dates completed.

The record was configured as:

| Field | Value |
|---|---|
| Is Formal Examination | No |
| Predicted Release Date | Completed |
| Predicted Submission Date | Completed |
| Predicted Feedback Date | Completed |

Expected result:

- the record should save successfully.

Observed result:

- the record saved successfully.

## 8. Test scenario 3: formal examination with blank dates

A formal examination was tested with blank predicted date fields.

The record was configured as:

| Field | Value |
|---|---|
| Assessment Type | Formal Examination |
| Is Formal Examination | Yes |
| Predicted Release Date | Blank |
| Predicted Submission Date | Blank |
| Predicted Feedback Date | Blank |

Expected result:

- the record should save successfully.

Observed result:

- the record saved successfully.

## 9. Impact on clean pilot design

This validation rule should be carried forward into the clean pilot version of `MAP_Assessments`.

The clean pilot should therefore use the following design:

| Field | Column-level required setting | Conditional rule |
|---|---|---|
| Predicted Release Date | No | Required when `Is Formal Examination` is No |
| Predicted Submission Date | No | Required when `Is Formal Examination` is No |
| Predicted Feedback Date | No | Required when `Is Formal Examination` is No |

This approach avoids forcing inappropriate dates onto formal examinations while still preventing module owners from omitting required planning dates for coursework and locally managed assessments.

## 10. Relationship with formal examinations

Formal examinations should still be included as assessment records because they contribute to the total summative assessment weighting.

The expected formal examination representation remains:

| Field | Expected value |
|---|---|
| Assessment Type | Formal Examination |
| Is Summative | Yes |
| Is Formal Examination | Yes |
| Include in EEECS Calendar | No |
| Predicted Release Date | Blank |
| Predicted Submission Date | Blank |
| Predicted Feedback Date | Blank |

The conditional validation rule supports this representation.

## 11. Relationship with coursework calendar planning

For coursework and locally managed assessments, predicted dates are essential.

The expected coursework representation is:

| Field | Expected value |
|---|---|
| Is Summative | Yes |
| Is Formal Examination | No |
| Include in EEECS Calendar | Yes |
| Predicted Release Date | Completed |
| Predicted Submission Date | Completed |
| Predicted Feedback Date | Completed |

The conditional validation rule ensures that these required planning dates cannot be ignored during staff entry.

## 12. QA monitoring value

The predicted date fields support later QA monitoring by allowing comparison between:

- predicted release date and actual release date;
- predicted submission date and actual submission date;
- predicted feedback date and actual feedback date;
- calculated feedback due date and actual feedback date.

This supports later classification of feedback status, such as:

- on time;
- late;
- missing;
- not yet due.

The validation rule therefore improves downstream data quality for both deterministic and agent-based QA checks.

## 13. Limitations

The current rule validates only whether predicted date fields are completed for non-exam assessments.

It does not yet validate:

- whether dates are in the correct order;
- whether the feedback date is within the expected feedback window;
- whether dates avoid weekends or holidays;
- whether assessment deadlines create bunching across modules;
- whether predicted dates align with semester dates;
- whether the selected assessment type and formal examination flag are consistent.

These checks should be handled later through deterministic validation logic, Power Apps, Power Automate or the agentic QA layer.

## 14. Data protection

No operational records, staff names, email addresses, module records, screenshots or exported Microsoft Lists files are included in this document.

Only the structural validation rule and anonymised test outcomes are recorded.

## 15. Conclusion

The prototype successfully validated the conditional predicted-date requirement.

The tested rule provides the correct balance between flexibility and data quality:

- formal examinations can be recorded without inappropriate coursework dates;
- non-exam assessments cannot be saved unless the three predicted planning dates are completed.

This rule should be included in the clean pilot version of the `MAP_Assessments` List.

## 16. Next steps

1. Add this validation rule to the clean pilot `MAP_Assessments` List.
2. Add a QA/admin view showing non-exam assessments with missing or problematic predicted dates, if needed.
3. Test the rule again in the clean pilot location.
4. Document any differences between the prototype and clean pilot behaviour.
5. Extend validation later to cover date order, feedback timing and assessment bunching.
