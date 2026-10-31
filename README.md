# Hallow Mud

A Halloween text MUD set on All Hallows' Eve, 1870, in [Swede Hollow](https://en.wikipedia.org/wiki/Swede_Hollow,_Saint_Paul), the Swedish immigrant ravine in Saint Paul, Minnesota. The dead of the Hollow are back tonight, and every one of them is played by [Gemma](https://ai.google.dev/gemma).

Built for the [Hacktoberfest Open-Source AI Challenge, Week 4: Ghost in the Machine](https://dev.to/challenges/hacktoberfest-week4-2026-10-26).

## What's in the Hollow

- **NPCs written by us, played by Gemma:** Mor Brita, the cholera ghost searching for her son's wooden horse; Järn-Gustaf, the dead brewery worker still guarding the cellar stairs; Fru Sigrid, the vampire in the cellars; Varg-Anders, the trapper turning into something else; Näcken, the water spirit fiddling by the creek; and Gamle Lars, the frightened lamplighter. Talk to them in plain language; they answer in character, remember you and react to each other.
- **The Stranger, written by no one:** each game, Gemma gets only the story context and the question *"Someone is here tonight who no one in the Hollow has ever seen before. Who are they?"* Whoever it invents steps out of the fog. See [`story/npcs/stranger.py`](story/npcs/stranger.py).
- **Room descriptions rewritten by the model** when the server starts, so each night's Hollow reads differently. All players share the rewrite, so looking around is instant.
- **Portraits and room pictures** in the style of hand-tinted 1870s tintypes, painted once in advance by Gemini's image model from the game's own descriptions ([`tools/paint_resources.py`](tools/paint_resources.py)). The web client wears Hacktoberfest's colours ([`story/resources/story.css`](story/resources/story.css)).

## Play it

- **[q-bert.bearded-panga.ts.net](https://q-bert.bearded-panga.ts.net/tale/)**: local Gemma on our own GPU, published with Tailscale Funnel; fast, but only up while that machine is.
- **[hallow-mud.onrender.com](https://hallow-mud.onrender.com/tale/)**: Gemma on the Gemini API, on Render's free plan; always there, slow to wake and to think.
- **[hallow-mud-terminal.onrender.com](https://hallow-mud-terminal.onrender.com/)**: the old way, a terminal in the browser (ttyd) with a single-player game of your own per tab; same Gemini backend, three players at a time. Names are lowercase, and wait for the `>>` prompt before typing.

## Running it

Requires Python 3.13.

```sh
make install   # creates venv/, installs the LlamaTale fork from the submodule
make run       # interactive fiction mode in the terminal
make run-mud   # multi-player MUD server mode
make test      # LlamaTale's test suite
```

### Choosing a Gemma backend

Set `BACKEND` in `LlamaTale/llm_config.yaml`:

- **`ollama`** (default): local Gemma on [Ollama](https://ollama.com). `LlamaTale/backend_ollama.yaml` points at our machine; change `URL` to your own server and `model` to a Gemma you have pulled. We use `gemma3:12b` with an 8k context (`num_ctx 8192` in a Modelfile), which runs fully on a 12 GB GPU at about 40 tokens/s.
- **`gemini`**: hosted `gemma-4-31b-it` via the Gemini API. Put your [Google AI Studio](https://aistudio.google.com) key in a `.env` file in the repo root (it's git-ignored):

  ```sh
  GEMINI_API_KEY=your-key
  ```

  Gemma 4 always reasons before answering on this API, so expect slower turns and better prose.

## Layout

- `story/`: the Hallow Mud story (zone, NPCs, items, the Stranger)
- `LlamaTale/`: submodule with our fork of the game engine, branch [`hallow-mud`](https://github.com/tobese/LlamaTale/tree/hallow-mud)
- `tools/`: the script that painted the portraits and room pictures
- `docs/`: the challenge submission post

## Credits

The engine is [LlamaTale](https://github.com/neph1/LlamaTale) by neph1, which builds on [Tale](https://github.com/irmen/Tale) by Irmen de Jong. Our fork adds a Gemini backend and fixes for NPC targeting, reasoning-model output, unparseable dialogue and macOS; some of them are offered upstream: [#145](https://github.com/neph1/LlamaTale/pull/145) (merged) and [#146](https://github.com/neph1/LlamaTale/pull/146).
