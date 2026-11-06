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
  const pre = p === 'index.html' ? '' : '../';
  ok('icon   ' + p, ['favicon.svg', 'favicon-32.png', 'apple-touch-icon.png'].every(f => html.includes('href="' + pre + f + '"') && fs.existsSync(path.join(L.ROOT, f))), 'favicon and home-screen icon');
  ok('turn   ' + p, html.includes('class="turnme"') && /orientation:\s*landscape/.test(html), 'sideways cover');
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

// 5. Reading levels: a round only uses open levels; 8 right first time opens the next level, 5 misses go back one;
//    choices never use words more than one level above the picture's.
{ const r = L.reading(), per = r.LEVELS.map((_, i) => r.WORDS.filter(x => x.lv === i).length), bad = [];
  if (per.some(v => v < 10)) bad.push('a level has under 10 words: ' + per.join('/'));
  for (let i = 0; i < 300; i++) if (r.pickRound(5).some(x => x.lv > r.LV.lv)) { bad.push('round uses a closed level'); break; }
  const extra = new Set(r.EXTRA), lvOf = Object.fromEntries(r.WORDS.map(x => [x.w, x.lv]));
  for (const x of r.WORDS) for (let k = 0; k < 10; k++) for (const z of r.options(x)) if (z !== x.w && !extra.has(z) && lvOf[z] > x.lv + 1) bad.push(x.w + ' offered ' + z);
  for (let i = 0; i < 8; i++) r.record(1); const up = r.LV.lv;
  for (let i = 0; i < 5; i++) r.record(0); const down = r.LV.lv;
  if (up !== 1 || down !== 0) bad.push('level up/down: ' + up + ', ' + down);
  ok('reading levels', !bad.length, bad.length ? bad.slice(0, 3).join(' | ') : per.length + ' levels of ' + per.join('/') + ' words; up after 8 right, down after 5 misses'); }

// 6. Stars and prizes: the star-bank code is the same on every page that has it; every game adds its gold stars to it;
//    the menu, Prizes and Options pages use it; the Prizes and Options pages list the same prizes.
{ const pages = ['index.html', ...fs.readdirSync(L.ROOT).filter(d => fs.existsSync(path.join(L.ROOT, d, 'index.html'))).map(d => d + '/index.html')];
  const src = p => fs.readFileSync(path.join(L.ROOT, p), 'utf8');
  const blk = p => { const s = L.scripts(src(p)).join('\n'), i = s.indexOf('// Star bank, shared by every game'); if (i < 0) return null; const j = s.indexOf('function addStar(){', i); return s.slice(i, s.indexOf('\n', j)); };
  const ref = blk('prizes/index.html'), bad = [];
  for (const p of pages) { const b = blk(p), js = L.scripts(src(p)).join('\n'), game = /function mark\(ok\)/.test(js);
    if ((game || ['index.html', 'prizes/index.html', 'options/index.html'].includes(p)) && !b) bad.push(p + ' has no star bank');
    if (b && b !== ref) bad.push(p + ' star bank differs from prizes/');
    if (game && !/function mark\(ok\)\{[^}]*if\(ok\)addStar\(\)/.test(js)) bad.push(p + ' does not bank gold stars'); }
  const plist = p => { const s = L.scripts(src(p)).join('\n'), m = s.match(/var PRIZES=(\[[\s\S]*?\]);/); return m ? m[1] : null; };
  if (!plist('prizes/index.html') || plist('prizes/index.html') !== plist('options/index.html')) bad.push('PRIZES differ between prizes/ and options/');
  ok('stars  bank and prizes', !bad.length, bad.length ? bad.slice(0, 3).join(' | ') : 'same star bank on every page, every game banks gold stars, prize lists match'); }

// 7. iPhone sound rules (see the skill's "Sound on iPhone"): no delay between cancel and speak in pages without a microphone;
//    speech marks spokeSince; tap games remake the sound engine in the answer tap; Scribble tries a fresh one after each stroke;
//    Tricky Words (microphone) keeps afterMic for the cheer and buzz and never sets the audio session.
{ const src = p => L.scripts(fs.readFileSync(path.join(L.ROOT, p), 'utf8')).join('\n'), bad = [];
  for (const p of ['maths/index.html', 'scribble/index.html', 'reading/index.html', 'prizes/index.html']) { const s = src(p);
    if (/ss\.cancel\(\);setTimeout\(go,/.test(s)) bad.push(p + ': delay between cancel and speak');
    if (!/function say\(t\)\{spokeSince=true;/.test(s)) bad.push(p + ': say() does not set spokeSince'); }
  for (const p of ['maths/index.html', 'reading/index.html']) if (!/function answer\(b,v\)\{[^}]*freshAudio\(\)/.test(src(p))) bad.push(p + ': answer tap does not call freshAudio()');
  if (!/function askyes|\$\('askyes'\)\.onclick=function\(\)\{[^}]*freshAudio\(\)/.test(src('prizes/index.html'))) bad.push('prizes: tick tap does not call freshAudio()');
  { const s = src('scribble/index.html'); if (!/addEventListener\('touchend',trySwap\)/.test(s) || !/afterSwap\(function\(\)\{whenAudio\(cheer\)\}\)/.test(s)) bad.push('scribble: no trySwap after strokes'); }
  { const s = src('tricky-words/index.html'); if (!/afterMic\(cheer\)/.test(s) || !/afterMic\(buzz\)/.test(s)) bad.push('tricky-words: cheer/buzz not after the mic closes');
    if (/audioSession\.type\s*=/.test(s)) bad.push('tricky-words: sets the audio session (breaks the mic)'); }
  ok('sound  iPhone rules', !bad.length, bad.length ? bad.join(' | ') : 'speech in the tap, sound engine remade after speech, Tricky Words mic path unchanged'); }

process.exit(fail ? 1 : 0);
