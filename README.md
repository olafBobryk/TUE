# TU/e skills

Agent skills for students at Eindhoven University of Technology (TU/e). They use the portable `SKILL.md` format and work with Codex, Claude Code, and other compatible agents.

**Independent work by Olaf Bobryk. Not an official TU/e product and not affiliated with or endorsed by TU/e.**

| Skill | What it does |
| --- | --- |
| [`tue-academic-writing`](skills/tue-academic-writing/README.md) | Draft, revise, and review English academic writing based on the TU/e *Academic Writing Reader*, with LaTeX templates (the school's two-column starter by default) and an Overleaf workflow. |
| [`tue-course-setup`](skills/tue-course-setup/README.md) | Download a Canvas course through your signed-in browser and file it into a course folder with a `COURSE.md` index, a dated Canvas snapshot, and a sync record that tells later agents when to refresh. |

The two work together: course setup puts each course's briefs, rubrics, and templates on disk and records when Canvas was last synced; the writing skill reads that `COURSE.md` to find them and flags stale course context before writing.

## Install

Install with the [skills CLI](https://github.com/vercel-labs/skills) and choose the skills and agents:

```sh
npx skills add olafBobryk/TUE
```

Or install one skill globally for one agent, for example:

```sh
npx skills add olafBobryk/TUE --skill tue-course-setup --agent codex --global
```

Update installed skills with `npx skills update`.

## License

Original repository content: [MIT](LICENSE), copyright 2026 Olaf Bobryk. School-supplied material is excluded; see the [school template notice](skills/tue-academic-writing/assets/templates/tue-school-essay/NOTICE.md).
