#!/usr/bin/env bash
set -euo pipefail
[[ "$SETUPTOOLS_SCM_PRETEND_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.dev[0-9]+$ ]]
python -m build
