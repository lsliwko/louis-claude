# Games

Simple learning games, published with GitHub Pages at https://lsliwko.github.io/louis-claude/

## Layout

- `index.html` is the menu. It shows one picture tile per game.
- Each game lives in its own folder with its own `index.html`, for example `tricky-words/`.
- `favicon.svg`, `favicon-32.png` and `apple-touch-icon.png` are the site icon (a gold star on blue), linked from every page.
- Portrait only: when the phone is held sideways, every page is covered by a picture of a phone turning upright (web pages can't lock rotation on iPhone; Portrait Orientation Lock in Control Centre does).

## Adding a game

1. Create a new folder, for example `counting/`, with an `index.html` inside.
2. In the game page, add a home button that links to `../` so it can get back to the menu.
3. In the root `index.html`, copy the existing tile and change its link, colours, icon and name.

## Deploying

`.github/workflows/pages.yml` publishes the site to GitHub Pages on every push to `main` (only the game files: dot-folders, `docs/`, `README.md` and `AGENTS.md` are left out). A newer push cancels an older run that hasn't finished, so an old version can't overwrite a newer one. Pages must be set to **Settings → Pages → Build and deployment → Source: GitHub Actions**.

## Tools

Full reference: `docs/tools.md`. Session handover notes: `docs/handover.md`.

- `node tools/check.js`: quick checks for every page (syntax, house rules, Tricky Words clashes and frequencies, Maths answers and levels).
- `node tools/match.js WORD heard...`: whether what the phone heard counts for a Tricky Words word.
- `python3 tools/smoke.py [--scribble] [--shots]`: opens every game in a headless phone-sized browser.
- `bash tools/deploy-status.sh`: waits for the latest Pages deploy and prints the result.

## Claude skill

`.claude/skills/kids-mini-games/SKILL.md` holds the rules and conventions for building games here (design for a non-reader, speech and microphone handling on iPhone, stars, fireworks, testing). Claude Code loads it automatically when working in this repo, and `AGENTS.md` points other coding agents to it.

## Games

- `tricky-words/`: Tricky Words. A word is shown, the child taps the microphone and says it. A right answer plays cheering and fireworks; a wrong one asks to try again; two mistakes are allowed, and after a third wrong try the game moves on. Each round is 5 words picked at random, with a gold star for each word said right within three tries and a grey star for each one missed. The current batch of new words (the `NEW` list in the game) comes up more often, and words he gets wrong on the first try also come up more often in later rounds; this is remembered in the browser on that phone.
- `maths/`: Maths. Each question is either a times question or an adding question, with equal chance. Numbers start small and grow as he does well: adding uses numbers up to 5, then up to 10, 15, 20 and 25; times uses 2 to 5, then 2 to 7 and 2 to 10 (never × 1, which is too easy). He moves up after scoring 7 out of the last 8 for that kind (1 for right first time, ½ for right after a mistake), and back down if he scores 1½ or less out of the last 5. The current levels show at the bottom of the end screen and are remembered in the browser on that phone. Questions are shown with four answer buttons in a 2×2 grid, one of them right. The speaker button reads the question out ("6 times 8 is?"). A right answer plays cheering and fireworks; a wrong answer buzzes, greys out that button and asks to try again. One mistake is allowed: after a second wrong answer the right one is shown and read out, and the game moves on. Each round is 5 questions with the same gold and grey stars, and questions he gets wrong on the first try come up more often later.
- `scribble/`: Scribble. It opens with a big ▶ start button (on iPhone, sound only turns on after a tap, and drawing doesn't count). A lowercase or capital letter or a digit is shown as a big faint shape on a drawing pad, and the game says what it is: letters as "bee like ball", numbers as "Draw number seven". The child draws over it with a finger. When most of the shape is covered (90%) and the ink stays mostly on it (no more than 25% of the ink off it, counting from just past the shape's edge), he gets cheering, fireworks and a gold star. Scribbling all over the pad doesn't count: it buzzes, rubs out and asks to stay on the shape. Two messy tries are allowed; the third moves on with a grey star. The speaker button repeats what to draw and the rubber button clears the pad. Under the buttons, letters show a small picture and a simple word with its first letter in bold blue, matching the shape's case (🍎 apple or Apple, ⚽ ball or Ball … 🦓 zebra); numbers show no word. Rounds are 5 shapes, and shapes he struggled with come up more often.
- `reading/`: Reading. A big picture (an emoji built into the phone) and four words in a 2×2 grid; tap the word that matches. Each question shows its words in one letter case, picked at random: cat, CAT or Cat. It opens with a big ▶ start button (so sound works on iPhone), says the word when each new picture appears, and has a speaker button to hear it again. The wrong words look alike (same first letter, a rhyme), never another name for the same picture, and the right word's place is shuffled. 292 words in 6 levels (three-letter words, blends, sh/ch/oo/ar sounds, long vowels, two syllables, longer words); he starts on level 1 and new levels open as he gets words right, like Maths. One mistake is allowed: the second wrong tap shows the right word in green, says "It says cat", gives a grey star and moves on. 5 words per round; words missed on the first try come up more often.
- `prizes/`: Prizes (tile uses the site's gold-star icon). Every gold star from every game is saved on the phone (`star-bank`); the menu shows the stars he has (earned minus spent). Prizes: Sushi and Strawberry milkshake, 100 stars each; a bar shows progress to each. Tapping one with enough stars asks with a big tick or cross before spending; one of each prize at a time: a bought prize gets a gold star badge and can't be bought again (it says "Sushi is coming! Ask a grown-up.") until a grown-up marks it on the Options page: **Given** (stars stay spent) or **Give stars back**.
- `options/`: Options, for grown-ups (a small link under the menu tiles; asks for the year you were born first, 18 to 110 years ago). Levels: each game's level (Maths adding and times, Reading), with "Back to level 1" for each. Prizes: what's been bought and is waiting to be given (Given / Give stars back), and the star totals. Voice: hear the British voices on this phone and choose one for every game, saved on the phone. On iPhone and iPad the default is the phone's own British voice (no voice named, only British English); elsewhere the games pick a British voice by name.
