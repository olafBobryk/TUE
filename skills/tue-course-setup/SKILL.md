---
name: tue-course-setup
description: >-
  Set up or refresh a TU/e course folder from Canvas. Finds and confirms the
  student's course library, downloads every module file plus a dated snapshot
  of the syllabus, pages, assignments, and announcements through the student's
  signed-in browser, and files everything into a standard course structure
  with a COURSE.md index and sync record. Use when a student asks to set up,
  download, import, sync, or refresh a TU/e Canvas course, or when a course's
  COURSE.md shows its Canvas context is stale or incomplete.
license: MIT
metadata:
  version: "1.0.0"
---

# TU/e Course Setup

Turn a TU/e Canvas course into a local course folder that future agents can work from, and keep it current as the course progresses.

**Inputs:** a course name or code (e.g. "Networks" or "2IRR20"). The student is signed in to `canvas.tue.nl` in a browser the agent can control.

**Outputs:** `<library>/[<year folder>/]<Course Name> <CODE>/` with `COURSE.md`, source-faithful files under `course-materials/<kind>/`, a dated text snapshot under `course-materials/canvas-snapshots/<YYYY-MM-DD>/`, and a Canvas source record. See [the course layout](references/course-layout.md).

## Modes

- **Setup:** the course folder does not exist yet. Run every step.
- **Refresh:** the folder exists (its `COURSE.md` has a `## Canvas sync` section). Run the same steps; the organizer skips files already present, adds only new ones, and writes a new dated snapshot. Never overwrite or delete earlier material, then update the sync section.

A course folder that exists without a `## Canvas sync` section was organized by hand: read its `COURSE.md` and any `AGENTS.md`, follow its conventions, and ask before adding to it.

## Steps

1. **Find and confirm the library.** Look for an existing course library before asking: search the home folder's `Documents` (and, on Windows, `OneDrive\Documents`) a few levels deep for folders containing `COURSE.md` files, or named like `TUe`, `TU/e`, `Tue`, `University`, or `Study`. Show the best candidate, including whether it groups courses into year folders (e.g. `Year 2/`), and **ask the student to confirm it or give another path**. Ask which year folder to use if the library has them. With no candidate, propose `~/Documents/TUe` and ask. Read the library's `AGENTS.md`, `README.md`, or an existing `COURSE.md` and follow its conventions where they differ from the defaults here.

2. **Open Canvas and find the course.** Use a browser tool that runs in the student's own signed-in session (for example Claude in Chrome, or the agent's built-in browser after the student signs in there). Open `https://canvas.tue.nl/courses`. If Canvas shows a login page, ask the student to sign in; never ask for, type, or store Canvas credentials. Run the course lookup from [Canvas collection](references/canvas-collection.md) and match the name or code. Ask when more than one course matches.

3. **Collect.** Run the collection script from [Canvas collection](references/canvas-collection.md). It gathers modules and their files, file links in pages, pages, assignments with rubrics, the syllabus, and announcements into `window._tue`. Do not await long-running scripts; start them and poll their status. Report the file count and total size, and confirm before downloading more than about 1 GB.

4. **Download through the browser.** File URLs need the Canvas session and expire, so download from the page, not with `curl`. Run the download script. It saves each file as `<CODE>__M<NN>__F<id>__<name>` and the course manifest as `<CODE>__manifest.json` in the browser's download folder.
   - Browsers block multiple downloads at first. If only the first file arrives, ask the student to click **Allow** on "canvas.tue.nl wants to download multiple files", then rerun the missing files.
   - Poll `window._tue.dl` for progress; screenshots may time out while downloads run.
   - Ignore partial `.crdownload` / `.part` files until they finish.

5. **Decide where each module goes.** Map every module to a material kind (`course-information`, `lectures`, `tutorials`, `labs`, `assignments`, `exams`, `readings`, `other`), or to a topic folder when a module is clearly one piece of coursework (e.g. `essay`). Files found only through page links go to `other` unless their page makes the kind clear. Show the student the module → folder table and ask only about the unclear ones. Write the mapping to a JSON file in a scratch folder, as described in [the course layout](references/course-layout.md#module-mapping).

6. **Organize.** Run the bundled organizer with Python 3 (standard library only):

   ```sh
   python3 scripts/organize_course.py --downloads <download folder> --course-dir "<course folder>" --mapping <mapping.json> --move
   ```

   Run it once without `--move` first: it checks that every expected file is present with the right size and prints what it would do. Rerun missing downloads until it reports none. With `--move` it copies each file into place, verifies the size, and deletes only that prefixed download. It never overwrites an existing file; it reports conflicts instead. It writes the dated snapshot, creates `COURSE.md` and the Canvas `SOURCE.md` when they are missing, and updates the `## Canvas sync` section in `COURSE.md` (see [Canvas sync](references/course-layout.md#canvas-sync)). Moving files out of the download folder may need the student's permission; name the `<CODE>__*` files when asking.

7. **Report.** Close any browser tab you opened. Tell the student the course folder, the files added and skipped, anything not downloadable (videos, external tools, locked items listed in `modules.md`), and any conflicts. Suggest starting future agent sessions from the course folder (for example a Claude or Codex project connected to it) so its `COURSE.md` is read first.

## Rules

- Only download material the student can already access on Canvas. Treat `course-materials/` as immutable source material: never edit, rename, or delete downloaded files after filing them.
- Keep `COURSE.md` factual and organizational: course facts, folder map, routing, sources, and the sync record. Do not add study progress, plans, or inferred course content.
- Never record signed or expiring download URLs, tokens, or cookies on disk or in chat.
- Leave everything in the download folder that this run did not create.
- Do not infer the teaching order or future content from older public material; the snapshot records what Canvas showed on its capture date.
