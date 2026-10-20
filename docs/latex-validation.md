# LaTeX and Overleaf validation

Validation of version 1.2.0 on 20 October 2026. This is a maintenance record, not required agent context. The existing complete writing guide and its source coverage record are unchanged.

## Executed checks

| Check | Result |
| --- | --- |
| Academic essay ZIP imported into a new Overleaf project | `main.tex`, `sections/body.tex`, and `references.bib` present; main file verified |
| IEEE report ZIP imported into a separate Overleaf project | Same file structure; main file verified |
| Both starters compiled in Overleaf | pdfLaTeX, TeX Live 2026; each produced a one-page PDF; UI log reported zero errors and zero warnings |
| Both PDF previews inspected | Titles, headings, placeholder text and page boundaries readable; IEEE document uses conference column layout |
| Essay title edited through the browser | Scoped selection changed only the title; recompile showed the new title in the PDF |
| Essay project reopened | Edited source and updated PDF persisted after reload |
| Both starters compiled locally with Tectonic | Successful supplemental smoke builds; one page each |
| Bibliography and cross-reference fixtures | Separate temporary copies with synthetic test entries built successfully with BibTeX (`plain` and `IEEEtran`); no unresolved citations/references in final logs |

Tectonic uses a XeTeX-based engine and reported inputenc warnings plus initial font substitution warnings for IEEEtran. Those local builds are supplemental checks, not proof of exact pdfLaTeX typography; the recommended pdfLaTeX configuration was verified separately in Overleaf with clean UI logs. Synthetic bibliography fixtures were not included in the package or uploaded as scholarly evidence.

The ZIP compilation checks used the three source files. Release ZIPs additionally contain the repository MIT license, which does not participate in compilation. No course submissions or private project identifiers are published here. New isolated projects were used for the browser checks.

## Instruction review

The following were walkthroughs of the instructions, not independent model benchmarks:

- A required course template takes priority over either bundled starter.
- A request to set up or compile a template does not trigger unsolicited rewriting.
- A review-only Overleaf request returns findings without source edits.
- A grammar-only request preserves argument, structure, and template settings.
- Missing evidence and citations remain explicit gaps; blank bibliography assets contain no example sources to accidentally reuse.
- Existing collaborative content is reread before editing; the workflow addresses virtualized editor excerpts, stale local copies, and stale PDF output.
- A missing browser integration produces a local artifact and a specific access limitation, not a claim that Overleaf was edited.

Concurrent editing conflicts, compiler service outages, error-repair limits, and all third-party browser-control implementations were not exercised. The workflow describes how to handle those conditions; this record does not certify them as tested.

## Packaging

The skill-creator validator and relative-link checks are run before publication. Templates require only the packaged files and a TeX distribution; the university PDF, private filesystem paths, and local coursework are not dependencies. The release contains source ZIPs, not generated coursework or cached build files.

## Maintainer references

Overleaf documentation used when preparing the workflow:

- [Upload a project](https://docs.overleaf.com/managing-projects-and-files/uploading-a-project)
- [Files that should not be included](https://docs.overleaf.com/managing-projects-and-files/adding-files-to-a-project/uploading-files-to-a-project/files-that-should-not-be-included-in-a-project)
- [Recompiling a project](https://docs.overleaf.com/getting-started/recompiling-your-project)
- [History and versioning](https://docs.overleaf.com/writing-and-editing/history-and-versioning)

UI wording can change. The agent-facing workflow intentionally uses observed controls and outcomes rather than fixed coordinates or stored element identifiers.

## Version 1.2.1 — school starter

The school-supplied `essay_template_latex.tex` is included as `assets/templates/tue-school-essay/main.tex`. Byte comparison against the supplied archive confirms that only the filename changed. Its sample bibliography and course instructions are retained as source content; the template guide instructs agents to replace the examples, preserve actual authorship, and apply course-specific requirements only in their relevant assignment.

The default routing now selects this two-column starter for a new LaTeX document with no other requested or required format. Existing documents and explicit assignment templates take precedence. The core writing guide is unchanged. The school starter has a separate attribution notice and is excluded from the MIT licensing claim for original repository content.

Validation for the added school starter: the desktop editor compiler returned success. A supplemental Tectonic build produced a one-page PDF, which was visually inspected for the expected two columns, three author blocks, subtitle, section prompts, and bibliography. Tectonic reported font substitution warnings and an encoding warning in its `algorithmic.sty` dependency, so this supplemental render is not a claim of exact pdfLaTeX typography. The new school starter was not uploaded to Overleaf during this revision; the earlier live tests above cover the two independent starters only.
