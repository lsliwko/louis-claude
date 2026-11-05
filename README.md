# Games

Simple learning games, published with GitHub Pages at https://lsliwko.github.io/louis-claude/

## Layout

- `index.html` is the menu. It shows one picture tile per game.
- Each game lives in its own folder with its own `index.html`, for example `tricky-words/`.

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
- `voices/`: Voice (for grown-ups, a small link under the menu tiles). Lists the British voices on this phone, plays a sample of each, and saves the chosen one on the phone; every game then uses it (otherwise the games pick an enhanced/premium British voice).
