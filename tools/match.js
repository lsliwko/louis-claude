#!/usr/bin/env node
// Try what the iPhone might hear against a Tricky Words word.
//   node tools/match.js the duh yeah "there there"     -> Y/n for each heard text
const { tricky } = require('./lib');
const [word, ...heard] = process.argv.slice(2);
if (!word) { console.log('usage: node tools/match.js WORD HEARD...'); process.exit(1); }
const t = tricky(), x = t.W.find(v => v.w.toLowerCase() === word.toLowerCase());
if (!x) { console.log('not a game word. Words: ' + t.W.map(v => v.w).join(' ')); process.exit(1); }
console.log(heard.map(h => h + ':' + (t.matches(x, t.norm(h)) ? 'Y' : 'n')).join('  '));
