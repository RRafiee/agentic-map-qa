# MAP-QA Readiness Gate Implementation Summary

## Purpose

This document summarises the completed MAP-QA readiness gate implementation and validation work across Microsoft Lists and the customised SharePoint/Power Apps form.

The purpose of this summary is to provide a closure record for the readiness-gate stage of the Agentic MAP-QA pilot workflow.

## Background

The readiness gate was developed to control whether a module plan can be saved or submitted directly based on its readiness state.

The implementation uses the Microsoft Lists field:

- `Submission Readiness Status`

with supporting information from:

- `Submission Readiness Notes`

The readiness gate was implemented in the customised SharePoint/Power Apps form using:

- `SharePointIntegration.OnSave`

This was necessary because the MAP module-plan interface is a customised SharePoint list form rather than a standalone Power Apps canvas app with a separate visible submit button.

## Correct Implementation Target

The readiness gate was implemented for the Microsoft Lists pilot list:

- `MAP_Module_Plans_Pilot_2026_27`

This is the correct list because it contains the module-plan records and the readiness fields required to control save/submission behaviour.

The readiness gate was not applied to:

- `MAP_Module_Catalogue_Pilot_2026_27`

The module catalogue list contains module catalogue information and is not the correct target for the MAP module-plan submission readiness gate.

## Readiness Fields

Two fields were used to support the readiness gate:

| Field | Purpose |
|---|---|
| `Submission Readiness Status` | Controls whether the module plan is ready for direct save/submission. |
| `Submission Readiness Notes` | Provides supporting information where QA review is recommended. |

The expected readiness values for the representative pilot records were:

| Pilot Record | Submission Readiness Status |
|---|---|
| `PILOT101` | `Ready to submit` |
| `PILOT102` | `Ready to submit` |
| `PILOT103` | `Ready to submit` |
| `PILOT104` | `Ready to submit` |
| `PILOT105` | `Warning - QA review recommended` |

## Microsoft Lists Preparation

The readiness fields were added to `MAP_Module_Plans_Pilot_2026_27` and manually checked against the five representative pilot records.

A dedicated Microsoft Lists view was then created to support Power Apps readiness-gate testing.

The view focused on the five representative records:

- `PILOT101`
- `PILOT102`
- `PILOT103`
- `PILOT104`
- `PILOT105`

The view made the following fields visible for testing:

- `Plan Reference`
- `Module Code`
- `Module Title`
- `Submission Readiness Status`
- `Submission Readiness Notes`

This made it possible to check the readiness values clearly before and during Power Apps testing.

## Power Apps / SharePoint Form Implementation

The customised SharePoint/Power Apps form was updated to include the readiness fields:

- `Submission Readiness Status`
- `Submission Readiness Notes`

The readiness gate was then implemented through the form save action:

- `SharePointIntegration.OnSave`

The implemented rule was:

```text
If Submission Readiness Status = "Ready to submit"
    Allow save/submission
Else
    Block save/submission and show a warning message
```

The implemented Power Apps formula was:

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

## Warning Message

For records not marked as ready, the following warning message was shown:

```text
This module plan is not ready for direct submission. Please review the Submission Readiness Notes before submitting.
```

This message directs the user to check the readiness notes before attempting direct save/submission.

## Validation Results

The implemented readiness gate was tested across all five representative pilot records.

| Pilot Record | Submission Readiness Status | Validated Behaviour |
|---|---|---|
| `PILOT101` | `Ready to submit` | Save allowed |
| `PILOT102` | `Ready to submit` | Save allowed |
| `PILOT103` | `Ready to submit` | Save allowed |
| `PILOT104` | `Ready to submit` | Save allowed |
| `PILOT105` | `Warning - QA review recommended` | Save blocked and warning message shown |

The test confirmed that the readiness gate behaved as expected for both ready records and the warning record.

## Implementation Outcome

The MAP-QA readiness gate has been implemented and validated for the representative pilot records.

The completed implementation confirms that:

- The readiness fields are present in `MAP_Module_Plans_Pilot_2026_27`.
- The readiness values are visible in the Microsoft Lists testing view.
- The customised SharePoint/Power Apps form includes the readiness fields.
- The save action is controlled through `SharePointIntegration.OnSave`.
- Records marked `Ready to submit` can be saved.
- Records marked `Warning - QA review recommended` are blocked from direct save/submission.
- A clear warning message is shown when QA review is recommended.

## Relationship to Previous Documentation

This summary brings together the readiness-gate work documented in:

- `docs/21-submission-readiness-status-field.md`
- `docs/22-submission-readiness-fields-manual-test.md`
- `docs/23-power-apps-submit-button-readiness-test.md`
- `docs/24-power-apps-readiness-gate-implementation-steps.md`
- `docs/25-power-apps-readiness-gate-pilot-test.md`
- `docs/26-microsoft-lists-power-apps-readiness-test-view.md`
- `docs/27-power-apps-readiness-gate-implementation-result.md`
- `docs/28-power-apps-readiness-gate-all-pilot-records-test.md`

## Closure Statement

The readiness-gate stage of the Agentic MAP-QA pilot workflow is complete.

The Microsoft Lists readiness fields, supporting test view, customised SharePoint/Power Apps form update, save-action gate, and all-pilot-record validation have been completed and documented.

This provides a validated foundation for later MAP-QA workflow stages, including wider module-plan testing, user-facing workflow refinement, and future automation or agentic QA checks.
