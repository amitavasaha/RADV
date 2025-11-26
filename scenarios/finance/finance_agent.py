import argparse
import os
import uvicorn
from dotenv import load_dotenv
load_dotenv()

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)

# Import tools
from finance_tools import (
    google_web_search,
    edgar_search,
    parse_html_page,
    retrieve_information,
    set_model_ref,
)

instruction = """You are a financial agent. Today is April 07, 2025. 
You are given a question and you need to answer it using the tools provided.

IMPORTANT: You MUST automatically use the available tools to find the answer. Do not ask for permission or interact with the user - immediately use the tools to search for information and answer the question.

Available tools:
- google_web_search: Search the web for information
- edgar_search: Search SEC EDGAR database for filings  
- parse_html_page: Parse and extract content from web pages
- retrieve_information: Retrieve and analyze information from stored documents

You may not interact with the user or ask questions. You must automatically use the tools to find the answer.

When you have the answer, you should respond with 'FINAL ANSWER:' followed by your answer.
At the end of your answer, you should provide your sources in a dictionary with the following format:
{{
    "sources": [
        {{
            "url": "https://example.com",
            "name": "Name of the source"
        }},
        ...
    ]
}}

Answer the user's question by automatically using the available tools to find the information."""

def main():
    parser = argparse.ArgumentParser(description="Run the A2A finance agent.")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind the server")
    parser.add_argument("--port", type=int, default=9099, help="Port to bind the server")
    parser.add_argument("--card-url", type=str, help="External URL to provide in the agent card")
    parser.add_argument("--model", type=str, default="gemini-2.0-flash", help="Model to use")
    args = parser.parse_args()

    # Create tools
    tools = [
        FunctionTool(func=google_web_search),
        FunctionTool(func=edgar_search),
        FunctionTool(func=parse_html_page),
        FunctionTool(func=retrieve_information),
    ]
    
    # Create the agent with a callback to set the model reference
    def set_model_callback(callback_context):
        """Callback to set the model reference after agent initialization."""
        try:
            # Try to access the model from the callback context
            if hasattr(callback_context, 'agent') and hasattr(callback_context.agent, '_model'):
                set_model_ref(callback_context.agent._model)
            elif hasattr(callback_context, 'model'):
                set_model_ref(callback_context.model)
        except Exception:
            pass
    
    root_agent = Agent(
        name="finance_agent",
        model=args.model,
        description="A financial research agent that answers questions using SEC filings, web search, and document analysis.",
        instruction=instruction,
        tools=tools,
        after_agent_callback=set_model_callback,
    )

    # Define the agent's skill
    skill = AgentSkill(
        id='financial_research',
        name='Financial Research and Analysis',
        description='Answer financial questions by researching SEC filings, web sources, and analyzing financial documents. Provides answers with proper source citations.',
        tags=['finance', 'research', 'SEC', 'EDGAR', 'financial-analysis'],
        examples=[
            "What was Apple's revenue in 2023?",
            "What are Tesla's key risk factors mentioned in their latest 10-K?",
            "Compare Amazon and Microsoft's capital expenditure guidance for 2025",
            "What is Netflix's subscriber growth trend over the past 3 years?"
        ]
    )

    agent_card = AgentCard(
        name="finance_agent",
        description='A financial research agent that answers questions using SEC filings, web search, and document analysis.',
        url=args.card_url or f'http://{args.host}:{args.port}/',
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )

    a2a_app = to_a2a(root_agent, agent_card=agent_card)
    uvicorn.run(a2a_app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()

