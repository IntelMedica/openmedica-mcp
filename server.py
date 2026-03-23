"""OpenMedica MCP Server - AI agent integration via FastMCP."""

import os
import asyncio
from mcp.server import Server
from mcp.types import Tool
from mcp.tools import (
    clinical_search_tool,
    document_lookup_tool,
    call_clinical_search,
    call_document_lookup,
)

APP_NAME = "openmedica"
APP_VERSION = "1.0.0"

server = Server(APP_NAME)


@server.list_tools()
async def list_tools():
    """List all available MCP tools."""
    return [clinical_search_tool, document_lookup_tool]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    if name == "clinical_search":
        return await call_clinical_search(**arguments)
    elif name == "document_lookup":
        return await call_document_lookup(**arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


def get_api_url() -> str:
    """Get API base URL from environment."""
    return os.getenv("OPENMEDICA_API_URL", "http://localhost:8000/api/v1")


def main():
    """Run the MCP server."""
    from mcp.server.stdio import stdio_server

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )

    asyncio.run(run())


if __name__ == "__main__":
    main()
