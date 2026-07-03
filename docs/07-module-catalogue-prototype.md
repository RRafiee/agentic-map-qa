# MAP Module Catalogue Prototype

**Project:** Agentic MAP-QA  
**Document version:** 0.1  
**Status:** Initial prototype implemented  

## 1. Purpose

This document records the initial implementation of the
`MAP_Module_Catalogue` Microsoft List.

The catalogue provides a controlled source of module information for the
annual Module Assessment Plan workflow. Module owners will later select a
module from this catalogue rather than manually entering module codes,
titles and ownership information.

## 2. Current implementation

The initial List has been created in Microsoft Lists under:

`MAP_Module_Catalogue`

The current version is a private prototype. The final operational Lists
should be stored in an appropriate organisational SharePoint site so that
related Lists, lookup columns, permissions and workflows can be managed
together.

## 3. Implemented columns

| Column | Type | Required | Configuration |
|---|---|---:|---|
| Module Code | Single line of text | Yes | Unique values enabled |
| Module Title | Single line of text | Yes | Free-text official module title |
| Programme | Choice | Yes | CS or EEE/CE |
| Default Module Owner | Person | Yes | Multiple selections enabled |
| Default Moderator | Person | No | One person |
| Delivery Period | Choice | Yes | Semester 1, Semester 2 or Full Year |
| Active Module | Yes/No | Yes | Default value: Yes |
| MAP Required | Yes/No | Yes | Default value: Yes |

## 4. Controlled choices

### Programme

The broad programme grouping is restricted to:

- `CS`
- `EEE/CE`

`CS` covers areas including Computer Science, Software Engineering,
Business Information Technology, Computing and Information Technology,
and Data Science.

`EEE/CE` covers Electrical and Electronic Engineering and Computer
Engineering.

More detailed programme, stage and cohort relationships will be stored
separately because one module may be shared across several programmes.

### Delivery Period

The controlled values are:

- `Semester 1`
- `Semester 2`
- `Full Year`

A full-year module may have different module owners for different teaching
periods. The multiple-person module-owner field supports initial
co-ownership, while detailed semester-specific responsibilities may later
be represented in a separate module-owner assignment List.

## 5. Administrative fields

The following fields are intended primarily for the QA team and should not
normally be editable by module owners:

- `Active Module`
- `MAP Required`

`Active Module` allows suspended, retired or historical modules to remain
in the catalogue without appearing in current module-selection controls.

`MAP Required` identifies whether a Module Assessment Plan is required for
the relevant module. In the final design, this may be moved to an annual
module-planning record because the value can change between academic
years.

## 6. Interface considerations

Module owners should not receive direct editing access to the catalogue.

The later module-owner interface should:

1. display only eligible catalogue modules;
2. allow the owner to select their module;
3. retrieve the module title and associated metadata automatically;
4. hide administrative catalogue fields;
5. store annual planning information separately from the reference
   catalogue.

## 7. Initial validation requirements

The prototype should verify that:

- a module cannot be saved without a module code;
- a module cannot be saved without a module title;
- duplicate module codes are rejected;
- Programme accepts only `CS` or `EEE/CE`;
- Delivery Period accepts only the controlled values;
- multiple module owners can be selected;
- Active Module defaults to Yes;
- MAP Required defaults to Yes.

## 8. Data protection

The public repository must not contain:

- real staff names;
- staff email addresses;
- confidential module records;
- private Microsoft Lists or SharePoint links;
- screenshots containing personal or institutional information.

Testing documented in the public repository will use synthetic module
codes, titles and identities.

## 9. Next steps

1. Add three synthetic catalogue records.
2. test required fields and duplicate module-code prevention;
3. confirm that multiple module owners can be selected;
4. document any Microsoft Lists configuration limitations;
5. create the `MAP_Module_Plans` List;
6. create the `MAP_Assessments` List;
7. configure and test lookup relationships.