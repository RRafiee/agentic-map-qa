# MAP Programme–Module Mapping Knowledge Base

## 1. Purpose

The `MAP_Programme_Module_Mapping` SharePoint list provides the programme, pathway, stage and module knowledge base required by the MAP assessment deconfliction system.

The list connects each undergraduate module with the student cohorts that may take it. It also records whether the module is core, compulsory, optional, conditional, placement-related or externally delivered.

This structured mapping will allow the future Assessment Deconfliction Agent to determine whether two assessments affect the same student cohort before analysing the proximity of their submission dates.

---

## 2. SharePoint List

**List name:**

`MAP_Programme_Module_Mapping`

**Description:**

Knowledge base mapping undergraduate modules to programme pathways, stages and module-selection rules for the MAP assessment deconfliction system.

The list is designed to support multiple academic years through the `Academic Year` column. Existing production MAP list names will remain unchanged while the 2026/27 submission process is live.

---

## 3. Data Model

Each list item represents one relationship between:

- an academic year;
- a programme pathway;
- a stage of study; and
- a module.

The same module may therefore appear in multiple records when it is delivered across several programmes or stages.

Example:

| Academic Year | Pathway | Stage | Module |
|---|---|---|---|
| 2026/27 | BSc Computer Science | Level 2 | CSC2059 |
| 2026/27 | BSc Data Science | Level 2 | CSC2059 |
| 2026/27 | MEng Computer Engineering | Level 2 | CSC2059 |

---

## 4. SharePoint Columns

| Column | Type | Required | Purpose |
|---|---|---:|---|
| Mapping ID | Single line of text | Yes | Unique identifier for the mapping record. This is the renamed default SharePoint `Title` column. |
| Academic Year | Choice | Yes | Academic year to which the mapping applies. Initial value: `2026/27`. |
| Programme Key | Single line of text | Yes | Short standard identifier for the programme, such as `BSC-CS`. |
| Pathway Code | Single line of text | Yes | Official pathway code used in the EEECS pathway documentation and student records. |
| Pathway Name | Single line of text | Yes | Full official programme pathway name. |
| Stage | Choice | Yes | Stage of study: Level 1, Level 2, Level 3, Level 4 or Placement. |
| Cohort Key | Single line of text | Yes | Identifier representing a specific pathway and stage, such as `BSC-CS-L2`. |
| Module Code | Single line of text | Yes | Official module code used to connect the mapping with MAP module and assessment records. |
| Module Title | Single line of text | Yes | Official module title for display and reporting. |
| Requirement Type | Choice | Yes | Indicates whether the module is Core, Compulsory, Optional, Conditional, Placement or External/INTO. |
| Selection Group ID | Single line of text | No | Groups modules governed by the same optional or conditional selection rule. |
| Selection Minimum | Number | No | Minimum number of modules students must select from a selection group. |
| Selection Maximum | Number | No | Maximum number of modules students may select from a selection group. |
| Route Condition | Single line of text | No | Entry or pathway condition, such as `With SSD or equivalent`. |
| CATS | Number | Yes | Module credit value. |
| Delivery Period | Choice | Yes | Semester 1, Semester 2, Full Year, Summer, Placement or External/Unknown. |
| Include in Deconfliction | Yes/No | Yes | Determines whether the mapping should be included in assessment conflict analysis. Default: Yes. |
| Source Page | Number | Yes | Page number in the approved EEECS Pathways document used as the source. |
| Active | Yes/No | Yes | Indicates whether the mapping is currently valid. Default: Yes. |
| Notes | Multiple lines of text | No | Additional exceptions, dependencies, co-requisites or special conditions. |

---

## 5. Choice Values

### 5.1 Stage

- Level 1
- Level 2
- Level 3
- Level 4
- Placement

Level 0 is currently excluded because Foundation Year modules are delivered by INTO and the individual module mappings are not identified in the EEECS pathway document. It may be added later if the relevant data become available.

### 5.2 Requirement Type

- Core
- Compulsory
- Optional
- Conditional
- Placement
- External / INTO

`Core` and `Compulsory` are retained separately to preserve the terminology used in the official pathway documentation, although both normally indicate definite cohort membership for deconfliction.

### 5.3 Delivery Period

- Semester 1
- Semester 2
- Full Year
- Summer
- Placement
- External / Unknown

`Summer` is included because CSC1038 is delivered as a summer module for the Software Engineering HLA pathway. This field describes module delivery and does not alter the assessment-period choices in the live MAP Submission App.

---

## 6. Identifier Conventions

### 6.1 Mapping ID

Recommended format:

`AcademicYear|ProgrammeKey|Stage|ModuleCode|RequirementType`

Example:

`2026-27|BSC-CS|L2|CSC2059|CORE`

### 6.2 Programme Key

Examples:

- `BSC-CS`
- `MENG-CS`
- `BENG-SE`
- `MENG-SE`
- `BSC-CIT`
- `BSC-BIT`
- `BSC-DS`
- `BENG-EEE`
- `MENG-EEE`
- `BENG-CE`
- `MENG-CE`

### 6.3 Cohort Key

Recommended format:

`ProgrammeKey-Level`

Examples:

- `BSC-CS-L1`
- `BSC-CS-L2`
- `BSC-CS-L3`
- `MENG-CS-L4`
- `BENG-SE-L3`
- `BSC-DS-L2`

The same Cohort Key is repeated for every module belonging to that programme and stage.

### 6.4 Selection Group ID

Recommended format:

`ProgrammeKey-Level-Group`

Examples:

- `BSC-CS-L2-OPT1`
- `MENG-CS-L3-OPT1`
- `BSC-CS-L1-SSD`
- `BSC-CS-L1-NONSSD`

---

## 7. Selection-Rule Examples

### 7.1 Choose One Module

For a pathway where students choose one module from CSC2056, CSC2062 and CSC2066:

| Field | Value |
|---|---|
| Selection Group ID | `BSC-CS-L2-OPT1` |
| Selection Minimum | 1 |
| Selection Maximum | 1 |

The same values are entered against all three module-mapping records.

### 7.2 Choose Three Modules

For a selection group requiring three modules:

| Field | Value |
|---|---|
| Selection Minimum | 3 |
| Selection Maximum | 3 |

### 7.3 At Least One Module

Where students must choose at least one module but may choose more:

| Field | Value |
|---|---|
| Selection Minimum | 1 |
| Selection Maximum | Blank |

### 7.4 Conditional Entry Routes

For standard Level 1 computing pathways:

**With SSD or equivalent**

- CSC1027
- CSC1035

**Without SSD or equivalent**

- CSC1025
- CSC1029

These records must use the appropriate `Route Condition` and should not be treated as modules taken by every student.

---

## 8. Deconfliction Interpretation

The future deconfliction system will use the mapping as follows:

| Relationship | Initial interpretation |
|---|---|
| Core–Core or Compulsory–Compulsory | Definite cohort overlap |
| Core–Optional | Potential cohort overlap |
| Optional–Optional | Potential overlap unless selection rules exclude it |
| Modules in the same choose-one group | Mutually exclusive within that pathway |
| Conditional routes | Overlap depends on the recorded route condition |
| Placement or external modules | Excluded unless they contain relevant summative assessments |
| Inactive mappings | Excluded |
| Include in Deconfliction = No | Excluded |

The actual assessment dates submitted through the MAP system will be used for conflict detection. Module Delivery Period is supporting information only.

---

## 9. Annual Reuse

The list is not restricted to 2026/27. Future mappings will be added using the Academic Year column.

The expected annual rollover process is:

1. copy the previous academic year’s mappings;
2. create draft records for the new year;
3. update changed pathways and modules;
4. validate against the approved pathway documentation;
5. mark obsolete mappings as inactive;
6. confirm the new mapping dataset before deconfliction begins.

Historical records must not be overwritten because they will support audit, evaluation and year-on-year analysis.

---

## 10. Data Source

The initial mappings are derived from:

**EEECS Pathways 2026–27 — Staff Only Copy**

The `Source Page` field provides an audit reference to the relevant pathway page.

Official module titles should be checked against the MAP Module Catalogue where possible.

---

## 11. Current Implementation Status

Completed:

- SharePoint list created;
- initial list description added;
- Mapping ID column established;
- all programme–module mapping columns created;
- choice values and defaults configured;
- multi-year design retained through the Academic Year column.

Not yet completed:

- creation of list views;
- population of pathway records;
- validation of programme and cohort identifiers;
- connection to Power Apps;
- connection to MAP Assessments;
- conflict-detection logic;
- Associate Programme Director review workflow;
- Deconfliction Agent implementation.

---

## 12. Next Development Step

The next step is to populate and validate one complete pathway as a controlled pilot:

**BSc Computer Science — Levels 1, 2 and 3**

This pilot will include:

- standard core modules;
- SSD and non-SSD conditional routes;
- Level 2 optional selection groups;
- Level 3 optional modules;
- full-year modules;
- pathway and cohort identifiers;
- source-page references.

The pilot mapping will then be tested against the MAP assessment submissions already received.