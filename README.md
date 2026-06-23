# hf-py-sdk

Typed **async** Python client for the [HyperFlow](https://hyperflowlabs.com) GraphQL API.

The client is generated from the live GraphQL schema with
[`ariadne-codegen`](https://github.com/mirumee/ariadne-codegen). The generated
package and the downloaded schema are **not** committed — they are regenerated
from the schema on every release.

## Install

```bash
pip install hf-py-sdk
```

## Usage

```python
import asyncio
from hyperflow import connect

async def main():
    # Reads HYPERFLOW_API_URL / HYPERFLOW_AUTH_HEADER / HYPERFLOW_AUTH_VALUE
    # from the environment, with arguments taking precedence.
    client = connect()
    # ...or pass explicitly:
    # client = connect(url="...", auth_header="Authorization", auth_value="Bearer X")
    # result = await client.query(...)

asyncio.run(main())
```

Configuration (argument → env var → default):

| Argument | Env var | Default |
| --- | --- | --- |
| `url` | `HYPERFLOW_API_URL` | Ethereum endpoint |
| `auth_header` | `HYPERFLOW_AUTH_HEADER` | `Authorization` |
| `auth_value` | `HYPERFLOW_AUTH_VALUE` | _(none — no auth)_ |

Copy `.env.example` to `.env` to set these locally.

## Regenerate the client locally

```bash
pip install ariadne-codegen
python codegen/generate.py
pip install -e .
```

This generates the typed package into `src/hyperflow/` (gitignored) on the fly,
straight from the live schema — nothing else is written to disk. The builder reads
the same env vars as the runtime client (`HYPERFLOW_API_URL`, and optionally
`HYPERFLOW_AUTH_HEADER` / `HYPERFLOW_AUTH_VALUE` for private endpoints), falling
back to the defaults in `codegen/ariadne.toml`.

## Release

Push a version tag to publish a new version to PyPI via GitHub Actions:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The release workflow regenerates the client from the live schema, builds the
package (version derived from the tag), and publishes it to PyPI using OIDC
trusted publishing. Configure a
[trusted publisher](https://docs.pypi.org/trusted-publishers/) for this repo and
a `pypi` environment in the GitHub repository settings.

## Layout

| Path | Purpose |
| --- | --- |
| `codegen/ariadne.toml` | `ariadne-codegen` configuration |
| `codegen/generate.py` | Builder: dump schema + generate client |
| `codegen/include/_client.py` | `connect()` convenience layer (shipped in the package) |
| `src/hyperflow/` | Generated client (gitignored) |
