# Clean Pilot Microsoft Lists Implementation

**Project:** Agentic MAP-QA  
**Related issue:** #25  
**Document version:** 0.1  
**Status:** Clean pilot implemented and tested  

## 1. Purpose

This document records the implementation of the clean pilot Microsoft Lists workflow for the MAP-QA process.

The pilot was created to test whether the three-List structure can support module catalogue management, annual module assessment planning, assessment-level records, predicted-date checking and formal examination handling.

## 2. Pilot location

The clean pilot Lists were created in the EEECS Staff SharePoint location.

This was used as the pilot location so that the three Lists could be created in the same SharePoint environment and linked through lookup columns.

All pilot Lists should remain in the same SharePoint location to preserve lookup relationships.

## 3. Implemented pilot Lists

The following three Lists were created:

| List | Purpose |
|---|---|
| `MAP_Module_Catalogue_Pilot_2026_27` | Stores stable module-level information |
| `MAP_Module_Plans_Pilot_2026_27` | Stores annual module planning information |
| `MAP_Assessments_Pilot_2026_27` | Stores one row per assessment component |

The implemented structure follows the principle:

- one module catalogue record can link to one or more annual module plans;
- one annual module plan can link to multiple assessment records;
- one assessment record represents one assessment component.

## 4. Module catalogue implementation

The pilot module catalogue List was created as:

`MAP_Module_Catalogue_Pilot_2026_27`

The implemented fields were:

| Field | Type | Notes |
|---|---|---|
| Module Code | Single line text | Required; unique values enabled |
| Module Title | Single line text | Required |
| Programme | Choice | Broad programme grouping |
| Default Module Owner(s) | Person | Multiple selections allowed |
| Default Moderator | Person | Single person |
| Delivery Period | Choice | Semester 1, Semester 2 or Full Year |
| CATS | Number | Valid values include 0, 10, 20 and 40 |
| Active Module | Yes/No | Admin-facing field |
| MAP Required | Yes/No | Admin-facing field |

`Module Code` is used as the main module identifier. The default `Title` column is not used as the main identifier.

The `CATS` validation was updated to allow 0 CATS, because at least one module may be non-credit-bearing or exceptional.

The intended valid CATS values are:

- 0
- 10
- 20
- 40

## 5. Module plans implementation

The pilot module plans List was created as:

`MAP_Module_Plans_Pilot_2026_27`

The implemented fields were:

| Field | Type | Notes |
|---|---|---|
| Academic Year | Choice | Annual planning year |
| Module | Lookup | Links to `MAP_Module_Catalogue_Pilot_2026_27` using `Module Code` |
| Module: CATS | Lookup helper field | Pulled through from the module catalogue |
| Confirmed Module Owners | Person | Multiple selections allowed |
| Coordinating Module Owner | Person | Single person responsible for coordinating the MAP entry |
| Confirmed Moderator | Person | Single person |
| Moderator Discussion Status | Choice | Tracks moderator discussion status |
| Submission Status | Choice | Draft, submitted, returned, resubmitted or approved |
| Owner Declaration | Yes/No | Used for final confirmation; not required for draft saving |
| Number of Summative Assessments | Number | Declared count of summative components |
| Assessment Count Justification | Multiple lines text | Used where assessment count needs explanation |
| Formative Assessment Methods | Choice | Multiple selections allowed |
| Student Support and Office Hours | Multiple lines text | Records support arrangements |
| Plan Reference | Single line text | Required; unique values enabled |

`Plan Reference` is used as the unique annual module-plan identifier.

Example format:

`2026-27_PILOT001`

For the pilot, this field is entered manually. In a later staff-facing implementation, it should be generated automatically using Power Apps or Power Automate.

## 6. Module ownership design

The pilot distinguishes between default ownership and confirmed annual ownership.

| List | Field | Purpose |
|---|---|---|
| Module catalogue | Default Module Owner(s) | Usual or default module owner information |
| Module plans | Confirmed Module Owners | Actual confirmed owners for the academic year |
| Module plans | Coordinating Module Owner | Main person responsible for completing or coordinating the MAP form |
| Assessments | Assessment Lead | Optional person responsible for a specific assessment component |

This supports modules with more than one owner while keeping one module-level plan per module.

The coordinating module owner should complete or coordinate the MAP entry for the whole module. Where responsibility for specific assessment components is shared, the assessment-level `Assessment Lead` field can be used.

## 7. Assessments implementation

The pilot assessment List was created as:

`MAP_Assessments_Pilot_2026_27`

The implemented fields were:

| Field | Type | Notes |
|---|---|---|
| Module Plan | Lookup | Links to `MAP_Module_Plans_Pilot_2026_27` using `Plan Reference` |
| Assessment Number | Number | Order of the assessment component |
| Assessment Title | Single line text | Local title of the assessment |
| Assessment Type | Choice | Controlled assessment taxonomy |
| Assessment Weight | Number | Whole-number percentage of module mark |
| Assessment Mode | Choice | Individual, Group or Mixed |
| Is Summative | Yes/No | Default should be Yes |
| Is Formal Examination | Yes/No | Default should be No |
| Include in EEECS Calendar | Yes/No | Default should be Yes |
| Assessment Lead | Person | Optional; used where an assessment has a specific lead |
| Assessment Period | Choice | Semester 1, Semester 2, Full Year or Not applicable |
| Predicted Release Date | Date | Optional at column level |
| Predicted Submission Date | Date | Optional at column level |
| Predicted Feedback Date | Date | Optional at column level |
| Actual Release Date | Date | Optional; completed later |
| Actual Submission Date | Date | Optional; completed later |
| Actual Feedback Date | Date | Optional; completed later |
| Feedback Monitoring Notes | Multiple lines text | QA monitoring notes |
| Predicted Date Status | Calculated | Flags predicted-date completion status |

The optional `Teaching Block / Weeks Covered` field was not included in the implemented pilot because it was considered unnecessary for the current workflow and could make the form longer for module owners.

## 8. Assessment type choices

The following assessment type choices were used:

- Coursework / Assignment
- Project
- Class Test
- Practical Test
- Laboratory Assessment
- Presentation / Oral / Demonstration
- Portfolio
- Report
- Formal Examination
- Other

The controlled `Assessment Type` field does not replace the free-text `Assessment Title` field.

## 9. Assessment period choices

The following choices were used for `Assessment Period`:

- Semester 1
- Semester 2
- Full Year
- Not applicable

`Not applicable` is used for formal examinations or centrally managed assessments that should not appear in the local EEECS coursework calendar.

## 10. Predicted-date status implementation

The clean pilot requires predicted release, submission and feedback dates for non-exam assessments.

However, these date fields cannot be made globally required at column level because formal examinations may not have local coursework dates.

The pilot therefore implemented a calculated helper column:

`Predicted Date Status`

The purpose of this column is to flag whether predicted dates are complete for non-exam assessments.

The calculated column returns:

| Status | Meaning |
|---|---|
| `Missing predicted dates` | Non-exam assessment is missing one or more predicted dates |
| `Complete` | Non-exam assessment has predicted release, submission and feedback dates |
| `Not required` | Formal examination; predicted coursework dates are not required |

This provides a QA/admin check in the current pilot.

## 11. Predicted-date enforcement limitation

The SharePoint location used for the pilot did not show the standard List-level `Validation settings` option.

As a result, the current pilot does not block module owners from saving a non-exam assessment with missing predicted dates.

Instead, the pilot uses:

- a calculated `Predicted Date Status` field;
- an admin-facing QA view;
- a process rule that a module plan is not ready for QA review if any linked non-exam assessment has missing predicted dates.

The final staff-facing implementation should enforce this rule through Power Apps or Power Automate.

The intended final rule is:

- if `Is Formal Examination` is `No`, then predicted release, submission and feedback dates must be completed;
- if `Is Formal Examination` is `Yes`, the predicted date fields may remain blank.

## 12. Assessment date QA view

A QA/admin view was created:

`Assessment date QA check`

This view shows the key fields required to review predicted-date completeness:

- Module Plan
- Assessment Number
- Assessment Title
- Assessment Type
- Assessment Weight
- Is Summative
- Is Formal Examination
- Include in EEECS Calendar
- Assessment Period
- Predicted Release Date
- Predicted Submission Date
- Predicted Feedback Date
- Predicted Date Status

This view allows the QA user to identify records where non-exam assessment dates are incomplete.

## 13. Formal examination handling

Formal examinations are retained as assessment records because they contribute to the summative assessment weighting.

The tested formal examination representation is:

| Field | Expected value |
|---|---|
| Assessment Type | Formal Examination |
| Is Summative | Yes |
| Is Formal Examination | Yes |
| Include in EEECS Calendar | No |
| Assessment Period | Not applicable |
| Predicted Release Date | Blank |
| Predicted Submission Date | Blank |
| Predicted Feedback Date | Blank |
| Predicted Date Status | Not required |

This confirms that formal examinations can be included for weighting while excluded from the local coursework calendar.

## 14. Coursework handling

Coursework and locally managed non-exam assessments should include predicted dates.

The tested coursework representation is:

| Field | Expected value |
|---|---|
| Assessment Type | Coursework / Assignment |
| Is Summative | Yes |
| Is Formal Examination | No |
| Include in EEECS Calendar | Yes |
| Assessment Period | Semester 1, Semester 2 or Full Year |
| Predicted Release Date | Completed |
| Predicted Submission Date | Completed |
| Predicted Feedback Date | Completed |
| Predicted Date Status | Complete |

If one or more predicted dates are missing, `Predicted Date Status` returns:

`Missing predicted dates`

## 15. Pilot tests completed

The following test cases were completed successfully.

| Test case | Expected result | Observed result |
|---|---|---|
| Non-exam assessment with completed predicted dates | `Predicted Date Status = Complete` | Passed |
| Formal examination with blank predicted dates | `Predicted Date Status = Not required` | Passed |
| Non-exam assessment with missing predicted dates | `Predicted Date Status = Missing predicted dates` | Passed |

The tests confirm that the calculated helper field correctly identifies the three required statuses.

## 16. Current pilot rule

For the clean pilot, the operational rule is:

A module plan should not be treated as ready for QA review if any linked non-exam assessment has:

`Predicted Date Status = Missing predicted dates`

This is a QA gate rather than an automatic save-blocking rule in the current pilot.

## 17. Items not yet automated

The following checks are not yet automated:

1. total assessment weight equals 100%;
2. number of assessment records matches the declared number of summative assessments;
3. predicted dates are in a valid order;
4. predicted feedback date satisfies the expected feedback window;
5. feedback due date is calculated from actual submission date;
6. feedback timeliness status is derived;
7. coursework bunching is detected across modules;
8. module plan submission is blocked when linked assessments are incomplete.

These checks should be developed later through deterministic validation logic, Power Apps, Power Automate or the agentic QA layer.

## 18. Data protection

No operational exports, staff names, staff email addresses, identifiable module records, screenshots or private SharePoint links are included in this document.

Only structural implementation decisions and anonymised pilot test outcomes are recorded.

## 19. Conclusion

The clean pilot Microsoft Lists workflow has been implemented and tested.

The three-List structure works as intended:

- the module catalogue stores stable module information;
- the module plans List stores annual MAP planning information;
- the assessments List stores one row per assessment component.

The pilot supports multiple module owners, coordinating module ownership, assessment-level responsibility, formal examination handling, predicted-date status checking and later feedback monitoring.

The main limitation is that the current Microsoft Lists form does not yet block incomplete non-exam assessments from being saved. This should be handled in the final staff-facing workflow through Power Apps or Power Automate.

## 20. Next steps

1. Test the clean pilot with a small number of representative modules.
2. Add more realistic pilot records while avoiding public exposure of operational data.
3. Define a Power Apps form to enforce predicted-date completion for non-exam assessments.
4. Define automated checks for assessment weighting and assessment-count consistency.
5. Define date-order and feedback-timeliness validation rules.
6. Export pilot assessment records and confirm compatibility with the target Assessment Pivot structure.
7. Record user feedback from a small group of trusted testers.
