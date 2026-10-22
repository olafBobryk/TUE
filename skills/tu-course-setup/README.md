# TU Course Setup

An agent skill that turns a university course on **Canvas** or **Brightspace** into a local course folder and keeps it current as the course progresses. Built for TU/e (Canvas) and TU Delft (Brightspace) students.

**Independent work by Olaf Bobryk. Not an official TU/e or TU Delft product and not affiliated with or endorsed by either university.**

## Platform status

| Platform | University | Status |
| --- | --- | --- |
| Canvas | TU/e (`canvas.tue.nl`) | Tested live on a real course |
| Brightspace | TU Delft (`brightspace.tudelft.nl`) and other Brightspace sites | **Experimental.** Written from D2L's published API documentation and tested only against a mock, because the author has no Brightspace login. It stops on the first unexpected answer. If you try it, please report what worked and what did not. |

## What it does

1. Finds your existing course library (or proposes one) and asks you to confirm it.
2. Opens your platform in a browser you are already signed in to and finds the course.
3. Collects every module file, linked pages, assignments (with rubrics where the platform exposes them), announcements and the syllabus.
4. Downloads the files through the browser, then files them with a bundled Python script:

```text
<Course Name> <CODE>/
├── COURSE.md                      course index, with a course sync record at the top
├── course-materials/
│   ├── lectures/, labs/, assignments/, exams/, ...
│   └── canvas-snapshots/ or brightspace-snapshots/<date>/   syllabus, pages, assignments, announcements, module list
└── external-sources/<university>-<platform>-course/SOURCE.md
```

Run it again later to **refresh**: it adds only new or changed files, keeps the old copies, writes a new dated snapshot, and updates the sync record. The sync record tells later agents (including [`tue-academic-writing`](../tue-academic-writing/README.md)) to suggest a refresh when the course is still running and the last sync is more than 14 days old, or when material a task needs is not on disk.

## Install

```sh
npx skills add olafBobryk/tu-skills --skill tu-course-setup --agent claude-code
npx skills add olafBobryk/tu-skills --skill tu-course-setup --agent codex --global
```

Or in Claude Code: `/plugin marketplace add olafBobryk/tu-skills`, then `/plugin install tu-skills --marketplace olafBobryk/tu-skills`.

## Requirements

- An agent with a browser tool that runs in your signed-in session (for example Claude in Chrome) and a shell with Python 3.
- You download only what your own account can access. The skill never asks for, types, or stores your credentials, and it drops download URLs and file access tokens from everything it saves. On Brightspace it may request a short-lived token from the site's own token endpoint, which stays in memory.

## Use

- Claude Code: “Set up Signals and Systems from Canvas” or `/tu-course-setup`.
- Codex: “Use $tu-course-setup to set up Signals and Systems.”

The [course layout](references/course-layout.md) documents the folder structure, the folder mapping, and the sync record. The [Canvas](references/canvas-collection.md) and [Brightspace](references/brightspace-collection.md) references hold the browser scripts.

## Validation

**Canvas:** tested live on a real TU/e course with no modules and a wiki home page: the collector followed the front page to 5 course pages and found all 28 linked files, matching an earlier hand-made capture, plus 8 announcements and 9 assignments. The 22 documents downloaded through the browser were filed byte-identical to that capture, except three lecture slide sets that Canvas had updated since; a refresh recognized all existing files, including those filed by hand. No access tokens were saved.

**Brightspace:** the collector was run only against a mock of the documented API (session login, token login, and failed login), and its manifest was filed correctly by the organizer. It has not touched a real Brightspace site.

The organizer is also tested on synthetic data covering modules, changed and duplicate files, locked files, an existing hand-written `COURSE.md`, and incomplete downloads.

## License

[MIT](LICENSE), copyright 2026 Olaf Bobryk.
