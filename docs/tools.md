# Tools

Small scripts in `tools/` that replace ad-hoc testing. Run them from the repo root. Each prints one short line per check, so the output is cheap to read.

| Tool | When to run | Takes |
|---|---|---|
| `node tools/check.js` | Before every push | ~2 s |
| `node tools/match.js WORD heard...` | A word is misheard or wrongly accepted | instant |
| `python3 tools/smoke.py` | Behaviour or layout changed | ~10 s |
| `python3 tools/smoke.py --scribble` | Scribble shapes or scoring changed | ~1 min |
| `python3 tools/smoke.py --shots` | Something visual changed | ~10 s |
| `bash tools/deploy-status.sh [sha]` | Right after pushing | 1–2 min |

## `node tools/check.js`

Static checks, no browser. Exit code 1 if anything fails.

- **syntax** of every page's `<script>` (the menu and every `*/index.html`).
- **voice**: every game uses the voice chosen on the Voice page, else ranks enhanced/premium en-GB voices first.
- **reading words**: every Reading word has a picture and is unique; every question has 4 different lowercase words with exactly one right; no word is offered with another name for the same picture (`SAME`); the right word lands in each place about equally often; rounds have no repeats; reports how often a same-first-letter and a rhyming word are offered.
- **reading levels**: every level has at least 10 words; a round only uses open levels; 8 right first time opens the next level and 5 misses go back one; choices never use words more than one level above the picture's.
- **icon**: every page links the favicon (`favicon.svg`, `favicon-32.png`) and the home-screen icon (`apple-touch-icon.png`), and the files exist.
- **turn**: every page has the sideways cover (`.turnme`, shown in landscape).
- **sound**: the iPhone sound rules: no delay between cancel and speak in Maths, Scribble, Reading and Prizes; `say()` sets `spokeSince`; the answer taps in Maths and Reading and the ✓ tap in Prizes call `freshAudio()`; Scribble calls `trySwap` after strokes; Tricky Words keeps `afterMic` and never sets the audio session.
- **levels options page**: the Options page's copy of the Maths levels and Reading level names matches the games.
- **stars**: the star-bank code is the same on every page that has it, every game banks its gold stars, and the Prizes and Options pages list the same prizes.
- **names**: no `var` shares a name with a function on the same page (the variable would replace the function).
- **house rules** on every page: `lang="en-GB"`, `user-scalable=no`, Safari gesture blocking (`gesturestart`) and selection blocking (`selectstart`).
- **Tricky Words clashes**: no game word is accepted for another game word (through sound-alikes, patterns or fuzzy matching).
- **Tricky Words frequency** (information only, never fails): the `NEW` batch and, for each word, the share of 4000 simulated rounds it appears in, with no misses remembered. The `NEW` words should be at the top.
- **Maths answers**: for every question (3 tries each, since options are random) there are exactly `CHOICES` different options, one is right, and none is below 0 (below 1 for times).
- **Maths levels**: rounds picked at the starting levels only use numbers inside those levels' ranges.

Example output:

```
ok   syntax index.html
ok   names  index.html
ok   rules  index.html - en-GB, no zoom, no select
...
ok   tricky clashes - 13 words, none
     tricky NEW=the,of,all,are | are 70% the 70% all 69% of 69% we 26% I 25% ...
ok   maths answers - 776 questions
ok   maths levels - start: adding 0-5, times 2-5
```

## `node tools/match.js WORD heard...`

Checks what the iPhone heard against one Tricky Words word, using the game's own matching code. Quote phrases.

```
$ node tools/match.js the duh yeah tea "there there" she
duh:Y  yeah:Y  tea:Y  there there:Y  she:n
```

Use it to confirm a reported mishearing fails before adding it to the word's `s:[...]` list, then passes after. `she:n` above is correct: another game word never counts.

## `python3 tools/smoke.py [--scribble] [--shots]`

Opens every page (the menu and every game) in headless Chromium with touch, at 320 px and 390 px wide, and reports one line per page and width:

- page loads with no JavaScript errors;
- no sideways scrolling;
- Stars and prizes: a gold star in Reading is banked and shown on the menu; Prizes refuses without enough stars, asks before spending (✕ keeps them), spends 100 and shows a badge; Options' Given keeps the stars spent and Give stars back returns them.
- Options page (at 390 px): a child's birth year is refused and an adult's opens it; then, with pretend voices, lists the phone's own voice plus British ones (a duplicate once), chooses one and checks Scribble then uses it, that "phone" leaves the voice unset, that with no choice an iPhone leaves the voice unset, and that elsewhere it goes back to the best British one.
- Maths and Reading: after the first wrong answer, all answers are disabled for 1s, then the three untried ones come back.
- Reading (at 390 px): before ▶ the speaker and the four words are disabled and a tap on a word is ignored; the ▶ start tap says the word inside the tap; the right word gives a gold star; that tap (after the word was spoken) remakes the sound engine and the cheer plays once; the next word is said when it appears; each question uses one letter case for all four words, all three cases turn up, and long words don't spill out of their buttons; two wrong words move on with a grey star.
- Maths (at 390 px): taps the right answer and checks it scores; after speech, an answer tap remakes the sound engine and the cheer plays once; then, on a fresh page, taps two wrong answers and checks it moves to the next question with a grey star and no errors.

It doesn't test speech recognition or real sound: those can only be tried on the phone.

Options:

- `--scribble`: also traces every one of the 62 Scribble shapes, row by row with a little wobble like a child's finger, and checks each one earns a star (printing the most ink any shape had outside, against the limit); then traces the middle of every stroke (skeleton, needs numpy/scikit-image/scipy) and checks it covers enough of each shape with the ink on it; then sends one batched (coalesced) move down an l and back up and checks the whole stroke is drawn; then scribbles zigzags over the whole pad for four shapes and checks none earns a star.
- `--shots`: saves a 390 px screenshot of each page to `/tmp/game-shots/` (`index.html.png`, `maths_index.html.png`, `scribble_index.html.png`, `tricky-words_index.html.png`). Look only at the one you need.

## `bash tools/deploy-status.sh [sha]`

Waits for the "Deploy to GitHub Pages" run of the commit you just pushed (default: `HEAD`), then prints one line:

```
deploy success e90e535 Skill: fix the sync path and point testing at the repo tools
```

If it failed, it also prints up to 5 error lines from the log. It gives up after 2 minutes if no run appears and 5 minutes if the run doesn't finish. If it failed because another deploy was still running ("in progress deployment", usually GitHub's built-in one until Pages source is set to GitHub Actions), it waits 30 s and starts a fresh deploy run of `main`, up to twice (re-running the same run doesn't work: it uploads a second site artifact and fails). Needs the `gh` CLI (pre-installed and authenticated in Claude sessions).

## `tools/lib.js` (for extending the tools)

Shared helpers that load a game's code straight from its `index.html`, so the tools always test the real game:

- `page(game)`, `scripts(html)`, `main(game)`: the page, its scripts, its main script.
- `between(js, from, to)`: the code between two anchor strings (throws if an anchor is missing, so a renamed anchor fails loudly).
- `tricky()`: `{W, matches, NEW, pickRound, norm}` from Tricky Words.
- `maths()`: `{QX, QA, ans, options, pickRound, range, record, LV, LEVELS, CHOICES}` from Maths, with a fake `localStorage`.

When a new game or rule needs checking, add a loader here and a check to `check.js` or `smoke.py` rather than writing a one-off script.
