# LaTeX templates

Read this reference when creating or adapting a LaTeX document. For prose work, also read the complete writing guidance required by `SKILL.md`.

## Select the starting point

An assignment-supplied or publisher-required template takes precedence. Preserve its document class, margins, fonts, bibliography style, and required headings unless the task explicitly calls for changing them. Do not replace an existing project just to use a bundled starter.

When no specific template is required, select the smallest suitable starter:

| Starter | Suitable use | Main file | Compiler | References |
| --- | --- | --- | --- | --- |
| [Academic essay](../assets/templates/academic-essay/main.tex) | A single-column essay or literature discussion without a prescribed layout | `main.tex` | pdfLaTeX | BibTeX, `plain` by default |
| [IEEE report](../assets/templates/ieee-report/main.tex) | A short two-column technical report when IEEE conference layout is appropriate | `main.tex` | pdfLaTeX | BibTeX, `IEEEtran` |

Each starter contains `main.tex`, `sections/body.tex`, and `references.bib`. Copy the **whole chosen directory** into a new document workspace. Resolve asset paths relative to this skill, not a particular user's home directory. Preserve the installed master templates and edit the document copy.

The IEEE starter uses the standard `IEEEtran` class supplied by a TeX distribution. It is not a course-approved template. Do not promise conformance to a particular assignment or conference merely because this class compiles. Neither starter requires shell escape, custom fonts, or private files.

## Populate the document

1. Replace title, author, affiliation or course, and date placeholders using supplied information. Do not infer student numbers, affiliations, coauthors, or email addresses. Omit optional fields that are not needed.
2. Replace or remove every `\placeholder{...}` in the body. The rendered starter intentionally shows unfinished fields. Keep unresolved factual gaps visibly marked in a draft; report them before calling it finished.
3. Adapt headings to the actual argument and assignment. The essay's argument/discussion structure and the report's method/results structure are starting points, not requirements. Do not invent an experiment to fill a Results section.
4. Preserve LaTeX syntax while editing prose. Escape literal `%`, `&`, `_`, `#`, and other special characters appropriately; do not escape genuine math or commands as prose. Keep labels and citation keys stable and use `\ref`/`\cite` instead of hard-coded numbering.
5. Add only source-checked entries to `references.bib`. It starts empty to avoid sample references becoming evidence. Once citations exist, uncomment the bibliography commands in `main.tex`; choose the required citation style rather than assuming either starter's default is compulsory. Do not mix BibTeX and biblatex/biber pipelines.
6. For figures, use relative asset paths and supplied or authorized content. Inspect captions, units, labels, and cross-references. In two columns, size ordinary figures and tables to `\columnwidth` or `\linewidth`; use full-width floats only when needed.

For a local BibTeX build, run pdfLaTeX, BibTeX, then pdfLaTeX twice, or use a configured build tool such as latexmk. Without bibliography commands, pdfLaTeX reruns are sufficient. Use available compilers; do not claim a compile when only source inspection was possible.

## Verify and package

Compile the actual main file with the intended engine. Check the log for errors, unresolved citations/references, missing glyphs or files, and overfull boxes. A successful exit is not a visual review: inspect the rendered PDF, including later pages, tables, equations, references, and page breaks. Resolve layout problems within the required template rather than shrinking text or changing margins to evade a page limit.

For an Overleaf upload, create a ZIP containing the selected project's **contents**, with `main.tex` at the ZIP root. Include source, bibliography, and used image/style files; omit build outputs, editor files, caches, secrets, and unrelated documents. When redistributing a starter, include the repository's [MIT license](../LICENSE). Do not upload the whole skill repository as a LaTeX project. Then follow [the Overleaf workflow](overleaf-workflow.md).

Deliver the source folder or ZIP, a PDF if compilation succeeded, and the exact unresolved issues. Distinguish a compilable starter from a completed academic submission.
