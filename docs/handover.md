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
  - All pages: held sideways, a turn-the-phone-upright cover shows (web pages can't lock rotation; told the user about Portrait Orientation Lock in Control Centre).
  - Reading and Scribble open with ▶; every button but home is faded and disabled until it's tapped (user's request, 6 Nov). Tricky Words and Maths have no ▶ (their first tap is a real tap).
  - **Reading** (`reading/`, added 6 Nov): letter case varies per question (cat / CAT / Cat, user's request); emoji picture + 4 look-alike words, ▶ start button, says the word on each new picture, one mistake allowed. 6 Nov: fireworks sound was silent (cheer started while the word was being spoken): now waits for speech to finish; bigger picture (grows with the screen height); speaker stays centred under it like the other games (user's request). Then (user asked for ~500, progressively unlocked): 292 words in 6 reading-difficulty levels, unlocked like Maths (`rd-level`); there aren't many more emoji with one clear child-friendly name. Then only the first round's fireworks had sound (11:57): each answer tap now stops speech and remakes the sound engine inside the tap if speech ran since. Waiting for the user to confirm on the iPhone.
  - **Scribble** (`scribble/`): trace a lowercase or capital letter or a digit with a finger (shapes fill 60–90% of the pad; 90% must be covered, at most 25% of the ink outside a 3% margin); a small emoji picture and a word with bold first letter under the buttons for letters (j is now juice); the pad shrinks so the page fits the screen.
- Deploy: `.github/workflows/pages.yml` (newer push cancels an older run). Check with `bash tools/deploy-status.sh`.
- The skill in the user's Claude account was updated from the repo copy on 4 Nov (card sent; the user saves it).

## Open items

- Pages source is set to GitHub Actions (done 4 Nov), so only `pages.yml` deploys now.
- Scribble speech on Safari (4 Nov): the first tap now unlocks speech so the prompt is heard without pressing the speaker. Not testable here; waiting for the user to confirm on the iPhone. Maths got the same unlock (a silent word on the first tap), since its "Please try again" is said from a timer.
- Tricky Words fireworks sound stopping after a few rounds (5 Nov): sound engine now restarts from iPhone's "interrupted" state and the cheer/buzz wait for the mic to close. Tested with a fake mic only; waiting for the user to confirm on the iPhone.
- Scribble (5 Nov): no sound at all on iPhone until the speaker was tapped, because drawing (a moving finger) never counts as a tap. Now opens with a big ▶ start button over the pad; its tap turns sound on and says the prompt. Waiting for the user to confirm on the phone. Also reported: drawing freezes for a second or two when a new shape appears, i.e. while the prompt starts (user's screenshot: the stroke became a straight start-to-end line). Game code takes <1ms there, so it's the iPhone starting speech. Now every batched finger point is drawn (`getCoalescedEvents`), so strokes come out right after the freeze. User confirmed that fixed it. Tried the standard British voice in all games; the user preferred enhanced, so it's back to enhanced/premium first. Don't switch voices again without asking. Then the user found Daniel robotic, and iPhone turned out to hide downloaded voices from web pages (it lists two Daniels: compact and super-compact). The user tried "Phone's British voice" (no voice named, `lang` en-GB only) and found it best (6 Nov), so it's the default on iPhone/iPad. The page is now **Options** (`options/`, small link under the menu), behind a grown-up gate: type the year you were born (18–110 years ago). Voice choices are saved by `voiceURI`. **Best voice found (6 Nov): Jamie (Premium).** It's set on the iPhone in Settings › Accessibility › Spoken Content › Voices › English (UK), and the games get it through "Phone's British voice" (no voice named). Confirmed working by the user. If the voice ever sounds wrong, check that setting first; don't change the games' voice code without asking.
- A Pages deploy on 5 Nov ~20:10 timed out at "updating_pages" (GitHub side); the next push deployed fine. If it happens again, push or `gh workflow run pages.yml` once rather than rerunning in a loop.
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
- Safari won't speak (or play Web Audio) until there's been a real tap (`touchend`/`click` without the finger moving; drawing never counts, nor does `pointerdown`): anything said on load or from a timer before that is silently dropped.
- Scribble: making shapes bigger thickens their strokes, so the finger coverage disc and ink width must grow with them (smoke checks a centre-line trace still covers 90%).
- A `var` with the same name as a function replaces it: `var spoken=false` (Safari speech fix) broke Maths' `spoken(x)`, so two wrong answers stopped the game (5 Nov). `check.js` now checks names, and smoke checks two wrong answers move on.
- `gh api` for Pages settings is blocked by the proxy; `gh run list/view/rerun` work.
