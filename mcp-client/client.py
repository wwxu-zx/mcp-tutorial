# https://github.com/modelcontextprotocol/quickstart-resources/tree/main/mcp-client-python
import asyncio
import os
import json
from typing import Any
from contextlib import AsyncExitStack
from pathlib import Path


from openai import OpenAI
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()  # load environment variables from .env

DEFAULT_OPENAI_MODEL = "gpt-5.2"
MAX_TOOL_TURNS = 10


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()
        self.model = os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
        self._openai: OpenAI | None = None

    @property
    def openai(self) -> OpenAI:
        """Lazy-initialize OpenAI client when needed."""
        if self._openai is None:
            self._openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        return self._openai

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith(".py")
        is_js = server_script_path.endswith(".js")
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        if is_python:
            path = Path(server_script_path).resolve()
            server_params = StdioServerParameters(
                command="uv",
                args=["--directory", str(path.parent), "run", path.name],
                env=None,
            )
        else:
            server_params = StdioServerParameters(
                command="node",
                args=[server_script_path],
                env=None,
            )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    @staticmethod
    def _format_tool_output(content: Any) -> str:
        """Convert MCP tool results into plain text for the Responses API."""
        if isinstance(content, str):
            return content

        if isinstance(content, list):
            parts = []
            for item in content:
                text = getattr(item, "text", None)
                if text is not None:
                    parts.append(text)
                    continue

                item_text = None
                if hasattr(item, "model_dump"):
                    dumped = item.model_dump()
                    item_text = dumped.get("text")
                elif isinstance(item, dict):
                    item_text = item.get("text")

                parts.append(item_text if item_text is not None else str(item))
            return "\n".join(parts)

        return str(content)

    async def process_query(self, query: str) -> str:
        """Process a query using OpenAI and available MCP tools."""
        tools_response = await self.session.list_tools()
        available_tools = [
            {
                "type": "function",
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema,
                "strict": False,
            }
            for tool in tools_response.tools
        ]

        final_text = []
        response = self.openai.responses.create(
            model=self.model,
            max_output_tokens=1000,
            input=query,
            tools=available_tools,
        )

        for _ in range(MAX_TOOL_TURNS):
            if response.output_text:
                final_text.append(response.output_text)

            tool_calls = [item for item in response.output if item.type == "function_call"]
            if not tool_calls:
                return "\n".join(final_text)

            tool_outputs = []
            for tool_call in tool_calls:
                tool_args = json.loads(tool_call.arguments) if tool_call.arguments else {}
                result = await self.session.call_tool(tool_call.name, tool_args)
                final_text.append(f"[Calling tool {tool_call.name} with args {tool_args}]")
                tool_outputs.append({
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": self._format_tool_output(result.content),
                })

            response = self.openai.responses.create(
                model=self.model,
                max_output_tokens=1000,
                previous_response_id=response.id,
                input=tool_outputs,
                tools=available_tools,
            )

        final_text.append(f"[Stopped after {MAX_TOOL_TURNS} tool-use turns]")
        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if query.lower() == "quit":
                break

            try:
                response = await self.process_query(query)
                print("\n" + response)
            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])

        # Check if we have a valid API key to continue
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("\nNo OPENAI_API_KEY found. To query these tools with OpenAI, set your API key:")
            print("  export OPENAI_API_KEY=your-api-key-here")
            return

        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    import sys
    asyncio.run(main())
