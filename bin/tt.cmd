@echo off
set UV_NO_SYNC=1
uv run python "%~dp0tt.py" %*
