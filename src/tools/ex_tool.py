from typing import Optional, Type
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool


@tool
def search(query: str) -> str:
    """Look up things online."""
    return query
