"""Builder: introspect the GraphQL API and generate the typed `hyperflow` package.

Usage (from the repository root):
    python codegen/generate.py

The endpoint and optional introspection auth are read from the same env vars the
runtime client uses (HYPERFLOW_API_URL / HYPERFLOW_AUTH_HEADER / HYPERFLOW_AUTH_VALUE),
falling back to the defaults in ``codegen/ariadne.toml``.

The client is generated on the fly straight from the live schema (introspection);
nothing is saved to disk except the generated, gitignored ``src/hyperflow`` package.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_CONFIG = ROOT / "codegen" / "ariadne.toml"

ENV_URL = "HYPERFLOW_API_URL"
ENV_AUTH_HEADER = "HYPERFLOW_AUTH_HEADER"
ENV_AUTH_VALUE = "HYPERFLOW_AUTH_VALUE"


def _build_config() -> str:
    """Write a config with env overrides applied and return its path."""
    text = BASE_CONFIG.read_text(encoding="utf-8")
    url = os.getenv(ENV_URL)
    if url:
        text = re.sub(
            r"(?m)^remote_schema_url\s*=.*$",
            f'remote_schema_url = "{url}"',
            text,
        )
    value = os.getenv(ENV_AUTH_VALUE)
    if value:
        header = os.getenv(ENV_AUTH_HEADER) or "Authorization"
        text += f'\nremote_schema_headers = {{ "{header}" = "{value}" }}\n'
    fd, path = tempfile.mkstemp(suffix=".toml")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


def _run(config: str, *args: str) -> None:
    cmd = [sys.executable, "-m", "ariadne_codegen", *args, "--config", config]
    print("$", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def _expose_connect() -> None:
    """Re-export the convenience factory at the package top level."""
    init = ROOT / "src" / "hyperflow" / "__init__.py"
    line = "from ._client import connect"
    text = init.read_text(encoding="utf-8")
    if line not in text:
        init.write_text(f"{text.rstrip()}\n{line}\n", encoding="utf-8")


def main() -> int:
    (ROOT / "src").mkdir(exist_ok=True)  # target_package_path must exist
    config = _build_config()
    try:
        _run(config)  # introspects live schema, writes src/hyperflow
    finally:
        os.unlink(config)
    _expose_connect()
    print("Generation complete: src/hyperflow")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
