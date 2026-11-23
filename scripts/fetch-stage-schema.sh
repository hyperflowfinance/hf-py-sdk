#!/usr/bin/env bash
set -euo pipefail
: "${SCHEMA_HASH:?}" "${SCHEMA_SDL_URL:?}" "${SCHEMA_INTROSPECTION_URL:?}"
[[ "$SCHEMA_HASH" =~ ^[0-9a-f]{64}$ ]]
[[ "$SCHEMA_SDL_URL" == "https://d2ykgs71sjxp8n.cloudfront.net/schema/versions/$SCHEMA_HASH/schema.graphql" ]]
[[ "$SCHEMA_INTROSPECTION_URL" == "https://d2ykgs71sjxp8n.cloudfront.net/schema/versions/$SCHEMA_HASH/introspection.json" ]]
curl -fsS "$SCHEMA_SDL_URL" -o stage-schema.graphql
curl -fsS "$SCHEMA_INTROSPECTION_URL" -o stage-introspection.json
actual=$(printf '\0' | cat stage-schema.graphql - stage-introspection.json | sha256sum | cut -d' ' -f1)
test "$actual" = "$SCHEMA_HASH"
