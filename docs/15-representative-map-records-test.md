# Representative MAP Records Test

**Project:** Agentic MAP-QA  
**Related issue:** #28  
**Document version:** 0.1  
**Status:** Representative pilot records tested  

## 1. Purpose

This document records the representative testing of the clean pilot Microsoft Lists workflow for MAP-QA.

The purpose of the test was to confirm that the three-List structure can represent realistic module assessment planning scenarios before wider pilot use.

The test focused on:

- module catalogue records;
- annual module plan records;
- assessment-level records;
- lookup relationships;
- multi-owner modules;
- formal examination handling;
- predicted-date status checking;
- calendar-inclusion checking;
- exceptional 0-CATS / non-credit cases.

## 2. Pilot Lists tested

The following pilot Lists were tested:

| List | Purpose |
|---|---|
| `MAP_Module_Catalogue_Pilot_2026_27` | Stores module catalogue records |
| `MAP_Module_Plans_Pilot_2026_27` | Stores annual module plan records |
| `MAP_Assessments_Pilot_2026_27` | Stores one row per assessment component |

The Lists were tested as a linked workflow, with assessment records linked to annual module plans and annual module plans linked to module catalogue records.

## 3. Representative test records

Five representative pilot module records were used.

| Pilot module | Test purpose |
|---|---|
| `PILOT101` | Basic single-owner module workflow |
| `PILOT102` | Multi-assessment module including a formal examination |
| `PILOT103` | Single 100% coursework/project assessment |
| `PILOT104` | Coursework plus formal examination handling |
| `PILOT105` | 0-CATS / non-credit exceptional case |

These records were created only for pilot testing. They are not operational module records.

## 4. Catalogue testing

The module catalogue List was tested using representative pilot records.

The following checks were completed:

| Check | Result |
|---|---|
| Module records can be added using `Module Code` as the main identifier | Passed |
| `Module Code` can be configured as a unique value | Passed |
| Duplicate module-code prevention was tested | Passed after enabling indexing and unique values |
| `CATS` values support 0, 20 and 40 in the pilot records | Passed |
| Multiple default module owners can be represented | Passed |
| Lookup values can be used by the module plans List | Passed |

A temporary issue was identified where duplicate module codes were initially accepted. This was resolved by enabling unique values on the `Module Code` column, which required indexing the column.

## 5. Module plan testing

Annual module plan records were created for the representative pilot modules.

The following checks were completed:

| Check | Result |
|---|---|
| Module lookup works from module plans to the catalogue | Passed |
| `Module: CATS` appears as a lookup helper field | Passed |
| `Plan Reference` can be used as a unique annual module-plan identifier | Passed |
| Duplicate `Plan Reference` values are rejected | Passed |
| `Confirmed Module Owners` allows multiple people | Passed |
| `Coordinating Module Owner` allows only one person | Passed after correcting the column setting |

A temporary issue was identified where `Coordinating Module Owner` allowed multiple people. This was corrected so that only one coordinating owner can be selected.

A temporary lookup-helper issue was also observed for one CATS value. The lookup helper field was refreshed and the value displayed correctly afterwards.

## 6. Assessment testing

Representative assessment records were created in:

`MAP_Assessments_Pilot_2026_27`

The test confirmed that one module plan can link to multiple assessment records and that one assessment record represents one assessment component.

## 7. PILOT102 test case

`2026-27_PILOT102` was tested with three assessment components:

- Pilot Coursework 1
- Pilot Coursework 2
- Formal Exam

This test case confirmed that the workflow can represent a module with multiple assessment components, including a formal examination.

Expected behaviour:

| Assessment type | Expected status |
|---|---|
| Coursework records | `Predicted Date Status = Complete` |
| Formal examination | `Predicted Date Status = Not required` |
| Formal examination calendar inclusion | `Calendar Inclusion Status = Correct - exam excluded` |

Observed result:

- the coursework records were represented as non-exam assessments;
- predicted dates were completed for coursework records;
- the formal examination was retained as a summative assessment;
- the formal examination was excluded from the EEECS coursework calendar;
- the status fields behaved as expected.

## 8. PILOT103 test case

`2026-27_PILOT103` was tested with one 100% coursework/project assessment.

This test case confirmed that the workflow can represent a module with a single summative assessment component.

Expected behaviour:

| Field | Expected value |
|---|---|
| Assessment Type | Coursework / Project-style assessment |
| Assessment Weight | 100 |
| Is Summative | Yes |
| Is Formal Examination | No |
| Include in EEECS Calendar | Yes |
| Predicted Date Status | Complete |
| Calendar Inclusion Status | Correct - included |

Observed result:

- the single-assessment structure was represented successfully;
- the predicted-date status behaved as expected.

## 9. PILOT104 test case

`2026-27_PILOT104` was tested with:

- one coursework assessment;
- one formal examination.

This test case confirmed that coursework and formal examination records can coexist under one module plan.

Expected behaviour:

| Assessment | Expected predicted-date status | Expected calendar status |
|---|---|---|
| Coursework | Complete | Correct - included |
| Formal examination | Not required | Correct - exam excluded |

Observed result:

- the coursework record behaved correctly;
- the formal examination record behaved correctly after ensuring `Is Formal Examination` was ticked;
- the formal examination was retained for weighting but excluded from the local EEECS coursework calendar;
- an incorrect calendar-inclusion setting for the formal examination was detected by `Calendar Inclusion Status` and then corrected.

This test identified a useful design risk: if a user selects `Assessment Type = Formal Examination` but forgets to tick `Is Formal Examination`, the workflow can become inconsistent. This risk was reduced by updating the `Predicted Date Status` logic to check both the formal-examination flag and the assessment type.

## 10. PILOT105 test case

`2026-27_PILOT105` was tested as a 0-CATS / non-credit exceptional case using a report-style assessment record.

This test confirmed that the workflow can represent exceptional or non-credit-bearing module records.

Expected behaviour:

| Field | Expected value |
|---|---|
| CATS | 0 |
| Assessment Weight | 0 |
| Assessment Type | Report |
| Predicted Date Status | Complete |
| Calendar Inclusion Status | Correct - included |

Observed result:

- the 0-CATS case could be represented;
- the report-style assessment could be entered;
- predicted-date status behaved as expected.

## 11. Predicted Date Status testing

The calculated helper column `Predicted Date Status` was tested.

The status values tested were:

| Scenario | Expected value | Observed result |
|---|---|---|
| Non-exam assessment with completed predicted dates | Complete | Passed |
| Formal examination with blank predicted dates | Not required | Passed |
| Non-exam assessment with missing predicted dates | Missing predicted dates | Passed |

The test confirmed that predicted-date completeness can be flagged reliably in the pilot.

This is currently a QA flag rather than a save-blocking validation rule.

## 12. Calendar Inclusion Status testing

A second calculated helper column was added:

`Calendar Inclusion Status`

This column checks whether formal examinations are excluded from the EEECS coursework calendar and whether non-exam assessments are included where expected.

The status values tested were:

| Scenario | Expected value | Observed result |
|---|---|---|
| Formal examination excluded from calendar | Correct - exam excluded | Passed |
| Non-exam assessment included in calendar | Correct - included | Passed |
| Formal examination incorrectly included in calendar | Check - formal exam included in calendar | Passed in test logic |
| Non-exam assessment excluded from calendar | Check - non-exam excluded from calendar | Available as QA warning |

This improves the pilot by highlighting possible calendar-inclusion errors.

## 13. Assessment date QA view

The view `Assessment date QA check` was used to review:

- Module Plan
- Assessment Number
- Assessment Title
- Assessment Type
- Assessment Weight
- Is Summative
- Is Formal Examination
- Include in EEECS Calendar
- Calendar Inclusion Status
- Assessment Period
- Predicted Release Date
- Predicted Submission Date
- Predicted Feedback Date
- Predicted Date Status

The final check confirmed:

- no unexpected `Missing predicted dates` statuses;
- formal examinations showed `Not required`;
- non-exam assessments showed `Complete`;
- formal examinations showed `Correct - exam excluded`;
- non-exam assessments showed `Correct - included`.

## 14. Manual weighting check

Assessment weighting was checked manually during this test.

The pilot confirmed that assessment weights can be entered and reviewed, but automatic per-module total-weight validation is not yet implemented.

A separate issue has been created to define assessment-weight validation before module plan submission.

Current intended rule:

- summative assessment weights should normally total 100%;
- formal examinations are included in the summative weighting total;
- 0-CATS or non-credit cases may be treated as exceptions;
- future submission should be blocked if the total weighting is invalid, unless an approved exception applies.

## 15. Issues identified during testing

The following issues or limitations were identified:

1. `Plan Reference` is currently entered manually.
2. `Plan Reference` should be generated automatically in the final staff-facing workflow.
3. Basic Microsoft Lists forms do not currently block incomplete non-exam assessment records from being saved.
4. `Predicted Date Status` is a QA flag rather than a hard validation rule.
5. `Calendar Inclusion Status` is a QA flag rather than a hard validation rule.
6. Assessment-weight totals are not yet automatically calculated or enforced per module plan.
7. The workflow should later reduce the need for module owners to manage linked logical fields manually.
8. Power Apps or Power Automate should be used later to implement submission gates.

## 16. Design implications

The representative test confirmed that the relational three-List design is suitable for the MAP-QA workflow.

The test also showed that some rules should be automated in the final staff-facing implementation, especially:

- automatic `Plan Reference` generation;
- automatic handling of formal examination flags;
- automatic exclusion of formal examinations from the coursework calendar;
- mandatory predicted dates for non-exam assessments;
- total assessment-weight validation before module-plan submission.

## 17. Data protection

No operational exports, staff names, staff email addresses, identifiable module records, screenshots or private SharePoint links are included in this document.

Only structural testing outcomes and anonymised pilot observations are recorded.

## 18. Conclusion

The representative MAP records test was completed successfully.

The clean pilot workflow can represent:

- single-assessment modules;
- multi-assessment modules;
- coursework plus formal examination structures;
- multi-owner modules;
- exceptional 0-CATS / non-credit cases;
- predicted-date completion status;
- calendar-inclusion status.

The main remaining implementation requirement is to move from QA warning fields to formal submission gates. This should be addressed through Power Apps, Power Automate or deterministic validation logic in later stages.

## 19. Next steps

1. Define assessment-weight validation before module plan submission.
2. Define automatic `Plan Reference` generation.
3. Define Power Apps logic for formal examination handling.
4. Define Power Apps or Power Automate logic for predicted-date enforcement.
5. Test with a small number of trusted module owners or QA colleagues.
6. Export pilot records and confirm compatibility with the target Assessment Pivot structure.
