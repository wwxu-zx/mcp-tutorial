# MCP Client

Interactive OpenAI client that connects to an MCP server over stdio. In this repo it is usually run with `../weather-server/weather.py`.

## Setup

Run this client from the `mcp-client` directory. Copy `.env.example` to `.env`, then set your API key.

```bash
cp .env.example .env
```

Required environment variable:

```bash
OPENAI_API_KEY=...
```

Optional environment variable:

```bash
OPENAI_MODEL=gpt-5.2
```

## Run

```bash
uv run client.py ../weather-server/weather.py
```

## Example Queries

- `What's the weather in Sacramento?`
- `What are the active weather alerts in Texas?`
- `What are the weather alerts in California?`

## Reference

Adapted from the official [mcp-client-python](https://github.com/modelcontextprotocol/quickstart-resources/tree/main/mcp-client-python) quickstart resource.
