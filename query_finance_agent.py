#!/usr/bin/env python3
"""Query the finance agent directly to see its answer."""
import argparse
import asyncio
import sys
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

async def query_finance_agent(question: str, endpoint: str = "http://127.0.0.1:9099"):
    """Query the finance agent directly."""
    print(f"📋 Question: {question}")
    print(f"🔗 Finance Agent: {endpoint}")
    print("\n🚀 Sending question to finance agent...\n")
    
    try:
        response = await send_message(
            message=question,
            base_url=endpoint,
            context_id=None,
            streaming=False
        )
        
        print("✅ Response received!")
        print("\n💬 Finance Agent Answer:")
        print("=" * 60)
        print(response.get('response', 'No response received'))
        print("=" * 60)
        
        return response.get('response', '')
        
    except Exception as e:
        print(f"❌ Error querying finance agent: {e}")
        print(f"\n💡 Make sure the finance agent is running on {endpoint}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Query the finance agent directly")
    parser.add_argument(
        "question",
        nargs="?",
        default="What was Apple's revenue in 2023?",
        help="Question to ask the finance agent"
    )
    parser.add_argument(
        "--endpoint",
        default="http://127.0.0.1:9099",
        help="Finance agent endpoint URL"
    )
    args = parser.parse_args()
    
    asyncio.run(query_finance_agent(args.question, args.endpoint))

if __name__ == "__main__":
    main()

