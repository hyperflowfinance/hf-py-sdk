"""Minimal example: one query and one subscription against the HyperFlow API.

Run (uses HYPERFLOW_API_URL / HYPERFLOW_AUTH_* env vars, or the defaults):

    python examples/app.py

Subscriptions require the websockets extra:  pip install "hf-py-sdk[subscriptions]"
"""

from __future__ import annotations

import asyncio

from hyperflow import connect
from hyperflow.custom_fields import MetadataFields
from hyperflow.custom_queries import Query

# Custom-operations builder generates Query/Mutation only, so the subscription
# is sent as a raw graphql-transport-ws operation over the websocket.
NEW_BLOCKS = """
subscription NewBlocks {
  newBlocks { number hash timestamp gasUsed }
}
"""


async def run_query(client) -> None:
    data = await client.query(
        Query.metadata().fields(
            MetadataFields.chain_id,
            MetadataFields.eth_block_number,
            MetadataFields.eth_gas_price,
            MetadataFields.client_version,
        ),
        operation_name="GetMetadata",
    )
    print("QUERY metadata ->", data)


async def run_subscription(client, limit: int = 3) -> None:
    print(f"SUBSCRIBE newBlocks (first {limit})...")
    count = 0
    async for message in client.execute_ws(NEW_BLOCKS, operation_name="NewBlocks"):
        print("  block ->", message)
        count += 1
        if count >= limit:
            break


async def main() -> None:
    async with connect() as client:
        await run_query(client)
        await run_subscription(client)


if __name__ == "__main__":
    asyncio.run(main())
