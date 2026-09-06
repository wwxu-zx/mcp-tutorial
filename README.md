# MCP Tutorial

Small tutorial repo with two Python projects that demonstrate an MCP server and an OpenAI client using that server's tools.

- `weather-server`: an MCP server that exposes US weather alert and forecast tools backed by the National Weather Service API.
- `mcp-client`: an interactive OpenAI client that connects to an MCP server over stdio and lets the model call its tools.

## Prerequisites

- Python 3.10+
- `uv`
- An OpenAI API key

## Setup

Create a local environment file and set your API key:

```bash
cp mcp-client/.env.example mcp-client/.env
```

Then edit `mcp-client/.env` and set `OPENAI_API_KEY`.

## Run

Start the interactive client from the `mcp-client` directory. It will launch `weather-server` over stdio:

```bash
cd mcp-client
uv run client.py ../weather-server/weather.py
```

Example queries:

- `What's the weather in Sacramento?`
- `What are the active weather alerts in Texas?`
- `What are the weather alerts in California?`

## Inspect Server

Use MCP Inspector to test the server tools without the OpenAI client:

```bash
cd weather-server
uv run mcp dev weather.py
```

You can also run Inspector directly with `npx` from the project root:

```bash
npx @modelcontextprotocol/inspector uv --directory weather-server run weather.py
```

## Project Layout

```text
.
├── mcp-client/
│   ├── client.py
│   └── pyproject.toml
└── weather-server/
    ├── weather.py
    └── pyproject.toml
```

## Subproject Docs

- See `mcp-client/README.md` for client-specific configuration.
- See `weather-server/README.md` for server-specific entry points.

## References

This project is adapted from the official MCP Python quickstart resources:

- [weather-server-python](https://github.com/modelcontextprotocol/quickstart-resources/tree/main/weather-server-python)
- [mcp-client-python](https://github.com/modelcontextprotocol/quickstart-resources/tree/main/mcp-client-python)

## Notes

The weather server uses the US National Weather Service API, so forecast and alert tools are intended for US locations.
