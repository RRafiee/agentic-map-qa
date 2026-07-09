# Submission Readiness Fields Manual Test

## Purpose

This document records the manual implementation test for the two submission readiness fields added to the Microsoft Lists pilot list:

- `Submission Readiness Status`
- `Submission Readiness Notes`

The fields were added to `MAP_Module_Plans_Pilot_2026_27` to make the module-plan submission state visible at list level before any future Power Apps submission workflow is applied.

## Scope

The test was limited to the five representative pilot records used throughout the MAP-QA pilot workflow:

- `PILOT101`
- `PILOT102`
- `PILOT103`
- `PILOT104`
- `PILOT105`

This test does not modify the underlying readiness logic, assessment-weight validation, formal examination handling, or Power Apps submit-button logic. It only confirms that the Microsoft Lists fields display the expected readiness outcome for the pilot records.

## Fields Tested

| Field | Purpose |
|---|---|
| `Submission Readiness Status` | Displays whether a module plan is ready for submission or requires further QA review. |
| `Submission Readiness Notes` | Provides supporting notes explaining any warning or review condition. |

## Expected Pilot Values

| Plan Reference | Expected Submission Readiness Status |
|---|---|
| `PILOT101` | `Ready to submit` |
| `PILOT102` | `Ready to submit` |
| `PILOT103` | `Ready to submit` |
| `PILOT104` | `Ready to submit` |
| `PILOT105` | `Warning - QA review recommended` |

## Manual Test Procedure

The following checks were carried out in `MAP_Module_Plans_Pilot_2026_27`:

1. Opened the Microsoft Lists pilot list.
2. Confirmed that the two fields were visible:
   - `Submission Readiness Status`
   - `Submission Readiness Notes`
3. Filtered or inspected the five representative pilot records only.
4. Compared the displayed `Submission Readiness Status` value against the expected pilot value.
5. Checked that `Submission Readiness Notes` behaved consistently with the displayed status.

## Observed Results

| Plan Reference | Expected Submission Readiness Status | Observed Submission Readiness Status |
|---|---|---|
| `PILOT101` | `Ready to submit` | `Ready to submit` |
| `PILOT102` | `Ready to submit` | `Ready to submit` |
| `PILOT103` | `Ready to submit` | `Ready to submit` |
| `PILOT104` | `Ready to submit` | `Ready to submit` |
| `PILOT105` | `Warning - QA review recommended` | `Warning - QA review recommended` |

## Notes Field Behaviour

For the four ready records, the notes field should either remain empty or indicate that no readiness issue has been identified, depending on the final Microsoft Lists implementation style.

For `PILOT105`, the notes field should provide a short explanation that the record is not fully blocked but should be reviewed by QA before submission.

The key requirement is that the notes field supports the status value and does not contradict it.

## Outcome

The manual Microsoft Lists check confirmed that the observed values in `Submission Readiness Status` matched the expected pilot values for all five representative records.

The four ready records displayed `Ready to submit`, while `PILOT105` displayed `Warning - QA review recommended`.

No additional Microsoft Lists test-result column was required. The test outcome is recorded in this Git documentation file.

## Related Documentation

This document follows:

- `docs/15-representative-map-records-test.md`
- `docs/16-assessment-weight-validation.md`
- `docs/17-automatic-plan-reference-generation.md`
- `docs/18-formal-examination-handling.md`
- `docs/19-module-plan-submission-readiness-gate.md`
- `docs/20-power-apps-submit-button-logic.md`
- `docs/21-submission-readiness-status-field.md`