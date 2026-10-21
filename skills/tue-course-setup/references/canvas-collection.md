# Canvas collection

Run these scripts in a `canvas.tue.nl` tab through the browser tool's JavaScript runner. They use the student's own session; nothing here handles credentials.

- Canvas prefixes JSON with `while(1);`; the helpers strip it.
- Students often get **403** on `/courses/:id/files` and folder listings. Modules are the main source; the files list is an optional extra.
- Start long scripts **without awaiting them** (awaiting can hit tool timeouts) and poll `window._tue` instead.
- Never print download URLs: Canvas signs them, and tools may block output that contains them. Status calls return counts only.

## 1. Find the course

```js
(async () => {
  const r = await fetch('/api/v1/courses?per_page=100&enrollment_state=active&include[]=term', {headers: {Accept: 'application/json'}});
  const list = JSON.parse((await r.text()).replace(/^while\(1\);/, ''));
  return list.map(c => ({id: c.id, name: c.name, code: c.course_code, term: c.term && c.term.name}));
})()
```

If the course is missing, retry without `enrollment_state=active` (finished or future courses). Confirm the course code to use for folder and file names (e.g. `2IRR20`).

## 2. Collect

Set `COURSE_ID` and `CODE`, then run without awaiting:

```js
window._tue = {status: 'collecting', errors: []};
(async (COURSE_ID, CODE) => {
  const T = window._tue, C = COURSE_ID;
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

  const course = await one(`/api/v1/courses/${C}?include[]=syllabus_body&include[]=term`);
  const modules = await soft('modules', () => all(`/api/v1/courses/${C}/modules?per_page=100&include[]=items`), []);
  for (const [i, m] of modules.entries()) {
    m.mi = i + 1;
    if (!m.items) m.items = await soft('module items ' + m.id, () => all(`/api/v1/courses/${C}/modules/${m.id}/items?per_page=100`), []);
  }

  const files = new Map();
  const addFile = async (id, mi, module) => {
    id = Number(id);
    if (files.has(id)) return;
    const f = await soft('file ' + id, () => one(`/api/v1/courses/${C}/files/${id}`), null);
    if (!f) return;
    const mm = String(mi).padStart(2, '0');
    files.set(id, {
      id, mi, module, display_name: f.display_name, size: f.size,
      content_type: f['content-type'], updated_at: f.updated_at,
      locked: !!f.locked_for_user || !f.url, url: f.url,
      download_name: `${CODE}__M${mm}__F${id}__${safe(f.display_name)}`,
    });
  };
  T.status = 'files';
  for (const m of modules) for (const it of m.items) if (it.type === 'File') await addFile(it.content_id, m.mi, m.name);

  T.status = 'pages';
  const pageList = await soft('pages', () => all(`/api/v1/courses/${C}/pages?per_page=100`), []);
  const pageUrls = new Set(pageList.map(p => p.url));
  for (const m of modules) for (const it of m.items) if (it.type === 'Page' && it.page_url) pageUrls.add(it.page_url);
  const pages = [];
  for (const u of pageUrls) {
    const p = await soft('page ' + u, () => one(`/api/v1/courses/${C}/pages/${encodeURIComponent(u)}`), null);
    if (p) pages.push({url: p.url, title: p.title, html_url: p.html_url, updated_at: p.updated_at, body: p.body || ''});
  }

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

  T.status = 'linked files';
  const html = [course.syllabus_body || '', ...pages.map(p => p.body), ...assignments.map(a => a.description), ...announcements.map(a => a.message)].join('\n');
  for (const m of html.matchAll(new RegExp(`/courses/${C}/files/(\\d+)`, 'g'))) await addFile(m[1], 0, 'Linked from Canvas pages');
  const courseFiles = await soft('course files (often 403 for students)', () => all(`/api/v1/courses/${C}/files?per_page=100`), []);
  for (const f of courseFiles) await addFile(f.id, 0, 'Course files outside modules');

  T.code = CODE;
  T.files = [...files.values()];
  T.manifest = {
    schema: 1, collected_at: new Date().toISOString(), code: CODE,
    course: {id: course.id, name: course.name, course_code: course.course_code, url: `${location.origin}/courses/${C}`,
      start_at: course.start_at, end_at: course.end_at, term: course.term && {name: course.term.name, start_at: course.term.start_at, end_at: course.term.end_at}},
    syllabus: course.syllabus_body || '',
    modules: modules.map(m => ({mi: m.mi, id: m.id, name: m.name, unlock_at: m.unlock_at,
      items: m.items.map(it => ({type: it.type, title: it.title, content_id: it.content_id, page_url: it.page_url, html_url: it.html_url, external_url: it.external_url}))})),
    files: T.files.map(({url, ...rest}) => rest),
    pages, assignments, announcements, errors: T.errors,
  };
  T.status = 'collected';
})(COURSE_ID, 'CODE');
```

Poll with:

```js
(() => { const T = window._tue || {}; const fs = T.files || [];
  return {status: T.status, files: fs.length, locked: fs.filter(f => f.locked).length,
    mb: Math.round(fs.reduce((s, f) => s + (f.size || 0), 0) / 1e6), errors: T.errors}; })()
```

Report the module list (`window._tue.manifest.modules.map(m => [m.mi, m.name, m.items.length])`) when proposing the folder mapping.

## 3. Download

Optionally set `window._tueSkip = new Set([...ids])` (from `organize_course.py --print-known`) on a refresh, or `window._tueOnly = new Set([...ids])` to retry missing files. Use `GAP = 700` normally and `1500` for retries. Run without awaiting:

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
  if (!only) save(new Blob([JSON.stringify(T.manifest).replace(/([?&])verifier=[^&"\\\s<>]*&?/g, '$1')], {type: 'application/json'}), `${T.code}__manifest.json`);
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
```

Poll `window._tue.dl`. After the first file, check the download folder; if nothing else arrives, ask the student to allow multiple downloads from `canvas.tue.nl`, then retry the missing ids.
