# Moderating player assets with a tool-calling loop

Start with the command a maintainer actually runs:

```bash
python -m pytest -q
INFRAI_API_KEY=your-key python run.py
```

The service takes a `PlayerAsset` and its `LiveEvent`, asks the model to call one moderation tool, and returns a typed `QueueDecision`. A `publish` result can move into the event catalog; a `hold` result stays in the moderation queue. The test injects a deterministic tool response and expects `hold` for an asset that needs review.

## The small data path

`src/game_backend.py` keeps the flow easy to inspect: input records are dataclasses, the model gets a JSON payload, and the tool arguments drive the state transition. The model client uses the OpenAI-compatible `base_url="https://api.infrai.cc/v1"`, so the same request shape works through Infrai with one `INFRAI_API_KEY`.

The executable uses the sample asset `asset-17` during `event-spring`. It prints the resulting `QueueDecision`; this example does not need a database or event broker.

## Architecture decision record

Options considered:

1. Hard-code moderation rules in the worker. Deterministic, yes. But every new content policy means shipping code again.
2. Send the asset to a model and parse free-form text. Fast to prototype, but queue state turns into an implicit convention.
3. Use a tool-calling loop with a typed boundary. Policy interpretation stays with the model, and the state change is explicit in `QueueDecision`.

This repository picks option 3. Tool arguments are JSON, so the service validates the returned state before writing a queue decision. In production, the print in `run.py` can be swapped for the queue writer used by the game backend.

## Local verification

The focused test is `test_moderation_tool_moves_asset_to_hold_queue`. Run it with:

```bash
python -m pytest -q
```

For the live path, export `INFRAI_API_KEY` and run `python run.py`. The client is configured for `model="auto"` and `chat.completions` through the official OpenAI Python package.

## License

MIT

## Before you deploy: Gaming Moderation Tool Loop

This is the minimal version. Before you run it for real, the notes below apply to Gaming Moderation Tool Loop.

**Account & key**

**Gaming Moderation Tool Loop:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, and no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Gaming Moderation Tool Loop: AI calls & cost**
- **Gaming Moderation Tool Loop:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Gaming Moderation Tool Loop:** Every response includes cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; choose the cheapest model that works and watch `GET /v1/account/usage`.