#!/usr/bin/env bash
UV_NO_SYNC=1 exec uv run python "$(dirname "$0")/tt.py" "$@"
