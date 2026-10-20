# TU/e Academic Writing

An agent skill for drafting, revising, and reviewing English academic essays and reports. Version **1.2.1** carries over every writing-related instruction from the TU/e Language and Writing Center's 17-page *Academic Writing Reader*, including the lessons in its figures, examples, footnote, and resource recommendations.

**Independent adaptation by Olaf Bobryk. Not an official TU/e product and not affiliated with or endorsed by TU/e.**

## Install

Install with the [skills CLI](https://github.com/vercel-labs/skills), then choose your agent:

```sh
npx skills add olafBobryk/TUE
```

To install globally for Codex:

```sh
npx skills add olafBobryk/TUE --skill tue-academic-writing --agent codex --global
```

The skill uses the portable `SKILL.md` format and has no executable helpers, API keys, or original-reader PDF dependency. Local LaTeX compilation requires a TeX compiler; the optional Overleaf workflow requires an authenticated project and an agent with browser control or a supported editing integration. The skill itself does not provide those tools. Codex display metadata is included; other compatible agents can use the core instructions.

## Use

In Codex, invoke `$tue-academic-writing` explicitly or let it be selected for relevant academic writing requests. Supply your assignment requirements, text or notes, and available evidence.

Example requests:

- “Use $tue-academic-writing to draft an introduction from these notes. Mark any missing evidence.”
- “Use $tue-academic-writing to revise this section for clarity while preserving my claims, citations, and technical details.”
- “Use $tue-academic-writing to review this essay. Give feedback on argumentation, readability, academic style, and referencing without rewriting it.”
- “Use $tue-academic-writing for a grammar-only pass on this paragraph. Keep its content and structure.”

## What is included

- The iterative prewriting, drafting, and evaluating process, including peer feedback and the cycle of collecting, inventorying, and extending source material.
- Main and supporting arguments; claim, evidence, and reasoning; relevance, strength, reliability, and accurate source representation.
- Standard paragraph structure, its exceptions, and the different jobs of conclusions and transitions.
- All four cohesion strategies and the distinction between a missing connector and missing explanatory information.
- Every listed style convention, with the reader's disciplinary qualifications preserved.
- Quotation formatting, paraphrasing, summarizing, source boundaries, tone and emphasis, note-taking advice, and citation styles.
- All writing resources linked by the reader, identified as source-provided addresses rather than guaranteed current links.

The agent reads `SKILL.md` and the [complete writing guide](references/writing-guidance.md). All writing guidance stays together. The optional LaTeX and Overleaf references are loaded only for those tasks. Both files contain actionable instructions and examples, without source page numbers, figure labels, or adaptation commentary.

Human-facing material stays here and in the [source coverage record](docs/source-coverage.md): attribution, installation instructions, provenance, source interpretation, and the mapping of every substantive source section, figure, footnote, and example lesson. These documents are outside the agent's required reading path.

The skill follows the requested mode and assignment constraints. It flags evidence gaps rather than inventing sources or results, and it distinguishes reviewing citations from verifying the underlying sources. It does not certify grades, institutional approval, or submission readiness.

## LaTeX templates and Overleaf

Version **1.2.1** makes the school-supplied **two-column essay template the default** for new LaTeX documents. A different requested or required format still takes precedence. The bundle includes:

- [TU/e school essay — default](assets/templates/tue-school-essay/main.tex): the supplied source, with its paper subtitle, three author blocks, abstract/section instructions, and inline bibliography. Only the filename is changed. Replace its sample references and unused author fields before use.
- [Academic essay](assets/templates/academic-essay/main.tex): single-column article with an argument/discussion structure.
- [IEEE report](assets/templates/ieee-report/main.tex): two-column technical report using the standard `IEEEtran` class.

Download an Overleaf-ready ZIP from [release 1.2.1](https://github.com/olafBobryk/TUE/releases/tag/v1.2.1), then use Overleaf’s **New project → Existing project (.zip)**. Each ZIP contains one template with `main.tex` at its root. The school starter includes its attribution notice; the independently authored starters include the MIT license.

Copy the whole chosen template folder. All three use pdfLaTeX. The school starter keeps sections and bibliography inline in `main.tex`; its sample references are demonstrations, not evidence. The two independent alternatives have `sections/body.tex` and an empty `references.bib`. The school source is attributed in its [notice](assets/templates/tue-school-essay/NOTICE.md); the other starters are general alternatives, not official TU/e or publisher-approved templates. Use the current assignment’s own template when supplied.

The [template guide](references/latex-templates.md) explains selection, filling fields, bibliography setup, compilation, and ZIP packaging. The [Overleaf workflow](references/overleaf-workflow.md) covers importing a project, preserving live collaborative changes, editing, checking compilation logs, inspecting the PDF, and iterating on concrete findings. A skill installation does not grant browser access or log in to Overleaf.

Example requests:

- “Use $tue-academic-writing to create a LaTeX essay from these notes and export an Overleaf-ready ZIP. Keep missing evidence marked.”
- “Use $tue-academic-writing with this required course template. Preserve its layout and citation style.”
- “Use $tue-academic-writing to revise the introduction in this Overleaf project, recompile, and inspect the PDF for layout problems.”
- “Review this Overleaf report without changing its source.”

The [validation record](docs/latex-validation.md) distinguishes local template builds from live Overleaf verification.

## Source and attribution

Based on the TU/e Language and Writing Center's *Academic Writing Reader*, a 17-page reader supplied as university course material. The human-facing coverage record identifies the relevant page ranges and source interpretation notes. The source's recommendations remain the defaults, with explicit assignment or publication requirements taking precedence when they differ.

The university PDF is not included. The writing instructions and examples are independently written; the skill works without access to the source reader. The school LaTeX template is the separately attributed exception described below. MIT licensing applies to this repository's original content, not to the TU/e reader, name, or branding. The two generic LaTeX starters and workflow are independent additions, not guidance attributed to the reader. The school starter preserves separately attributed course-supplied source; it is not covered by this repository’s MIT license. LaTeX packages such as `IEEEtran` remain separately licensed dependencies supplied by your TeX distribution; their source is not bundled here.

## Sharing and updates

This GitHub repository is the distribution source. According to the [skills.sh FAQ](https://www.skills.sh/docs/faq), skills can appear in its directory through installation telemetry; publication does not guarantee immediate listing. No separate npm package or marketplace upload is required.

Existing installations do not receive repository changes automatically. To fetch the latest versions of installed skills through the skills CLI:

```sh
npx skills update
```

To install or refresh just this skill globally for Codex:

```sh
npx skills add olafBobryk/TUE --skill tue-academic-writing --agent codex --global --yes
```

Both commands retrieve published repository content. Version `1.2.1` is recorded in the skill metadata; this revision adds the school-supplied essay starter and makes its two-column layout the default. The skill name remains `tue-academic-writing`, and the complete writing guidance is unchanged. A fresh or refreshed installation should include `references/writing-guidance.md` alongside `SKILL.md`; the human-facing coverage record is in `docs/source-coverage.md`.

## License

Original repository content: [MIT](LICENSE), copyright 2026 Olaf Bobryk. The school-supplied template is excluded; see its [notice](assets/templates/tue-school-essay/NOTICE.md).
