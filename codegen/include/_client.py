"""Convenience layer shipped inside the generated ``hyperflow`` package.

This file is committed (it lives in ``codegen/include/``) and copied into the
generated package via the ``files_to_include`` option, so it survives every
regeneration. It provides a small factory on top of the generated, fully typed
``Client`` with a configurable URL and a configurable auth header, all of which
can be supplied via environment variables.
"""

from __future__ import annotations

import os
import re
from typing import Optional

from .client import Client

# Default endpoint. Override to target a different network/deployment.
DEFAULT_URL = "https://api.hyperflowlabs.com/ethereum/graphql"

# Environment variable names.
ENV_URL = "HYPERFLOW_API_URL"
ENV_AUTH_HEADER = "HYPERFLOW_AUTH_HEADER"  # header name, e.g. "Authorization"
ENV_AUTH_VALUE = "HYPERFLOW_AUTH_VALUE"  # header value, e.g. "Bearer <token>"


def connect(
    url: Optional[str] = None,
    auth_header: Optional[str] = None,
    auth_value: Optional[str] = None,
    *,
    headers: Optional[dict] = None,
    **kwargs,
) -> Client:
    """Create a typed async ``Client``.

    Each argument falls back to an environment variable, then to a default.

    Args:
        url: GraphQL endpoint. Env: ``HYPERFLOW_API_URL``. Defaults to Ethereum.
        auth_header: Auth header name. Env: ``HYPERFLOW_AUTH_HEADER``.
            Defaults to ``"Authorization"`` when a value is present.
        auth_value: Auth header value. Env: ``HYPERFLOW_AUTH_VALUE``.
        headers: Extra headers merged into every request.
        **kwargs: Forwarded to the generated ``Client`` (e.g. ``http_client``).
    """
    url = url or os.getenv(ENV_URL) or DEFAULT_URL
    auth_value = auth_value or os.getenv(ENV_AUTH_VALUE)
    auth_header = auth_header or os.getenv(ENV_AUTH_HEADER) or "Authorization"

    merged = dict(headers or {})
    if auth_value:
        merged.setdefault(auth_header, auth_value)

    # Derive the websocket endpoint (http->ws, https->wss) for subscriptions.
    kwargs.setdefault("ws_url", re.sub(r"^http", "ws", url))
    kwargs.setdefault("ws_headers", merged)
    return Client(url=url, headers=merged, **kwargs)
