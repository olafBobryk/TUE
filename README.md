# TU skills for Claude Code and Codex

Agent skills for students at Dutch technical universities, starting with **TU/e (Eindhoven)** and **TU Delft**: an academic writing assistant with LaTeX and Overleaf support, and a course setup that downloads a whole Canvas or Brightspace course into an organized folder. They use the portable `SKILL.md` format, so they work in **Claude Code** and **Codex** (both used with these skills) and in other agents that read `SKILL.md` skills.

**Independent work by Olaf Bobryk. Not an official TU/e or TU Delft product and not affiliated with or endorsed by either university.**

| Skill | What it does | University support |
| --- | --- | --- |
| [`tu-course-setup`](skills/tu-course-setup/README.md) | Download a course through your signed-in browser and file it into a course folder with a `COURSE.md` index, a dated snapshot, and a sync record that tells later agents when to refresh. | TU/e on **Canvas**: tested live. TU Delft on **Brightspace**: experimental, tested only against a mock of the documented API. |
| [`tue-academic-writing`](skills/tue-academic-writing/README.md) | Draft, revise, and review English academic writing based on the TU/e *Academic Writing Reader*, with LaTeX templates (the school's two-column starter by default) and an Overleaf workflow. | Guidance is based on the TU/e reader; the general writing advice applies anywhere. It reads course folders from either platform. TU Delft's own writing guidance is not included. |

The two work together: course setup puts each course's briefs, rubrics, and templates on disk and records when it was last synced; the writing skill reads that `COURSE.md` to find them and flags stale course context before writing.

## Install

**Claude Code** (plugin marketplace):

```text
/plugin marketplace add olafBobryk/tu-skills
/plugin install tu-skills --marketplace olafBobryk/tu-skills
```

**Claude Code or Codex** with the [skills CLI](https://github.com/vercel-labs/skills):

```sh
npx skills add olafBobryk/tu-skills --agent claude-code
npx skills add olafBobryk/tu-skills --agent codex --global
```

Leave out `--agent` to choose interactively. Install a single skill with `--skill tu-course-setup` or `--skill tue-academic-writing`. The repository was called `TUE` before version 1.4.0; old links and `olafBobryk/TUE` still redirect. Update later with `npx skills update`.

## Use

- Claude Code: ask in plain words, or run `/tue-academic-writing` or `/tu-course-setup`.
- Codex: mention `$tue-academic-writing` or `$tu-course-setup`.

Example: “Set up my Networks course from Canvas”, then “Review my essay draft against the assignment brief”.

## Contribute

Issues, discussions, and pull requests are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md). The most useful thing right now is a [Brightspace test report](https://github.com/olafBobryk/tu-skills/issues/new?template=brightspace-test-report.yml), for example from a TU Delft student.

## License

Original repository content: [MIT](LICENSE), copyright 2026 Olaf Bobryk. School-supplied material is excluded; see the [school template notice](skills/tue-academic-writing/assets/templates/tue-school-essay/NOTICE.md).
