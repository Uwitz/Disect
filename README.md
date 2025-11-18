# Disect

[![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?&logo=discord&logoColor=white)](https://discord.gg/YwC6VpEPfq) [![Actions status](https://github.com/Uwitz/Disect/actions/workflows/codeql.yml/badge.svg)](https://github.com/Uwitz/Disect/actions)

A discord bot to automate all of the backend functionality of Uwitz.
## Installation
If you don't have `uv` installed:
```bash
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh
```
```bash
# On Windows.
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Install dependencies with `uv`:
```
uv sync
```
## Setup
1. Create a `resources` folder and store your mongo certificate as `mongo_cert.pem`.
2. `.env` should contain the `MONGO` and `TOKEN` variables.
3. `metadata.json` should have the following schema:
```json
{
    "GUILD": 000000000000000000,
    "EMOJI_FAIL": ":prohibited:",
    "EMOJI_SUCCESS": ":white_check_mark:"
}
```

After setup, you can use `uv` to run the bot:
```bash
uv run main.py
```