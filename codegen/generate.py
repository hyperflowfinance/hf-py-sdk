"""Generate the typed package from local SDL or live schema introspection."""

from __future__ import annotations

import json
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
ENV_SCHEMA_PATH = "HYPERFLOW_SCHEMA_PATH"
ENV_DEFAULT_URL = "HYPERFLOW_DEFAULT_API_URL"


def _toml_str(value: str) -> str:
    """Quote a TOML basic string; JSON string escapes are valid TOML escapes."""
    return json.dumps(value)


def _build_config() -> str:
    """Write a config with env overrides applied and return its path."""
    text = BASE_CONFIG.read_text(encoding="utf-8")
    schema_path = os.getenv(ENV_SCHEMA_PATH)
    if schema_path:
        text = re.sub(r"(?m)^remote_schema_url\s*=.*\n?", "", text)
        path = Path(schema_path)
        if not path.is_absolute():
            path = ROOT / path
        text += f"\nschema_path = {_toml_str(str(path.resolve()))}\n"
    url = os.getenv(ENV_URL)
    if url and not schema_path:
        text = re.sub(
            r"(?m)^remote_schema_url\s*=.*$",
            lambda _: f"remote_schema_url = {_toml_str(url)}",
            text,
        )
    value = os.getenv(ENV_AUTH_VALUE)
    if value:
        header = os.getenv(ENV_AUTH_HEADER) or "Authorization"
        text += f"\nremote_schema_headers = {{ {_toml_str(header)} = {_toml_str(value)} }}\n"
    fd, path = tempfile.mkstemp(suffix=".toml")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


def _run(config: str, *args: str) -> None:
    cmd = [sys.executable, "-m", "ariadne_codegen", *args, "--config", config]
    print("$", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def _finish_package() -> None:
    """Re-export connect() and mark the package as typed (PEP 561)."""
    package = ROOT / "src" / "hyperflow"
    init = package / "__init__.py"
    line = "from ._client import connect"
    text = init.read_text(encoding="utf-8")
    if line not in text:
        init.write_text(f"{text.rstrip()}\n{line}\n", encoding="utf-8")
    endpoint = os.getenv(ENV_DEFAULT_URL)
    if endpoint:
        client = package / "_client.py"
        text, count = re.subn(
            r'(?m)^DEFAULT_URL = .+$',
            f"DEFAULT_URL = {_toml_str(endpoint)}",
            client.read_text(encoding="utf-8"),
        )
        if count != 1:
            raise RuntimeError("Could not set generated client default endpoint")
        client.write_text(text, encoding="utf-8")
    (package / "py.typed").touch()


def main() -> int:
    (ROOT / "src").mkdir(exist_ok=True)  # target_package_path must exist
    config = _build_config()
    try:
        _run(config)  # introspects live schema, writes src/hyperflow
    finally:
        os.unlink(config)
    _finish_package()
    print("Generation complete: src/hyperflow")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
