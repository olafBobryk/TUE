# Contributing

Thanks for helping. This repository holds agent skills for students at Dutch technical universities, starting with TU/e and TU Delft. Issues, discussions, and pull requests are all welcome.

## Ways to help

- **Test the Brightspace path.** `tu-course-setup` supports Brightspace (for example TU Delft) but has only been tested against a mock of D2L's API. A [Brightspace test report](https://github.com/olafBobryk/tu-skills/issues/new?template=brightspace-test-report.yml) is the most useful contribution right now, whether it worked or not.
- **Report bugs** or **suggest a university or platform** with an issue.
- **Ask questions or share what worked** in [Discussions](https://github.com/olafBobryk/tu-skills/discussions).
- **Open a pull request** for a fix or improvement. For anything larger than a small fix, open an issue or discussion first so we can agree on the approach.

## Please never share

Passwords, cookies, access tokens, signed download links, or private course material and personal data (grades, submissions, group details). Describe what you saw instead, and remove names and links from output you paste. Test fixtures must be made up.

## Working on the skills

- Each skill lives in `skills/<name>/` with a `SKILL.md`; keep instructions short and put detail in `references/`.
- `skills/tu-course-setup/scripts/organize_course.py` uses only the Python standard library. After a change, run it on made-up data covering a first setup and a refresh, and say what you tested in the pull request.
- Keep claims honest: say what was tested live, what only against a mock, and what is untested.
- `COURSE.md` files stay factual and organizational; skills must not add study progress or invented course content.
- Run `claude plugin validate .` after editing `.claude-plugin/marketplace.json`.

By contributing you agree that your contribution is licensed under the repository's [MIT license](LICENSE). School-supplied material, such as the TU/e essay template, keeps its own notice and is not relicensed.
