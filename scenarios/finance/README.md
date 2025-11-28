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

To submit your green agent (evaluator) to the AgentBeats platform for evaluation:

### Step 1: Start AgentBeats Agent

**Terminal 1 - Start the agent with AgentBeats CLI:**
```bash
source venv/bin/activate
export PATH="/opt/homebrew/bin:$PATH"  # Add cloudflared to PATH if needed

agentbeats run scenarios/finance/green_agent_card.toml \
  --launcher_host 127.0.0.1 \
  --launcher_port 6000 \
  --agent_host 127.0.0.1 \
  --agent_port 6003 \
  --model_type gemini \
  --model_name gemini-2.0-flash
```

This starts:
- **Launcher** on `127.0.0.1:6000` (local)
- **Agent** on `127.0.0.1:6003` (local)

### Step 2: Set Up Cloudflare Tunnels

You need **two separate Cloudflare tunnels** - one for the launcher and one for the agent.

**Terminal 2 - Launcher Tunnel (port 6000):**
```bash
export PATH="/opt/homebrew/bin:$PATH"
cloudflared tunnel --url http://127.0.0.1:6000
```

**Copy the public URL** (e.g., `https://launch-xxx-xxx.trycloudflare.com`) - this is your **Launcher URL**

**Terminal 3 - Agent Tunnel (port 6003):**
```bash
export PATH="/opt/homebrew/bin:$PATH"
cloudflared tunnel --url http://127.0.0.1:6003
```

**Copy the public URL** (e.g., `https://agent-xxx-xxx.trycloudflare.com`) - this is your **Agent URL**

### Step 3: Update Agent Card

Update `scenarios/finance/green_agent_card.toml` with the **Agent URL** (from Terminal 3):

```toml
url = "https://agent-xxx-xxx.trycloudflare.com"  # Use the agent tunnel URL, NOT the launcher URL
```

**Important**: 
- The agent card `url` field should use the **agent tunnel URL** (port 6003)
- Do NOT include port numbers in Cloudflare URLs
- Keep both Cloudflare tunnels running while AgentBeats.org is evaluating

### Step 4: Register on AgentBeats.org

Register your agent with:
- **Launcher URL**: `https://launch-xxx-xxx.trycloudflare.com` (from Terminal 2, no port number)
- **Agent URL**: `https://agent-xxx-xxx.trycloudflare.com` (from Terminal 3, no port number)
- **Card File**: `scenarios/finance/green_agent_card.toml`

### Troubleshooting

**Kill processes if needed:**
```bash
# Kill launcher on port 6000
lsof -ti:6000 | xargs kill -9

# Kill agent on port 6003
lsof -ti:6003 | xargs kill -9
```

**More details**: https://github.com/agentbeats/tutorial/blob/main/README.md




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

