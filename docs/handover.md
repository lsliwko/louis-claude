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
  - **Scribble** (`scribble/`): trace a lowercase or capital letter or a digit with a finger; word with bold first letter under the buttons for letters.
- Deploy: `.github/workflows/pages.yml` (newer push cancels an older run). Check with `bash tools/deploy-status.sh`.
- The skill in the user's Claude account was updated from the repo copy on 4 Nov (card sent; the user saves it).

## Open items

- Pages source is set to GitHub Actions (done 4 Nov), so only `pages.yml` deploys now.
- **Deploys blocked since 22:43 on 4 Nov** by a GitHub incident ("Incident with Actions and Pages", githubstatus.com): every run fails with "due to in progress deployment. Please cancel 0574466… first", although that deployment shows as finished (cancelling it says "it's finished"). The live site is 0574466, which has all the game changes; only docs and tool changes came after, and those aren't published anyway. First thing next session: push or run `gh workflow run pages.yml --repo lsliwko/louis-claude --ref main`, then `bash tools/deploy-status.sh`. If it still clashes after the incident is over, ask the user to switch Pages source to "Deploy from a branch" and back to "GitHub Actions".
- Nothing else pending.

## How the user works

- A parent testing on the child's iPhone (Chrome, sometimes Safari). Sends short change requests, often several in one message, sometimes from the phone with typos.
- Wants: the change made, checked, pushed, and a short reply ("live in a minute or two, close and reopen the tab"). Wants token use kept low: use the tools, grep instead of reading files, short replies.
- Commit straight to `main`; never force push; keep the repo name. Never put the child's name in files, commits or page text (public repo).
- British English everywhere.
- Things that can't be tested here (real speech recognition, iPhone sound) must be said plainly so he can try them on the phone.

## Lessons already learnt (don't repeat)

- Never start a SpeechRecognition on page load and never reload the page to restart: both broke the iPhone microphone.
- The shallow clone has no `origin/main` ref: use `git fetch origin main` + `FETCH_HEAD`.
- `gh api` for Pages settings is blocked by the proxy; `gh run list/view/rerun` work.
