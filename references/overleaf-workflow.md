# Overleaf editing and iteration

Read this reference when the user asks to create, edit, or iterate on an Overleaf project. Read [LaTeX templates](latex-templates.md) when selecting or importing a starter. For prose changes, the full writing guidance remains required.

## Establish the project and tools

Use an available supported Overleaf integration or browser-control tool. This skill supplies instructions and assets; it does not install a browser controller, authenticate an account, or provide an Overleaf API. Follow the host tool's interaction and permission rules. Without authenticated project access or an editing tool, prepare a local source/ZIP and explain the specific missing capability; do not imply that Overleaf was updated.

Confirm the target project from the user's link or visible project list. Inspect its title, file tree, main document, compiler, and relevant source before editing. Read the assignment requirements and identify the requested scope. Do not assume that an open editor is the intended project.

For an existing Overleaf task, treat the live project as the source of truth unless the user establishes another source. Read fresh contents before applying changes; a local mirror or previous chat excerpt may be stale. Preserve collaborator changes, comments, custom commands, citation keys, and existing layout. If authorship changes overlap the intended passage, reconcile them or ask about the actual conflict rather than replacing the entire file.

## Start or import

- For an existing project, use its current structure. Record the relevant starting contents or download a source backup when substantial edits need a recoverable checkpoint. Use available history features when helpful; do not assume every account has the same history access.
- For a new bundled template, prepare the selected template ZIP as described in the template reference. Use the visible project creation/upload controls. Verify the resulting file tree and explicitly check `main.tex` is selected as the main document and pdfLaTeX as the compiler.
- For a user-supplied template, retain its dependencies and intended engine. Check for missing files before trying to repair unrelated source. Do not publish or share the user's project as a side effect of importing it.

## Edit, compile, inspect, repeat

1. **Inspect the current source.** Use the code editor for LaTeX changes. Virtualized editors may expose only visible lines in accessibility text; do not mistake that excerpt for the whole file. Use a supported full-source export, editor selection/copy, or another documented reading method when the whole file is needed.
2. **Make a bounded change.** Edit the relevant passage or file, retaining the rest of the project. For review-only requests, provide findings rather than changing source; for grammar-only requests, do not restructure the document or apply a new template. Read back the changed source and check that the editor has saved/synchronized before navigating away or exporting. If the UI offers no explicit saved indicator, verify persistence by reopening the file or project after the save has had time to complete.
3. **Compile the current revision.** Trigger Recompile and observe completion. Inspect the log, not merely the existence of a PDF: Overleaf may display an older PDF or produce one despite errors. Use stop-on-first-error when it helps isolate the first actual source error; later errors can be consequences of it.
4. **Classify failures.** Fix source errors at their reported location. Resolve missing bibliography keys or cross-references from supplied evidence, not invented entries. For a timeout, disconnect, or service failure, preserve edits and distinguish the infrastructure failure from a LaTeX error. Recompile from scratch can help stale auxiliary data; it is not a substitute for fixing source.
5. **Inspect the new PDF.** Verify a changed passage or other visible marker to establish freshness. Check affected pages and any later pages whose layout shifted, including column overflow, table widths, math, captions, bibliography, and page count. Download/render the PDF with an available tool if the browser preview cannot be inspected adequately.
6. **Iterate toward the requested outcome.** Make the next change based on a concrete log or visual finding, then recompile. Do not keep repeating identical failing actions. After three unsuccessful repair attempts for the same issue, preserve the current source, report the precise blocker and attempted fixes, and continue only with independent work or a materially different supported approach.

Before a later edit, reread the target passage if a collaborator or another tool may have changed it. Never overwrite a collaborative project from an old local copy to force convergence. Keep template settings fixed unless a change is required by the assignment or explicitly requested.

## Deliver and state what was verified

Give the direct project link and a concise description of the change. Report separately whether the edit persisted, compilation succeeded, and the rendered PDF was inspected. Include source or PDF exports when requested. Identify remaining citation gaps, placeholders, warnings, access problems, or compilation limits specifically.

A compile does not establish factual accuracy, source support, course compliance, or readiness for submission. Do not submit, change sharing permissions, or invite collaborators merely to complete a writing or layout task.
