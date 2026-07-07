# Clean Pilot Microsoft Lists Plan

**Project:** Agentic MAP-QA  
**Related issue:** #21  
**Document version:** 0.1  
**Status:** Pilot design plan  

## 1. Purpose

This document defines the clean pilot version of the Microsoft Lists workflow for the MAP-QA process.

The clean pilot will be used to test whether the proposed MAP-QA data structure is understandable, usable and operationally suitable before wider use.

The pilot is not the final production system. It is a controlled version for testing the structure, lookup relationships, views and staff-facing workflow.

## 2. Pilot objective

The objective of the clean pilot is to create a simplified but realistic Microsoft Lists workflow that supports:

- module catalogue management;
- annual module assessment planning;
- assessment-level data capture;
- assessment weighting checks;
- predicted release, submission and feedback dates;
- formal examination representation;
- later actual feedback monitoring;
- export to an Assessment Pivot-compatible structure.

## 3. Recommended pilot location

The clean pilot should preferably be created in an appropriate School or EEECS SharePoint location rather than under a personal Microsoft Lists area.

This is recommended because a shared SharePoint location provides better support for:

- long-term ownership;
- permissions management;
- continuity if individual staff roles change;
- lookup relationships between Lists;
- future Power Apps integration;
- future Power Automate workflows;
- controlled access for module owners and QA administrators.

If a suitable SharePoint location is not immediately available, the pilot may temporarily remain in a controlled prototype area, but the final production workflow should not depend on a personal workspace.

## 4. Pilot Lists

The clean pilot should contain three core Lists:

| Pilot List | Purpose |
|---|---|
| `MAP_Module_Catalogue_Pilot_2026_27` | Stores stable module-level information |
| `MAP_Module_Plans_Pilot_2026_27` | Stores annual module planning information |
| `MAP_Assessments_Pilot_2026_27` | Stores one row per assessment component |

The three-List structure should be retained because it separates stable module information from annual planning and assessment-level records.

## 5. Data model principle

The pilot should follow a relational structure:

- one module catalogue record may link to many annual module plans;
- one annual module plan may link to many assessment records;
- one assessment record should represent one assessment component.

This avoids the limitations of a fixed-form structure where multiple assessment components are stored in repeated columns.

## 6. List 1: module catalogue

The module catalogue List should contain stable module-level information.

Recommended fields:

| Field | Type | Required | Notes |
|---|---|---|---|
| Module Code | Single line text | Yes | Unique module identifier |
| Module Title | Single line text | Yes | Official module title |
| Programme | Choice | Yes | Broad programme grouping |
| Default Module Owner(s) | Person | Yes | Multiple selections allowed |
| Default Moderator | Person | No | Single selection |
| Delivery Period | Choice | Yes | Semester 1, Semester 2 or Full Year |
| CATS | Number | Yes | Restricted to valid CATS values |
| Active Module | Yes/No | Yes | Admin-facing field |
| MAP Required | Yes/No | Yes | Admin-facing field |

The default `Title` column should not be used as the main module identifier. The main user-facing identifier should be `Module Code`.

## 7. List 2: module plans

The module plans List should contain annual planning information for each module.

Recommended fields:

| Field | Type | Required | Notes |
|---|---|---|---|
| Academic Year | Choice | Yes | Example: 2026/27 |
| Module | Lookup | Yes | Lookup to module catalogue using Module Code |
| Confirmed Module Owners | Person | Yes | Multiple selections allowed |
| Confirmed Moderator | Person | No | Single selection |
| Moderator Discussion Status | Choice | Yes | Records whether the moderator has been consulted |
| Submission Status | Choice | Yes | Draft, Submitted, Returned, Resubmitted or Approved |
| Owner Declaration | Yes/No | No | Should not block draft saving |
| Number of Summative Assessments | Number | Yes | Declared count of summative components |
| Assessment Count Justification | Multiple lines text | No | Used when assessment count is unusually high |
| Formative Assessment Methods | Choice | Yes | Multiple selections allowed |
| Student Support and Office Hours | Multiple lines text | Yes | Captures support arrangements |
| Plan Reference | Single line text | Yes | Unique reference used for lookup from assessments |

`Plan Reference` should remain a unique field because it provides a clean link from assessment records to the correct annual module plan.

## 8. List 3: assessments

The assessments List should store one row per assessment component.

Recommended fields:

| Field | Type | Required | Notes |
|---|---|---|---|
| Module Plan | Lookup | Yes | Lookup to module plans using Plan Reference |
| Assessment Number | Number | Yes | Order of assessment component |
| Assessment Title | Single line text | Yes | Local title of the assessment |
| Assessment Type | Choice | Yes | Controlled assessment taxonomy |
| Assessment Weight | Number | Yes | Enter as whole number percentage |
| Assessment Mode | Choice | Yes | Individual, Group or Mixed |
| Is Summative | Yes/No | Yes | Default should be Yes |
| Is Formal Examination | Yes/No | Yes | Default should be No |
| Include in EEECS Calendar | Yes/No | Yes | Default should be Yes |
| Predicted Release Date | Date | No | Optional at List level |
| Predicted Submission Date | Date | No | Optional at List level |
| Predicted Feedback Date | Date | No | Optional at List level |
| Actual Release Date | Date | No | Optional at List level |
| Actual Submission Date | Date | No | Optional at List level |
| Actual Feedback Date | Date | No | Optional at List level |
| Feedback Monitoring Notes | Multiple lines text | No | Used later for QA monitoring |

All date fields should remain optional at Microsoft List level because formal examinations and centrally managed assessments may not have locally controlled coursework dates.

## 9. Assessment type choices

The pilot should use a short controlled taxonomy for `Assessment Type`.

Recommended choices:

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

The controlled type should not replace the free-text `Assessment Title`. The title field should remain available so module owners can describe the assessment in their own module-specific terms.

## 10. Formal examination representation

Formal examinations should be retained as assessment records because they contribute to the total module weighting.

The correct representation is:

| Field | Expected value |
|---|---|
| Assessment Type | Formal Examination |
| Is Summative | Yes |
| Is Formal Examination | Yes |
| Include in EEECS Calendar | No |
| Predicted Release Date | Blank |
| Predicted Submission Date | Blank |
| Predicted Feedback Date | Blank |
| Actual Release Date | Blank |
| Actual Submission Date | Blank |
| Actual Feedback Date | Blank |

This design keeps formal examinations visible in the summative assessment structure while excluding them from the local coursework calendar.

## 11. Coursework representation

Coursework and locally managed assessment records should normally include predicted dates.

The expected representation is:

| Field | Expected value |
|---|---|
| Is Summative | Yes |
| Is Formal Examination | No |
| Include in EEECS Calendar | Yes |
| Predicted Release Date | Completed where applicable |
| Predicted Submission Date | Completed where applicable |
| Predicted Feedback Date | Completed where applicable |
| Actual dates | Blank at planning stage |

Actual dates should be completed later during semester delivery and QA monitoring.

## 12. User-facing views

The pilot should include simplified views for module owners.

Recommended module-owner views:

| View | Purpose |
|---|---|
| My Module Plans | Shows the module plans relevant to the current owner |
| Module Plan Detail | Shows planning fields for one annual module plan |
| Assessment Components | Shows assessment records linked to a selected module plan |
| Coursework Calendar View | Shows only records where `Include in EEECS Calendar` is Yes |

The staff-facing views should avoid unnecessary technical fields where possible.

## 13. QA and admin views

The pilot should also include QA/admin views.

Recommended QA/admin views:

| View | Purpose |
|---|---|
| All Module Plans | Full overview of annual module plans |
| Plans Awaiting Submission | Tracks incomplete plans |
| Plans Returned for Revision | Tracks records requiring action |
| Assessment Weighting Check | Supports checking total weighting by module plan |
| Calendar-Included Assessments | Shows locally managed assessments for calendar planning |
| Formal Examinations | Shows formal exams retained for weighting but excluded from local calendar |
| Feedback Monitoring | Shows actual submission and feedback fields for later QA monitoring |

Admin views can include fields that are hidden from normal module-owner views.

## 14. Fields to hide from normal users

The following fields should be hidden from normal module-owner views where possible:

- `Active Module`
- `MAP Required`
- technical lookup IDs;
- duplicated lookup helper fields;
- internal workflow fields not needed for staff entry;
- calculated or derived export fields if later added.

These fields may remain visible in QA/admin views.

## 15. Fields to avoid duplicating

The pilot should avoid unnecessary duplication across Lists.

The following fields should not be manually duplicated in `MAP_Assessments` if they can be joined or derived later:

- module title;
- module owner;
- programme;
- delivery period;
- academic year;
- CATS;
- assignment code;
- feedback status;
- feedback due date.

The preferred approach is to keep the Lists relational and generate output fields through an export or transformation layer.

## 16. Pilot testing group

The pilot should be tested with a small group before wider use.

Recommended testing group:

- three to five module owners;
- one or two QA colleagues;
- one Stage Associate Director or equivalent reviewer;
- one administrator involved in assessment planning or calendar preparation.

The pilot should not be released to all academic staff until the workflow has been tested and refined.

## 17. Pilot test scenarios

The pilot should test the following scenarios:

1. Create or select a module catalogue record.
2. Create an annual module plan linked to the catalogue.
3. Add one coursework assessment.
4. Add multiple coursework assessments.
5. Add a formal examination with no coursework dates.
6. Confirm that assessment weights can total 100%.
7. Confirm that formal examinations are excluded from the coursework calendar view.
8. Confirm that actual feedback fields are available but not required at planning stage.
9. Export assessment records and check whether the structure remains compatible with the target Assessment Pivot output.
10. Identify fields or labels that are confusing for module owners.

## 18. Data protection rules

The clean pilot must not expose unnecessary personal or operational information.

The public GitHub repository must not include:

- exported Microsoft Lists files containing operational data;
- staff names;
- staff email addresses;
- identifiable module records;
- screenshots containing personal or institutional information;
- private SharePoint or Microsoft Lists links.

Only anonymised structural findings and design decisions should be documented in the public repository.

## 19. Current limitations

The clean pilot will not yet include:

- Power Apps forms;
- Power Automate reminders;
- automatic assessment-weight validation;
- automatic assessment-count validation;
- automatic date-order validation;
- automatic feedback due-date calculation;
- agent-based deconfliction;
- production-level permissions design.

These should be developed after the clean pilot structure has been tested.

## 20. Success criteria

The clean pilot will be considered successful if:

1. the three-List structure works in a shared pilot location;
2. lookup relationships work reliably;
3. module owners can understand the required fields;
4. multiple assessments can be linked to one module plan;
5. formal examinations can be represented correctly;
6. coursework records can include predicted dates;
7. actual feedback fields remain available for later monitoring;
8. assessment records can be exported for transformation into the target Assessment Pivot structure;
9. QA/admin views support review and monitoring;
10. no sensitive operational data are added to the public repository.

## 21. Next steps

1. Confirm the appropriate SharePoint location for the clean pilot.
2. Create the three pilot Lists.
3. Recreate the tested field structure.
4. Configure module-owner and QA/admin views.
5. Add a small number of representative test records.
6. Run pilot test scenarios.
7. Record usability issues and required improvements.
8. Document pilot implementation outcomes in a follow-up file.
