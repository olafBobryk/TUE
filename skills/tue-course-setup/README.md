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

Tested live on 21 October 2026 on a real TU/e course that has no modules and links everything from a wiki home page: the collector followed the front page to 5 course pages and found all 28 linked files, matching an earlier hand-made capture, plus 8 announcements and 9 assignments. The 22 documents downloaded through the browser were filed byte-identical to that capture, except three lecture slide sets that Canvas had updated since; a second run as a refresh recognized all 22 as already present. Snapshot pages link to the local files and to each other, and no Canvas access tokens were saved. The organizer is also tested on synthetic data covering modules, changed and duplicate files, locked files, an existing hand-written `COURSE.md`, and incomplete downloads.

## License

[MIT](LICENSE), copyright 2026 Olaf Bobryk.
