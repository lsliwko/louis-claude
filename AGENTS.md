# Agent instructions

This repo is a small set of learning games for a 5-year-old who can't read yet. He plays them on an iPhone in Chrome. The site is published with GitHub Pages from the `main` branch at https://lsliwko.github.io/louis-claude/

## Before you change anything

Read `.claude/skills/kids-mini-games/SKILL.md` first. It holds the rules for every game: design for a non-reader, the speech and microphone handling that works on iPhone, stars, sounds and fireworks, round length and tries, and how to test.

## Layout

- `index.html` is the games menu, with one picture tile per game.
- Each game is a single self-contained `index.html` in its own folder, e.g. `tricky-words/`.
- `tricky-words/index.html` is the reference implementation. Copy shared code from it rather than rewriting it.
- `README.md` lists the games. Keep it up to date.

## Working rules

- British English everywhere: spoken voice and speech recognition use `en-GB` only (never fall back to a US voice), and pages are marked `lang="en-GB"`.
- Plain HTML, CSS and JavaScript only: no build step, no frameworks, and no external assets apart from Google Fonts.
- Never reload the page to restart a game; reset the round in place (reloading leaves the iPhone microphone stuck).
- Test in a headless browser with a simulated speech recognizer before pushing, and say plainly what couldn't be tested on a real phone.
- Commit straight to `main` with a short message describing the change. GitHub Pages takes a few minutes to update.
