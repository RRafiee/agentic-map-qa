# MAP Submission App Version 1.1 – Final System Documentation
# MAP Submission App Version 1.1 – Final System Documentation

## 1. Purpose and Scope

The Module Assessment Planning (MAP) Submission App supports the collection of module assessment plans for the EEECS School for the 2026/27 academic year.

The app enables module owners to:

- select their module;
- confirm the module owner or owners;
- identify the Coordinating Module Owner completing the submission;
- enter all summative assessment components;
- provide assessment titles, weightings, submission dates and feedback release dates;
- submit the completed MAP;
- provide feedback on the submission process.

The app was designed to provide a structured submission workflow while limiting direct user access to the underlying SharePoint lists.

Version 1.1 represents the tested and published production baseline following pilot feedback and usability improvements.

## 2. Final System Architecture

The final solution uses the following Microsoft 365 components:

- Microsoft Power Apps Canvas App;
- SharePoint Lists;
- SharePoint Person and Lookup fields;
- Power Fx formulas;
- Microsoft 365 access and sharing permissions.

The app acts as the user-facing submission interface. SharePoint stores catalogue, module-plan and assessment data.

The core data flow is:

1. The user opens the published Power Apps link.
2. The user selects a module from the Module Catalogue.
3. Module information and default module owners are retrieved from SharePoint.
4. The user confirms ownership details.
5. The user enters the required summative assessments.
6. The app validates the submission.
7. The module-plan record is created.
8. Related assessment records are written to the assessment list.
9. User feedback is collected separately within the app.

The system uses three primary SharePoint lists:

- `MAP_Module_Catalogue_Pilot_2026_27`
- `MAP_Module_Plans_Pilot_2026_27`
- `MAP_Assessments_Pilot_2026_27`

The current list names retain the word `Pilot`, although the app has now been tested and published as the Version 1.1 production baseline.

## 3. SharePoint Data Model

### 3.1 Module Catalogue

The Module Catalogue is the authoritative source for module-level reference information.

It stores information such as:

- module code;
- module title;
- default module owner or owners;
- other catalogue information required by the app.

The field:

```text
Default Module Owner(s)
```

is a multi-person SharePoint field.

The app uses the selected catalogue record ID to retrieve the full module record.

### 3.2 Module Plans

The Module Plans list stores one submitted MAP record per module submission.

It captures information including:

- selected module;
- confirmed module owners;
- Coordinating Module Owner;
- submission metadata;
- readiness status;
- readiness notes;
- other module-plan fields.

The Student Support and Office Hours field remains in SharePoint but is currently hidden in the app and is not required in Version 1.1.

### 3.3 Assessments

The Assessments list stores individual summative assessment records associated with the submitted module plan.

Each record captures assessment-level information such as:

- assessment title;
- assessment weighting;
- assessment date;
- feedback release date;
- relationship to the submitted module plan.

This structure allows a module plan to contain multiple assessment records.

## 4. Module Catalogue Lookup Process

The module selection control is:

```text
cmbModule
```

The selected value contains the lookup record, including the selected catalogue item ID.

The full catalogue record is retrieved using:

```powerfx
LookUp(
    MAP_Module_Catalogue_Pilot_2026_27,
    ID = cmbModule.Selected.Id
)
```

This is necessary because the selected lookup value does not itself expose all fields from the Module Catalogue.

The default module owners are retrieved using:

```powerfx
LookUp(
    MAP_Module_Catalogue_Pilot_2026_27,
    ID = cmbModule.Selected.Id
).'Default Module Owner(s)'
```

This pattern is used to populate the Confirmed Module Owners field.

## 5. Module Ownership Logic

### 5.1 Confirmed Module Owners

The Confirmed Module Owners field is automatically populated from the Module Catalogue.

The relevant ComboBox is:

```text
DataCardValue11
```

Its `DefaultSelectedItems` property is:

```powerfx
If(
    frmModulePlan.Mode = FormMode.New,
    LookUp(
        MAP_Module_Catalogue_Pilot_2026_27,
        ID = cmbModule.Selected.Id
    ).'Default Module Owner(s)',
    Parent.Default
)
```

The field remains editable so users can correct or update the owner list where necessary.

The control supports multiple selections:

```powerfx
SelectMultiple = true
```

The form writes the selected people back to SharePoint using:

```powerfx
DataCardValue11.SelectedItems
```

When the selected module changes, the Confirmed Module Owners control is reset using:

```powerfx
Reset(DataCardValue11)
```

This formula is placed in:

```text
cmbModule.OnChange
```

The reset ensures the displayed owner list refreshes when a different module is selected.

### 5.2 Coordinating Module Owner

The Coordinating Module Owner is not automatically assigned from the Module Catalogue.

This is intentional.

Where two or more academics deliver a module, the person completing the MAP submission may not be the first person listed in the catalogue.

The Coordinating Module Owner must therefore be selected manually by the person completing the form.

The field is used to identify:

- the person completing the MAP submission;
- the primary contact for follow-up queries.

The placeholder text is:

```text
Select the academic staff member completing this MAP submission
```

The Person control displays both name and email to help distinguish staff members with identical names.

The relevant properties include:

```powerfx
DisplayFields = ["DisplayName","Email"]
```

```powerfx
SearchFields = ["DisplayName","Email"]
```

## 6. Assessment Generation and Validation

The app supports multiple summative assessments for each module.

The assessment interface uses a repeating Power Apps gallery rather than a fixed number of manually created assessment sections.

Users enter information including:

- assessment title;
- assessment weighting;
- assessment date;
- feedback release date.

The screen includes guidance reminding users to scroll through all assessment rows where a module contains more than one summative assessment.

The current guidance is:

```text
If your module has more than one summative assessment, please scroll down to complete all assessment details before submitting.
```

The app validates the submission before writing records to SharePoint.

Validation includes checks such as:

- required fields are completed;
- assessment information is present;
- assessment weights are valid;
- the submission meets the readiness condition.

The app prevents incomplete or non-ready submissions from being saved.

Feedback release guidance is displayed near the Feedback Release Date field:

```text
Feedback must normally be released no later than 20 working days after submission and before the next assessment is due.
```

## 7. Submission Readiness Gate

The Module Plans list includes:

- `Submission Readiness Status`
- `Submission Readiness Notes`

The submission readiness gate prevents records that are not classified as Ready from being submitted.

The form `OnSave` logic checks the readiness status.

Where the status is not Ready, the app displays a warning and blocks submission.

Pilot testing confirmed that:

- a Ready record could be saved;
- a Warning record was blocked.

This gate provides an additional quality-assurance control before data is committed to SharePoint.

## 8. Feedback Collection

The app includes a feedback mechanism for users to comment on the MAP submission process.

The feedback function is separate from the assessment-planning fields.

It is intended to collect information about:

- usability;
- clarity of wording;
- access;
- navigation;
- difficulties encountered during submission;
- suggested improvements.

Feedback collected during testing informed the Version 1.1 changes.

## 9. Sharing and Permissions

The app is shared with academic staff using Run-only access.

Users must also approve access to the connected SharePoint data sources when first opening the app.

The intended permission model is:

- users can run the app;
- users can submit data through the app;
- users do not need direct access to browse or edit the full SharePoint lists;
- app owners retain access for configuration, monitoring and support.

Testing identified that users who had not been granted Run-only access received a request-access message.

After appropriate sharing permission was granted, the user was able to open and complete the app successfully.

The production release process must therefore ensure that:

- the app is shared with the intended staff group;
- SharePoint connector permissions are available;
- users can open the published link;
- users can submit without needing manual intervention.

## 10. Testing Evidence

Version 1.1 was tested through direct and colleague-based testing.

Testing covered:

- opening the shared app;
- accepting SharePoint access;
- selecting a module;
- retrieving one default module owner;
- retrieving multiple default module owners;
- refreshing owners when the selected module changes;
- manually selecting the Coordinating Module Owner;
- entering multiple assessments;
- validating assessment information;
- blocking non-ready submissions;
- saving module-plan data;
- saving assessment data;
- collecting feedback;
- verifying SharePoint records after submission.

A colleague successfully completed a MAP submission using Run-only access.

The resulting SharePoint data was checked and confirmed to have been stored correctly.

The final published version was regression-tested after the Version 1.1 changes and worked without reported errors.

## 11. Known Limitations

The current Version 1.1 system has the following known limitations:

1. The SharePoint list names still include the term `Pilot`.
2. The app does not automatically calculate a Feedback Release Date based on 20 working days.
3. The app does not currently exclude weekends, holidays or closure days when evaluating feedback dates.
4. The Coordinating Module Owner must be selected manually.
5. The current system does not prevent duplicate MAP submissions for the same module unless this is checked operationally.
6. The app depends on the accuracy of the Module Catalogue.
7. Changes to module ownership must be reflected in the Catalogue or manually corrected during submission.
8. Student Support and Office Hours are retained in SharePoint but hidden and not collected in Version 1.1.
9. Questions relating to assessment criteria, specialist EEECS facilities and resit strategy are not collected as structured app fields.
10. These additional considerations will instead be included in guidance issued to module owners.
11. The current system focuses on structured submission and validation rather than automated cross-module QA analysis.
12. Advanced Agentic AI, automated conflict checking and recommendation functions remain future work.

## 12. Version 1.1 Release Note

### Version 1.1

Usability improvements following pilot testing, including:

- clearer Coordinating Module Owner guidance;
- improved Person control search using name and email;
- automatic retrieval of Confirmed Module Owners from the Module Catalogue;
- refresh of confirmed owners when the selected module changes;
- office-hours guidance added and later hidden following Education Committee feedback;
- assessment-screen scrolling guidance;
- feedback release guidance aligned with the 20-working-day expectation;
- successful Run-only access testing;
- final regression testing and publication.

The published app description is:

> The Module Assessment Planning (MAP) Submission App enables EEECS module owners to complete and submit their Module Assessment Plans for the 2026/27 academic year. It captures module ownership details, summative assessment information, assessment weightings and dates, validates submissions, stores the data in SharePoint, and collects user feedback on the submission process.
>
> Version 1.1: Usability improvements following pilot testing, including clearer module-owner guidance, an office-hours example, assessment-screen scrolling guidance, and automatic retrieval of confirmed module owners from the Module Catalogue.

## 13. Production Status

Version 1.1 has been:

- configured;
- tested;
- tested by a colleague;
- regression-tested;
- published;
- confirmed to save data correctly;
- prepared for wider staff testing before release.

The system is now treated as the working production baseline.

Further changes should be limited to:

- confirmed defects;
- access failures;
- incorrect data storage;
- issues that prevent submission.

Non-critical suggestions should be recorded for a future version rather than added immediately to the production baseline.
