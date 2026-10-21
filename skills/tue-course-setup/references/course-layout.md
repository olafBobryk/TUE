# Course layout

The default structure for one course. Follow an existing library's own conventions where they differ.

```text
<library>/[<year folder>/]<Course Name> <CODE>/
├── COURSE.md                      course index and Canvas sync record
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
│   └── canvas-snapshots/
│       ├── files.json             file id → filed path, size, Canvas update time
│       └── <YYYY-MM-DD>/          one folder per sync, never edited afterwards
│           ├── README.md          capture summary, counts, files filed, errors
│           ├── modules.md         every module item, with local or Canvas links
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
  "modules": {
    "0": "other",
    "1": "course-information",
    "2": "lectures",
    "3": "labs",
    "4": "essay"
  }
}
```

Keys are module numbers in Canvas order (`mi` in the manifest, starting at 1). `0` holds files found outside modules (page links, course files). Unmapped modules go to `other`. Folder names must be plain relative names without `/`.

## COURSE.md

The organizer creates `COURSE.md` when it is missing, with front matter (`course_name`, `course_code`, `institution`, `academic_year`, `document_role: course-index`), the Canvas sync section, a directory map, agent rules, upload routing, and sources. Edit it later only for factual, organizational changes; never add study progress or plans.

## Canvas sync

Every sync replaces the block between `<!-- canvas-sync:start -->` and `<!-- canvas-sync:end -->` directly under the `COURSE.md` title, so it is the first thing a later agent reads. When an existing `COURSE.md` has no block yet, the organizer inserts one under the title and leaves the rest untouched. The block records:

- the last sync date and a link to its snapshot;
- the course run (term and dates) when Canvas provides them;
- what was captured (modules, files and size, pages, assignments, announcements);
- how many items could not be downloaded;
- the staleness rule for agents: if the course is still running and the last sync is more than 14 days old, or a task needs course material that is not on disk, tell the student the course context may be out of date or incomplete and offer to refresh it with `tue-course-setup`. Do not refresh without their go-ahead.

## Refresh behaviour

- Files already filed (same Canvas id, size, and update time in `files.json`) are skipped; `--print-known` lists their ids so the download script can skip them.
- A file whose Canvas copy changed is filed next to the old one as `<name> (updated YYYY-MM-DD).<ext>`; the old copy stays.
- A name that already exists for a different file gets ` (F<id>)` before the extension.
- Each sync writes a new snapshot folder; a second sync on the same day gets a `-2` suffix.
