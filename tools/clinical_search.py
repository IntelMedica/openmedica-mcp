"""Clinical search tool for AI agents - MCP-02."""

import os
from typing import Optional
from mcp.types import Tool, TextContent
import httpx


class ClinicalSearchTool:
    """Clinical search tool implementation."""

    name = "clinical_search"
    description = """Search clinical evidence across multiple databases.
    
    This tool searches PostgreSQL (full-text), Qdrant (semantic vectors), 
    and SurrealDB (relationships) to find relevant clinical documents.
    
    Use this when:
    - Searching for research papers or clinical guidelines
    - Finding information about diseases, treatments, or medications
    - Querying medical literature for AI agent reasoning
    
    Returns ranked results with relevance scores from each database.
    """

    input_schema = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Clinical search query (e.g., 'diabetes treatment options')",
            },
            "category": {
                "type": "string",
                "description": "Filter by category (optional)",
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Filter by tags (optional)",
            },
            "limit": {
                "type": "integer",
                "default": 10,
                "description": "Maximum results (1-100)",
            },
        },
        "required": ["query"],
    }


clinical_search_tool = Tool(
    name=ClinicalSearchTool.name,
    description=ClinicalSearchTool.description,
    inputSchema=ClinicalSearchTool.input_schema,
)


async def call_clinical_search(
    query: str,
    category: Optional[str] = None,
    tags: Optional[list[str]] = None,
    limit: int = 10,
) -> list[TextContent]:
    """Execute clinical search and return formatted results."""
    api_url = os.getenv("OPENMEDICA_API_URL", "http://localhost:8000/api/v1")

    params = {"q": query, "limit": limit}
    if category:
        params["category"] = category
    if tags:
        params["tags"] = ",".join(tags)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{api_url}/search", params=params)
            response.raise_for_status()
            result = response.json()

        results = result.get("results", [])

        if not results:
            return [
                TextContent(
                    type="text",
                    text="No clinical documents found matching your query. Try different search terms or broaden your search.",
                )
            ]

        formatted = []
        for r in results:
            doc = r["document"]
            score = r.get("score", 0)
            source = r.get("source", "unknown")

            formatted.append(f"""
## {doc["title"]}

**Relevance:** {score:.2f} | **Source:** {source}

{doc["content"][:500]}{"..." if len(doc["content"]) > 500 else ""}

Category: {doc.get("category") or "N/A"} | Tags: {", ".join(doc.get("tags", [])) or "N/A"}
---
""")

        return [
            TextContent(
                type="text",
                text=f"Found {len(results)} results:\n\n" + "\n".join(formatted),
            )
        ]

    except httpx.HTTPError as e:
        return [
            TextContent(
                type="text",
                text=f"Search failed: {str(e)}. Ensure the OpenMedica API is running at {api_url}",
            )
        ]
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Unexpected error during search: {str(e)}. Please try again or contact support.",
            )
        ]
