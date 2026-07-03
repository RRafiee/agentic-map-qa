# MAP Module Plans Prototype

**Project:** Agentic MAP-QA  
**Related issue:** #13  
**Document version:** 0.1  
**Status:** Initial prototype implemented and tested  

## 1. Purpose

This document records the initial implementation of the `MAP_Module_Plans` Microsoft List.

The List stores one annual module assessment-planning record for each module. It links each annual plan to the controlled `MAP_Module_Catalogue` and captures module-level ownership, moderation, workflow, formative-assessment and student-support information.

Individual assessment components, including assessment titles, weightings and dates, will be stored separately in the planned `MAP_Assessments` List.

## 2. Relationship with the module catalogue

Each annual module plan is linked to `MAP_Module_Catalogue` through a Microsoft Lists Lookup column.

The primary lookup displays the module code. The following additional fields are retrieved automatically from the catalogue:

- `Module Title`
- `CATS`

The module code is not included again as an additional lookup field because the primary `Module` lookup already displays it.

`Programme` and `Delivery Period` are stored in the catalogue as Choice columns. They are not currently available as additional lookup fields through the standard Microsoft Lists relationship.

These values may later be displayed through Power Apps or copied through an automated workflow.

## 3. Implemented columns

| Column | Type | Required | Configuration |
|---|---|---:|---|
| Academic Year | Choice | Yes | Controlled academic-year values |
| Module | Lookup | Yes | Links to `Module Code` in `MAP_Module_Catalogue` |
| Module: Module Title | Lookup-derived | No | Retrieved automatically |
| Module: CATS | Lookup-derived | No | Retrieved automatically |
| Confirmed Module Owners | Person | Yes | Multiple selections enabled |
| Confirmed Moderator | Person | No | One person |
| Moderator Discussion Status | Choice | Yes | Controlled values; default is `Discussion pending` |
| Submission Status | Choice | Yes | Controlled workflow values; default is `Draft` |
| Owner Declaration | Yes/No | Yes | Default is `No` |
| Number of Summative Assessments | Number | Yes | Whole number between 1 and 12 |
| Assessment Count Justification | Multiple lines of text | No | Intended for plans with more than four assessments |
| Formative Assessment Methods | Choice | Yes | Multiple selections enabled |
| Student Support and Office Hours | Multiple lines of text | Yes | Records module-level support arrangements |

## 4. Academic year

The initial controlled academic-year values are:

- `2026/27`
- `2027/28`
- `2028/29`

Each module plan represents one module in one academic year.

## 5. Module ownership

`Confirmed Module Owners` records the owner or owners responsible for the module during the selected academic year.

Multiple selections are enabled to support:

- modules delivered jointly by co-owners;
- modules with more than one lecturer;
- full-year modules with different teaching responsibilities.

The current field records co-ownership but does not identify which owner is responsible for a particular semester or assessment.

A separate owner-assignment structure may be introduced later if this level of detail is required.

## 6. Moderation information

### 6.1 Confirmed Moderator

`Confirmed Moderator` is an optional Person field that records the moderator confirmed for the selected academic year.

It remains optional because a moderator may not yet have been allocated when the module plan is first created.

### 6.2 Moderator Discussion Status

The controlled values are:

- `Agreed with moderator`
- `Discussion pending`
- `Moderator not yet assigned`
- `Not applicable`

The default value is:

- `Discussion pending`

## 7. Submission workflow

`Submission Status` indicates the current stage of the annual module assessment plan.

The controlled values are:

- `Draft`
- `Submitted`
- `Returned for revision`
- `Resubmitted`
- `Approved`

The default status is `Draft`.

The intended workflow is:

1. The module owner prepares the plan as a Draft.
2. The owner submits the completed plan.
3. The QA team reviews the plan.
4. The plan may be returned for revision.
5. The owner resubmits the revised plan.
6. The plan is approved when the QA checks are complete.

## 8. Owner declaration

`Owner Declaration` confirms that the module owner has reviewed the plan and considers the submitted information complete and accurate.

The default value is `No`.

While the plan remains in `Draft`, the declaration should remain `No`. It should be changed to `Yes` when the owner submits the completed plan.

A later Power Apps or Power Automate rule may enforce the following relationship:

```text
Submission Status = Submitted
Owner Declaration = Yes

## 9. Number of summative assessments

`Number of Summative Assessments` records the total number of planned summative assessment components for the module, including any formal examination.

The field is configured to:

- accept whole numbers only;
- require a minimum value of 1;
- allow a maximum value of 12.

The declared number will later be compared with the number of assessment records linked to the module plan in `MAP_Assessments`.

`Assessment Count Justification` allows the module owner to explain why a relatively high number of summative assessments is necessary and how student assessment workload has been considered.

The justification field is currently optional. In the later Power Apps interface, it may become conditionally required when:

```text
Number of Summative Assessments > 4
```

## 10. Formative assessment methods

`Formative Assessment Methods` is a multiple-selection Choice field.

The available choices are:

- `Practice exercises with feedback`
- `Mock class test`
- `Quizzes`
- `Laboratory practice`
- `Peer-review activity`
- `Formative presentation`
- `Tutorial or workshop activities`
- `Worked examples`

Module owners may select more than one method.

Fill-in choices are disabled to maintain consistent and analysable data.

## 11. Student support and office hours

`Student Support and Office Hours` is a required multiple-lines-of-text field.

It records the arrangements through which students can:

- obtain academic support;
- ask questions about the module;
- discuss their academic progress;
- access office hours;
- receive support through tutorials, workshops or online channels.

This information is stored at module-plan level because support arrangements normally apply across the module rather than to an individual assessment component.

## 12. Initial prototype validation

A draft annual module plan was created successfully using a module selected from the controlled `MAP_Module_Catalogue`.

The initial test confirmed that:

- a module can be selected through the catalogue lookup;
- the module title is retrieved automatically;
- the CATS value is retrieved automatically;
- duplicate display of the module code can be removed;
- multiple confirmed module owners can be recorded;
- a confirmed moderator can be recorded when available;
- moderator discussion status uses controlled values;
- submission status defaults to `Draft`;
- `Owner Declaration` can remain `No` while the plan is in `Draft`;
- the number of summative assessments can be recorded;
- multiple formative assessment methods can be selected;
- student-support arrangements can be recorded.

The prototype currently contains operational test data only within the institutional Microsoft 365 environment. No identifiable records are included in the public repository.

## 13. Data protection

The public GitHub repository must not include:

- staff names;
- staff email addresses;
- real module-owner assignments;
- real moderator assignments;
- identifiable institutional module records;
- private Microsoft Lists or SharePoint links;
- exports containing operational data;
- screenshots containing personal or confidential information.

The public documentation records only:

- the List structure;
- field configurations;
- controlled values;
- anonymised validation outcomes;
- identified design limitations.

Operational data remain within the approved institutional Microsoft 365 environment.

## 14. Current limitations

The current prototype has the following limitations:

1. `Programme` and `Delivery Period` are not retrieved as additional lookup fields because they are stored as Choice columns in `MAP_Module_Catalogue`.
2. The multiple-owner field records co-ownership but does not distinguish semester-specific responsibilities.
3. Conditional requirements are not yet enforced through Power Apps.
4. `Owner Declaration` is not yet automatically linked to `Submission Status`.
5. Assessment-component details are not stored in this List.
6. Assessment release, submission and feedback dates are not stored in this List.
7. Workflow permissions, notifications and automated reminders have not yet been implemented.
8. Programme-, pathway- and stage-level cohort mappings have not yet been integrated.

## 15. Next steps

1. Complete the remaining module-plan validation tests.
2. Create the `MAP_Assessments` Microsoft List.
3. Link each assessment record to one annual module plan.
4. Store one assessment component per row.
5. Add assessment number, title, type and weighting.
6. Add predicted release, submission and feedback dates.
7. Represent formal examinations consistently.
8. Add assessment-specific quality-assurance fields.
9. Validate that assessment weightings total 100%.
10. Validate the order of release, submission and feedback dates.
11. Compare the assessment export with the target Assessment Pivot structure.
12. Evaluate Power Apps for the module-owner data-entry interface.
13. Evaluate Power Automate for workflow status, reminders and initial validation.
14. Prepare the structured records for later deterministic and agent-based deconfliction.