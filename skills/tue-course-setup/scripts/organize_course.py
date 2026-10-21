#!/usr/bin/env python3
"""File a Canvas download into a TU/e course folder.

Reads the newest <CODE>__manifest*.json and the <CODE>__M..__F<id>__* files from
the download folder, files them under course-materials/<kind>/, writes a dated
Canvas snapshot, and creates or updates COURSE.md. Standard library only.

Without --move it only checks and prints the plan. See references/course-layout.md.
"""

import argparse
import datetime as dt
import filecmp
import html
import json
import os
import re
import shutil
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

CANVAS = "https://canvas.tue.nl"
SYNC_START, SYNC_END = "<!-- canvas-sync:start -->", "<!-- canvas-sync:end -->"
README_START, README_END = "<!-- canvas-contents:start -->", "<!-- canvas-contents:end -->"
PARTIAL = (".crdownload", ".part", ".download")
VERIFIER = re.compile(r"([?&])verifier=[^&\"'\s<>\\]*&?")


def safe_name(name, limit=150):
    name = re.sub(r'[\\/:*?"<>|\x00-\x1f]', "_", str(name))
    name = re.sub(r"\s+", " ", name).strip().strip(".")
    return name[:limit] or "untitled"


def slug(text, limit=80):
    text = re.sub(r"[^\w\s-]", "", str(text).lower(), flags=re.UNICODE)
    return re.sub(r"[\s_-]+", "-", text).strip("-")[:limit] or "untitled"


def with_suffix_tag(path, tag):
    return path.with_name(f"{path.stem} ({tag}){path.suffix}")


def rel(target, start):
    """Relative POSIX link from directory `start` to `target`."""
    return Path(os.path.relpath(target, start)).as_posix()


def md_link_path(path):
    return path.replace(" ", "%20").replace("(", "%28").replace(")", "%29")


def fmt_size(n):
    n = n or 0
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024


def fmt_date(value):
    return value[:10] if value else "—"


# --- HTML to Markdown -------------------------------------------------------


class Markdown(HTMLParser):
    """Small, forgiving HTML→Markdown converter for Canvas rich text."""

    def __init__(self, link):
        super().__init__(convert_charrefs=True)
        self.link = link
        self.stack = [[]]  # output buffers; a table cell writes into its own buffer
        self.lists, self.href, self.tables = [], [], []
        self.skip = self.pre = 0

    @property
    def buf(self):
        return self.stack[-1]

    def in_cell(self):
        return len(self.stack) > 1

    def nl(self, n=1):
        if self.in_cell():
            self.buf.append(" ")
            return
        text = "".join(self.buf)
        have = len(text) - len(text.rstrip("\n"))
        if text and have < n:
            self.buf.append("\n" * (n - have))

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style"):
            self.skip += 1
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.nl(2)
            if not self.in_cell():
                self.buf.append("#" * min(int(tag[1]) + 1, 6) + " ")
        elif tag in ("p", "div", "section", "blockquote", "figure"):
            self.nl(2)
        elif tag == "br":
            self.buf.append(" " if self.in_cell() else "  \n")
        elif tag == "hr":
            self.nl(2)
            self.buf.append("---")
            self.nl(2)
        elif tag in ("ul", "ol"):
            self.nl(1 if self.lists else 2)
            self.lists.append([tag, 0])
        elif tag == "li":
            self.nl()
            depth = max(len(self.lists) - 1, 0)
            kind = self.lists[-1] if self.lists else ["ul", 0]
            kind[1] += 1
            marker = f"{kind[1]}. " if kind[0] == "ol" else "- "
            self.buf.append(marker if self.in_cell() else "  " * depth + marker)
        elif tag in ("strong", "b"):
            self.buf.append("**")
        elif tag in ("em", "i"):
            self.buf.append("*")
        elif tag == "code" and not self.pre:
            self.buf.append("`")
        elif tag == "pre":
            self.nl(2)
            self.buf.append("```\n")
            self.pre += 1
        elif tag == "a":
            self.href.append(self.link(a.get("href") or ""))
            self.buf.append("[")
        elif tag == "img":
            self.buf.append(f"![{a.get('alt') or 'image'}]({self.link(a.get('src') or '')})")
        elif tag == "iframe":
            self.nl(2)
            self.buf.append(f"[Embedded content]({self.link(a.get('src') or '')})")
            self.nl(2)
        elif tag == "table":
            self.tables.append({"rows": [], "row": None})
        elif tag == "tr" and self.tables:
            self.tables[-1]["row"] = []
        elif tag in ("td", "th") and self.tables:
            self.stack.append([])

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(self.skip - 1, 0)
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "section", "blockquote", "figure"):
            self.nl(2)
        elif tag in ("ul", "ol"):
            if self.lists:
                self.lists.pop()
            self.nl(2 if not self.lists else 1)
        elif tag in ("strong", "b"):
            self.buf.append("**")
        elif tag in ("em", "i"):
            self.buf.append("*")
        elif tag == "code" and not self.pre:
            self.buf.append("`")
        elif tag == "pre":
            self.nl()
            self.buf.append("```")
            self.nl(2)
            self.pre = max(self.pre - 1, 0)
        elif tag == "a":
            href = self.href.pop() if self.href else ""
            self.buf.append(f"]({href})" if href else "]")
        elif tag in ("td", "th") and self.in_cell():
            text = "".join(self.stack.pop())
            text = re.sub(r"\*\*\s*\*\*", "", text)
            text = " ".join(text.split()).replace("|", "\\|")
            table = self.tables[-1] if self.tables else None
            if table is not None:
                if table["row"] is None:
                    table["row"] = []
                table["row"].append(text)
        elif tag == "tr" and self.tables:
            table = self.tables[-1]
            if table["row"] is not None:
                table["rows"].append(table["row"])
            table["row"] = None
        elif tag == "table" and self.tables:
            self.render_table(self.tables.pop())

    def render_table(self, table):
        rows = [r for r in table["rows"] if any(c.strip() for c in r)]
        if not rows:
            return
        width = max(len(r) for r in rows)
        rows = [r + [""] * (width - len(r)) for r in rows]
        if self.in_cell():
            self.buf.append(" " + "; ".join(" / ".join(c for c in r if c) for r in rows) + " ")
            return
        lines = ["| " + " | ".join(rows[0]) + " |", "|" + " --- |" * width]
        lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
        self.nl(2)
        self.buf.append("\n".join(lines))
        self.nl(2)

    def handle_data(self, data):
        if self.skip:
            return
        self.buf.append(data if self.pre else re.sub(r"\s+", " ", data))

    def text(self):
        while self.in_cell():  # unclosed cells in malformed HTML
            self.stack[-2].extend(self.stack.pop())
        text = "".join(self.buf)
        text = re.sub(r"\*\*\s*\*\*", "", text)
        text = re.sub(r"\[\s*\]\([^)]*\)", "", text)
        text = re.sub(r"[ \t]+\n", "\n", text)
        # Drop stray leading spaces, but keep nested list indentation.
        text = "\n".join(l if re.match(r" {2,}(- |\d+\. )", l) else l.lstrip() for l in text.split("\n"))
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip() + "\n"


# --- Organizer --------------------------------------------------------------


class Organizer:
    def __init__(self, args):
        self.downloads = Path(args.downloads).expanduser()
        self.course = Path(args.course_dir).expanduser()
        self.mapping = json.loads(Path(args.mapping).read_text(encoding="utf-8"))
        self.code = self.mapping["code"]
        self.move = args.move
        self.materials = self.course / "course-materials"
        self.index_path = self.materials / "canvas-snapshots" / "files.json"
        self.index = json.loads(self.index_path.read_text(encoding="utf-8")) if self.index_path.exists() else {}
        self.manifest_path = self.find_manifest()
        self.manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.course_id = self.manifest["course"]["id"]
        self.filed = {}  # file id -> Path (this run and earlier runs)
        for fid, rec in self.index.items():
            self.filed[int(fid)] = self.course / rec["path"]
        self.report = {"filed": [], "already": [], "updated": [], "conflicts": [], "missing": [], "size_mismatch": [], "locked": [], "skipped": [], "adopted": []}

    def find_manifest(self):
        found = [p for p in self.downloads.glob(f"{self.code}__manifest*.json")]
        if not found:
            sys.exit(f"No {self.code}__manifest*.json in {self.downloads}")
        return max(found, key=lambda p: p.stat().st_mtime)

    def kind(self, f):
        """Folder for a file: a per-file entry wins over its module's; null means skip."""
        per_file = self.mapping.get("files", {})
        if str(f["id"]) in per_file:
            name = per_file[str(f["id"])]
        else:
            name = self.mapping.get("modules", {}).get(str(f["mi"]), "other")
        if name is None:
            return None
        if "/" in name or "\\" in name or name in ("", ".", ".."):
            sys.exit(f"Invalid folder name for file {f['id']}: {name!r}")
        return safe_name(name)

    def known(self, f):
        rec = self.index.get(str(f["id"]))
        return bool(rec and rec.get("size") == f.get("size") and rec.get("updated_at") == f.get("updated_at")
                    and (self.course / rec["path"]).exists())

    def find_download(self, f):
        prefix = f"{self.code}__M{int(f['mi']):02d}__F{f['id']}__"
        hits = [p for p in self.downloads.glob(prefix + "*") if not p.name.endswith(PARTIAL)]
        if not hits:
            return None
        sized = [p for p in hits if p.stat().st_size == f.get("size")]
        return max(sized or hits, key=lambda p: p.stat().st_mtime)

    def destination(self, f, planned):
        folder = self.materials / self.kind(f)
        dest = folder / safe_name(f["display_name"])
        previous = self.filed.get(f["id"])
        if previous is not None and previous.exists():
            dest = with_suffix_tag(dest, "updated " + dt.date.today().isoformat())
            if dest.exists() or dest in planned:
                dest = with_suffix_tag(dest, f"F{f['id']}")
            return dest, "updated"
        tracked = {p.resolve() for p in self.filed.values()}
        if dest in planned or (dest.exists() and dest.resolve() in tracked):
            return with_suffix_tag(dest, f"F{f['id']}"), "conflict"
        if dest.exists():
            # Filed earlier by hand or another tool, and different from Canvas's copy.
            dest = with_suffix_tag(dest, "updated " + dt.date.today().isoformat())
            return dest, "updated"
        return dest, "new"

    def untracked_copy(self, f):
        """A file filed earlier without this tool, at the place this one would go."""
        dest = self.materials / self.kind(f) / safe_name(f["display_name"])
        tracked = {p.resolve() for p in self.filed.values()}
        return dest if dest.exists() and dest.resolve() not in tracked else None

    def adopt(self, f, path, src=None):
        self.report["adopted"].append((f, path))
        self.filed[f["id"]] = path
        self.index[str(f["id"])] = {"path": rel(path, self.course), "size": f.get("size"),
                                    "updated_at": f.get("updated_at"), "display_name": f["display_name"]}
        if src is not None and self.move:
            src.unlink()

    def file_all(self):
        planned = set()
        for f in self.manifest["files"]:
            if f.get("locked"):
                self.report["locked"].append(f)
                continue
            if self.kind(f) is None:
                self.report["skipped"].append(f)
                src = self.find_download(f)
                if src and self.move:
                    src.unlink()
                continue
            if self.known(f):
                self.report["already"].append(f)
                src = self.find_download(f)
                if src and self.move:
                    src.unlink()
                continue
            src = self.find_download(f)
            existing = self.untracked_copy(f)
            if src is None:
                if existing is not None and existing.stat().st_size == f.get("size"):
                    self.adopt(f, existing)
                else:
                    self.report["missing"].append(f)
                continue
            if f.get("size") is not None and src.stat().st_size != f["size"]:
                self.report["size_mismatch"].append((f, src.stat().st_size))
                continue
            if existing is not None and filecmp.cmp(src, existing, shallow=False):
                self.adopt(f, existing, src)
                continue
            dest, state = self.destination(f, planned)
            planned.add(dest)
            self.report["updated" if state == "updated" else "conflicts" if state == "conflict" else "filed"].append((f, dest))
            if self.move:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
                if dest.stat().st_size != src.stat().st_size:
                    dest.unlink()
                    sys.exit(f"Copy size mismatch for {src.name}; download kept.")
                src.unlink()
                self.filed[f["id"]] = dest
                self.index[str(f["id"])] = {"path": rel(dest, self.course), "size": f.get("size"),
                                            "updated_at": f.get("updated_at"), "display_name": f["display_name"]}

    # links inside snapshot text
    def linker(self, from_dir):
        def link(href):
            if not href:
                return ""
            href = html.unescape(href)
            parts = urlsplit(href)
            if parts.scheme in ("mailto", "tel") or href.startswith("#"):
                return href
            path = parts.path
            page = re.search(r"/courses/\d+/pages/([^/?#]+)", path)
            if page and getattr(self, "snap", None) is not None:
                local = self.page_files.get(unquote(page.group(1)))
                if local is not None:
                    return md_link_path(rel(self.snap / local, from_dir))
            m = re.search(r"/courses/\d+/files/(\d+)", path)
            if m:
                local = self.filed.get(int(m.group(1)))
                if local is not None and local.exists():
                    return md_link_path(rel(local, from_dir))
                # Canvas file links can carry access tokens (verifier=...); drop the query.
                return f"{CANVAS}/courses/{self.course_id}/files/{m.group(1)}"
            if not parts.scheme:
                href = CANVAS + (href if href.startswith("/") else "/" + href)
            return href
        return link

    def md(self, body, from_dir):
        parser = Markdown(self.linker(from_dir))
        parser.feed(body or "")
        parser.close()
        return parser.text()

    def snapshot_dir(self):
        day = self.manifest["collected_at"][:10]
        base = self.materials / "canvas-snapshots" / day
        snap, n = base, 2
        while snap.exists():
            snap = base.with_name(f"{day}-{n}")
            n += 1
        return snap

    def write(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def write_snapshot(self):
        m, snap = self.manifest, self.snapshot_dir()
        self.snap, self.page_files = snap, {}
        title = f"{m['course']['name']}"
        unique = {}

        def unique_name(folder, base):
            key = (folder, base)
            unique[key] = unique.get(key, 0) + 1
            return base if unique[key] == 1 else f"{base}-{unique[key]}"

        self.write(snap / "syllabus.md", f"# Syllabus — {title}\n\n" + (self.md(m.get("syllabus"), snap) if m.get("syllabus") else "_No syllabus text on Canvas._\n"))

        page_links = {}
        for p in m.get("pages", []):
            page_links[p["url"]] = "pages/" + unique_name("pages", slug(p["title"] or p["url"])) + ".md"
        self.page_files = page_links
        for p in m.get("pages", []):
            name = page_links[p["url"]][len("pages/"):]
            head = f"# {p['title']}\n\nCanvas: {p.get('html_url') or ''}  \nUpdated: {fmt_date(p.get('updated_at'))}\n\n"
            self.write(snap / "pages" / name, head + self.md(p.get("body"), snap / "pages"))

        assignment_links = {}
        for a in m.get("assignments", []):
            name = unique_name("assignments", slug(a["name"])) + ".md"
            assignment_links[a["id"]] = f"assignments/{name}"
            lines = [f"# {a['name']}", "", f"Canvas: {a.get('html_url') or ''}  ",
                     f"Due: {fmt_date(a.get('due_at'))} · Available from: {fmt_date(a.get('unlock_at'))} · Until: {fmt_date(a.get('lock_at'))}  ",
                     f"Points: {a.get('points_possible') if a.get('points_possible') is not None else '—'} · Submission: {', '.join(a.get('submission_types') or []) or '—'}", ""]
            body = self.md(a.get("description"), snap / "assignments")
            lines.append(body if body.strip() else "_No description on Canvas._\n")
            if a.get("rubric"):
                lines += ["## Rubric", "", "| Criterion | Points | Ratings |", "| --- | --- | --- |"]
                for c in a["rubric"]:
                    ratings = "; ".join(f"{r.get('description') or ''} ({r.get('points')})" for r in c.get("ratings", []))
                    crit = (c.get("description") or "") + (f" — {c['long_description']}" if c.get("long_description") else "")
                    lines.append(f"| {crit.replace('|', '/')} | {c.get('points')} | {ratings.replace('|', '/')} |")
                lines.append("")
            self.write(snap / "assignments" / name, "\n".join(lines))

        for a in m.get("announcements", []):
            name = unique_name("announcements", f"{fmt_date(a.get('posted_at'))}-{slug(a['title'], 60)}") + ".md"
            head = f"# {a['title']}\n\nPosted: {fmt_date(a.get('posted_at'))} by {a.get('author') or 'unknown'}  \nCanvas: {a.get('html_url') or ''}\n\n"
            self.write(snap / "announcements" / name, head + self.md(a.get("message"), snap / "announcements"))

        files_by_id = {f["id"]: f for f in m.get("files", [])}
        out = [f"# Modules — {title}", "", f"Captured {m['collected_at'][:10]}. Local links point to filed copies; other items link to Canvas.", ""]
        not_downloadable = 0
        for mod in m.get("modules", []):
            out += [f"## {mod['mi']:02d} {mod['name']}", ""]
            if mod.get("unlock_at"):
                out += [f"Unlocks: {fmt_date(mod['unlock_at'])}", ""]
            if not mod.get("items"):
                out += ["_No items._", ""]
                continue
            for it in mod["items"]:
                t, label = it.get("type"), it.get("title") or "untitled"
                local = self.filed.get(it.get("content_id")) if t == "File" else None
                if t == "SubHeader":
                    out.append(f"- **{label}**")
                elif local is not None and local.exists():
                    out.append(f"- File: [{label}]({md_link_path(rel(local, snap))})")
                elif t == "Page" and it.get("page_url") in page_links:
                    out.append(f"- Page: [{label}]({page_links[it['page_url']]})")
                elif t == "Assignment" and it.get("content_id") in assignment_links:
                    out.append(f"- Assignment: [{label}]({assignment_links[it['content_id']]})")
                else:
                    target = it.get("external_url") or it.get("html_url") or ""
                    if t == "File" and files_by_id.get(it.get("content_id"), {}).get("locked"):
                        label += " (locked on Canvas)"
                    not_downloadable += t == "ExternalTool"
                    out.append(f"- {t}: [{label}]({target})" if target else f"- {t}: {label}")
            out.append("")
        if not m.get("modules"):
            out += ["_This course has no modules; its content is linked from pages._", ""]
        outside = [f for f in m.get("files", []) if f["mi"] == 0]
        if outside:
            out += ["## Files outside modules", ""]
            for f in outside:
                local = self.filed.get(f["id"])
                name = f["display_name"]
                if local is not None and local.exists():
                    entry = f"[{name}]({md_link_path(rel(local, snap))})"
                elif f.get("locked"):
                    entry = f"{name} (locked on Canvas)"
                elif self.kind(f) is None:
                    entry = f"{name} (skipped)"
                else:
                    entry = f"{name} (not filed)"
                out.append(f"- {entry} — from {f.get('source') or 'Canvas'}")
            out.append("")
        self.write(snap / "modules.md", "\n".join(out))
        self.not_downloadable = not_downloadable + len(self.report["locked"])

        # Raw capture for later diffs, without download URLs or file access tokens.
        raw = json.dumps(self.manifest, indent=1, ensure_ascii=False)
        self.write(snap / "canvas-manifest.json", VERIFIER.sub(r"\1", raw))

        r = self.report
        lines = [f"# Canvas snapshot {snap.name} — {title}", "",
                 f"Captured from {m['course']['url']} at {m['collected_at']} by tue-course-setup.", "",
                 "## Contents", "",
                 f"- [Modules](modules.md): {len(m.get('modules', []))}",
                 f"- [Syllabus](syllabus.md)",
                 f"- Pages: {len(m.get('pages', []))}",
                 f"- Assignments: {len(m.get('assignments', []))}",
                 f"- Announcements: {len(m.get('announcements', []))}",
                 f"- Files filed this sync: {len(r['filed']) + len(r['updated']) + len(r['conflicts'])}; already present: {len(r['already']) + len(r['adopted'])}; skipped by mapping: {len(r['skipped'])}",
                 f"- Not downloadable (locked, video, or external tool): {self.not_downloadable}", ""]
        if r["filed"] or r["updated"] or r["conflicts"]:
            lines += ["## Files filed", ""]
            for f, dest in r["filed"] + r["updated"] + r["conflicts"]:
                lines.append(f"- [{f['display_name']}]({md_link_path(rel(dest, snap))}) — {fmt_size(f.get('size'))}, from {f.get('source') or 'module %02d' % f['mi']}")
            lines.append("")
        if m.get("errors"):
            lines += ["## Collection errors", ""] + [f"- {e}" for e in m["errors"]] + [""]
        self.write(snap / "README.md", "\n".join(lines))

    def write_index_files(self):
        self.write(self.index_path, json.dumps(self.index, indent=1, ensure_ascii=False, sort_keys=True))
        readme = self.materials / "README.md"
        kinds = sorted(p.name for p in self.materials.iterdir() if p.is_dir() and p.name != "canvas-snapshots")
        block = [README_START] + [f"- [`{k}/`]({md_link_path(k)}/)" for k in kinds]
        block += [f"- [`canvas-snapshots/`](canvas-snapshots/) — latest: [{self.snap.name}]({md_link_path(rel(self.snap, self.materials))}/README.md)", README_END]
        block = "\n".join(block)
        if not readme.exists():
            name = self.manifest["course"]["name"]
            self.write(readme, f"# {name} course materials\n\nSource-faithful TU/e course materials downloaded from Canvas. Do not edit them.\n\n## Contents\n\n{block}\n")
        else:
            text = readme.read_text(encoding="utf-8")
            if README_START in text and README_END in text:
                text = re.sub(re.escape(README_START) + ".*?" + re.escape(README_END), lambda _: block, text, flags=re.S)
                self.write(readme, text)
            else:
                print(f"note: {readme} is hand-written; left unchanged. Add new folders to it if needed.")

        source = self.course / "external-sources" / "tue-canvas-course" / "SOURCE.md"
        if not source.exists():
            c = self.manifest["course"]
            self.write(source, f"---\ntitle: {c['name']} Canvas course\nurl: {c['url']}\npublisher: Eindhoven University of Technology\nsource_type: official-course-platform\naccessed_on: {self.manifest['collected_at'][:10]}\n---\n\n# TU/e Canvas course\n\nAuthenticated course root. Expiring download URLs are intentionally omitted.\n\n## Local attachments\n\nTU/e downloads from this course belong under `../../course-materials/`.\n")

    def sync_block(self):
        m, r = self.manifest, self.report
        c = m["course"]
        term = c.get("term") or {}
        start, end = c.get("start_at") or term.get("start_at"), c.get("end_at") or term.get("end_at")
        run = ", ".join(x for x in (term.get("name"), f"{fmt_date(start)} to {fmt_date(end)}" if start or end else None) if x)
        kept = [f for f in m.get("files", []) if not f.get("locked") and self.kind(f) is not None]
        total = sum(f.get("size") or 0 for f in kept)
        skipped = len(m.get("files", [])) - len(kept)
        lines = [SYNC_START, "## Canvas sync", "",
                 f"- Last synced: {m['collected_at'][:10]} with `tue-course-setup` ([snapshot]({md_link_path(rel(self.snap, self.course))}/README.md))"]
        if run:
            lines.append(f"- Course run: {run}")
        lines += [f"- Captured: {len(m.get('modules', []))} modules, {len(kept)} files ({fmt_size(total)}{f'; {skipped} skipped or locked' if skipped else ''}), "
                  f"{len(m.get('pages', []))} pages, {len(m.get('assignments', []))} assignments, {len(m.get('announcements', []))} announcements",
                  f"- Not downloaded: {self.not_downloadable} items (locked, video, or external; see the snapshot's module list)",
                  "",
                  "Agents: if this course is still running and the last sync is more than 14 days old, or a task needs course material "
                  "(a brief, rubric, slides, or template) that is not on disk, tell the student the course context may be out of date or "
                  "incomplete and offer to refresh it with `tue-course-setup`. Do not refresh without their go-ahead.",
                  SYNC_END]
        return "\n".join(lines)

    def write_course_md(self):
        path = self.course / "COURSE.md"
        block = self.sync_block()
        if path.exists():
            text = path.read_text(encoding="utf-8")
            if SYNC_START in text and SYNC_END in text:
                text = re.sub(re.escape(SYNC_START) + ".*?" + re.escape(SYNC_END), lambda _: block, text, flags=re.S)
            else:
                lines = text.split("\n")
                at = next((i for i, l in enumerate(lines) if l.startswith("# ")), None)
                at = len(lines) if at is None else at + 1
                lines[at:at] = ["", block]
                text = "\n".join(lines)
            self.write(path, text)
            return
        mp, c = self.mapping, self.manifest["course"]
        name = mp.get("course_name") or c["name"]
        year = mp.get("academic_year") or ""
        self.write(path, f"""---
course_name: {name}
course_code: {self.code}
institution: Eindhoven University of Technology
academic_year: {year}
document_role: course-index
---

# {name} — {self.code}

{block}

## Directory map

- `course-materials/` — TU/e-provided course files and dated Canvas snapshots; see its [README](course-materials/README.md).
- `external-sources/` — non-TU/e sources and source records.
- `notes/` — authored notes.
- `assignments/` — coursework and practical exercises.
- `projects/` — substantial course projects.
- `exam-prep/` — examination preparation.
- `submissions/` — frozen submitted artifacts.
- `archive/` — superseded or historical material.

## Agent rules

- Treat `course-materials/` as immutable TU/e material.
- Assignment briefs, rubrics, and required templates are under `course-materials/` and in the latest Canvas snapshot's `assignments/`; check them before writing coursework.
- Do not infer the current Canvas teaching order from older public resources.
- Keep this file factual and organizational; do not add study progress.

## Upload routing

- Route every new file before adding it to this course; never leave course content at the course root.
- Official TU/e course material goes in `course-materials/<kind-or-topic>/` unchanged; external references go in `external-sources/<source-slug>/`.
- Assignment work, project material, personal notes, exam preparation, and final hand-ins go respectively in `assignments/<slug>/`, `projects/<slug>/`, `notes/`, `exam-prep/`, and `submissions/` (create the destination only when needed).
- If the source or purpose is not clear, ask before filing it.

## Sources

- [TU/e Canvas course](external-sources/tue-canvas-course/SOURCE.md)
""")

    def print_plan(self):
        r = self.report
        verb = "Filed" if self.move else "Would file"
        for f, dest in r["filed"]:
            print(f"{verb}: {rel(dest, self.course)}")
        for f, dest in r["updated"]:
            print(f"{verb} (changed on Canvas, old copy kept): {rel(dest, self.course)}")
        for f, dest in r["conflicts"]:
            print(f"{verb} (name taken, renamed): {rel(dest, self.course)}")
        if r["adopted"]:
            print(f"Already filed by hand, now tracked: {len(r['adopted'])}")
        print(f"Already present: {len(r['already'])}; skipped by mapping: {len(r['skipped'])}; locked on Canvas: {len(r['locked'])}")
        for f, got in r["size_mismatch"]:
            print(f"SIZE MISMATCH (left in downloads): F{f['id']} {f['display_name']} expected {f.get('size')} got {got}")
        if r["missing"]:
            print("MISSING downloads (retry these ids):", json.dumps([f["id"] for f in r["missing"]]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--downloads", required=True, help="browser download folder")
    ap.add_argument("--course-dir", required=True, help="course folder, e.g. '~/Documents/TUe/Networks 2IRR20'")
    ap.add_argument("--mapping", required=True, help="module → folder JSON (see references/course-layout.md)")
    ap.add_argument("--move", action="store_true", help="file the downloads and write the snapshot (default: check only)")
    ap.add_argument("--print-known", action="store_true", help="print ids not to download (already filed and unchanged, or skipped by the mapping), then exit")
    ap.add_argument("--allow-missing", action="store_true", help="with --move, proceed even if some downloads are missing")
    args = ap.parse_args()

    org = Organizer(args)
    if args.print_known:
        print(json.dumps([f["id"] for f in org.manifest["files"] if org.known(f) or org.kind(f) is None]))
        return
    if org.move:
        # Check first so a partial download never produces a half-filed course.
        check = Organizer(argparse.Namespace(**{**vars(args), "move": False}))
        check.file_all()
        if (check.report["missing"] or check.report["size_mismatch"]) and not args.allow_missing:
            check.print_plan()
            sys.exit("Downloads incomplete; retry the missing ids or pass --allow-missing.")
    org.file_all()
    org.print_plan()
    if not org.move:
        return
    org.write_snapshot()
    org.write_index_files()
    org.write_course_md()
    org.manifest_path.unlink()
    print(f"Snapshot: {rel(org.snap, org.course)}")


if __name__ == "__main__":
    main()
