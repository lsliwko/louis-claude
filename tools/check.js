#!/usr/bin/env node
// Quick checks for every game, printed as one short line each. Run before pushing:
//   node tools/check.js
const fs = require('fs'), path = require('path');
const L = require('./lib');
let fail = 0; const ok = (name, good, info) => { console.log((good ? 'ok   ' : 'FAIL ') + name + (info ? ' - ' + info : '')); if (!good) fail++; };

// 1. Every page's scripts parse.
const pages = ['index.html', ...fs.readdirSync(L.ROOT).filter(d => fs.existsSync(path.join(L.ROOT, d, 'index.html'))).map(d => d + '/index.html')];
for (const p of pages) { const html = fs.readFileSync(path.join(L.ROOT, p), 'utf8'); let err = '';
  try { L.scripts(html).forEach(s => new Function(s)); } catch (e) { err = e.message; }
  ok('syntax ' + p, !err, err);
  ok('rules  ' + p, /lang="en-GB"/.test(html) && /user-scalable=no/.test(html) && /gesturestart/.test(html) && /selectstart/.test(html), 'en-GB, no zoom, no select');
}

// 2. Tricky Words: no game word counts for another; how often each word comes up.
const t = L.tricky(), clash = [];
for (const a of t.W) for (const b of t.W) if (a !== b && t.matches(a, b.w.toLowerCase())) clash.push(b.w + '→' + a.w);
ok('tricky clashes', !clash.length, clash.join(', ') || t.W.length + ' words, none');
const c = {}; for (let i = 0; i < 4000; i++) t.pickRound(5).forEach(v => c[v.w] = (c[v.w] || 0) + 1);
console.log('     tricky NEW=' + t.NEW.join(',') + ' | ' + Object.entries(c).sort((a, b) => b[1] - a[1]).map(([w, n]) => w + ' ' + Math.round(n / 40) + '%').join(' '));

// 3. Maths: every question has CHOICES different answers, one right, none below 0 (times below 1).
const m = L.maths(); let bad = 0;
for (const x of m.QX.concat(m.QA)) for (let r = 0; r < 3; r++) { const o = m.options(x), v = m.ans(x), lo = x.op === '+' ? 0 : 1;
  if (o.length !== m.CHOICES || new Set(o).size !== m.CHOICES || !o.includes(v) || o.some(z => z < lo)) bad++; }
ok('maths answers', !bad, (m.QX.length + m.QA.length) + ' questions');
const rx = m.range('x'), ra = m.range('+'), rr = []; for (let i = 0; i < 400; i++) rr.push(...m.pickRound(5));
ok('maths levels', rr.every(q => { const r = q.op === 'x' ? rx : ra; return q.a >= r[0] && q.a <= r[1] && q.b >= r[0] && q.b <= r[1]; }), 'start: adding ' + ra.join('-') + ', times ' + rx.join('-'));

process.exit(fail ? 1 : 0);
