#!/usr/bin/env bash
# Wait for the "Deploy to GitHub Pages" run of the commit you just pushed and print one line: result and commit.
#   bash tools/deploy-status.sh            (uses the current HEAD)
repo=lsliwko/louis-claude; sha=${1:-$(git -C "$(dirname "$0")/.." rev-parse HEAD)}
q='[.[]|select(.headSha=="'$sha'")][0].databaseId // empty'
timeout 120 bash -c "until [ -n \"\$(gh run list --repo $repo --workflow pages.yml --limit 10 --json databaseId,headSha -q '$q')\" ]; do sleep 5; done" || { echo "no deploy run found for ${sha:0:7}"; exit 1; }
id=$(gh run list --repo $repo --workflow pages.yml --limit 10 --json databaseId,headSha -q "$q")
wait_run(){ timeout 300 bash -c "until [ \"\$(gh run view $id --repo $repo --json status -q .status 2>/dev/null)\" = completed ]; do sleep 5; done"; }
wait_run
# Another Pages deploy still running (e.g. GitHub's built-in one) makes ours fail. Re-running the same run would upload a
# second artifact and fail again, so start a fresh run instead (up to twice).
for i in 1 2; do
  [ "$(gh run view "$id" --repo $repo --json conclusion -q .conclusion)" = failure ] && gh run view "$id" --repo $repo --log-failed 2>/dev/null | grep -q "in progress deployment" || break
  echo "clashed with a deploy in progress; starting a fresh run in 30s"; sleep 30; old=$id
  gh workflow run pages.yml --repo $repo --ref main
  timeout 60 bash -c "until [ \"\$(gh run list --repo $repo --workflow pages.yml --limit 1 --json databaseId -q '.[0].databaseId')\" != $old ]; do sleep 3; done"
  id=$(gh run list --repo $repo --workflow pages.yml --limit 1 --json databaseId -q '.[0].databaseId'); wait_run
done
gh run view "$id" --repo $repo --json conclusion,headSha,displayTitle -q '"deploy " + .conclusion + " " + .headSha[0:7] + " " + .displayTitle'
[ "$(gh run view "$id" --repo $repo --json conclusion -q .conclusion)" = success ] || gh run view "$id" --repo $repo --log-failed | grep -E '##\[error\]' | head -5
