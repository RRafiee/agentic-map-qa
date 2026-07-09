# Power Apps Readiness Gate Implementation Result

## Purpose

This document records the actual implementation result for the Power Apps readiness gate applied to the customised SharePoint form connected to:

- `MAP_Module_Plans_Pilot_2026_27`

The purpose of this implementation is to prevent records that are not ready from being saved or submitted directly without QA review.

## Background

Earlier documentation defined the planned readiness-gate behaviour for Power Apps using the Microsoft Lists field:

- `Submission Readiness Status`

The supporting field is:

- `Submission Readiness Notes`

During implementation, it was confirmed that the form is a customised SharePoint form rather than a standalone Power Apps canvas app with a separate visible submit button.

Therefore, the correct implementation point is:

- `SharePointIntegration.OnSave`

This controls the save action for the SharePoint-integrated form.

## Correct Implementation Target

The readiness gate was applied to the customised form connected to:

- `MAP_Module_Plans_Pilot_2026_27`

This is the correct list because it contains the module-plan records and the readiness fields.

The readiness gate was not applied to:

- `MAP_Module_Catalogue_Pilot_2026_27`

The module catalogue list contains module catalogue information and is not the correct target for the MAP module-plan submission readiness gate.

## Fields Used

| Field | Purpose |
|---|---|
| `Submission Readiness Status` | Controls whether the record is ready for direct save/submission. |
| `Submission Readiness Notes` | Provides supporting information where QA review is recommended. |

## Implementation Point

The readiness gate was implemented through the Power Apps formula for:

- `SharePointIntegration.OnSave`

This is the correct control point for a customised SharePoint list form.

## Implemented Logic

The implemented logic allows save/submission only when the readiness status is:

- `Ready to submit`

For all other readiness statuses, the save action is blocked and a warning message is shown.

The readiness-gate formula is:

```powerfx
If(
    SharePointForm1.Updates.'Submission Readiness Status'.Value = "Ready to submit",
    SubmitForm(SharePointForm1),
    Notify(
        "This module plan is not ready for direct submission. Please review the Submission Readiness Notes before submitting.",
        NotificationType.Warning
    )
)
```

## Expected Behaviour

| Submission Readiness Status | Expected Save Behaviour |
|---|---|
| `Ready to submit` | Save allowed |
| `Warning - QA review recommended` | Save blocked and warning message shown |

## Pilot Records Tested

The implementation was tested using two representative pilot records:

| Pilot Record | Submission Readiness Status | Purpose of Test |
|---|---|---|
| `PILOT101` | `Ready to submit` | Confirm that a ready record can be saved. |
| `PILOT105` | `Warning - QA review recommended` | Confirm that a warning record is blocked and the warning message is shown. |

## Observed Results

| Pilot Record | Submission Readiness Status | Expected Behaviour | Observed Result |
|---|---|---|---|
| `PILOT101` | `Ready to submit` | Save allowed | Save completed without being blocked. No data change was required. |
| `PILOT105` | `Warning - QA review recommended` | Save blocked and warning message shown | Save was blocked and the warning message was displayed. |

## Warning Message Observed

For `PILOT105`, the following warning message was shown:

```text
This module plan is not ready for direct submission. Please review the Submission Readiness Notes before submitting.
```

This confirms that the readiness gate prevents direct save/submission when QA review is recommended.

## Important Implementation Note

The original workflow referred to a Power Apps submit button. During implementation, it was confirmed that this is a SharePoint-integrated Power Apps form.

Therefore, the practical implementation uses the SharePoint form save action:

- `SharePointIntegration.OnSave`

rather than a standalone button control.

In future documentation, this behaviour should be referred to as the Power Apps save-action readiness gate or SharePoint form save-action readiness gate.

## Outcome

The Power Apps readiness gate was implemented successfully.

The test confirmed that:

- `PILOT101`, marked `Ready to submit`, can be saved successfully.
- `PILOT105`, marked `Warning - QA review recommended`, is blocked from direct save/submission.
- The warning message is shown correctly for the warning record.
- The readiness gate is applied to the correct list: `MAP_Module_Plans_Pilot_2026_27`.

This confirms that the Microsoft Lists field `Submission Readiness Status` can control the SharePoint-integrated Power Apps save action.

## Relationship to Previous Documentation

This document follows:

- `docs/23-power-apps-submit-button-readiness-test.md`
- `docs/24-power-apps-readiness-gate-implementation-steps.md`
- `docs/25-power-apps-readiness-gate-pilot-test.md`
- `docs/26-microsoft-lists-power-apps-readiness-test-view.md`
