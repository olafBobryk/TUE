---
name: tu-course-setup
description: >-
  Set up or refresh a university course folder from its learning platform:
  Canvas (TU/e, tested) or Brightspace (TU Delft and others, experimental).
  Finds and confirms the student's course library, downloads every module file
  plus a dated snapshot of the syllabus, pages, assignments, and announcements
  through the student's signed-in browser, and files everything into a standard
  course structure with a COURSE.md index and sync record. Use when a student
  asks to set up, download, import, sync, or refresh a Canvas or Brightspace
  course, or when a course's COURSE.md shows its course context is stale or
  incomplete.
license: MIT
metadata:
  version: "1.1.0"
---

# TU Course Setup

Turn a Canvas or Brightspace course into a local course folder that future agents can work from, and keep it current as the course progresses.

**Platforms:**

| Platform | Typical sites | Status | Collection reference |
| --- | --- | --- | --- |
| Canvas | `canvas.tue.nl` (TU/e) | Tested live on a real TU/e course | [Canvas collection](references/canvas-collection.md) |
| Brightspace | `brightspace.tudelft.nl` (TU Delft), other Brightspace sites | **Experimental**: written from D2L's API documentation and tested only against a mock, never on a real Brightspace site | [Brightspace collection](references/brightspace-collection.md) |

Pick the platform from the student's site: a Canvas address has `/courses/<id>`, a Brightspace address has `/d2l/`. Ask when it is unclear. For Brightspace, tell the student up front that this path is experimental, and stop on the first unexpected response instead of improvising.

**Inputs:** a course name or code (e.g. "Networks" or "2IRR20"). The student is signed in to their platform in a browser the agent can control.

**Outputs:** `<library>/[<year folder>/]<Course Name> <CODE>/` with `COURSE.md`, source-faithful files under `course-materials/<kind>/`, a dated text snapshot under `course-materials/<platform>-snapshots/<YYYY-MM-DD>/` (`canvas-snapshots` or `brightspace-snapshots`), and a source record. See [the course layout](references/course-layout.md).

## Modes

- **Setup:** the course folder does not exist yet. Run every step.
- **Refresh:** the folder exists (its `COURSE.md` has a `## Course sync` section, or the older `## Canvas sync`). Run the same steps; the organizer skips files already present, adds only new ones, and writes a new dated snapshot. Never overwrite or delete earlier material, then update the sync section.

A course folder that exists without a sync section was organized by hand: read its `COURSE.md` and any `AGENTS.md`, follow its conventions, and ask before adding to it.

## Steps

1. **Find and confirm the library.** Look for an existing course library before asking: search the home folder's `Documents` (and, on Windows, `OneDrive\Documents`) a few levels deep for folders containing `COURSE.md` files, or named like `TUe`, `TU/e`, `Tue`, `University`, or `Study`. Show the best candidate, including whether it groups courses into year folders (e.g. `Year 2/`), and **ask the student to confirm it or give another path**. Ask which year folder to use if the library has them. With no candidate, propose `~/Documents/TUe` and ask. Read the library's `AGENTS.md`, `README.md`, or an existing `COURSE.md` and follow its conventions where they differ from the defaults here.

2. **Open the platform and find the course.** Use a browser that runs in the student's own signed-in session and can save downloads, such as the student's Chrome through Claude in Chrome or the agent's built-in browser. Some built-in browsers ask the student to approve every download; step 5 tells them before anything is sent. Open the platform's course list (for Canvas `https://canvas.tue.nl/courses`; for Brightspace the student's own site). If the platform shows a login page, ask the student to sign in; never ask for, type, or store credentials. Run the course lookup from the platform's collection reference and match the name or code. Ask when more than one course matches.

3. **Collect.** Run the collection script from the platform's collection reference ([Canvas](references/canvas-collection.md) or [Brightspace](references/brightspace-collection.md)). Both produce the same manifest: modules, pages (Canvas wiki-style home pages are followed link by link), assignments, announcements, and every file with its source. Do not await long-running scripts; start them and poll their status. Report the file count and total size, and confirm before downloading more than about 1 GB.

4. **Decide where everything goes, before downloading.** Map each module to a material kind (`course-information`, `lectures`, `tutorials`, `labs`, `assignments`, `exams`, `readings`, `other`), or to a topic folder when it is clearly one piece of coursework (e.g. `essay`). Files outside modules are mapped one by one from their name and source page; a home page often mixes slides, labs, and course information. Skip decorative images (banners, staff photos, book covers) by mapping them to `null`. Show the student the table and ask only about unclear rows. Add `institution`, `institution_short` and `institution_slug` to the mapping when the site is not TU/e or TU Delft (they name the source folder and `COURSE.md`). Write the mapping JSON to a scratch folder as described in [the course layout](references/course-layout.md#module-mapping), and pass the skipped ids to the download script.

5. **Download through the browser.** File URLs need the student's login session and expire, so download from the page, not with `curl`. **Before sending anything, tell the student how many downloads are coming and that their browser may ask them to approve each one (or offer to allow all).** Save only the manifest first and check that `<CODE>__manifest.json` arrived in the download folder. If it did not, ask the student whether a download prompt is waiting; if their browser cannot save downloads, ask them to switch to one that can. Then run the file download. Each file is saved as `<CODE>__M<NN>__F<id>__<name>`.
   - Browsers block multiple downloads at first. If only the first file arrives, ask the student to click **Allow** on the browser's "wants to download multiple files" prompt, then rerun the missing files.
   - Poll `window._tue.dl` for progress; screenshots may time out while downloads run. A finished status only means the browser was asked to save; the organizer's check is what counts.
   - Ignore partial `.crdownload` / `.part` files until they finish.

6. **Organize.** Run the bundled organizer with Python 3 (standard library only):

   ```sh
   python3 scripts/organize_course.py --downloads <download folder> --course-dir "<course folder>" --mapping <mapping.json> --move
   ```

   Run it once without `--move` first: it checks that every expected file is present with the right size and prints what it would do. Rerun missing downloads until it reports none. With `--move` it copies each file into place, verifies the size, and deletes only that prefixed download. It never overwrites an existing file; it reports conflicts instead. It writes the dated snapshot, creates `COURSE.md` and the Canvas `SOURCE.md` when they are missing, and updates the `## Canvas sync` section in `COURSE.md` (see [Canvas sync](references/course-layout.md#canvas-sync)). Moving files out of the download folder may need the student's permission; name the `<CODE>__*` files when asking.

7. **Report.** Close any browser tab you opened. Tell the student the course folder, the files added and skipped, anything not downloadable (videos, external tools, locked items listed in `modules.md`), and any conflicts. Suggest starting future agent sessions from the course folder (for example a Claude or Codex project connected to it) so its `COURSE.md` is read first.

## Rules

- Only download material the student can already access on their platform. Treat `course-materials/` as immutable source material: never edit, rename, or delete downloaded files after filing them.
- Keep `COURSE.md` factual and organizational: course facts, folder map, routing, sources, and the sync record. Do not add study progress, plans, or inferred course content.
- Never record signed or expiring download URLs, tokens, or cookies on disk or in chat.
- Leave everything in the download folder that this run did not create.
- Do not infer the teaching order or future content from older public material; the snapshot records what the platform showed on its capture date.
