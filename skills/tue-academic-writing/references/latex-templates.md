# LaTeX templates

Read this reference when creating or adapting a LaTeX document. For prose work, also read the complete writing guidance required by `SKILL.md`.

## Select the starting point

An assignment-supplied or publisher-required template takes precedence. Preserve its document class, margins, fonts, bibliography style, and required headings unless the task explicitly calls for changing them. Do not replace an existing project just to use a bundled starter.

**Default for a new LaTeX document: the school-supplied two-column essay starter.** Use a different starter only when the user requests it or the required format calls for it. Existing projects and explicitly supplied assignment/publisher templates retain precedence.

| Starter | Suitable use | Main file | Compiler | References |
| --- | --- | --- | --- | --- |
| [TU/e school essay — default](../assets/templates/tue-school-essay/main.tex) | The school-supplied two-column essay layout, with paper subtitle and author/ID/email fields | `main.tex` | pdfLaTeX | Inline `thebibliography` |
| [Academic essay](../assets/templates/academic-essay/main.tex) | A single-column essay or literature discussion without a prescribed layout | `main.tex` | pdfLaTeX | BibTeX, `plain` by default |
| [IEEE report](../assets/templates/ieee-report/main.tex) | A short two-column technical report when IEEE conference layout is appropriate | `main.tex` | pdfLaTeX | BibTeX, `IEEEtran` |

The school starter contains `main.tex` and an attribution notice; its sections and bibliography are inline. The two independently authored alternatives contain `main.tex`, `sections/body.tex`, and `references.bib`. Copy the **whole chosen directory** into a new document workspace. Resolve asset paths relative to this skill, not a particular user's home directory. Preserve the installed master templates and edit the document copy.

Both two-column starters use the standard `IEEEtran` class supplied by a TeX distribution. The school starter preserves the supplied source; the generic IEEE report is independently authored. Do not promise conformance to a current assignment or conference merely because a template compiles. None of the starters requires shell escape, custom fonts, or private files.

For the school starter, preserve its title/subtitle, author-block layout, and two-column class by default. Fill or remove unused author blocks according to the actual authors; never invent two coauthors to fill the three slots. Keep its abstract and section prompts as scaffolding until writing. Its 100–150-word abstract instruction, course-material links, and assessment statements are course-specific: apply them when that assignment calls for them, not as universal academic-writing rules. All seven inline bibliography entries are examples, including incomplete entries. Remove or replace them with verified sources before delivering a populated draft; never use them as evidence merely because the template contains them.

## Populate the document

1. Replace title, author, affiliation or course, and date placeholders using supplied information. Do not infer student numbers, affiliations, coauthors, or email addresses. Omit optional fields that are not needed.
2. Replace or remove the school starter’s instructional prose and example fields, or every `\placeholder{...}` in the alternative starters. The rendered starter intentionally shows unfinished fields. Keep unresolved factual gaps visibly marked in a draft; report them before calling it finished.
3. Adapt headings to the actual argument and assignment. The essay's argument/discussion structure and the report's method/results structure are starting points, not requirements. Do not invent an experiment to fill a Results section.
4. Preserve LaTeX syntax while editing prose. Escape literal `%`, `&`, `_`, `#`, and other special characters appropriately; do not escape genuine math or commands as prose. Keep labels and citation keys stable and use `\ref`/`\cite` instead of hard-coded numbering.
5. In the school starter, replace the inline sample `\bibitem` entries with verified references and keep `\cite` keys consistent. If no sources are available yet, leave a visible evidence gap instead of sample citations. The alternative starters use an initially empty `references.bib`; once verified entries and citations exist, uncomment their bibliography commands in `main.tex`. Use the required citation style. Do not mix inline bibliography, BibTeX, and biblatex/biber pipelines inadvertently.
6. For figures, use relative asset paths and supplied or authorized content. Inspect captions, units, labels, and cross-references. In two columns, size ordinary figures and tables to `\columnwidth` or `\linewidth`; use full-width floats only when needed.

For a local BibTeX build, run pdfLaTeX, BibTeX, then pdfLaTeX twice, or use a configured build tool such as latexmk. For the school starter’s inline bibliography, pdfLaTeX reruns are sufficient; do not run BibTeX unless the project has been deliberately converted to it. Use available compilers; do not claim a compile when only source inspection was possible.

## Verify and package

Compile the actual main file with the intended engine. Check the log for errors, unresolved citations/references, missing glyphs or files, and overfull boxes. A successful exit is not a visual review: inspect the rendered PDF, including later pages, tables, equations, references, and page breaks. Resolve layout problems within the required template rather than shrinking text or changing margins to evade a page limit.

For an Overleaf upload, create a ZIP containing the selected project's **contents**, with `main.tex` at the ZIP root. Include source, bibliography, and used image/style files; omit build outputs, editor files, caches, secrets, and unrelated documents. When redistributing an independently authored starter, include the repository's [MIT license](../LICENSE). Include the school starter's `NOTICE.md` with that starter; do not relabel school-supplied material as MIT. Do not upload the whole skill repository as a LaTeX project. Then follow [the Overleaf workflow](overleaf-workflow.md).

Deliver the source folder or ZIP, a PDF if compilation succeeded, and the exact unresolved issues. Distinguish a compilable starter from a completed academic submission.
