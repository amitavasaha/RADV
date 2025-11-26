#!/usr/bin/env python3
"""Simple script to run the finance agent scenario."""
import argparse
import asyncio
import json
import sys
import os
from pathlib import Path

# Import A2A client directly
import httpx
from uuid import uuid4
from a2a.client import (
    A2ACardResolver,
    ClientConfig,
    ClientFactory,
)
from a2a.types import (
    Message,
    Part,
    Role,
    TextPart,
)

DEFAULT_TIMEOUT = 300

def create_message(*, role: Role = Role.user, text: str, context_id: str | None = None) -> Message:
    return Message(
        kind="message",
        role=role,
        parts=[Part(TextPart(kind="text", text=text))],
        message_id=uuid4().hex,
        context_id=context_id
    )

def merge_parts(parts: list[Part]) -> str:
    chunks = []
    for part in parts:
        if isinstance(part.root, TextPart):
            chunks.append(part.root.text)
    return "\n".join(chunks)

async def send_message(message: str, base_url: str, context_id: str | None = None, streaming=False, consumer=None):
    """Send message to an A2A agent."""
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as httpx_client:
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=base_url)
        agent_card = await resolver.get_agent_card()
        config = ClientConfig(
            httpx_client=httpx_client,
            streaming=streaming,
        )
        factory = ClientFactory(config)
        client = factory.create(agent_card)
        if consumer:
            await client.add_event_consumer(consumer)

        outbound_msg = create_message(text=message, context_id=context_id)
        last_event = None
        outputs = {
            "response": "",
            "context_id": None
        }

        async for event in client.send_message(outbound_msg):
            last_event = event

        if isinstance(last_event, Message):
            outputs["context_id"] = last_event.context_id
            outputs["response"] += merge_parts(last_event.parts)
        elif isinstance(last_event, tuple) and len(last_event) == 2:
            task, update = last_event
            outputs["context_id"] = task.context_id
            outputs["status"] = task.status.state.value
            msg = task.status.message
            if msg:
                outputs["response"] += merge_parts(msg.parts)
            if task.artifacts:
                for artifact in task.artifacts:
                    outputs["response"] += merge_parts(artifact.parts)

        return outputs

async def run_scenario(scenario_path: str):
    """Run the finance scenario by sending an assessment request to the green agent."""
    # Try tomllib first (Python 3.11+), fallback to tomli
    try:
        import tomllib
        with open(scenario_path, 'rb') as f:
            config = tomllib.load(f)
    except ImportError:
        try:
            import tomli as tomllib
            with open(scenario_path, 'rb') as f:
                config = tomllib.load(f)
        except ImportError:
            print("❌ Error: Need tomllib (Python 3.11+) or tomli package")
            print("   Install with: pip install tomli")
            sys.exit(1)
    
    green_agent_endpoint = config['green_agent']['endpoint']
    participants = {p['role']: p['endpoint'] for p in config['participants']}
    question = config['config'].get('question', '')
    
    # Create assessment request
    assessment_request = {
        "participants": participants,
        "config": config['config']
    }
    
    print(f"📋 Question: {question}")
    print(f"🔗 Green Agent: {green_agent_endpoint}")
    print(f"👥 Participants: {participants}")
    print("\n🚀 Sending assessment request to green agent...\n")
    
    # Send assessment request to green agent
    request_text = json.dumps(assessment_request, indent=2)
    
    try:
        response = await send_message(
            message=request_text,
            base_url=green_agent_endpoint,
            context_id=None,
            streaming=False
        )
        
        print("✅ Assessment completed!")
        print("\n📊 Results:")
        print("-" * 60)
        print(response.get('response', 'No response received'))
        print("-" * 60)
        
    except Exception as e:
        print(f"❌ Error running scenario: {e}")
        print("\n💡 Make sure both agents are running:")
        print(f"   Terminal 1: python scenarios/finance/finance_evaluator.py")
        print(f"   Terminal 2: python scenarios/finance/finance_agent.py")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Run the finance agent scenario")
    parser.add_argument(
        "scenario",
        nargs="?",
        default="scenarios/finance/scenario.toml",
        help="Path to scenario.toml file"
    )
    args = parser.parse_args()
    
    scenario_path = Path(args.scenario)
    if not scenario_path.exists():
        print(f"❌ Scenario file not found: {scenario_path}")
        sys.exit(1)
    
    asyncio.run(run_scenario(str(scenario_path)))

if __name__ == "__main__":
    main()

