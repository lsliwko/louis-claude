# Games

Simple learning games, published with GitHub Pages at https://lsliwko.github.io/louis-claude/

## Layout

- `index.html` is the menu. It shows one picture tile per game.
- Each game lives in its own folder with its own `index.html`, for example `tricky-words/`.

## Adding a game

1. Create a new folder, for example `counting/`, with an `index.html` inside.
2. In the game page, add a home button that links to `../` so it can get back to the menu.
3. In the root `index.html`, copy the existing tile and change its link, colours, icon and name.

## Claude skill

`.claude/skills/kids-mini-games/SKILL.md` holds the rules and conventions for building games here (design for a non-reader, speech and microphone handling on iPhone, stars, fireworks, testing). Claude Code loads it automatically when working in this repo, and `AGENTS.md` points other coding agents to it.

## Games

- `tricky-words/`: Tricky Words. A word is shown, the child taps the microphone and says it. A right answer plays cheering and fireworks; a wrong one asks to try again, and after four tries the game moves on. Each round is 5 words picked at random, with a gold star for each word said right within four tries and a grey star for each one missed. The current batch of new words (the `NEW` list in the game) comes up more often, and words he gets wrong on the first try also come up more often in later rounds; this is remembered in the browser on that phone.
- `maths/`: Maths. Each question is either a times question (a × b, both numbers from 1 to 10) or an adding question (a + b, both numbers from 0 to 40), with equal chance, shown with three answer buttons, one of them right. The speaker button reads the question out ("6 times 8 is?"). A right answer plays cheering and fireworks; a wrong answer buzzes, greys out that button and asks to try again. After two wrong answers the right one is shown and read out, and the game moves on. Each round is 5 questions with the same gold and grey stars, and questions he gets wrong on the first try come up more often later.
