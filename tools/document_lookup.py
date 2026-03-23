"""Document lookup tool for AI agents - MCP-03."""

import os
from mcp.types import Tool, TextContent
import httpx


class DocumentLookupTool:
    """Document lookup tool implementation."""

    name = "document_lookup"
    description = """Look up a specific clinical document by ID.
    
    Use this when:
    - You have a document ID from a previous search
    - You need to retrieve full document content
    - You want detailed information about a specific clinical resource
    
    Returns the complete document content including metadata.
    """

    input_schema = {
        "type": "object",
        "properties": {
            "document_id": {
                "type": "string",
                "description": "The document ID to retrieve",
            }
        },
        "required": ["document_id"],
    }


document_lookup_tool = Tool(
    name=DocumentLookupTool.name,
    description=DocumentLookupTool.description,
    inputSchema=DocumentLookupTool.input_schema,
)


async def call_document_lookup(document_id: str) -> list[TextContent]:
    """Look up a document by ID and return full content."""
    api_url = os.getenv("OPENMEDICA_API_URL", "http://localhost:8000/api/v1")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{api_url}/documents/{document_id}")
            response.raise_for_status()
            doc = response.json()

        content = f"""
# {doc["title"]}

**Document ID:** {doc["id"]}
**Category:** {doc.get("category") or "N/A"}
**Tags:** {", ".join(doc.get("tags", [])) or "N/A"}
**Source:** {doc.get("source") or "N/A"}
**Created:** {doc.get("created_at", "Unknown")}
**Updated:** {doc.get("updated_at", "Unknown")}

---

## Content

{doc["content"]}
"""

        return [TextContent(type="text", text=content)]

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return [
                TextContent(
                    type="text",
                    text=f"Document not found: {document_id}. The document may have been deleted or the ID is incorrect.",
                )
            ]
        return [
            TextContent(
                type="text",
                text=f"Failed to retrieve document: {e.response.status_code} - {str(e)}",
            )
        ]
    except httpx.HTTPError as e:
        return [
            TextContent(
                type="text",
                text=f"Connection error: {str(e)}. Ensure the OpenMedica API is running at {api_url}",
            )
        ]
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Unexpected error retrieving document: {str(e)}. Please try again or contact support.",
            )
        ]
