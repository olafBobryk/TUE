# TU/e agent skills for Claude Code and Codex

Agent skills for students at Eindhoven University of Technology (TU/e): an academic writing assistant with LaTeX and Overleaf support, and a Canvas course setup that downloads and organizes a whole course. They use the portable `SKILL.md` format, so they work in **Claude Code** and **Codex** (both used with these skills) and in other agents that read `SKILL.md` skills.

**Independent work by Olaf Bobryk. Not an official TU/e product and not affiliated with or endorsed by TU/e.**

| Skill | What it does |
| --- | --- |
| [`tue-academic-writing`](skills/tue-academic-writing/README.md) | Draft, revise, and review English academic writing based on the TU/e *Academic Writing Reader*, with LaTeX templates (the school's two-column starter by default) and an Overleaf workflow. |
| [`tue-course-setup`](skills/tue-course-setup/README.md) | Download a Canvas course through your signed-in browser and file it into a course folder with a `COURSE.md` index, a dated Canvas snapshot, and a sync record that tells later agents when to refresh. |

The two work together: course setup puts each course's briefs, rubrics, and templates on disk and records when Canvas was last synced; the writing skill reads that `COURSE.md` to find them and flags stale course context before writing.

## Install

**Claude Code** (plugin marketplace):

```text
/plugin marketplace add olafBobryk/TUE
/plugin install tue-skills --marketplace olafBobryk/TUE
```

**Claude Code or Codex** with the [skills CLI](https://github.com/vercel-labs/skills):

```sh
npx skills add olafBobryk/TUE --agent claude-code
npx skills add olafBobryk/TUE --agent codex --global
```

Leave out `--agent` to choose interactively. Install a single skill with `--skill tue-course-setup` or `--skill tue-academic-writing`. Update later with `npx skills update`.

## Use

- Claude Code: ask in plain words, or run `/tue-academic-writing` or `/tue-course-setup`.
- Codex: mention `$tue-academic-writing` or `$tue-course-setup`.

Example: “Set up my Networks course from Canvas”, then “Review my essay draft against the assignment brief”.

## License

Original repository content: [MIT](LICENSE), copyright 2026 Olaf Bobryk. School-supplied material is excluded; see the [school template notice](skills/tue-academic-writing/assets/templates/tue-school-essay/NOTICE.md).
