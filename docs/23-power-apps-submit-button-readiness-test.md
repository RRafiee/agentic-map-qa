# Power Apps Submit-Button Readiness Test

## Purpose

This document records the expected Power Apps submit-button behaviour based on the `Submission Readiness Status` field in the Microsoft Lists pilot list:

- `MAP_Module_Plans_Pilot_2026_27`

The test follows the manual Microsoft Lists readiness-field check documented in:

- `docs/22-submission-readiness-fields-manual-test.md`

## Background

The MAP-QA pilot workflow includes a submission-readiness gate to prevent incomplete or review-required module plans from being submitted without appropriate checking.

The relevant Microsoft Lists fields are:

| Field | Purpose |
|---|---|
| `Submission Readiness Status` | Indicates whether the module plan is ready for submission or requires QA review. |
| `Submission Readiness Notes` | Provides supporting notes explaining any warning or review condition. |

This document defines how the Power Apps submit button should respond to those fields.

## Pilot Records Tested

The test is limited to the five representative pilot records:

- `PILOT101`
- `PILOT102`
- `PILOT103`
- `PILOT104`
- `PILOT105`

## Expected Submit-Button Behaviour

| Plan Reference | Submission Readiness Status | Expected Submit-Button Behaviour |
|---|---|---|
| `PILOT101` | `Ready to submit` | Submit button enabled. The user can proceed with submission. |
| `PILOT102` | `Ready to submit` | Submit button enabled. The user can proceed with submission. |
| `PILOT103` | `Ready to submit` | Submit button enabled. The user can proceed with submission. |
| `PILOT104` | `Ready to submit` | Submit button enabled. The user can proceed with submission. |
| `PILOT105` | `Warning - QA review recommended` | Submit button should not allow direct final submission without QA review. |

## Behaviour Rule

The expected button logic is:

```text
If Submission Readiness Status = "Ready to submit"
    Enable submission
Else if Submission Readiness Status = "Warning - QA review recommended"
    Prevent direct final submission and show a QA review message
Else
    Prevent submission and show a readiness incomplete message