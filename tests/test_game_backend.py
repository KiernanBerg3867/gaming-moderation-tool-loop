from dataclasses import dataclass

from src.game_backend import LiveEvent, ModerationItem, PlayerAsset, decide_queue


@dataclass
class Function:
    arguments: str


@dataclass
class ToolCall:
    function: Function


@dataclass
class Message:
    tool_calls: list[ToolCall]


@dataclass
class Choice:
    message: Message


@dataclass
class Response:
    choices: list[Choice]


def test_moderation_tool_moves_asset_to_hold_queue():
    item = ModerationItem(
        PlayerAsset("asset-9", "player-2", "Arena banner", "A banner for the ranked event."),
        LiveEvent("event-ranked", "Ranked Finals", "review"),
    )

    def fake_model(messages, tools):
        assert "asset-9" in messages[1]["content"]
        assert tools[0]["function"]["name"] == "record_moderation_decision"
        return Response([Choice(Message([ToolCall(Function('{"state":"hold","reason":"needs review"}'))]))])

    decision = decide_queue(item, fake_model)

    assert decision == type(decision)("asset-9", "hold", "needs review")
