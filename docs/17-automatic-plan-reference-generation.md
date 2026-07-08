# Automatic Plan Reference Generation

**Project:** Agentic MAP-QA  
**Related issue:** #32  
**Document version:** 0.1  
**Status:** Design rule defined  

## 1. Purpose

This document defines how MAP-QA should automatically generate a unique Plan Reference for each annual module plan.

The Plan Reference is the stable identifier that links a module plan to its assessment records. It should therefore be generated consistently and should not rely on manual entry by module owners.

## 2. Current pilot approach

In the current Microsoft Lists pilot, the Plan Reference is entered manually in the module plan List.

Example:

| Academic Year | Module Code | Plan Reference |
|---|---|---|
| 2026/27 | PILOT101 | 2026-27_PILOT101 |

This approach works for early testing because it allows the assessment List to use Plan Reference as a lookup value.

However, manual entry is not suitable for the final staff-facing workflow because it creates risks of inconsistent or duplicate identifiers.

## 3. Required Plan Reference format

The recommended Plan Reference format is:

`AcademicYear_ModuleCode`

Example:

`2026-27_PILOT101`

The academic year should use a consistent hyphenated format:

| Academic year display value | Plan Reference value |
|---|---|
| 2026/27 | 2026-27 |
| 2027/28 | 2027-28 |
| 2028/29 | 2028-29 |

The module code should match the official module code stored in the module catalogue.

## 4. Example generated values

| Academic Year | Module Code | Generated Plan Reference |
|---|---|---|
| 2026/27 | PILOT101 | 2026-27_PILOT101 |
| 2026/27 | PILOT102 | 2026-27_PILOT102 |
| 2027/28 | PILOT101 | 2027-28_PILOT101 |
| 2028/29 | PILOT101 | 2028-29_PILOT101 |

This structure allows the same module code to have different annual module plans across different academic years.

## 5. Why the value should not be entered manually

Plan Reference should not be manually entered by module owners because manual entry creates several risks.

Examples of possible errors:

| Error type | Example |
|---|---|
| Typing error | 2026-27_PILT101 |
| Inconsistent separator | 2026/27-PILOT101 |
| Inconsistent academic-year format | 2026_27_PILOT101 |
| Duplicate value | Two records both using 2026-27_PILOT101 |
| Wrong module code | Plan Reference does not match selected module |
| Wrong academic year | 2025-26 used in a 2026/27 plan |

These errors would make lookup relationships less reliable and could cause assessment records to be linked to the wrong module plan.

## 6. Why Plan Reference should remain a normal text field

Plan Reference should remain a normal single-line text field rather than a calculated column.

This is because the assessment List uses Plan Reference as a lookup value when linking assessment records to module plans.

A normal text field is more suitable because it can be:

- indexed;
- configured to enforce unique values;
- used reliably as a lookup display value;
- populated automatically by Power Apps or Power Automate;
- retained as a stable identifier even if display formatting changes later.

A calculated column may appear convenient, but it is less suitable for the final workflow because calculated values can be more difficult to manage as stable lookup identifiers across linked Lists.

## 7. Required uniqueness rule

Plan Reference should be unique in the module plan List.

The uniqueness rule should prevent two module plan records from having the same combination of academic year and module code.

Expected behaviour:

| Scenario | Expected result |
|---|---|
| First record for 2026-27_PILOT101 | Allowed |
| Second record for 2026-27_PILOT101 | Blocked |
| Record for 2027-28_PILOT101 | Allowed |
| Record for 2026-27_PILOT102 | Allowed |

This allows the same module to appear in different academic years while preventing duplicate annual plans in the same academic year.

## 8. Relationship to the assessment List

The assessment List should link to the module plan List using the Plan Reference.

This means each assessment record should be connected to one annual module plan.

Example:

| Module Plan | Assessment Number | Assessment Title |
|---|---:|---|
| 2026-27_PILOT101 | 1 | Coursework 1 |
| 2026-27_PILOT101 | 2 | Coursework 2 |
| 2026-27_PILOT102 | 1 | Pilot Coursework 1 |
| 2026-27_PILOT102 | 2 | Pilot Coursework 2 |
| 2026-27_PILOT102 | 3 | Formal Exam |

This structure supports one-to-many relationships:

- one module catalogue record can have many annual module plans;
- one annual module plan can have many assessment records;
- each assessment record belongs to one annual module plan.

## 9. Recommended generation logic

The final workflow should generate Plan Reference automatically when a module plan is created or saved.

Recommended logic:

1. Read the selected Academic Year.
2. Convert the academic year into the required Plan Reference format.
3. Read the selected Module Code from the module lookup.
4. Join the formatted academic year and module code using an underscore.
5. Write the generated value into the Plan Reference field.
6. Check that the generated Plan Reference is unique.
7. Prevent saving or submission if a duplicate already exists.

Example transformation:

| Input field | Input value |
|---|---|
| Academic Year | 2026/27 |
| Module Code | PILOT101 |

Generated value:

`2026-27_PILOT101`

## 10. Power Apps implementation option

In a Power Apps staff-facing form, the Plan Reference field should normally be hidden from module owners.

Power Apps can generate the value when the user selects the academic year and module.

Recommended behaviour:

| User action | System behaviour |
|---|---|
| User selects Academic Year | Store selected academic year |
| User selects Module | Read module code |
| User saves module plan | Generate Plan Reference |
| Duplicate exists | Show error and prevent save or submission |
| No duplicate exists | Save module plan |

The module owner should not need to type the Plan Reference.

Suggested user-facing message if a duplicate exists:

> A module plan already exists for this module and academic year. Please check the existing plan instead of creating a duplicate.

## 11. Power Automate implementation option

Power Automate could also generate Plan Reference after a module plan item is created or modified.

Recommended flow logic:

1. Trigger when a module plan item is created or modified.
2. Read Academic Year.
3. Read selected Module Code.
4. Generate Plan Reference.
5. Search the module plan List for existing records with the same Plan Reference.
6. If no duplicate exists, update the Plan Reference field.
7. If a duplicate exists, update the record with an error status or notify the QA owner.

This option may be useful for background correction or administration.

However, Power Automate alone may not provide immediate feedback to the module owner at the point of form completion. For this reason, Power Apps is preferred for the staff-facing submission workflow.

## 12. Recommended final approach

The recommended final approach is:

| Requirement | Recommended solution |
|---|---|
| Generate Plan Reference automatically | Power Apps |
| Hide Plan Reference from module owners | Power Apps |
| Prevent duplicate annual module plans | Unique column and Power Apps validation |
| Maintain stable lookup value | Normal text field |
| Support assessment lookup relationship | Use Plan Reference as module plan lookup display value |
| Background consistency checking | Power Automate if needed |

## 13. Validation requirements

Before a module plan can be submitted, the system should confirm that:

- Plan Reference is present;
- Plan Reference matches the selected Academic Year and Module Code;
- Plan Reference is unique;
- the selected module exists in the module catalogue;
- the selected academic year is valid;
- linked assessment records use the correct module plan reference.

## 14. Suggested QA status checks

A future QA dashboard or review view could include:

| Field | Purpose |
|---|---|
| Plan Reference | Shows the generated identifier |
| Academic Year | Confirms the year |
| Module | Confirms the linked module |
| Module Code | Confirms the module identifier |
| Plan Reference Status | Shows whether the generated value is valid |
| Duplicate Check Status | Shows whether a duplicate has been detected |

Possible status values:

| Status | Meaning |
|---|---|
| Valid | Plan Reference is present and correctly generated |
| Missing | Plan Reference has not been generated |
| Mismatch | Plan Reference does not match academic year and module code |
| Duplicate | Another record has the same Plan Reference |

## 15. Data protection

This document contains only structural design rules and anonymised pilot examples.

It does not include:

- operational module data;
- staff names;
- student data;
- email addresses;
- screenshots;
- private SharePoint links;
- identifiable assessment records.

## 16. Acceptance criteria

This document satisfies Issue #32 by defining that:

- Plan Reference should be generated automatically;
- the required format is `AcademicYear_ModuleCode`;
- module owners should not manually enter the value;
- Plan Reference should remain a normal text field rather than a calculated column;
- Plan Reference should be unique in the module plan List;
- Plan Reference supports the lookup relationship between module plans and assessments;
- Power Apps is the preferred staff-facing implementation route;
- Power Automate may be used for background consistency checking;
- no operational or identifiable data is committed.

## 17. Next steps

1. Define whether Power Apps or Power Automate will generate the first implementation.
2. Create a prototype generation rule using the existing pilot Lists.
3. Test duplicate prevention using representative pilot records.
4. Confirm that assessment records can reliably link to generated Plan References.
5. Add Plan Reference generation to the final MAP-QA submission workflow.