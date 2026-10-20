# TU/e Academic Writing

An agent skill for drafting, revising, and reviewing English academic essays and reports. It turns the core principles of the TU/e Language and Writing Center's *Academic Writing Reader* into practical writing guidance.

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

## What it checks

- A clear main message and supporting claims connected to evidence through explicit reasoning.
- Purposeful paragraphs and readable connections between sentences and sections.
- Precise, concise language with conclusions no stronger than the evidence supports.
- Faithful paraphrasing, clear attribution, and consistent referencing.

The skill follows the requested mode and assignment constraints. It flags evidence gaps rather than inventing sources or results, and it distinguishes reviewing citations from verifying the underlying sources. It does not certify grades, institutional approval, or submission readiness.

## Source and attribution

Based on the TU/e Language and Writing Center's *Academic Writing Reader*, a 17-page reader supplied as university course material. The [review guidance](references/writing-guidance.md) identifies the relevant page ranges and explains contextual adaptations.

The university PDF is not included. Instructions and examples in this repository are independently written; the skill works without access to the source document. MIT licensing applies to this repository's original content, not to the TU/e reader, name, or branding.

## Sharing and updates

This GitHub repository is the distribution source. According to the [skills.sh FAQ](https://www.skills.sh/docs/faq), skills can appear in its directory through installation telemetry; publication does not guarantee immediate listing. No separate npm package or marketplace upload is required.

For updates through the skills CLI:

```sh
npx skills update
```

## License

[MIT](LICENSE), copyright 2026 Olaf Bobryk.
