"""Per-request headers may be a mapping or HTTPX-style (name, value) pairs."""

import unittest

import httpx

from hyperflow import connect


class HeaderMergeTests(unittest.IsolatedAsyncioTestCase):
    async def _send(self, headers) -> httpx.Request:
        seen: list[httpx.Request] = []
        transport = httpx.MockTransport(
            lambda request: seen.append(request) or httpx.Response(200, json={})
        )
        async with httpx.AsyncClient(transport=transport) as http:
            client = connect(http_client=http, auth_value="key", headers={"x-a": "1"})
            await client.execute("{ __typename }", headers=headers)
        return seen[0]

    async def test_list_headers_are_merged(self) -> None:
        request = await self._send([("x-b", "2"), ("x-a", "override")])
        self.assertEqual(request.headers["authorization"], "key")
        self.assertEqual(request.headers["x-b"], "2")
        self.assertEqual(request.headers["x-a"], "override")

    async def test_mapping_headers_are_merged(self) -> None:
        request = await self._send({"X-B": "2"})
        self.assertEqual(request.headers["x-a"], "1")
        self.assertEqual(request.headers["x-b"], "2")


if __name__ == "__main__":
    unittest.main()
