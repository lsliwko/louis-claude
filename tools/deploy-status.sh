#!/usr/bin/env bash
# Wait for the latest "Deploy to GitHub Pages" run and print one line: result and commit.
#   bash tools/deploy-status.sh
repo=lsliwko/louis-claude
id=$(gh run list --repo $repo --workflow pages.yml --limit 1 --json databaseId -q '.[0].databaseId')
timeout 300 bash -c "until [ \"\$(gh run view $id --repo $repo --json status -q .status 2>/dev/null)\" = completed ]; do sleep 5; done"
gh run view "$id" --repo $repo --json conclusion,headSha,displayTitle -q '"deploy " + .conclusion + " " + .headSha[0:7] + " " + .displayTitle'
[ "$(gh run view "$id" --repo $repo --json conclusion -q .conclusion)" = success ] || gh run view "$id" --repo $repo --log-failed | grep -E '##\[error\]' | head -5
