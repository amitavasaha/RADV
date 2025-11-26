# Finance Agent Scenario

This scenario implements a finance agent that can answer financial questions using SEC filings, web search, and document analysis.

## Structure

- `finance_agent.py`: The purple agent (participant) that answers financial questions
- `finance_evaluator.py`: The green agent (evaluator) that evaluates the finance agent's responses
- `finance_tools.py`: Tool adapters for Google ADK
- `scenario.toml`: Configuration file for running the scenario

## Running the Scenario
0. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
#or . venv/bin/activate
```

1. Make sure you have all dependencies installed:
```bash
pip install -r requirements.txt
# Or if using uv:
uv sync
```

2. Set up your environment variables in `.env`:
   - Copy the `.env` file in the root directory (or create one from `.env.example` if available)
   - Fill in your API keys:
     ```
     GOOGLE_API_KEY=your_google_api_key_here
     SERP_API_KEY=your_serpapi_key_here
     SEC_EDGAR_API_KEY=your_sec_edgar_api_key_here
     ```
   - Get your keys from:
     - Google API: https://ai.google.dev/gemini-api/docs/api-key
     - SerpAPI: https://serpapi.com/
     - SEC EDGAR API: https://sec-api.io/

3. Run the scenario:

**Option 1: Local Testing (recommended for development)**

First, start the agents in separate terminals:

**Terminal 1 (Green Agent - Evaluator):**
```bash
python scenarios/finance/finance_evaluator.py --host 127.0.0.1 --port 9000
```

**Terminal 2 (Purple Agent - Finance Agent):**
```bash
python scenarios/finance/finance_agent.py --host 127.0.0.1 --port 9099
```

**Terminal 3: Run the scenario**
```bash
python run_scenario.py scenarios/finance/scenario.toml
```

**Kill processes if needed:**
```bash
# Kill evaluator on port 9000
lsof -ti:9000 | xargs kill -9

# Kill finance agent on port 9099
lsof -ti:9099 | xargs kill -9
```

**Option 2: AgentBeats Platform Submission**

To submit your agent to the AgentBeats platform for evaluation:

1. **Start Cloudflare Tunnel** (pointing to finance agent):
```bash
cloudflared tunnel --url http://127.0.0.1:9099
```
Copy the public URL (e.g., `https://xxx.trycloudflare.com`)

2. **Start Finance Agent with public URL**:
```bash
python scenarios/finance/finance_agent.py --host 127.0.0.1 --port 9099 --card-url https://YOUR-CLOUDFLARE-URL.trycloudflare.com
```

3. **Register on agentbeats.org** with your Cloudflare public URL

More details: https://github.com/agentbeats/tutorial/blob/main/README.md

**Option 3: Test Agent Directly**

Query the finance agent directly:
```bash
python query_finance_agent.py "What was Apple's revenue in 2023?"
```

Sample response:
```
📋 Question: What was Apple's revenue in 2023?
🔗 Finance Agent: http://127.0.0.1:9099

🚀 Sending question to finance agent...

✅ Response received!

💬 Finance Agent Answer:
============================================================
Apple's total revenue in fiscal year 2023 was $383 billion.
{
    "sources": [
        {
            "url": "https://www.cnbc.com/2023/12/29/apple-underperformed-mega-cap-peers-in-2023-due-to-revenue-slide.html",
            "name": "CNBC"
        }
    ]
}
============================================================
```

## Available Tools

The finance agent has access to the following tools:

1. **google_web_search**: Search the web for information
2. **edgar_search**: Search the SEC's EDGAR database for filings
3. **parse_html_page**: Parse and extract content from web pages
4. **retrieve_information**: Retrieve and analyze information from stored documents

## Note on RetrieveInformation Tool

The `retrieve_information` tool requires access to an LLM model to process prompts with document content. The current implementation attempts to access the model through the agent's callback mechanism. If you encounter issues with this tool, you may need to adjust the model access method based on your Google ADK version.

## License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

