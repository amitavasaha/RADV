"""Tool adapters for the finance agent using Google ADK."""
import json
import re
import os
import sys
from typing import Optional, List

# Import tools from local directory
from tools import GoogleWebSearch, EDGARSearch, ParseHtmlPage, RetrieveInformation

# Global storage for data and model references
_data_storage = {}
_model_ref = None


def set_model_ref(model):
    """Set the model reference for tools that need it."""
    global _model_ref
    _model_ref = model


def get_data_storage(context_id: str = "default"):
    """Get or create data storage for a given context."""
    if context_id not in _data_storage:
        _data_storage[context_id] = {}
    return _data_storage[context_id]


async def google_web_search(search_query: str) -> str:
    """Search the web for information using Google Search.
    
    Args:
        search_query: The query to search for
        
    Returns:
        JSON string containing search results
    """
    tool = GoogleWebSearch()
    result = await tool.call_tool({"search_query": search_query})
    return json.dumps(result) if isinstance(result, list) else str(result)


async def edgar_search(
    query: str,
    form_types: Optional[List[str]] = None,
    ciks: Optional[List[str]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: str = "1",
    top_n_results: int = 10
) -> str:
    """Search the EDGAR Database through the SEC API.
    
    Args:
        query: The keyword or phrase to search
        form_types: List of form types (e.g., ['8-K', '10-Q'])
        ciks: List of CIKs to filter by
        start_date: Start date in yyyy-mm-dd format
        end_date: End date in yyyy-mm-dd format
        page: Page number for pagination
        top_n_results: Number of results to return
        
    Returns:
        JSON string containing filing results
    """
    tool = EDGARSearch()
    result = await tool.call_tool({
        "query": query,
        "form_types": form_types or [],
        "ciks": ciks or [],
        "start_date": start_date,
        "end_date": end_date,
        "page": page,
        "top_n_results": top_n_results
    })
    return json.dumps(result) if isinstance(result, list) else str(result)


async def parse_html_page(url: str, key: str, context_id: str = "default") -> str:
    """Parse an HTML page and save the content to data storage.
    
    Args:
        url: The URL of the HTML page to parse
        key: The key to use when saving the result in the data storage
        context_id: Optional context ID for conversation isolation
        
    Returns:
        Success message with storage information
    """
    tool = ParseHtmlPage()
    data_storage = get_data_storage(context_id)
    result = await tool.call_tool({"url": url, "key": key}, data_storage)
    return result if isinstance(result, str) else json.dumps(result)


async def retrieve_information(
    prompt: str,
    input_character_ranges: Optional[str] = None,
    context_id: str = "default"
) -> str:
    """Retrieve information from the conversation's data structure.
    
    Args:
        prompt: The prompt that will be passed to the LLM. Must include at least one data storage key in the format {{key_name}}
        input_character_ranges: Optional JSON string of array mapping document keys to character ranges. Format: '[{"key": "doc_key", "range": [0, 100]}]'
        context_id: Optional context ID for conversation isolation
        
    Returns:
        The result from the LLM that receives the prompt with inserted data
    """
    if _model_ref is None:
        raise ValueError("Model reference not set. This tool requires a model to function.")
    
    tool = RetrieveInformation()
    data_storage = get_data_storage(context_id)
    arguments = {"prompt": prompt}
    if input_character_ranges:
        # Parse JSON string if provided
        try:
            parsed_ranges = json.loads(input_character_ranges)
            arguments["input_character_ranges"] = parsed_ranges
        except json.JSONDecodeError:
            # If not valid JSON, treat as empty
            pass
    
    result = await tool.call_tool(arguments, data_storage, _model_ref)
    return result.get("retrieval", "") if isinstance(result, dict) else str(result)

