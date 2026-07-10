#! /usr/bin/env bash

# Exit in case of error
set -e

# Start the full stack in watch mode with the frontend running as a live Vite dev
# server (HMR + devtools). Layers the opt-in compose.dev.yml overlay on top of the
# default dev stack. Production/staging (`-f compose.yml`) and CI are unaffected.
docker compose -f compose.yml -f compose.override.yml -f compose.dev.yml watch
