# Course layout

The default structure for one course. Follow an existing library's own conventions where they differ.

```text
<library>/[<year folder>/]<Course Name> <CODE>/
├── COURSE.md                      course index and course sync record
├── course-materials/              TU/e material, unchanged
│   ├── README.md                  contents list
│   ├── course-information/        syllabus files, course guide, policies
│   ├── lectures/                  slides, lecture notes, handouts
│   ├── tutorials/                 exercise sets, instruction sessions, answers
│   ├── labs/                      lab and practical instructions
│   ├── assignments/               assignment and project briefs, rubrics, required templates
│   ├── exams/                     sample exams, old exams, solutions
│   ├── readings/                  articles, reader chapters
│   ├── other/                     anything that does not fit the above
│   └── <platform>-snapshots/        canvas-snapshots or brightspace-snapshots
│       ├── files.json             file id → filed path, size, platform update time
│       └── <YYYY-MM-DD>/          one folder per sync, never edited afterwards
│           ├── README.md          capture summary, counts, files filed, errors
│           ├── modules.md         every module item, with local or platform links
│           ├── syllabus.md
│           ├── pages/<page>.md
│           ├── assignments/<assignment>.md   description, dates, points, rubric
│           ├── announcements/<date>-<title>.md
│           └── canvas-manifest.json          raw capture without download URLs
└── external-sources/
    └── tue-canvas-course/SOURCE.md
```

`notes/`, `assignments/` (the student's own work), `projects/`, `exam-prep/`, `submissions/`, and `archive/` belong to the student. `COURSE.md` lists them; create one only when something goes into it.

Use only the kind folders a course needs. A topic folder (e.g. `course-materials/essay/`) is fine when a module is clearly one piece of coursework.

## Module mapping

The organizer reads a JSON mapping written by the agent after the student has seen the module → folder table:

```json
{
  "code": "2IRR20",
  "course_name": "Networks",
  "academic_year": "2026-2027",
  "institution": "Eindhoven University of Technology",
  "institution_short": "TU/e",
  "institution_slug": "tue",
  "modules": {
    "0": "other",
    "1": "course-information",
    "2": "lectures",
    "3": "labs",
    "4": "essay"
  },
  "files": {
    "7174820": "course-information",
    "7174731": "lectures",
    "7174723": null
  }
}
```

`modules` keys are module numbers in platform order (`mi` in the manifest, starting at 1); `0` holds files found outside modules (linked from pages, the syllabus, assignments, or announcements). `files` maps single file ids and wins over the module entry; `null` skips a file (decorative images, banners, staff photos). The three `institution` fields are optional for TU/e and TU Delft sites (derived from the address) and name the source folder and `COURSE.md`; give them for any other site. Unmapped files go to `other`. Folder names must be plain relative names without `/`.

## COURSE.md

The organizer creates `COURSE.md` when it is missing, with front matter (`course_name`, `course_code`, `institution`, `academic_year`, `document_role: course-index`), the Canvas sync section, a directory map, agent rules, upload routing, and sources. Edit it later only for factual, organizational changes; never add study progress or plans.

## Course sync

Every sync replaces the block between `<!-- course-sync:start -->` and `<!-- course-sync:end -->` (a block written by version 1.0 with `canvas-sync` markers is replaced and renamed) directly under the `COURSE.md` title, so it is the first thing a later agent reads. When an existing `COURSE.md` has no block yet, the organizer inserts one under the title and leaves the rest untouched. The block records:

- the last sync date and a link to its snapshot;
- the course run (term and dates) when the platform provides them;
- what was captured (modules, files and size, pages, assignments, announcements);
- how many items could not be downloaded;
- the staleness rule for agents: if the course is still running and the last sync is more than 14 days old, or a task needs course material that is not on disk, tell the student the course context may be out of date or incomplete and offer to refresh it with `tu-course-setup`. Do not refresh without their go-ahead.

## Refresh behaviour

- Files already filed (same platform id, size, and update time in `files.json`) are skipped; `--print-known` lists their ids so the download script can skip them.
- A file whose platform copy changed is filed next to the old one as `<name> (updated YYYY-MM-DD).<ext>`; the old copy stays.
- A file already in place from an earlier hand-made or other capture (same folder and name, and the same size, or identical bytes when a fresh download exists) is adopted into `files.json` instead of being copied again, so only new and changed files need downloading. A same-named untracked file with different contents is treated as an older version: the new one is filed as `<name> (updated YYYY-MM-DD).<ext>`.
- A name that already belongs to another file from the platform gets ` (F<id>)` before the extension.
- Each sync writes a new snapshot folder; a second sync on the same day gets a `-2` suffix.
