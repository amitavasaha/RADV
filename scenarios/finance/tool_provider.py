"""Tool provider for communicating with other agents."""
import sys
import os

# Add path for agentbeats client if available
# Try to find agentbeats in common locations
possible_paths = [
    os.path.join(os.path.dirname(__file__), '../../tutorial-template/src'),
    os.path.join(os.path.dirname(__file__), '../../../tutorial-template/src'),
]

for path in possible_paths:
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)
        break

try:
    from agentbeats.client import send_message
except ImportError:
    # Fallback: define send_message locally if agentbeats is not available
    import asyncio
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
        """Returns dict with context_id, response and status (if exists)"""
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


class ToolProvider:
    def __init__(self):
        self._context_ids = {}

    async def talk_to_agent(self, message: str, url: str, new_conversation: bool = False):
        """
        Communicate with another agent by sending a message and receiving their response.

        Args:
            message: The message to send to the agent
            url: The agent's URL endpoint
            new_conversation: If True, start fresh conversation; if False, continue existing conversation

        Returns:
            str: The agent's response message
        """
        outputs = await send_message(
            message=message, 
            base_url=url, 
            context_id=None if new_conversation else self._context_ids.get(url, None)
        )
        if outputs.get("status", "completed") != "completed":
            raise RuntimeError(f"{url} responded with: {outputs}")
        self._context_ids[url] = outputs.get("context_id", None)
        return outputs["response"]

    def reset(self):
        self._context_ids = {}

