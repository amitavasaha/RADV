# Research, Analysis, Design, and Verification Agent (a Finance Agent) for AgentBeats

A financial research agent that answers questions using SEC filings, web search, and document analysis. Built with Google ADK and compatible with the A2A protocol for agent interoperability.

## Features

- 🔍 **Web Search**: Query financial information from the web using SerpAPI
- 📊 **SEC EDGAR Search**: Access company filings from the SEC database
- 📄 **HTML Parsing**: Extract and analyze content from web pages
- 🤖 **AI-Powered Analysis**: Use Google's Gemini model for information retrieval and synthesis

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd RADV

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file with your API keys:

```bash
GOOGLE_API_KEY=your_google_api_key_here
SERP_API_KEY=your_serpapi_key_here
SEC_EDGAR_API_KEY=your_sec_edgar_api_key_here
```

Get your API keys from:
- [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-key)
- [SerpAPI](https://serpapi.com/)
- [SEC EDGAR API](https://sec-api.io/)

### 3. Run the Agent

**For local testing:**
```bash
python scenarios/finance/finance_agent.py --host 127.0.0.1 --port 9099
```

**For AgentBeats platform submission:**
```bash
# Start Cloudflare tunnel
cloudflared tunnel --url http://127.0.0.1:9099

# In another terminal, start agent with public URL
python scenarios/finance/finance_agent.py --host 127.0.0.1 --port 9099 --card-url https://YOUR-URL.trycloudflare.com
```

### 4. Query the Agent

```bash
python query_finance_agent.py "What was Apple's revenue in 2023?"
```

## Project Structure

```
RADV/
├── data/
│   └── public.csv              # Validation dataset
├── scenarios/
│   └── finance/
│       ├── finance_agent.py    # Main agent implementation
│       ├── finance_evaluator.py # Evaluator for testing
│       ├── finance_tools.py    # Tool adapters for Google ADK
│       ├── tools.py            # Core tool implementations
│       ├── utils.py            # Utility functions
│       ├── scenario.toml       # Scenario configuration
│       └── README.md           # Detailed documentation
├── query_finance_agent.py      # Direct query utility
├── run_scenario.py             # Scenario runner
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Project configuration
└── .env                        # API keys (not in repo)
```

## Documentation

For detailed usage instructions, see [scenarios/finance/README.md](scenarios/finance/README.md)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Google ADK](https://github.com/google/adk)
- Compatible with [AgentBeats](https://agentbeats.org) evaluation platform
- Uses the [A2A Protocol](https://a2a.ai) for agent interoperability

