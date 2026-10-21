# Canvas collection

Run these scripts in a `canvas.tue.nl` tab through the browser tool's JavaScript runner. They use the student's own session; nothing here handles credentials.

- Canvas prefixes JSON with `while(1);`; the helpers strip it.
- Courses are built in two ways, and the script handles both: **modules** (files listed per week or topic), or a **wiki home page** whose links lead to other pages and files. Students often get **403/404** on the files list and the pages list, so the script follows links from the front page, syllabus, assignments, and announcements instead.
- Start long scripts **without awaiting them** (awaiting can hit tool timeouts) and poll `window._tue` instead.
- Never print download URLs: Canvas signs them, and tools may block output that contains them. Status calls return counts only.

## 1. Find the course

```js
(async () => {
  const r = await fetch('/api/v1/courses?per_page=100&enrollment_state=active&include[]=term', {headers: {Accept: 'application/json'}});
  const list = JSON.parse((await r.text()).replace(/^while\(1\);/, ''));
  return list.map(c => ({id: c.id, name: c.name, code: c.course_code.split(/\s+/)[0], term: c.term && c.term.name}));
})()
```

If the course is missing, retry without `enrollment_state=active` (finished or future courses). Canvas's `course_code` usually includes the course name (`2IRR20 Networks`); the snippet keeps the first word. Confirm the code with the student when it does not look like a TU/e code.

## 2. Collect

Set the course id and code in the last line, then run without awaiting:

```js
window._tue = {status: 'collecting', errors: []};
(async (C, CODE) => {
  const T = window._tue;
  const parse = async r => JSON.parse((await r.text()).replace(/^while\(1\);/, ''));
  const one = async u => {
    const r = await fetch(u, {headers: {Accept: 'application/json'}});
    if (!r.ok) throw new Error(r.status + ' ' + u);
    return parse(r);
  };
  const all = async u => {
    let out = [];
    while (u) {
      const r = await fetch(u, {headers: {Accept: 'application/json'}});
      if (!r.ok) throw new Error(r.status + ' ' + u);
      out = out.concat(await parse(r));
      const m = /<([^>]+)>;\s*rel="next"/.exec(r.headers.get('Link') || '');
      u = m ? m[1] : null;
    }
    return out;
  };
  const soft = async (label, fn, fallback) => {
    try { return await fn(); } catch (e) { T.errors.push(label + ': ' + e.message); return fallback; }
  };
  const safe = s => String(s).replace(/[\\/:*?"<>|\u0000-\u001f]/g, '_').replace(/\s+/g, ' ').trim().slice(0, 150);
  const fileIds = html => [...String(html).matchAll(/(?:\/courses\/(\d+))?\/files\/(\d+)/g)]
    .filter(m => !m[1] || Number(m[1]) === C).map(m => Number(m[2]));
  const pageSlugs = html => [...String(html).matchAll(new RegExp(`/courses/${C}/pages/([^"'?#<>\\s/]+)`, 'g'))]
    .map(m => { try { return decodeURIComponent(m[1]); } catch (e) { return m[1]; } });

  T.status = 'course';
  const course = await one(`/api/v1/courses/${C}?include[]=syllabus_body&include[]=term`);
  const modules = await soft('modules', () => all(`/api/v1/courses/${C}/modules?per_page=100&include[]=items`), []);
  for (const [i, m] of modules.entries()) {
    m.mi = i + 1;
    if (!m.items) m.items = await soft('module items ' + m.id, () => all(`/api/v1/courses/${C}/modules/${m.id}/items?per_page=100`), []);
  }

  const files = new Map();
  const addFile = async (id, mi, source) => {
    id = Number(id);
    if (files.has(id)) return;
    files.set(id, null);
    const f = await soft('file ' + id, () => one(`/api/v1/files/${id}`), null);
    if (!f) { files.delete(id); return; }
    files.set(id, {
      id, mi, source, display_name: f.display_name, size: f.size,
      content_type: f['content-type'], updated_at: f.updated_at,
      locked: !!f.locked_for_user || !f.url, url: f.url,
      download_name: `${CODE}__M${String(mi).padStart(2, '0')}__F${id}__${safe(f.display_name)}`,
    });
  };
  T.status = 'module files';
  for (const m of modules) for (const it of m.items) if (it.type === 'File') await addFile(it.content_id, m.mi, 'Module: ' + m.name);

  T.status = 'assignments';
  const assignments = (await soft('assignments', () => all(`/api/v1/courses/${C}/assignments?per_page=100`), [])).map(a => ({
    id: a.id, name: a.name, due_at: a.due_at, unlock_at: a.unlock_at, lock_at: a.lock_at,
    points_possible: a.points_possible, submission_types: a.submission_types, html_url: a.html_url,
    description: a.description || '',
    rubric: (a.rubric || []).map(c => ({description: c.description, long_description: c.long_description, points: c.points,
      ratings: (c.ratings || []).map(r => ({description: r.description, long_description: r.long_description, points: r.points}))})),
  }));

  T.status = 'announcements';
  const announcements = (await soft('announcements', () => all(`/api/v1/announcements?context_codes[]=course_${C}&per_page=100&start_date=2000-01-01&end_date=2100-01-01`), [])).map(a => ({
    id: a.id, title: a.title, posted_at: a.posted_at, author: a.author && a.author.display_name, html_url: a.html_url, message: a.message || '',
  }));

  // Pages: the front page, the pages list when students may see it, module pages, and every page linked from those.
  T.status = 'pages';
  const front = await soft('front page', () => one(`/api/v1/courses/${C}/front_page`), null);
  const pageList = await soft('pages list (often 404 for students)', () => all(`/api/v1/courses/${C}/pages?per_page=100`), []);
  const queue = [...pageList.map(p => p.url)];
  for (const m of modules) for (const it of m.items) if (it.type === 'Page' && it.page_url) queue.push(it.page_url);
  for (const h of [course.syllabus_body, ...assignments.map(a => a.description), ...announcements.map(a => a.message)]) queue.push(...pageSlugs(h || ''));
  const pages = [], seen = new Set();
  const keep = p => {
    if (seen.has(p.url)) return;
    seen.add(p.url);
    pages.push({url: p.url, title: p.title, front_page: !!p.front_page, html_url: p.html_url, updated_at: p.updated_at, body: p.body || ''});
    queue.push(...pageSlugs(p.body || ''));
  };
  if (front) keep(front);
  while (queue.length && pages.length < 300) {
    const u = queue.shift();
    if (seen.has(u)) continue;
    const p = await soft('page ' + u, () => one(`/api/v1/courses/${C}/pages/${encodeURIComponent(u)}`), null);
    if (p) keep(p);
    seen.add(u);
  }

  T.status = 'linked files';
  const sources = [
    ...pages.map(p => ['Page: ' + p.title, p.body]),
    ['Syllabus', course.syllabus_body || ''],
    ...assignments.map(a => ['Assignment: ' + a.name, a.description]),
    ...announcements.map(a => ['Announcement: ' + a.title, a.message]),
  ];
  for (const [source, h] of sources) for (const id of fileIds(h)) await addFile(id, 0, source);
  const courseFiles = await soft('files list (often 403 for students)', () => all(`/api/v1/courses/${C}/files?per_page=100`), []);
  for (const f of courseFiles) await addFile(f.id, 0, 'Course files');

  T.code = CODE;
  T.files = [...files.values()].filter(Boolean);
  T.manifest = {
    schema: 1, collected_at: new Date().toISOString(), code: CODE,
    course: {id: course.id, name: course.name, course_code: course.course_code, url: `${location.origin}/courses/${C}`,
      default_view: course.default_view, start_at: course.start_at, end_at: course.end_at,
      term: course.term && {name: course.term.name, start_at: course.term.start_at, end_at: course.term.end_at}},
    syllabus: course.syllabus_body || '',
    modules: modules.map(m => ({mi: m.mi, id: m.id, name: m.name, unlock_at: m.unlock_at,
      items: m.items.map(it => ({type: it.type, title: it.title, content_id: it.content_id, page_url: it.page_url, html_url: it.html_url, external_url: it.external_url}))})),
    files: T.files.map(({url, ...rest}) => rest),
    pages, assignments, announcements, errors: T.errors,
  };
  T.status = 'collected';
})(COURSE_ID, 'CODE').catch(e => { window._tue.status = 'failed: ' + e.message; });
'started'
```

Poll with:

```js
(() => { const T = window._tue || {}, M = T.manifest, fs = T.files || [];
  return {status: T.status, files: fs.length, locked: fs.filter(f => f.locked).length,
    mb: Math.round(fs.reduce((s, f) => s + (f.size || 0), 0) / 1e6), errors: T.errors,
    modules: M && M.modules.length, pages: M && M.pages.length, assignments: M && M.assignments.length,
    announcements: M && M.announcements.length}; })()
```

To propose the folder mapping, list modules (`window._tue.manifest.modules.map(m => [m.mi, m.name, m.items.length])`) and, for files outside modules, `window._tue.files.filter(f => f.mi === 0).map(f => [f.id, f.display_name, f.source])`.

## 3. Check that downloads reach the disk

Save the manifest first, then look for `<CODE>__manifest.json` in the download folder. If it is not there after a few seconds, this browser does not save downloads (some built-in preview browsers drop them silently): stop and switch browsers before downloading files.

```js
(() => {
  const T = window._tue, a = document.createElement('a');
  const json = JSON.stringify(T.manifest).replace(/([?&])verifier=[^&"\\\s<>]*&?/g, '$1');
  a.href = URL.createObjectURL(new Blob([json], {type: 'application/json'}));
  a.download = `${T.code}__manifest.json`;
  document.body.appendChild(a); a.click(); a.remove();
  return 'saved manifest';
})()
```

## 4. Download files

Set `window._tueSkip = new Set([...ids])` to the ids the mapping skips (on a refresh, use the output of `organize_course.py --print-known`, which also includes files already filed), or `window._tueOnly = new Set([...ids])` to retry missing files. Use `GAP = 700` normally and `1500` for retries. Run without awaiting:

```js
(async (GAP) => {
  const T = window._tue, only = window._tueOnly, skip = window._tueSkip;
  const save = (blob, name) => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 120000);
  };
  T.dl = {status: 'running', done: 0, skipped: 0, err: []};
  for (const f of T.files) {
    if (f.locked || (only && !only.has(f.id)) || (skip && skip.has(f.id))) { T.dl.skipped++; continue; }
    try {
      const r = await fetch(f.url);
      if (!r.ok) throw new Error(String(r.status));
      save(await r.blob(), f.download_name);
      T.dl.done++;
    } catch (e) { T.dl.err.push(f.id + ': ' + e.message); }
    await new Promise(res => setTimeout(res, GAP));
  }
  T.dl.status = 'finished';
})(700);
'started'
```

Poll `window._tue.dl`. `done` counts files the browser was asked to save, not files on disk; the organizer's dry run is the real check. After the first file, check the download folder; if nothing else arrives, ask the student to allow multiple downloads from `canvas.tue.nl`, then retry the missing ids.
