# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install agentbeats if not in requirements
RUN pip install --no-cache-dir agentbeats || true

# Copy application code
COPY scenarios/ ./scenarios/
COPY data/ ./data/
COPY run_scenario.py query_finance_agent.py ./

# Create .env file placeholder (will be overridden by environment variables or volume mount)
RUN touch .env

# Expose ports
# 6000: Launcher (AgentBeats)
# 6003: Agent (AgentBeats)
# 9000: Evaluator (local)
# 9099: Finance Agent (local)
EXPOSE 6000 6003 9000 9099

# Default command (can be overridden)
# Run finance agent by default
CMD ["python", "scenarios/finance/finance_agent.py", "--host", "0.0.0.0", "--port", "9099"]

