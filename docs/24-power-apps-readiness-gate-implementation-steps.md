# Power Apps Readiness Gate Implementation Steps

## Purpose

This document defines the practical implementation steps for applying the MAP-QA submission-readiness gate in Power Apps.

The readiness gate will use the Microsoft Lists field:

- `Submission Readiness Status`

The purpose is to ensure that a module plan can only proceed to direct final submission when it is marked as ready.

## Background

The MAP-QA pilot workflow has already introduced and tested two Microsoft Lists fields in `MAP_Module_Plans_Pilot_2026_27`:

| Field | Purpose |
|---|---|
| `Submission Readiness Status` | Indicates whether the module plan is ready for submission or requires QA review. |
| `Submission Readiness Notes` | Provides supporting notes explaining any warning or review condition. |

The expected submit-button behaviour was documented in:

- `docs/23-power-apps-submit-button-readiness-test.md`

This document now defines the implementation steps needed to apply that behaviour in Power Apps.

## Scope

This document covers the planned Power Apps implementation sequence only.

It does not confirm that the Power Apps interface has already been updated or deployed.

The implementation should be tested separately after the button logic has been added to the app.

## Implementation Steps

### Step 1: Identify the submission screen

Locate the Power Apps screen that contains the module-plan submission button.

This is the screen where a module owner or relevant user would submit a completed MAP record for review or final processing.

### Step 2: Confirm the data source connection

Confirm that the Power Apps app is connected to the Microsoft Lists data source:

- `MAP_Module_Plans_Pilot_2026_27`

The app must be able to read the following fields:

- `Submission Readiness Status`
- `Submission Readiness Notes`

### Step 3: Connect the submit button to readiness status

The submit button should use `Submission Readiness Status` as the controlling field.

The basic rule is:

```text
If Submission Readiness Status = "Ready to submit"
    Allow direct submission
Else
    Prevent direct final submission
```

### Step 4: Enable submission for ready records

For records where `Submission Readiness Status` is `Ready to submit`, the submit button should be enabled.

Expected behaviour:

- The user can proceed with submission.
- No QA warning message is required.
- The submission action can continue to the next workflow stage.

### Step 5: Prevent direct submission for warning records

For records where `Submission Readiness Status` is `Warning - QA review recommended`, the submit button should not allow direct final submission.

Expected behaviour:

- The user should not be able to submit directly.
- The app should show a clear warning message.
- The user should be directed to review `Submission Readiness Notes`.
- The record should require QA review before final submission.

### Step 6: Display a readiness message

When the record is not ready for direct submission, the app should display a message such as:

```text
This module plan is not ready for direct submission. Please review the Submission Readiness Notes and complete the required QA review before submitting.
```

The message should be visible enough for the user to understand why submission is blocked or delayed.

### Step 7: Keep the logic aligned with pilot records

The implementation should remain aligned with the five representative pilot records:

| Plan Reference | Submission Readiness Status | Expected Power Apps Behaviour |
|---|---|---|
| `PILOT101` | `Ready to submit` | Submit button enabled |
| `PILOT102` | `Ready to submit` | Submit button enabled |
| `PILOT103` | `Ready to submit` | Submit button enabled |
| `PILOT104` | `Ready to submit` | Submit button enabled |
| `PILOT105` | `Warning - QA review recommended` | Direct final submission prevented; QA review recommended |

## Suggested Power Apps Formula

The following formula can be used as a future implementation reference for the submit button `DisplayMode` property:

```powerfx
If(
    ThisItem.'Submission Readiness Status'.Value = "Ready to submit",
    DisplayMode.Edit,
    DisplayMode.Disabled
)
```

A supporting warning-message visibility rule could be:

```powerfx
If(
    ThisItem.'Submission Readiness Status'.Value <> "Ready to submit",
    true,
    false
)
```

These formulas are included as implementation guidance. They should be checked against the final Power Apps data structure because the exact syntax may depend on whether the field is stored as a Choice, Text, or calculated value.

## Expected Outcome

After implementation, Power Apps should use `Submission Readiness Status` as the controlling field for the submit-button readiness gate.

Records marked `Ready to submit` should allow direct submission.

Records marked `Warning - QA review recommended` should prevent direct final submission and direct the user to review `Submission Readiness Notes`.

## Relationship to Previous Documentation

This document follows:

- `docs/19-module-plan-submission-readiness-gate.md`
- `docs/20-power-apps-submit-button-logic.md`
- `docs/21-submission-readiness-status-field.md`
- `docs/22-submission-readiness-fields-manual-test.md`
- `docs/23-power-apps-submit-button-readiness-test.md`

## Outcome

The planned Power Apps readiness gate implementation steps have been defined.

This provides a clear implementation bridge between the Microsoft Lists readiness fields and the future Power Apps submit-button behaviour.
