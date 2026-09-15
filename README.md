# Agentic MAP-QA

## A Verifier-Grounded Multi-Agent AI System for Policy-Constrained Assessment Planning

<p align="center">
  <img
    src="docs/assets/map_qa_multi_agent_architecture.png"
    alt="Architecture diagram of the MAP-QA verifier-grounded multi-agent system showing data sources, deterministic agents, validation and governance checks, APD human-in-the-loop review, optional Gemini/RAG advisory layer, and final QA/calendar outputs"
    width="900">
</p>

<p align="center">
  <em>
    Figure 1. MAP-QA multi-agent architecture. Structured Power Apps and SharePoint MAP records are processed through deterministic readiness, cohort-mapping, conflict-detection, deconfliction and validation agents before APD-led human review. The optional Gemini/RAG layer is advisory only and supports explanation, critique and communication drafting without autonomous calculation, approval, publication or email sending.
  </em>
</p>


This repository contains the working implementation of **Agentic MAP-QA**, a verifier-grounded **multi-agent system** for Module Assessment Planning (MAP) quality assurance, assessment deconfliction, and calendar-readiness checking.

The system supports the 2026/27 MAP process in the School of Electronics, Electrical Engineering and Computer Science (EEECS), Queen’s University Belfast. It combines deterministic data validation, programme-cohort mapping, calendar-rule checks, APD review packs, and human-in-the-loop academic decision-making.

The system does **not** automatically approve, publish, or change assessment dates. It produces evidence-based outputs for APDs, module owners, and QA review.

---

## Core idea

Agentic MAP-QA is designed as a **multi-agent QA workflow** rather than a single script. Each agent performs a clearly bounded role and produces auditable intermediate outputs.

The approach is:

1. Validate raw MAP data.
2. Map assessments to affected programme-stage cohorts.
3. Detect cohort-level assessment pressure.
4. Apply calendar and policy constraints.
5. Generate APD-specific review evidence.
6. Validate generated outputs.
7. Support final human APD/module-owner decisions.

---

## Multi-agent system architecture

| Agent / Component | Role |
|---|---|
| Data Readiness Agent | Checks raw MAP exports for missing fields, date issues, feedback timing, assessment counts, and approved exceptions. |
| Assessment Board Agent | Creates assessment-board style views by submission date, same-day pressure, near-date pressure, and feedback warnings. |
| Programme-Cohort Mapping Agent | Links modules and assessments to programme-stage cohorts using the MAP programme-module mapping list. |
| Deconfliction Case Builder Agent | Creates APD-ready date deconfliction cases, calendar warnings, feedback warnings, unmapped cases, and assessment-only/manual review cases. |
| Validation Agent | Checks APD-facing outputs for UK date format, blocked dates, release-date safety, and stale APD routing files. |
| Human APD / Module Owner Review | Final human-in-the-loop stage where APDs liaise with module owners and record agreed actions. |

This design keeps the workflow **verifier-grounded**: each step is traceable, deterministic, and reviewable.

---

## Current workflow

```text
Raw MAP exports
    ↓
Data Readiness Agent
    ↓
Assessment Board Agent
    ↓
Programme-Cohort Mapping Agent
    ↓
Deconfliction Case Builder Agent
    ↓
Validation Agent
    ↓
APD live review workbook
    ↓
Final QA check
    ↓
EEECS Assessment Calendar preparation
```

---

## Main scripts

| Script | Purpose |
|---|---|
| `src/agents/data_readiness_agent/data_readiness_agent.py` | Performs core MAP data readiness checks. |
| `src/agents/data_readiness_agent/create_assessment_board.py` | Creates assessment-board and pressure-summary outputs. |
| `src/agents/programme_cohort_mapping_agent.py` | Expands assessments into affected programme-stage cohort rows. |
| `src/agents/create_deconfliction_cases.py` | Builds APD-ready deconfliction and review outputs. |
| `src/agents/validate_deconfliction_outputs.py` | Validates APD-facing outputs before sharing. |
| `src/agents/inspect_deconfliction_cases.py` | Provides inspection summaries for manual QA review. |

---

## Output types

The workflow generates the following main output categories:

| Output | Purpose |
|---|---|
| `MAP_Deconfliction_Cases_Draft.csv` | Main same-day and near-date deconfliction cases. |
| `MAP_Calendar_Rule_Warnings.csv` | Calendar-rule issues such as Independent Study Week, weekend, or QUB closure dates. |
| `MAP_Feedback_Timing_Warnings.csv` | Feedback-return timing warnings. |
| `MAP_Unmapped_Calendar_Modules.csv` | Calendar-included modules not mapped to normal programme-stage cohorts. |
| `MAP_Assessment_Only_Manual_Cases.csv` | Assessment-only/manual review cases such as `CSC1034`. |
| `MAP_APD_Review_Pack.csv` | Combined APD review evidence pack. |
| `apd_review_packs/*.csv` | APD-specific review files. |

Generated outputs and operational workbooks should not be committed to GitHub.

---

## Severity model

| Severity | Meaning |
|---|---|
| Critical | Definite or very high-priority issue requiring immediate APD/module-owner review. |
| High | Important workload or calendar issue requiring APD sense-check. |
| Warning | Issue to review if time allows or where local judgement is needed. |
| Exception | Approved or manually handled case outside normal rule logic. |

---

## Calendar and policy constraints

The system checks assessment dates against MAP-relevant calendar constraints, including:

- Independent Study Weeks
- weekends
- QUB closure periods
- formal assessment period restrictions for alternative coursework/class-test suggestions
- feedback timing expectations
- release-date safety for suggested alternatives

Suggested alternative dates are generated only as decision support. APDs and module owners remain responsible for final academic judgement.

---

## APD live deconfliction workflow

For the 2026/27 MAP cycle, APDs use a shared live workbook in the Education folder:

```text
MAP_Assessment_Deconfliction_Working_2026_27_FIXED_UK_DATES.xlsx
```

APDs are asked to:

- open `Assessment_Plan_Working`
- filter by `APD Owner`
- review Critical, High and Calendar rule warning rows first
- liaise with module owners where needed
- record agreed outcomes in APD editable columns only
- avoid overwriting original predicted dates

The shared workbook is an operational working file and should not be committed to GitHub.

---

## Data governance

Do not commit:

```text
data/raw/
outputs/
*.csv generated from MAP exports
*.xlsx operational workbooks
local debug files
VS Code local settings
```

The repository should contain source code, configuration, documentation, and reusable validation logic only.

---

## Current status

As of 15 September 2026:

- v0.5 of `create_deconfliction_cases.py` is active.
- APD-facing dates use UK format: `DD/MM/YYYY`.
- Release-date-safe alternative suggestions are implemented.
- Data Science APD routing is assigned to Dr Neil Anderson for this MAP review.
- `CSC1034` is handled as an assessment-only/manual review case.
- Validation confirmed:
  - alternative dates before release date = 0
  - blocked alternative date issues = 0
  - stale Joseph APD files = 0
  - APD-specific files created = 7

---

## Research framing

Agentic MAP-QA demonstrates a practical, policy-constrained, verifier-grounded multi-agent system for academic quality assurance. It is designed to support transparent decision-making rather than replace human academic judgement.

