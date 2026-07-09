# Power Apps Readiness Gate Pilot Test

## Purpose

This document records the pilot test framework for the Power Apps submission-readiness gate.

The test checks whether the Power Apps submit-button behaviour matches the expected readiness outcome for the five representative pilot records in:

- `MAP_Module_Plans_Pilot_2026_27`

## Background

The readiness gate uses the Microsoft Lists field:

- `Submission Readiness Status`

The purpose of the gate is to allow direct submission only when a module plan is marked as ready.

The implementation steps were documented in:

- `docs/24-power-apps-readiness-gate-implementation-steps.md`

## Scope

This test is limited to the five representative pilot records:

- `PILOT101`
- `PILOT102`
- `PILOT103`
- `PILOT104`
- `PILOT105`

The test checks the Power Apps submit-button behaviour against the expected readiness status for each record.

## Fields Used

| Field | Purpose |
|---|---|
| `Submission Readiness Status` | Controls whether direct submission is allowed. |
| `Submission Readiness Notes` | Provides the reason or supporting explanation when QA review is recommended. |

## Expected Behaviour

| Plan Reference | Submission Readiness Status | Expected Power Apps Behaviour |
|---|---|---|
| `PILOT101` | `Ready to submit` | Submit button enabled |
| `PILOT102` | `Ready to submit` | Submit button enabled |
| `PILOT103` | `Ready to submit` | Submit button enabled |
| `PILOT104` | `Ready to submit` | Submit button enabled |
| `PILOT105` | `Warning - QA review recommended` | Direct final submission prevented; QA review message shown |

## Test Procedure

The following manual test procedure should be applied in Power Apps:

1. Open the Power Apps interface connected to `MAP_Module_Plans_Pilot_2026_27`.
2. Open or select each representative pilot record.
3. Check the value shown in `Submission Readiness Status`.
4. Check the submit-button behaviour.
5. Confirm that records marked `Ready to submit` allow direct submission.
6. Confirm that records marked `Warning - QA review recommended` do not allow direct final submission.
7. Confirm that a clear QA review or readiness warning message is shown for the warning record.

## Observed Results

| Plan Reference | Expected Power Apps Behaviour | Observed Power Apps Behaviour |
|---|---|---|
| `PILOT101` | Submit button enabled | To be confirmed |
| `PILOT102` | Submit button enabled | To be confirmed |
| `PILOT103` | Submit button enabled | To be confirmed |
| `PILOT104` | Submit button enabled | To be confirmed |
| `PILOT105` | Direct final submission prevented; QA review message shown | To be confirmed |

## Review Message Check

For `PILOT105`, the app should show a clear message similar to:

```text
This module plan is not ready for direct submission. Please review the Submission Readiness Notes and complete the required QA review before submitting.
```

The exact wording may be adjusted in Power Apps, but the message should clearly explain that QA review is required before final submission.

## Expected Outcome

The Power Apps readiness gate should behave as follows:

- Records marked `Ready to submit` should allow direct submission.
- Records marked `Warning - QA review recommended` should prevent direct final submission.
- The user should be directed to review `Submission Readiness Notes` when QA review is recommended.

## Relationship to Previous Documentation

This document follows:

- `docs/20-power-apps-submit-button-logic.md`
- `docs/23-power-apps-submit-button-readiness-test.md`
- `docs/24-power-apps-readiness-gate-implementation-steps.md`

## Outcome

The pilot test framework for the Power Apps readiness gate has been defined.

The observed results should be updated after the pilot records are tested in the Power Apps interface.
