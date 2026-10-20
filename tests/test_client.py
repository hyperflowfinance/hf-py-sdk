"""Behavioural tests for the generated package (run after codegen/generate.py)."""

from __future__ import annotations

import importlib.util
import json
import os
import unittest
from importlib.resources import files
from pathlib import Path
from unittest import mock

import httpx
from graphql import parse

from hyperflow import async_base_client, connect
from hyperflow.custom_fields import MetadataFields
from hyperflow.custom_queries import Query

try:
    import tomllib
except ImportError:  # Python 3.10
    tomllib = None

ROOT = Path(__file__).resolve().parent.parent


def _recording_client(seen: list[httpx.Request]) -> httpx.AsyncClient:
    def reply(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"data": {"info": {"chainId": "0x1"}}})

    return httpx.AsyncClient(transport=httpx.MockTransport(reply))


class ClientTests(unittest.IsolatedAsyncioTestCase):
    async def _query(self, **connect_kwargs) -> list[httpx.Request]:
        seen: list[httpx.Request] = []
        async with _recording_client(seen) as http:
            async with connect(http_client=http, **connect_kwargs) as client:
                data = await client.query(
                    Query.metadata().alias("info").fields(MetadataFields.chain_id()),
                    operation_name="Metadata",
                )
        self.assertEqual(data, {"info": {"chainId": "0x1"}})
        return seen

    async def test_query_sends_valid_graphql(self) -> None:
        (request,) = await self._query()
        parse(json.loads(request.content)["query"])

    async def test_auth_reaches_custom_http_client(self) -> None:
        (request,) = await self._query(
            auth_header="x-api-key", auth_value="test-key", headers={"x-extra": "1"}
        )
        self.assertEqual(request.headers["x-api-key"], "test-key")
        self.assertEqual(request.headers["x-extra"], "1")

    async def test_custom_http_client_is_not_mutated(self) -> None:
        async with httpx.AsyncClient() as http:
            connect(http_client=http, auth_value="test-key")
            self.assertNotIn("authorization", http.headers)


class PackagingTests(unittest.TestCase):
    def test_package_is_typed(self) -> None:
        self.assertTrue(files("hyperflow").joinpath("py.typed").is_file())

    @unittest.skipUnless(importlib.util.find_spec("websockets"), "subscriptions extra")
    def test_subscriptions_use_real_websockets(self) -> None:
        self.assertTrue(async_base_client.ws_connect.__module__.startswith("websockets"))


@unittest.skipIf(tomllib is None, "tomllib needs Python 3.11+")
class CodegenConfigTests(unittest.TestCase):
    def test_env_values_are_toml_escaped(self) -> None:
        spec = importlib.util.spec_from_file_location("gen", ROOT / "codegen/generate.py")
        gen = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gen)
        env = {
            "HYPERFLOW_API_URL": 'https://example.test/"q"\\graphql',
            "HYPERFLOW_AUTH_HEADER": "x-api-key",
            "HYPERFLOW_AUTH_VALUE": 'to"ken\\value',
        }
        with mock.patch.dict(os.environ, env):
            path = gen._build_config()
        try:
            config = tomllib.loads(Path(path).read_text(encoding="utf-8"))
        finally:
            os.unlink(path)
        section = config["tool"]["ariadne-codegen"]
        self.assertEqual(section["remote_schema_url"], env["HYPERFLOW_API_URL"])
        self.assertEqual(section["remote_schema_headers"], {"x-api-key": env["HYPERFLOW_AUTH_VALUE"]})


if __name__ == "__main__":
    unittest.main()
