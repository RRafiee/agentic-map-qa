## 12. BSc Computer Science Pilot Mapping Implementation

The first programme mapping pilot has now been implemented in the
`MAP_Programme_Module_Mapping` SharePoint list for BSc Computer Science.

A dedicated public SharePoint view was created:

`BSc Computer Science Mapping`

The view:

- filters records to `Pathway Name = BSc Computer Science`;
- groups records by `Stage`;
- sorts module records by module code;
- supports inspection of Levels 1–3 and placement mappings.

### Level 1

Eight Level 1 module mappings were added.

Core modules:

- CSC1026 — Fundamentals of Maths for Computing
- CSC1032 — Introduction to Cyber Security
- CSC1033 — Introduction to Computer Architecture
- CSC1036 — Digital Futures: AI, Data and Responsible Technology

Conditional route modules:

**With SSD or equivalent**

- CSC1027 — Programming
- CSC1035 — Introduction to Embedded Systems

**Without SSD or equivalent**

- CSC1025 — Procedural Programming
- CSC1029 — Object Oriented Programming

The common cohort identifier is:

`BSC-CS-L1`

Conditional modules use route-specific Selection Group IDs:

- `BSC-CS-L1-SSD`
- `BSC-CS-L1-NONSSD`

### Level 2

The Level 2 mapping includes four core modules:

- CSC2058 — Software Engineering and Systems Development
- CSC2059 — Data Structures and Algorithms
- CSC2060 — Theory of Computation
- CSC2065 — Professional and Transferrable Skills

Students choose one module from:

- CSC2056 — Systems Security and Cryptography
- CSC2062 — Introduction to AI and Machine Learning
- CSC2066 — Networks and Protocols

These optional modules use:

`Selection Group ID = BSC-CS-L2-OPT1`

with:

`Selection Minimum = 1`

`Selection Maximum = 1`

The common Level 2 cohort identifier is:

`BSC-CS-L2`

### Placement

CSC2034 — Year of Professional Experience was recorded separately as a
placement mapping.

The verified module information is:

- Credits: 120 CATS
- Duration: 24 weeks
- Stage: Placement
- Cohort Key: `BSC-CS-PLACEMENT`
- Pathway Code: `CSC-BSC-P`
- Delivery Period: Placement
- Include in Deconfliction: No

The placement module is listed under Level 2 in the official pathway
documentation because it follows Stage 2, but it represents the separate
professional placement year.

### Level 3

The Level 3 mapping includes:

Core:

- CSC3002 — Computer Science Project / Data Science Project — 40 CATS

Optional modules:

- CSC3001
- CSC3021
- CSC3056
- CSC3058
- CSC3059
- CSC3064
- CSC3065
- CSC3066
- CSC3067

The common Level 3 cohort identifier is:

`BSC-CS-L3`

The optional modules use:

`Selection Group ID = BSC-CS-L3-OPT1`

Selection Minimum and Selection Maximum are currently left blank because
the official pathway documentation states that students select remaining
modules to reach 120 CATS rather than expressing the requirement as a
simple fixed-number selection rule.

### Mapping ID Convention

The implementation uses underscores rather than pipe characters.

Format:

`AcademicYear_ProgrammeKey_Level_ModuleCode_RequirementType`

Examples:

`2026-27_BSC-CS_L1_CSC1026_CORE`

`2026-27_BSC-CS_L2_CSC2062_OPTIONAL`

`2026-27_BSC-CS_L3_CSC3002_CORE`

`2026-27_BSC-CS_PLACEMENT_CSC2034_PLACEMENT`

This convention was selected to simplify later use in Power Apps,
Power Automate, APIs and programmatic processing.

### Audit Source

BSc Computer Science mappings use:

`Source Page = 3`

corresponding to the BSc Computer Science page of the approved EEECS
Pathways 2026/27 document.

---

## 13. Revised Next Development Step

The original pilot plan proposed proceeding directly from BSc Computer
Science to the Programme Cohort / APD mapping layer.

Following further consideration of the operational deconfliction process,
the implementation sequence has been revised.

Assessment deconfliction must operate across all students within a stage
while respecting programme/pathway membership. Therefore, a single-programme
mapping is not sufficient for the first operational deconfliction test.

The next development step is:

1. complete the Level 1 programme–module mappings across all relevant
   undergraduate pathways;
2. represent shared, conditional and pathway-specific Level 1 module
   membership;
3. identify INTO/external Level 1 mappings where information is available;
4. validate the complete Stage 1 knowledge base;
5. create the Programme Cohort / Associate Programme Director mapping layer;
6. connect submitted MAP assessments to the Stage 1 cohort mappings;
7. perform the first stage-wide assessment deconfliction prototype.

This approach ensures that the first deconfliction test is student-centric
and reflects the actual shared-module structure across EEECS pathways.