# Handover

Read this at the start of every session, after `AGENTS.md`. Update it at the end of a session (or when something here stops being true) so the next session can start without re-reading the history.

## Start a session

```
cd /home/claude/louis-claude && git fetch -q origin main && git reset -q --hard FETCH_HEAD   # or clone if missing
node tools/check.js                                                                        # should be all "ok"
```

Then read `.claude/skills/kids-mini-games/SKILL.md` for the rules and `docs/tools.md` for the tools. Don't read whole game files: grep for the part you need.

## Current state (4 Nov 2026)

- Live at https://lsliwko.github.io/louis-claude/. Latest work is all pushed to `main`; deploys succeed.
- Games on the menu (all blue tiles):
  - **Tricky Words** (`tricky-words/`): say the shown word. Words: I, be, me, we, to, he, she, the, do, of, all, are, was. New-words batch `NEW = the, of, all, are`. Two mistakes allowed.
  - **Maths** (`maths/`): times (2–10, levels 2–5 → 2–7 → 2–10) and adding (levels 0–5 … 0–25), 4 answers in a 2×2 grid, one mistake allowed, levels go up and down with how he does.
  - **Scribble** (`scribble/`): trace a lowercase or capital letter or a digit with a finger (90% of the shape must be covered, at most 25% of the ink outside a 3% margin); word with bold first letter under the buttons for letters.
- Deploy: `.github/workflows/pages.yml` (newer push cancels an older run). Check with `bash tools/deploy-status.sh`.
- The skill in the user's Claude account was updated from the repo copy on 4 Nov (card sent; the user saves it).

## Open items

- Pages source is set to GitHub Actions (done 4 Nov), so only `pages.yml` deploys now.
- Scribble speech on Safari (4 Nov): the first tap now unlocks speech so the prompt is heard without pressing the speaker. Not testable here; waiting for the user to confirm on the iPhone. Maths got the same unlock (a silent word on the first tap), since its "Please try again" is said from a timer.
- Nothing else pending. (The GitHub incident that blocked deploys on the evening of 4 Nov cleared by itself: the 22:50 run succeeded. If a run ever fails with "due to in progress deployment … cancel … first" again, check githubstatus.com and wait rather than retrying in a loop; as a last resort ask the user to switch Pages source to "Deploy from a branch" and back to "GitHub Actions".)

## How the user works

- A parent testing on the child's iPhone (Chrome, sometimes Safari). Sends short change requests, often several in one message, sometimes from the phone with typos.
- Wants: the change made, checked, pushed, and a short reply ("live in a minute or two, close and reopen the tab"). Wants token use kept low: use the tools, grep instead of reading files, short replies.
- Commit straight to `main`; never force push; keep the repo name. Never put the child's name in files, commits or page text (public repo).
- British English everywhere.
- Things that can't be tested here (real speech recognition, iPhone sound) must be said plainly so he can try them on the phone.

## Lessons already learnt (don't repeat)

- Never start a SpeechRecognition on page load and never reload the page to restart: both broke the iPhone microphone.
- The shallow clone has no `origin/main` ref: use `git fetch origin main` + `FETCH_HEAD`.
- Safari won't speak until speech is first started inside a tap (`touchend`/`click`, not `pointerdown`): anything said on load or from a timer before that is silently dropped.
- `gh api` for Pages settings is blocked by the proxy; `gh run list/view/rerun` work.
