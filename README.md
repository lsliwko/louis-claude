# Games

Simple learning games, published with GitHub Pages at https://lsliwko.github.io/louis-claude/

## Layout

- `index.html` is the menu. It shows one picture tile per game.
- Each game lives in its own folder with its own `index.html`, for example `tricky-words/`.

## Adding a game

1. Create a new folder, for example `counting/`, with an `index.html` inside.
2. In the game page, add a home button that links to `../` so it can get back to the menu.
3. In the root `index.html`, copy the existing tile and change its link, colours, icon and name.

## Games

- `tricky-words/`: Tricky Words. A word is shown, the child taps the microphone and says it. A right answer plays cheering and fireworks; a wrong one asks to try again, and after four tries the game moves on. Each round is 5 words picked at random, with a gold star for each word said right within four tries and a grey star for each one missed. Words he gets wrong on the first try come up more often in later rounds; this is remembered in the browser on that phone.
