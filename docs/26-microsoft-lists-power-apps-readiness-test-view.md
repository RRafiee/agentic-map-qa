# Microsoft Lists Power Apps Readiness Test View

## Purpose

This document records the Microsoft Lists view created to support testing of the planned Power Apps submission-readiness gate.

The view was created in:

- `MAP_Module_Plans_Pilot_2026_27`

The purpose of the view is to make the readiness status and supporting notes clearly visible for the five representative pilot records before or during Power Apps readiness-gate testing.

## Background

The Power Apps readiness gate is expected to use the Microsoft Lists field:

- `Submission Readiness Status`

to determine whether direct final submission should be allowed.

The supporting field is:

- `Submission Readiness Notes`

This view provides a focused testing layout so that the relevant pilot records can be reviewed consistently.

## Microsoft Lists View

Suggested view name:

- `Power Apps Readiness Test View`

## Pilot Records Included

The view focuses on the five representative pilot records:

- `PILOT101`
- `PILOT102`
- `PILOT103`
- `PILOT104`
- `PILOT105`

## Fields Included

The view should include the following core fields:

| Field | Purpose |
|---|---|
| `Plan Reference` | Identifies the pilot MAP record. |
| `Module Code` | Shows the module code linked to the MAP record. |
| `Module Title` | Shows the module title linked to the MAP record. |
| `Submission Readiness Status` | Shows whether the record is ready to submit or requires QA review. |
| `Submission Readiness Notes` | Provides supporting information where QA review is recommended. |

Optional fields may also be included if useful and already available in the list:

- `Module Owner`
- `Assessment Weight Validation Status`
- `Formal Examination Status`
- `Submission Status`

## Expected Readiness Values

| Plan Reference | Expected Submission Readiness Status |
|---|---|
| `PILOT101` | `Ready to submit` |
| `PILOT102` | `Ready to submit` |
| `PILOT103` | `Ready to submit` |
| `PILOT104` | `Ready to submit` |
| `PILOT105` | `Warning - QA review recommended` |

## View Behaviour

The view should make it easy to confirm that:

- The four ready records display `Ready to submit`.
- `PILOT105` displays `Warning - QA review recommended`.
- The `Submission Readiness Notes` field is visible for checking the reason for any warning.
- The pilot records can be reviewed without searching across the full list.

## Relationship to Power Apps Testing

This Microsoft Lists view supports the later Power Apps readiness-gate test documented in:

- `docs/25-power-apps-readiness-gate-pilot-test.md`

The view does not implement the Power Apps button logic itself. It provides a clean data-checking view to support that testing.

## Outcome

A dedicated Microsoft Lists view has been defined for Power Apps readiness-gate testing.

The view supports clear review of the five representative pilot records and the readiness fields required for the planned Power Apps submission gate.