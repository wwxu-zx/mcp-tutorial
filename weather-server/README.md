# Weather Server

MCP server backed by the US National Weather Service API. It exposes tools for US weather alerts and forecasts.

## Run Directly

```bash
uv run weather.py
```

## Inspect

Use MCP Inspector to test `get_alerts` and `get_forecast` directly:

```bash
uv run mcp dev weather.py
```

Or run Inspector directly with `npx`:

```bash
npx @modelcontextprotocol/inspector uv run weather.py
```

## Connect From Client

The usual tutorial flow starts the server through the client:

```bash
cd ../mcp-client
uv run client.py ../weather-server/weather.py
```

## Reference

Adapted from the official [weather-server-python](https://github.com/modelcontextprotocol/quickstart-resources/tree/main/weather-server-python) quickstart resource.
