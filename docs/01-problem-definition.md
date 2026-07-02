# Problem Definition

**Project:** Agentic MAP-QA
**Document version:** 0.1
**Status:** Initial definition

## 1. Overview

Module Assessment Planning (MAP) is a policy-constrained organisational workflow in which assessment information must be collected, validated, deconflicted and transformed into a reliable calendar for students and staff.

The process requires more than storing assessment dates. It involves validating structured information, identifying missing or inconsistent entries, detecting workload pressure across shared student cohorts, applying institutional rules and supporting human negotiation when changes may be needed.

The Agentic MAP-QA project investigates how a verifier-grounded agentic AI system can support this workflow while preserving human responsibility for final academic and operational decisions.

## 2. Current Problem

The current workflow depends substantially on spreadsheets, manual checking and communication between quality-assurance staff, programme representatives and module owners.

The principal challenges include:

* assessment information may be incomplete, inconsistent or entered in different formats;
* module-level assessment components must be checked for valid dates, weighting and sequencing;
* assessment pressure must be analysed according to shared pathway and academic stage rather than across a single global calendar;
* large or high-weight assessments scheduled close together may create workload pressure for the same student cohort;
* relevant policy and guidance must be identified and applied consistently;
* resolving conflicts requires communication and negotiation with module owners;
* decisions, exceptions and approved changes require an auditable record;
* the final output must be converted into a clean, calendar-ready dataset.

These activities are time-consuming and can be difficult to perform consistently across a large number of modules and assessment components.

## 3. Limitations of a Purely LLM-Based Approach

A general-purpose large language model should not be used as the sole decision-maker for this workflow.

Tasks such as calculating assessment weight totals, comparing dates, identifying missing values and detecting deadline collisions require deterministic and reproducible validation. An LLM may provide useful explanations and recommendations, but it can produce inconsistent results when used for calculations or policy enforcement without external verification.

The system should therefore combine:

1. structured assessment data;
2. deterministic validation rules;
3. policy retrieval and evidence grounding;
4. tool-using agentic workflows;
5. human review and approval;
6. complete audit records.

## 4. System Objective

The initial objective is to develop a verifier-grounded agentic AI system that can:

* ingest structured module assessment plans;
* normalise assessment information into one record per assessment component;
* detect missing, malformed or inconsistent data;
* validate assessment dates and weighting;
* map modules to relevant pathways and academic stages;
* identify potential assessment-pressure points for shared student cohorts;
* retrieve relevant policy or guidance;
* explain why an assessment plan has been flagged;
* recommend possible actions or alternative scheduling windows;
* prepare draft communications for human review;
* produce a validated, calendar-ready output;
* record decisions, exceptions and approval status.

The system will provide decision support rather than autonomous institutional decision-making.

## 5. Initial Case-Study Boundary

The first implementation will focus on the module assessment planning stage:

```text
Assessment-plan submission
        ↓
Data normalisation
        ↓
Deterministic validation
        ↓
Pathway and stage mapping
        ↓
Assessment-pressure analysis
        ↓
Policy-grounded explanation
        ↓
Human review and resolution
        ↓
Calendar-ready export
```

Monitoring actual assessment release, submission and feedback dates may be introduced in a later phase, but it is outside the initial implementation boundary.

## 6. In Scope

The initial system will cover:

* structured assessment records;
* data completeness checks;
* date-order validation;
* module assessment-weight validation;
* pathway- and stage-specific deadline analysis;
* same-day and near-date conflict detection;
* assessment-pressure scoring;
* policy-grounded explanations;
* human approval and escalation;
* calendar-ready data export;
* audit logging.

## 7. Out of Scope

The initial system will not:

* make final decisions on behalf of academic staff;
* automatically change assessment dates;
* send communications without human approval;
* access student-level personal data;
* assess the academic quality of assessment content;
* replace programme or quality-assurance governance;
* treat an LLM response as authoritative policy;
* expose confidential institutional data in the public repository.

## 8. Expected Outputs

The first operational outputs are expected to include:

1. a clean assessment-level master dataset;
2. a missing-data and validation report;
3. pathway- and stage-specific assessment-pressure summaries;
4. a list of high-priority scheduling risks;
5. evidence-grounded explanations and recommended actions;
6. an auditable record of human decisions;
7. a calendar-ready spreadsheet export.

## 9. Research Motivation

The project will also provide an experimental environment for investigating reliable agentic AI in policy-constrained workflows.

Potential research questions include:

* Can deterministic verifiers improve the reliability of tool-using LLM agents?
* Can policy-grounded retrieval reduce unsupported recommendations?
* Can an adaptive agent harness improve performance over a fixed agent harness?
* Can in-context reinforcement learning improve tool selection and multi-step task completion?
* How well does the system generalise to unseen modules, policies and workflow constraints?
* What trade-offs exist between task accuracy, policy compliance, latency, cost and human intervention?

The module assessment planning workflow is therefore treated as an applied benchmark for agentic AI methodology rather than as the sole research contribution.

## 10. Data Governance

The public repository will contain only synthetic, anonymised or openly licensed material.

Real institutional workbooks, staff information, internal comments, credentials and restricted policy documents will remain outside version control. Private data will be stored only in ignored local directories and will not be committed to the repository.

## 11. Initial Success Criteria

The first implementation will be considered successful when it can:

* transform a structured input workbook into a valid assessment-level dataset;
* identify known missing-data and date-validation errors;
* detect predefined pathway-stage scheduling conflicts;
* produce reproducible rule-based results;
* provide policy-grounded explanations for flagged cases;
* generate a calendar-ready output;
* preserve a human approval point before any operational action;
* maintain an auditable execution record.
