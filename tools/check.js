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
  // a variable and a function with the same name: the variable replaces the function (this broke Maths' "3 times 4 is 12")
  const code = L.scripts(html).join('\n'), fns = new Set([...code.matchAll(/function\s+([A-Za-z_$][\w$]*)\s*\(/g)].map(x => x[1]));
  const vars = new Set(); for (const v of code.matchAll(/\bvar\s+([^;]*)/g)) for (const x of v[1].matchAll(/(?:^|,)\s*([A-Za-z_$][\w$]*)\s*(?==|,|$)/g)) vars.add(x[1]);
  const dup = [...fns].filter(f => vars.has(f));
  ok('names  ' + p, !dup.length, dup.length ? 'variable and function share a name: ' + dup.join(', ') : '');
  const rk = (code.match(/var rank=function\(v\)\{.*?\}\}?/) || [''])[0];
  if (rk) ok('voice  ' + p, /enhanced[^?]*\?0:2/.test(rk) && /localStorage\.getItem\('voice'\)/.test(code), 'uses the voice chosen on the Options page, else enhanced/premium en-GB first');
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

// 4. Reading: every word has a picture and is unique; every question has CHOICES different lowercase words, exactly one right;
//    rounds have no repeats. Also reports how often a same-first-letter and a rhyming distractor are offered.
const rd = L.reading(); let rbad = [], first = 0, rhyme = 0, runs = 0; const pos = [0, 0, 0, 0];
const names = rd.WORDS.map(x => x.w); if (new Set(names).size !== names.length) rbad.push('duplicate word');
for (const x of rd.WORDS) { if (!x.pic) rbad.push(x.w + ' has no picture');
  for (let r = 0; r < 30; r++) { const o = rd.options(x); runs++;
    if (o.length !== rd.CHOICES || new Set(o).size !== rd.CHOICES || o.filter(z => z === x.w).length !== 1 || o.some(z => !/^[a-z]+$/.test(z))) rbad.push(x.w + ': ' + o.join(','));
    if (o.some(z => z !== x.w && rd.same(x.w, z))) rbad.push(x.w + ' offered with ' + o.filter(z => z !== x.w && rd.same(x.w, z)));
    pos[o.indexOf(x.w)]++;
    if (o.some(z => z !== x.w && z[0] === x.w[0])) first++; if (o.some(z => z !== x.w && z.slice(-2) === x.w.slice(-2))) rhyme++; } }
for (let i = 0; i < 300; i++) { const r = rd.pickRound(5); if (new Set(r.map(x => x.w)).size !== 5) { rbad.push('repeat in a round'); break; } }
// the right word must land in each of the 4 places about equally often (so he can't learn a position)
if (pos.some(v => Math.abs(v / runs - 0.25) > 0.04)) rbad.push('right word positions uneven: ' + pos.join('/'));
ok('reading words', !rbad.length, rbad.length ? rbad.slice(0, 3).join(' | ') : rd.WORDS.length + ' words; same first letter offered ' + Math.round(first / runs * 100) + '%, a rhyme ' + Math.round(rhyme / runs * 100) + '%; right word in places 1-4: ' + pos.map(v => Math.round(v / runs * 100) + '%').join(' '));

process.exit(fail ? 1 : 0);
