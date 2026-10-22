# Brightspace collection (experimental)

**Status: experimental and untested on a real Brightspace site.** It is written from D2L's published Valence API documentation and exercised only against a mock of that API, because the author has no Brightspace login. Say so to the student, stop on the first unexpected response instead of working around it, and ask them to report what happened (an issue on the skill's repository helps the next student).

Run these scripts in a tab on the student's Brightspace host (for example `brightspace.tudelft.nl`) through the browser tool's JavaScript runner. They only read what the student's own account can see.

- Start long scripts **without awaiting them** and poll `window._tue`.
- Never print access tokens or download URLs. The scripts keep any token in memory only.
- The manifest they build has the same shape as the Canvas one, plus `platform: "brightspace"`, so the same download check, mapping, and `organize_course.py` steps apply.

## How the scripts authenticate

Brightspace's web pages call its API with the student's login session. The scripts first try the same-origin session; if the API answers 401 or 403, they ask Brightspace's own token endpoint (`POST /d2l/lp/auth/oauth2/token`, the one its own pages use, with the page's anti-forgery token) for a short-lived token for the same session and retry with it. If both fail, the status becomes `auth failed`: stop and tell the student. Do not look for other ways in, and never ask for or type credentials.

## 1. Find the course

```js
(async () => {
  const api = async u => { const r = await fetch(u, {credentials: 'include'}); if (!r.ok) throw new Error(r.status + ' ' + u); return r.json(); };
  const v = await api('/d2l/api/versions/');
  const pick = code => v.filter(x => x.ProductCode === code).map(x => x.LatestVersion).sort((a, b) => parseFloat(b) - parseFloat(a))[0];
  const lp = pick('lp'), le = pick('le');
  let out = [], bookmark = '';
  do {
    const page = await api(`/d2l/api/lp/${lp}/enrollments/myenrollments/?orgUnitTypeId=3${bookmark ? '&bookmark=' + bookmark : ''}`);
    out = out.concat(page.Items.map(i => ({id: i.OrgUnit.Id, name: i.OrgUnit.Name, code: i.OrgUnit.Code})));
    bookmark = page.PagingInfo && page.PagingInfo.HasMoreItems ? page.PagingInfo.Bookmark : '';
  } while (bookmark);
  return {lp, le, courses: out};
})()
```

`orgUnitTypeId=3` limits the list to course offerings. If this fails with 401 or 403, run the token step from the collection script below first, or stop with `auth failed`. Confirm the course code to use for folder and file names (often the first word of the name).

## 2. Collect

Set the course id (`ORG_UNIT`) and `CODE` in the last line, then run without awaiting:

```js
window._tue = {status: 'collecting', errors: [], platform: 'brightspace'};
(async (ORG, CODE) => {
  const T = window._tue;
  let bearer = null;
  const authed = async (u, init = {}) => {
    const headers = Object.assign({}, init.headers || {}, bearer ? {Authorization: 'Bearer ' + bearer} : {});
    return fetch(u, Object.assign({}, init, {credentials: 'include', headers}));
  };
  const getToken = async () => {
    const xsrf = localStorage.getItem('XSRF.Token');
    if (!xsrf) return false;
    const r = await fetch('/d2l/lp/auth/oauth2/token', {method: 'POST', credentials: 'include',
      headers: {'Content-Type': 'application/x-www-form-urlencoded', 'X-Csrf-Token': xsrf}, body: 'scope=*:*:*'});
    if (!r.ok) return false;
    bearer = (await r.json()).access_token || null;
    return !!bearer;
  };
  const api = async u => {
    let r = await authed(u);
    if ((r.status === 401 || r.status === 403) && !bearer && await getToken()) r = await authed(u);
    if (r.status === 401 || r.status === 403) { const e = new Error('auth failed ' + r.status); e.auth = true; throw e; }
    if (!r.ok) throw new Error(r.status + ' ' + u);
    return r.status === 204 ? null : r.json();
  };
  const soft = async (label, fn, fallback) => {
    try { return await fn(); } catch (e) { if (e.auth) throw e; T.errors.push(label + ': ' + e.message); return fallback; }
  };
  const safe = s => String(s).replace(/[\\/:*?"<>|\u0000-\u001f]/g, '_').replace(/\s+/g, ' ').trim().slice(0, 150);
  const dateOf = d => d || null;

  T.status = 'versions';
  const versions = await api('/d2l/api/versions/');
  const pick = code => versions.filter(x => x.ProductCode === code).map(x => x.LatestVersion).sort((a, b) => parseFloat(b) - parseFloat(a))[0];
  const LE = pick('le'), LP = pick('lp');
  if (!LE || !LP) throw new Error('could not read API versions');
  const base = `/d2l/api/le/${LE}/${ORG}`;

  T.status = 'course';
  const info = await api(`/d2l/api/lp/${LP}/courses/${ORG}`);

  // Content: top-level units become modules; nested modules and topics are flattened into items.
  T.status = 'content';
  const files = new Map(), pages = [];
  const modules = [];
  const topicUrl = id => `${base}/content/topics/${id}/file?stream=true`;
  const nameFromPath = (p, fallback) => { try { return decodeURIComponent(String(p || '').split('?')[0].split('/').pop()) || fallback; } catch (e) { return fallback; } };
  const addTopic = async (t, mod, trail) => {
    // Files (ActivityType 1) are downloadable documents; Url is the file's path in the course.
    const id = String(t.Id);
    const item = {type: 'Topic', title: t.Title, content_id: id, html_url: `${location.origin}/d2l/le/content/${ORG}/viewContent/${id}/View`};
    const isFile = t.TopicType === 1 || t.ActivityType === 1 || (t.Url && /\.[A-Za-z0-9]{2,5}($|\?)/.test(t.Url) && !t.Url.startsWith('http'));
    const isLink = t.TopicType === 3 || t.ActivityType === 2;
    if (isLink) { item.type = 'ExternalUrl'; item.external_url = t.Url; mod.items.push(item); return; }
    if (!isFile) { mod.items.push(item); return; }
    const name = nameFromPath(t.Url, t.Title);
    const ext = (name.match(/\.([A-Za-z0-9]+)$/) || [])[1] || '';
    if (/^(html?|htm)$/i.test(ext)) {
      const r = await soft('page ' + id, () => authed(topicUrl(id)).then(x => x.ok ? x.text() : Promise.reject(new Error(x.status))), null);
      if (r !== null) {
        pages.push({url: id, title: t.Title, front_page: false, html_url: item.html_url, updated_at: dateOf(t.LastModifiedDate), body: r});
        item.type = 'Page'; item.page_url = id; mod.items.push(item); return;
      }
    }
    let size = null;
    const h = await soft('size ' + id, () => authed(topicUrl(id), {method: 'HEAD'}), null);
    if (h && h.ok) size = Number(h.headers.get('Content-Length')) || null;
    files.set(id, {id, mi: mod.mi, source: 'Module: ' + trail, display_name: name, size, content_type: null,
      updated_at: dateOf(t.LastModifiedDate), locked: false, fetch: topicUrl(id),
      download_name: `${CODE}__M${String(mod.mi).padStart(2, '0')}__F${id}__${safe(name)}`});
    item.type = 'File'; mod.items.push(item);
  };
  const walk = async (children, mod, trail) => {
    for (const c of children) {
      if (c.Type === 0) {
        const t = trail + ' / ' + c.Title;
        mod.items.push({type: 'SubHeader', title: t});
        const kids = await soft('module ' + c.Id, () => api(`${base}/content/modules/${c.Id}/structure/`), []);
        await walk(kids, mod, t);
      } else await addTopic(c, mod, trail);
    }
  };
  const roots = await api(`${base}/content/root/`);
  for (const [i, r] of roots.entries()) {
    const mod = {mi: i + 1, id: r.Id, name: r.Title, unlock_at: dateOf(r.StartDate), items: []};
    modules.push(mod);
    const kids = await soft('module ' + r.Id, () => api(`${base}/content/modules/${r.Id}/structure/`), []);
    await walk(kids, mod, r.Title);
  }

  T.status = 'assignments';
  const folders = await soft('assignment folders', () => api(`${base}/dropbox/folders/`), []);
  const assignments = [];
  for (const f of folders) {
    const instr = f.CustomInstructions || {};
    assignments.push({id: f.Id, name: f.Name, due_at: dateOf(f.DueDate), unlock_at: dateOf(f.Availability && f.Availability.StartDate),
      lock_at: dateOf(f.Availability && f.Availability.EndDate), points_possible: f.Assessment ? f.Assessment.ScoreDenominator : null,
      submission_types: [], html_url: `${location.origin}/d2l/lms/dropbox/user/folder_submit_files.d2l?db=${f.Id}&grpid=0&isprv=0&bp=0&ou=${ORG}`,
      description: instr.Html || instr.Text || '', rubric: []});
    for (const a of (f.Attachments || [])) {
      const id = `a${f.Id}_${a.FileId}`;
      files.set(id, {id, mi: 0, source: 'Assignment: ' + f.Name, display_name: a.FileName, size: a.Size || null, content_type: null,
        updated_at: null, locked: false, fetch: `${base}/dropbox/folders/${f.Id}/attachments/${a.FileId}`,
        download_name: `${CODE}__M00__F${id}__${safe(a.FileName)}`});
    }
  }

  T.status = 'announcements';
  const news = await soft('announcements', () => api(`${base}/news/`), []);
  const announcements = (news || []).map(n => ({id: n.Id, title: n.Title, posted_at: dateOf(n.StartDate || n.CreatedDate), author: n.CreatedBy ? String(n.CreatedBy) : null,
    html_url: `${location.origin}/d2l/lms/news/main.d2l?ou=${ORG}`, message: (n.Body && (n.Body.Html || n.Body.Text)) || ''}));

  T.code = CODE;
  T.files = [...files.values()];
  T.manifest = {
    schema: 1, platform: 'brightspace', collected_at: new Date().toISOString(), code: CODE,
    course: {id: ORG, name: info.Name, course_code: info.Code, url: `${location.origin}/d2l/home/${ORG}`,
      start_at: info.StartDate || null, end_at: info.EndDate || null, term: null},
    syllabus: '', modules,
    files: T.files.map(({fetch, ...rest}) => rest),
    pages, assignments, announcements, errors: T.errors,
  };
  T.fetchFile = async f => authed(f.fetch);
  T.status = 'collected';
})(ORG_UNIT, 'CODE').catch(e => { window._tue.status = e.auth ? 'auth failed: ' + e.message : 'failed: ' + e.message; });
'started'
```

Poll with:

```js
(() => { const T = window._tue || {}, M = T.manifest, fs = T.files || [];
  return {status: T.status, files: fs.length, mb: Math.round(fs.reduce((s, f) => s + (f.size || 0), 0) / 1e6),
    errors: T.errors, modules: M && M.modules.length, pages: M && M.pages.length,
    assignments: M && M.assignments.length, announcements: M && M.announcements.length}; })()
```

File sizes can be unknown (`size` is null when Brightspace does not report one); the organizer then skips its size check for that file and relies on the file arriving complete. To propose the mapping, list modules (`window._tue.manifest.modules.map(m => [m.mi, m.name, m.items.length])`) and files outside modules (`window._tue.files.filter(f => f.mi === 0).map(f => [f.id, f.display_name, f.source])`).

## 3. Check that downloads reach the disk

Same as Canvas: save the manifest first and check that `<CODE>__manifest.json` arrived.

```js
(() => {
  const T = window._tue, a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([JSON.stringify(T.manifest)], {type: 'application/json'}));
  a.download = `${T.code}__manifest.json`;
  document.body.appendChild(a); a.click(); a.remove();
  return 'saved manifest';
})()
```

## 4. Download files

Set `window._tueSkip` (ids the mapping skips, plus `--print-known` output on a refresh) or `window._tueOnly` (retry ids) as ids in **text** (`new Set(['123', 'a45_6'])`). Run without awaiting:

```js
(async (GAP) => {
  const T = window._tue, only = window._tueOnly, skip = window._tueSkip;
  const save = (blob, name) => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 30 * 60000);
  };
  T.dl = {status: 'running', done: 0, skipped: 0, err: []};
  for (const f of T.files) {
    const id = String(f.id);
    if (f.locked || (only && !only.has(id)) || (skip && skip.has(id))) { T.dl.skipped++; continue; }
    try {
      const r = await T.fetchFile(f);
      if (!r.ok) throw new Error(String(r.status));
      save(await r.blob(), f.download_name);
      T.dl.done++;
    } catch (e) { T.dl.err.push(id + ': ' + e.message); }
    await new Promise(res => setTimeout(res, GAP));
  }
  T.dl.status = 'finished';
})(700);
'started'
```

Poll `window._tue.dl`. As for Canvas, `done` counts files the browser was asked to save, and the organizer's dry run is the real check. The browser may ask the student to approve each download.
