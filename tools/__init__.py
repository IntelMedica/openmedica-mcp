"""OpenMedica MCP tools for AI agents."""

from mcp.tools.clinical_search import (
    clinical_search_tool,
    call_clinical_search,
)
from mcp.tools.document_lookup import (
    document_lookup_tool,
    call_document_lookup,
)

__all__ = [
    "clinical_search_tool",
    "document_lookup_tool",
    "call_clinical_search",
    "call_document_lookup",
]
