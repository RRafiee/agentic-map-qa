# Power Apps Readiness Gate All Pilot Records Test

## Purpose

This document records the test of the implemented Power Apps readiness gate across all five representative pilot records in:

- `MAP_Module_Plans_Pilot_2026_27`

The purpose of this test is to confirm that the customised SharePoint/Power Apps form save action behaves correctly for both ready records and records requiring QA review.

## Background

The Power Apps readiness gate was implemented in the customised SharePoint form using:

- `SharePointIntegration.OnSave`

The gate uses the Microsoft Lists field:

- `Submission Readiness Status`

The supporting field is:

- `Submission Readiness Notes`

The implementation result was previously documented in:

- `docs/27-power-apps-readiness-gate-implementation-result.md`

Initial testing confirmed that:

- `PILOT101`, marked `Ready to submit`, saved successfully.
- `PILOT105`, marked `Warning - QA review recommended`, was blocked and showed the warning message.

This document extends the test to all five representative pilot records.

## Scope

This test is limited to the five representative pilot records:

- `PILOT101`
- `PILOT102`
- `PILOT103`
- `PILOT104`
- `PILOT105`

The test checks the implemented save-action readiness gate only.

It does not change the readiness logic, Microsoft Lists field structure, or Power Apps formula.

## Readiness Gate Logic

The implemented readiness gate allows the save action only when:

- `Submission Readiness Status` = `Ready to submit`

For all other readiness statuses, the save action is blocked and a warning message is shown.

## Pilot Records Tested

| Pilot Record | Submission Readiness Status | Expected Save Behaviour |
|---|---|---|
| `PILOT101` | `Ready to submit` | Save allowed |
| `PILOT102` | `Ready to submit` | Save allowed |
| `PILOT103` | `Ready to submit` | Save allowed |
| `PILOT104` | `Ready to submit` | Save allowed |
| `PILOT105` | `Warning - QA review recommended` | Save blocked and warning message shown |

## Test Procedure

For each pilot record, the following procedure was used:

1. Opened the record from `MAP_Module_Plans_Pilot_2026_27`.
2. Confirmed that the record opened in the customised SharePoint/Power Apps form.
3. Checked the value of `Submission Readiness Status`.
4. Attempted to save the form without making unnecessary data changes.
5. Recorded whether the save action was allowed or blocked.
6. For `PILOT105`, checked whether the warning message was shown.

## Observed Results

| Pilot Record | Submission Readiness Status | Expected Behaviour | Observed Result |
|---|---|---|---|
| `PILOT101` | `Ready to submit` | Save allowed | Save allowed |
| `PILOT102` | `Ready to submit` | Save allowed | Save allowed |
| `PILOT103` | `Ready to submit` | Save allowed | Save allowed |
| `PILOT104` | `Ready to submit` | Save allowed | Save allowed |
| `PILOT105` | `Warning - QA review recommended` | Save blocked and warning message shown | Save blocked and warning message shown |

## Warning Message Observed

For `PILOT105`, the following warning message was shown:

```text
This module plan is not ready for direct submission. Please review the Submission Readiness Notes before submitting.
```

This confirms that the implemented readiness gate blocks records where QA review is recommended.

## Outcome

The Power Apps readiness gate behaved as expected across all five representative pilot records.

The test confirmed that:

- `PILOT101` saved successfully.
- `PILOT102` saved successfully.
- `PILOT103` saved successfully.
- `PILOT104` saved successfully.
- `PILOT105` was blocked and showed the warning message.

This confirms that the `Submission Readiness Status` field is successfully controlling the customised SharePoint/Power Apps form save action.

## Relationship to Previous Documentation

This document follows:

- `docs/23-power-apps-submit-button-readiness-test.md`
- `docs/24-power-apps-readiness-gate-implementation-steps.md`
- `docs/25-power-apps-readiness-gate-pilot-test.md`
- `docs/26-microsoft-lists-power-apps-readiness-test-view.md`
- `docs/27-power-apps-readiness-gate-implementation-result.md`
