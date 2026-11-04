// Shared helpers for the check scripts: load a game's <script> code and pull out pieces of it.
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
function page(game) { return fs.readFileSync(path.join(ROOT, game, 'index.html'), 'utf8'); }
function scripts(html) { return html.split('<script>').slice(1).map(p => p.split('</script>')[0]); }
function main(game) { return scripts(page(game))[0]; }
function between(js, from, to) { const i = js.indexOf(from), j = js.indexOf(to, i); if (i < 0 || j < 0) throw new Error('anchor not found: ' + from + ' … ' + to); return js.slice(i, j); }
function shuf(a) { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; }
const store = () => { const m = {}; return { getItem: k => (k in m ? m[k] : null), setItem: (k, v) => { m[k] = String(v); } }; };
// Tricky Words: the word list and the matching function.
function tricky() {
  const js = main('tricky-words');
  const src = js.match(/var W=\[[\s\S]*?\];/)[0] + '\n' + js.match(/function lev[\s\S]*?\n  return uniq[^\n]*/)[0] + '\nreturn {W,matches};';
  const t = new Function(src)();
  t.NEW = eval(js.match(/var NEW=(\[[^\]]*\])/)[1]);
  t.pickRound = new Function('W', 'NEW', 'MISS', js.match(/function pickRound[\s\S]*?return out\}/)[0] + ';return pickRound')(t.W, t.NEW, {});
  t.norm = s => s.toLowerCase().replace(/[^a-z0-9 ]/g, '').trim();
  return t;
}
// Maths: questions, answer options and levels.
function maths() {
  const js = main('maths');
  return new Function('shuf', 'localStorage', between(js, '// Questions:', 'var ROUND=5') +
    ';return {QX,QA,ans,options,pickRound,range,record,LV,LEVELS,CHOICES}')(shuf, store());
}
module.exports = { ROOT, page, scripts, main, tricky, maths, shuf };
