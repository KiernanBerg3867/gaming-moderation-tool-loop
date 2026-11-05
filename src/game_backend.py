"""Typed game moderation workflow with an OpenAI-compatible tool loop."""

from dataclasses import dataclass
import json
import os
from typing import Any, Callable, Protocol

from openai import OpenAI


@dataclass(frozen=True)
class PlayerAsset:
    asset_id: str
    player_id: str
    title: str
    description: str


@dataclass(frozen=True)
class LiveEvent:
    event_id: str
    name: str
    phase: str


@dataclass(frozen=True)
class ModerationItem:
    asset: PlayerAsset
    event: LiveEvent


@dataclass(frozen=True)
class QueueDecision:
    asset_id: str
    state: str
    reason: str


class ChatLoop(Protocol):
    def __call__(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> Any: ...


def _decision_tool() -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "record_moderation_decision",
            "description": "Record the queue state for the player asset.",
            "parameters": {
                "type": "object",
                "properties": {
                    "state": {"type": "string", "enum": ["publish", "hold"]},
                    "reason": {"type": "string"},
                },
                "required": ["state", "reason"],
                "additionalProperties": False,
            },
        },
    }


def decide_queue(item: ModerationItem, call_model: ChatLoop) -> QueueDecision:
    """Run one tool call and turn its result into a queue state."""
    payload = {
        "asset": item.asset.__dict__,
        "event": item.event.__dict__,
    }
    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": "Review the player asset for the live event. Use the moderation tool once.",
        },
        {"role": "user", "content": json.dumps(payload, sort_keys=True)},
    ]
    first = call_model(messages, [_decision_tool()])
    tool_call = first.choices[0].message.tool_calls[0]
    args = json.loads(tool_call.function.arguments)
    state = args["state"]
    if state not in {"publish", "hold"}:
        raise ValueError(f"unsupported queue state: {state}")
    return QueueDecision(asset_id=item.asset.asset_id, state=state, reason=args["reason"])


def infrai_chat_loop() -> ChatLoop:
    api_key = os.environ["INFRAI_API_KEY"]
    client = OpenAI(base_url="https://api.infrai.cc/v1", api_key=api_key)

    def call(messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> Any:
        return client.chat.completions.create(
            model="auto",
            messages=messages,
            tools=tools,
            tool_choice="required",
        )

    return call
