#!/usr/bin/env bash
set -euo pipefail
status=$(curl -sS -o /dev/null -w '%{http_code}' "https://pypi.org/pypi/hf-py-sdk/$VERSION/json")
case "$status" in
  200) echo "exists=true" >> "$GITHUB_OUTPUT" ;;
  404) echo "exists=false" >> "$GITHUB_OUTPUT" ;;
  *) echo "Unexpected PyPI status $status"; exit 1 ;;
esac
