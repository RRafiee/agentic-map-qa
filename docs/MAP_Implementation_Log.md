# MAP Agentic QA System — Implementation Log

## Programme-Module Mapping Expansion

Date: 10 September 2026

The `MAP_Programme_Module_Mapping` list has been expanded from the initial BSc Computer Science pilot mapping to cover the main undergraduate deconfliction target areas:

- BSc Computer Science
- MEng Computer Science
- BEng Software Engineering
- MEng Software Engineering
- BSc Computing and Information Technology
- BSc Business Information Technology
- BSc Data Science
- BEng Electrical and Electronic Engineering
- MEng Electrical and Electronic Engineering
- BEng Computer Engineering
- MEng Computer Engineering

The mapping now follows a reusable Mapping ID convention that does not include the academic year. For example:

```text
BSC-CS_L3_CSC3067_OPTIONAL
MENG-CS_L4_CSC4006_CORE
BSC-DS_L3_CSC3066_CORE


## Operational Exceptions

Some deconfliction issues may arise outside the standard programme-stage mapping, for example HLA attendance constraints or students carrying modules across stages. These are not currently represented as standard mapping rules in the MAP Agentic QA system.

For the current version, such cases will be handled through APD and module-owner review rather than automated rule expansion. The system will continue to focus on normal programme-stage cohort deconfliction, with exceptional cases reviewed manually where required.


## 15 September 2026 – APD live deconfliction workflow

- Created v0.5 of `create_deconfliction_cases.py`.
- v0.5 keeps APD-facing dates in UK format (`DD/MM/YYYY`).
- Added release-date safeguard so suggested alternative submission dates are not earlier than the relevant predicted release date.
- Validated that:
  - alternative dates before release date = 0
  - blocked alternative date issues = 0
  - stale Joseph APD files = 0
  - APD-specific files created = 7
- Data Science APD routing is now Dr Neil Anderson for this MAP review.
- `CSC1034` is retained as an assessment-only/manual review case and is not included in normal L1 cohort deconfliction.
- A single shared live workbook was created for APD review and placed in the Education folder:
  `MAP_Assessment_Deconfliction_Working_2026_27_FIXED_UK_DATES.xlsx`
- The shared workbook is the operational working file for APDs. It should not be committed to GitHub.
- APDs were asked to filter `Assessment_Plan_Working` by APD Owner and review Critical, High and Calendar rule warning rows first.
- APDs should record agreed outcomes in the APD editable columns only, without overwriting the original predicted dates.
- APD deadline: Thursday 18 September before noon, to allow final QA checks and EEECS Calendar release in the afternoon.