---
name: "kids-mini-games"
description: "Build or change a learning mini-game for a 5-year-old who can't read yet, in the lsliwko/louis-claude GitHub Pages site, including adding it to the games menu."
---

# Kids mini-games (lsliwko/louis-claude)

Small learning games for a 5-year-old who can't read yet, played on an iPhone in Chrome (and sometimes Safari). They're hosted with GitHub Pages at https://lsliwko.github.io/louis-claude/

The repo is public: never put the child's name in files, commit messages or page text.

**Everything is British English:** spoken voice, speech recognition, page language (`<html lang="en-GB">`) and spelling in any text.

## Where things live

- Repo: `lsliwko/louis-claude`, branch `main`. Attach it with `add_repo` (access `push`), clone it, and push straight to `main`. GitHub Pages serves `main` from the root.
- `index.html` at the root is the **menu**: a 2-column grid of big picture tiles, one per game, plus an HTML comment showing how to add a tile.
- Each game lives in **its own folder** with its own `index.html`, e.g. `tricky-words/`. Use a short kebab-case folder name that matches the game's display name ("Tricky Words" → `tricky-words/`).
- `README.md` lists the layout and has one line per game. Update it whenever a game is added or its rules change.
- `AGENTS.md` gives other coding agents the repo rules and points them to this skill. This file is the repo copy of the skill; keep it in step with the copy saved in the Claude account.
- `tricky-words/index.html` is the **reference implementation**. When building a new game, copy the shared pieces from it (tokens, fonts, sounds, fireworks, stars, speech, microphone handling) instead of rewriting them.

## Adding a new game

1. Create `<folder>/index.html` as one self-contained file: inline CSS and JS, Google Fonts only, no other external assets.
2. Put a round **house button** in the top-left that links to `../`.
3. Add a tile to the root `index.html`: copy the existing `<a class="tile">`, change `href`, `aria-label`, the icon SVG and the name. Each game gets its own tile colour pair (add `--t2`/`--t2-bg` etc. tokens in all three theme blocks).
4. Add the game to `README.md`.
5. Test it (see Testing), commit, push, then tell the user it'll be live in a few minutes and to close and reopen the tab.

## Design rules (the user has asked for all of these)

- **Assume the child can't read.** Everything he uses is an icon: microphone, speaker, circular-arrow replay, house. Put text only in `aria-label` or a visually hidden `.sr` span. Any message he needs is also **spoken aloud**.
- **Large tap targets.** The main action button is full width and about 96px tall. The speaker button is a 72px circle.
- **Look:** fonts "Baloo 2" (display) and "Nunito" (body). Soft blue "playground" palette, defined as tokens on `:root` with dark-mode overrides under `prefers-color-scheme` and `[data-theme=dark]`. Reuse the token block from `tricky-words`.
- **One question at a time:** a big word or prompt in a white card, a speaker button that says it, and a progress bar.
- **Stars:** a row in the top-right that **grows as he goes**, adding one star per finished question. **Gold** = got it right within the allowed tries; **grey** = ran out of tries. The end screen repeats the row with "N of 5 words!" and a replay button.
- **Round length:** 5 questions.
- **Tries:** after a wrong answer, play the "wah-wah" buzz, say "Please try again" and **stay on the same question**. After the **4th** wrong try, say "Let's try the next one", give a grey star and move on.
- **Right answer:** play the cheering sound (trumpet arpeggio, crowd and claps via Web Audio) plus a **fireworks show of about 4 seconds** (rockets with trails; sphere, ring, heart, willow and crackle bursts; a soft boom per burst). Move to the next question only **after the fireworks have finished**. Pressing any button clears the fireworks straight away.
- **Perfect round:** say "Five stars! You are winning!" and show "FIVE stars! You are winning!".
- **New-words batch:** a `NEW` array near the top of the script lists the words the child is currently learning (now `the`, `we`, `do`, `of`). They get base weight 4 instead of 1 when a round is picked, so each comes up in about 3 rounds out of 4. When the user names a new batch, replace this list.
- **Adaptive practice:** remember items missed on the first try in `localStorage` (try/catch around every access) and pick them more often (weight `1 + 2 × misses`, capped at 5 misses). A first-try success lowers the count by one. Pick the 5 questions without repeats.
- **No grown-up controls** on the play screen.
- **Nothing can be selected or highlighted by touch** (menu and every game): `user-select:none`, `-webkit-touch-callout:none` and `-webkit-tap-highlight-color:transparent` on `*`; `touch-action:manipulation` on buttons and links; block `selectstart`, `contextmenu` and `dragstart`; and blur the focused element after each tap so no focus ring stays on screen.

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
- **Tap lock:** the speaker button ignores repeat taps for 1s; mic and replay buttons for 0.5s.
- **Never reload the page to restart** (`location.reload()` leaves the iPhone mic stuck until Chrome restarts). Reset the round in place. On `pagehide`, abort recognition, cancel speech and close the AudioContext.
- Request the mic with `getUserMedia` once per session on load (tracks stopped right away) so the parent can allow it up front. **Do not start a SpeechRecognition on page load** (a load-time "warm-up" recognizer to trigger Safari's speech prompt early broke the microphone on iPhone in both Chrome and Safari). Safari's speech prompt therefore appears on the first mic tap.
- Sounds only play after a user gesture, so create or resume the AudioContext inside the mic button's click handler.

## Testing (in the workspace, before pushing)

- Syntax check: `node -e` with `new Function(<script body>)`.
- Use Playwright (Chromium is pre-installed) with a **fake `SpeechRecognition`** injected via `add_init_script`. It should fire `onaudiostart`/`onresult`/`onend` according to a queued plan, so you can test right, wrong, silence and the auto-retry.
- Call `right()` directly to time the fireworks and screenshot them, and check the next question appears after the show.
- Unit-test the matching function against the reported mishearings, and check that no game word is accepted for another.
- Speech recognition can't really be tested here: say so, and ask the user to try it on the phone.

## Working with the user

- The user tests on the phone and sends short change requests. Make the change, test it, push, and reply with a short note of what changed and that it'll be live in a few minutes (close and reopen the tab).
- Commit messages are plain and describe the change. Use the session's attribution trailer if one is given.
- If the user reports a word being misheard, add the misheard form to that word's sound-alike list.