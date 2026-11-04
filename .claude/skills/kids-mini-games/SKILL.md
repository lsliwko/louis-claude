---
name: "kids-mini-games"
description: "Build or change a learning mini-game for a 5-year-old who can't read yet, in the lsliwko/louis-claude GitHub Pages site, including adding it to the games menu."
---

# Kids mini-games (lsliwko/louis-claude)

Small learning games for a 5-year-old who can't read yet, played on an iPhone in Chrome (and sometimes Safari). They're hosted with GitHub Pages at https://lsliwko.github.io/louis-claude/

The repo is public: never put the child's name in files, commit messages or page text.

**Everything is British English:** spoken voice, speech recognition, page language (`<html lang="en-GB">`) and spelling in any text.

## Work cheaply (saves tokens)

0. Read `docs/handover.md` first (current state and open items), and update it before finishing. `docs/tools.md` is the tools reference.
1. Sync, don't re-clone: `cd /home/claude/louis-claude && git fetch -q origin main && git reset -q --hard FETCH_HEAD` (the clone usually lives in `/home/claude/louis-claude`; clone only if it's missing).
2. Don't read whole game files (each is ~300 dense lines). Find the spot with `grep -n 'anchor' game/index.html | cut -c1-160`, then edit with an exact-string replace (Edit, or Python with `assert s.count(old)==1`).
3. Check with the repo tools, not new ad-hoc scripts:
   - `node tools/check.js`: always; syntax of every page, house rules (en-GB, no zoom, no select), Tricky Words clashes and word frequencies, every Maths answer set and level range.
   - `node tools/match.js WORD heard1 "heard 2"`: Y/n for reported mishearings.
   - `python3 tools/smoke.py`: when behaviour or layout changed; every page at 320/390px, no errors or sideways scroll, a Maths answer. Add `--scribble` for drawing changes and `--shots` (saves to `/tmp/game-shots/`) only when visuals changed, then look at just the one relevant screenshot.
   - Extend these tools when a new game or rule needs checking, rather than writing one-off tests.
4. Commit, push, then `bash tools/deploy-status.sh` (waits and prints one line).
5. Keep replies short: what changed, what was checked, "live in a minute or two".
6. Update this repo copy of the skill as rules change; send the full account-skill card only when the user asks for it.

## Where things live

- Repo: `lsliwko/louis-claude`, branch `main`. Attach it with `add_repo` (access `push`), clone it, and push straight to `main`. GitHub Pages is published by the workflow `.github/workflows/pages.yml` on every push to `main` (Pages source: GitHub Actions); it copies only the site files (no dot-folders, README or AGENTS) and has `concurrency` with `cancel-in-progress: true`, so a newer push cancels an older run. After pushing, check the run with `gh run list --repo lsliwko/louis-claude --limit 3`.
- `index.html` at the root is the **menu**: a 2-column grid of big picture tiles, one per game, plus an HTML comment showing how to add a tile.
- Each game lives in **its own folder** with its own `index.html`, e.g. `tricky-words/`. Use a short kebab-case folder name that matches the game's display name ("Tricky Words" → `tricky-words/`).
- `README.md` lists the layout and has one line per game. Update it whenever a game is added or its rules change.
- `AGENTS.md` gives other coding agents the repo rules and points them to this skill. This file is the repo copy of the skill; keep it in step with the copy saved in the Claude account.
- `tricky-words/index.html` is the **reference implementation**. When building a new game, copy the shared pieces from it (tokens, fonts, sounds, fireworks, stars, speech, microphone handling) instead of rewriting them.
- `maths/index.html` is the reference for **tap-to-answer** games (no microphone): each question is a times sum (a × b, up to 1 to 10) or an adding sum (a + b, up to 0 to 25); each slot in a round picks times or adding with equal chance, then a question from that pool (`QX`, `QA`) limited by the current **level**. Levels (`LEVELS`, [smallest, biggest] number: adding 0–5, 0–10, 0–15, 0–20, 0–25, which the user says is a good level; times 2–5, 2–7, 2–10, never × 1 because the user found it too easy) start at the first level and are kept per kind in `localStorage` under `mx-level-2` (adding progress is carried over from the older `mx-level` key; change the key if the level list changes shape). Each answer scores 1 (right first time), 0.5 (right after a mistake) or 0 (missed); 7+ points over the last 8 moves up a level, 1.5 or less over the last 5 moves down, and the history resets on each move. New levels apply from the next round; the end screen shows "Adding up to N · Times up to M" in small grey text for the parent and says "Bigger numbers next time!" after a level-up. A speaker button under the question says it as a question ("6 times 8 is?"); four big answer buttons in a 2×2 grid (`CHOICES=4`; white numbers on solid blue; green when right, grey when wrong). `ans(x)` and `sign(x)` handle the two kinds. Wrong answers: for times, a neighbouring times-table answer or the answer ± a little; for adding, the answer ± 1 to 3 or ± 10 (adding answers may be 0). A wrong tap buzzes, greys out that button and asks to try again; one mistake is allowed: on the 2nd wrong tap (`TRIES=2`) the right answer is shown in green, read aloud ("6 times 8 is 48", "3 plus 4 is 7"), a grey star is given and the game moves on. The question text shrinks to fit narrow phones (`fitQ`). Missed questions are remembered under `mx-misses` (keys like `6x8` and `3+4`).
- `scribble/index.html` is the reference for **finger-drawing** games: a lowercase or capital letter or a digit (`Q`, 62 shapes; British letter names for speech, "zed"; letters are said as "queue like queen", numbers as "Draw number seven") is drawn as a faint filled glyph in Baloo 2 on a square canvas (`#pad`, `touch-action:none`, pointer events with pointer capture), with dashed handwriting guide lines. Every shape uses the same font size, shrunk only to fit, and is centred by its own outline. The same glyph is rendered into a 100×100 mask; each finger point stamps a coverage disc (radius 8.5% of the grid) and a smaller ink disc (4.5%). On each finger lift: coverage ≥ 90% and ink off the (dilated) shape ≤ 45% gives a star; enough coverage but messier ink buzzes, clears the pad and asks to stay on the shape (`TRIES=3`, so two messy tries are allowed). A speaker button repeats the prompt and a rubber button clears the pad without counting as a try. Safari drops speech that wasn't first started inside a tap, so the load-time prompt is silent there: until an utterance has started (`onstart`), the first `touchend`/`click` anywhere says the prompt again (a silent utterance if the tap is on a button or the shape was just judged; nothing for the speaker button, which speaks itself). Wait for `document.fonts.load` (with a 1.5s fallback) before the first shape so the shape shown and the shape checked match. Under the buttons a word for each letter (`WORDS`: apple, ball, cat, dog, egg, fish, goat, hat, insect, jam, kite, lion, moon, nest, octopus, pig, queen, rabbit, sun, tree, umbrella, van, web, x-ray, yo-yo, zebra) is shown large with its first letter bold in the accent colour, capitalised for capital letters ("Queen"); it's hidden (keeping its space) for digits. Misses are remembered under `sc-misses`.

## Adding a new game

1. Create `<folder>/index.html` as one self-contained file: inline CSS and JS, Google Fonts only, no other external assets.
2. Put a round **house button** in the top-left that links to `../`.
3. Add a tile to the root `index.html`: copy the existing `<a class="tile">`, change `href`, `aria-label`, the icon SVG and the name. Tiles use the blue `--t1`/`--t1-bg` pair unless the user asks for another colour.
4. Add the game to `README.md`.
5. Test it (see Testing), commit, push, then tell the user it'll be live in a few minutes and to close and reopen the tab.

## Design rules (the user has asked for all of these)

- **Assume the child can't read.** Everything he uses is an icon: microphone, speaker, circular-arrow replay, house. Put text only in `aria-label` or a visually hidden `.sr` span. Any message he needs is also **spoken aloud**.
- **Large tap targets.** The main action button is full width and about 96px tall. The speaker button is a 72px circle.
- **Look:** fonts "Baloo 2" (display) and "Nunito" (body). Soft blue "playground" palette, defined as tokens on `:root` with dark-mode overrides under `prefers-color-scheme` and `[data-theme=dark]`. Reuse the token block from `tricky-words`.
- **One question at a time:** a big word or prompt in a white card, a speaker button that says it, and a progress bar.
- **Stars:** a row in the top-right that **grows as he goes**, adding one star per finished question. **Gold** = got it right within the allowed tries; **grey** = ran out of tries. The end screen repeats the row with "N of 5 words!" and a replay button.
- **Round length:** 5 questions.
- **Tries:** after a wrong answer, play the "wah-wah" buzz, say "Please try again" and **stay on the same question**. In Tricky Words two mistakes are allowed: after the **3rd** wrong try, say "Let's try the next one", give a grey star and move on (Maths allows one mistake; see above).
- **Right answer:** play the cheering sound (trumpet arpeggio, crowd and claps via Web Audio) plus a **fireworks show of about 4 seconds** (rockets with trails; sphere, ring, heart, willow and crackle bursts; a soft boom per burst). Move to the next question only **after the fireworks have finished**. Pressing any button clears the fireworks straight away.
- **Perfect round:** say "Five stars! You are winning!" and show "FIVE stars! You are winning!".
- **New-words batch:** a `NEW` array near the top of the script lists the words the child is currently learning (now `the`, `of`, `all`, `are`; `the` and `of` carried over from the previous batch). They get base weight 4 instead of 1 when a round is picked, so they fill most of each round. When the user names a new batch, replace this list.
- **Adaptive practice:** remember items missed on the first try in `localStorage` (try/catch around every access) and pick them more often (weight `1 + 2 × misses`, capped at 5 misses). A first-try success lowers the count by one. Pick the 5 questions without repeats.
- **No grown-up controls** on the play screen.
- **Nothing can be selected or highlighted by touch** (menu and every game): `user-select:none`, `-webkit-touch-callout:none` and `-webkit-tap-highlight-color:transparent` on `*`; `touch-action:manipulation` on `html,body,*`; block `selectstart`, `contextmenu` and `dragstart`; and blur the focused element after each tap so no focus ring stays on screen.
- **No zooming** (menu and every game): viewport meta `maximum-scale=1,user-scalable=no`; `touch-action:manipulation` everywhere (stops double-tap zoom); and, because iPhone Safari ignores `user-scalable=no`, block `gesturestart`/`gesturechange`/`gestureend`, two-finger `touchmove` and `dblclick` with `preventDefault` (`{passive:false}`).

## Speech and microphone (iPhone Chrome = Safari's WebKit underneath)

- **Text-to-speech:** British English only. Pick an `en-GB` voice explicitly, preferring Enhanced/Premium UK voices (Daniel, Kate, Serena, Arthur, Martha). **Never fall back to a US or other English voice**: if no `en-GB` voice is listed yet, set no voice and `utterance.lang = 'en-GB'`, and re-check the voice list at speak time (it loads late on iPhone). Rate 0.8. Don't call `cancel()` and `speak()` in the same instant: if something is speaking, cancel it and speak after about 120ms. Give words that TTS misreads a spoken form, e.g. `{w:"I", sp:"eye"}` (a lone "I" is otherwise read as "capital I").
- **Speech recognition** (`webkitSpeechRecognition`, `lang = 'en-GB'`, `interimResults: true`, `maxAlternatives: 5`):
  - Before every listen, wait for the previous recognizer to end fully, then create a **new** one.
  - Show a pulsing yellow "getting ready" state, and switch to red "listening" only on `audiostart`/`soundstart`. Start the timer then.
  - Listen for **4.5 seconds**, shown as a white bar draining along the bottom of the mic button.
  - If audio hasn't started within 1.5s, silently retry once.
  - Accept a right answer as soon as any interim result matches.
  - If nothing is heard, say "I didn't hear you. Please try again" without counting it as a wrong try.
- **Matching is forgiving:** give each word a list of sound-alikes (e.g. `was` → horse, what, wars, does, oz). A word can also have a pattern `p` for very hard-to-recognise words: `the` uses `/^[a-z]{1,4}$/`, so any short word of up to 4 letters counts, because iPhone recognition rarely writes "the" for a child saying it on its own. A heard word that is another game word, or on another game word's sound-alike list, never counts (checked before squashing repeats, so "see" stays a `she` sound-alike). Also accept: one-letter-away matches for words of 3 or more letters (unless that's another game word); repeated letters collapsed ("bbbbb" → "b"); repeats of an accepted form ("bebe", "be be be"); and phrases of up to 2 distinct words containing a match. Never accept another word that's in the game, and when adding a word remove it from other words' sound-alike lists (e.g. adding `do` meant taking `do` out of `to`'s list). A pattern never accepts a sound-alike listed for another game word.
- **Disable the speaker button** while the mic is getting ready or listening.
- **Tap lock:** the speaker button ignores repeat taps for 3s (all games); mic and replay buttons for 0.5s.
- **Never reload the page to restart** (`location.reload()` leaves the iPhone mic stuck until Chrome restarts). Reset the round in place. On `pagehide`, abort recognition, cancel speech and close the AudioContext.
- Request the mic with `getUserMedia` once per session on load (tracks stopped right away) so the parent can allow it up front. **Do not start a SpeechRecognition on page load** (a load-time "warm-up" recognizer to trigger Safari's speech prompt early broke the microphone on iPhone in both Chrome and Safari). Safari's speech prompt therefore appears on the first mic tap.
- Sounds only play after a user gesture, so create or resume the AudioContext inside the mic button's click handler.
- **Games without a microphone** (like Maths) must work harder for sound on iPhone: without the mic the page's audio follows the silent switch and the AudioContext can end up `suspended`, `interrupted` (after speech) or `closed` (after a back/forward-cache restore). Set `navigator.audioSession.type='playback'` where supported (never in mic games, it would stop recording), recreate a closed context, call `resume()` whenever the state isn't `running`, wake audio on every `pointerdown`/`touchend`, unlock once with a 1-sample silent buffer, and start the cheer/buzz through `whenAudio(fn)` so they only play once the context is running.

## Testing (in the workspace, before pushing)

- Start with `node tools/check.js` and `python3 tools/smoke.py` (see Work cheaply); the points below are for things those don't cover yet.
- Use Playwright (Chromium is pre-installed) with a **fake `SpeechRecognition`** injected via `add_init_script`. It should fire `onaudiostart`/`onresult`/`onend` according to a queued plan, so you can test right, wrong, silence and the auto-retry.
- Call `right()` directly to time the fireworks and screenshot them, and check the next question appears after the show.
- Unit-test the matching function against the reported mishearings, and check that no game word is accepted for another.
- Speech recognition can't really be tested here: say so, and ask the user to try it on the phone.

## Working with the user

- The user tests on the phone and sends short change requests. Make the change, test it, push, and reply with a short note of what changed and that it'll be live in a few minutes (close and reopen the tab).
- Commit messages are plain and describe the change. Use the session's attribution trailer if one is given.
- If the user reports a word being misheard, add the misheard form to that word's sound-alike list.