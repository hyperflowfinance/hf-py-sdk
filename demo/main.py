"""Standalone demo for the published `hf-py-sdk` package.

Setup:
    python -m venv .venv
    .venv\\Scripts\\activate          # Windows (use source .venv/bin/activate on *nix)
    pip install "hf-py-sdk[subscriptions]"

Run against the public endpoint (no key needed):
    set HYPERFLOW_API_URL=https://api.hyperflow.finance/ethereum/graphql   # Windows
    python demo/main.py

For the key-protected default endpoint, set HYPERFLOW_AUTH_VALUE (and
HYPERFLOW_AUTH_HEADER, e.g. "x-api-key") instead.
"""

from __future__ import annotations

import asyncio

from hyperflow import connect
from hyperflow.custom_fields import MetadataFields
from hyperflow.custom_queries import Query

# The custom-operations builder emits Query/Mutation only, so subscriptions are
# sent as a raw graphql-transport-ws operation over the websocket.
NEW_BLOCKS = """
subscription NewBlocks {
  newBlocks { number hash timestamp gasUsed }
}
"""


async def fetch_metadata(client) -> None:
    data = await client.query(
        Query.metadata().fields(
            MetadataFields.chain_id,
            MetadataFields.eth_block_number,
            MetadataFields.eth_gas_price,
            MetadataFields.client_version,
        ),
        operation_name="GetMetadata",
    )
    print("metadata ->", data)


async def stream_blocks(client, limit: int = 3) -> None:
    print(f"streaming newBlocks (first {limit})...")
    seen = 0
    async for message in client.execute_ws(NEW_BLOCKS, operation_name="NewBlocks"):
        print("  block ->", message)
        seen += 1
        if seen >= limit:
            break


async def main() -> None:
    async with connect() as client:
        await fetch_metadata(client)
        await stream_blocks(client)


if __name__ == "__main__":
    asyncio.run(main())
