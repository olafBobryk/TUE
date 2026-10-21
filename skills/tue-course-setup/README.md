# TU/e Course Setup

An agent skill that turns a TU/e Canvas course into a local course folder and keeps it current as the course progresses.

**Independent work by Olaf Bobryk. Not an official TU/e product and not affiliated with or endorsed by TU/e.**

## What it does

1. Finds your existing course library (or proposes one) and asks you to confirm it.
2. Opens Canvas in a browser you are already signed in to and finds the course.
3. Collects every module file, files linked from pages, and a text snapshot of the syllabus, pages, assignments (with rubrics), and announcements.
4. Downloads the files through the browser, then files them with a bundled Python script:

```text
<Course Name> <CODE>/
├── COURSE.md                      course index, with a Canvas sync record at the top
├── course-materials/
│   ├── lectures/, labs/, assignments/, exams/, ...
│   └── canvas-snapshots/<date>/   syllabus, pages, assignments, announcements, module list
└── external-sources/tue-canvas-course/SOURCE.md
```

Run it again later to **refresh**: it adds only new or changed files, keeps the old copies, writes a new dated snapshot, and updates the sync record. The sync record tells later agents (including [`tue-academic-writing`](../tue-academic-writing/README.md)) to suggest a refresh when the course is still running and the last sync is more than 14 days old, or when material a task needs is not on disk.

## Requirements

- An agent with a browser tool that runs in your signed-in Canvas session (for example Claude in Chrome) and a shell with Python 3.
- You download only what your own Canvas account can access. The skill never asks for, types, or stores your credentials, and it drops Canvas download URLs and file access tokens from everything it saves.

## Use

- “Use $tue-course-setup to set up Signals and Systems.”
- “Refresh my Networks course from Canvas.”

The [course layout](references/course-layout.md) documents the folder structure, the module mapping, and the sync record. The [Canvas collection](references/canvas-collection.md) reference holds the browser scripts.

## Validation

The organizer script was tested on synthetic Canvas data covering a first setup, a refresh with changed and new files, an existing hand-written `COURSE.md`, duplicate file names, locked files, and incomplete downloads. The browser scripts have not yet been run against a live Canvas course.

## License

[MIT](LICENSE), copyright 2026 Olaf Bobryk.
