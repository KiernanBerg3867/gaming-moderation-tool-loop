"""Run the moderation queue example against Infrai."""

from src.game_backend import LiveEvent, ModerationItem, PlayerAsset, decide_queue, infrai_chat_loop


def main() -> None:
    item = ModerationItem(
        asset=PlayerAsset("asset-17", "player-4", "Moonlit Harbor", "A quiet dock for the spring event."),
        event=LiveEvent("event-spring", "Spring Festival", "review"),
    )
    print(decide_queue(item, infrai_chat_loop()))


if __name__ == "__main__":
    main()
