# TU/e Academic Writing

An agent skill for drafting, revising, and reviewing English academic essays and reports. Version **1.1.0** carries over every writing-related instruction from the TU/e Language and Writing Center's 17-page *Academic Writing Reader*, including the lessons in its figures, examples, footnote, and resource recommendations.

**Independent adaptation by Olaf Bobryk. Not an official TU/e product and not affiliated with or endorsed by TU/e.**

## Install

Install with the [skills CLI](https://github.com/vercel-labs/skills), then choose your agent:

```sh
npx skills add olafBobryk/tue-academic-writing
```

To install globally for Codex:

```sh
npx skills add olafBobryk/tue-academic-writing --skill tue-academic-writing --agent codex --global
```

The skill uses the portable `SKILL.md` format and has no scripts, API keys, external services, or PDF dependency. Codex display metadata is included; other compatible agents can use the core instructions.

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

The [complete writing guide](references/writing-guidance.md) is required reading whenever the skill runs. The short `SKILL.md` entrypoint routes the agent into that guide; it does not replace the guide with a summary. The [source coverage record](references/source-coverage.md) maps each substantive source section, figure, footnote, and example lesson to its destination.

The skill follows the requested mode and assignment constraints. It flags evidence gaps rather than inventing sources or results, and it distinguishes reviewing citations from verifying the underlying sources. It does not certify grades, institutional approval, or submission readiness.

## Source and attribution

Based on the TU/e Language and Writing Center's *Academic Writing Reader*, a 17-page reader supplied as university course material. The complete guide identifies the relevant page ranges. The source's recommendations remain the defaults, with explicit assignment or publication requirements taking precedence when they differ.

The university PDF is not included. Instructions and examples in this repository are independently written; the skill works without access to the source document. MIT licensing applies to this repository's original content, not to the TU/e reader, name, or branding.

## Sharing and updates

This GitHub repository is the distribution source. According to the [skills.sh FAQ](https://www.skills.sh/docs/faq), skills can appear in its directory through installation telemetry; publication does not guarantee immediate listing. No separate npm package or marketplace upload is required.

Existing installations do not receive repository changes automatically. To fetch the latest versions of installed skills through the skills CLI:

```sh
npx skills update
```

To install or refresh just this skill globally for Codex:

```sh
npx skills add olafBobryk/tue-academic-writing --skill tue-academic-writing --agent codex --global --yes
```

Both commands retrieve published repository content. Version `1.1.0` is recorded in the skill metadata; this revision replaces the earlier condensed guide with complete writing-guidance coverage. A fresh or refreshed installation should include `references/writing-guidance.md` and `references/source-coverage.md` alongside `SKILL.md`.

## License

[MIT](LICENSE), copyright 2026 Olaf Bobryk.
