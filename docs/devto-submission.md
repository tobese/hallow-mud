---
title: Hallow Mud: a Halloween MUD where Gemma invents the one ghost we didn't write
published: false
tags: devchallenge, hf26challenge, gemma, python
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 4: Ghost in the Machine](https://dev.to/challenges/hacktoberfest-week4-2026-10-26)*

## What I Built

**Hallow Mud** is a text MUD set on All Hallows' Eve, 1870, in Swede Hollow: the ravine in Saint Paul, Minnesota, where Swedish immigrants built shacks along Phalen Creek. The dead of the Hollow are back tonight:

- **Mor Brita**, a cholera ghost from 1854, drifting between the graves looking for her son's painted wooden horse
- **Järn-Gustaf**, a brewery worker crushed by ice blocks in 1866, who still thinks he's on shift guarding the cellar stairs
- **Fru Sigrid**, a vampire who sleeps in the cellars "because no one looks for the missing poor"
- **Varg-Anders**, a trapper bitten by something along the creek
- **Näcken**, the water spirit from Swedish folklore, who followed the immigrants across the ocean and fiddles at the water's edge
- **Gamle Lars**, the lamplighter: the last living soul who refused to flee

Every NPC is played by an open-weight model. You talk to them in plain language; they answer in character, remember you, react to each other, and wander the Hollow on their own. Room descriptions are rewritten live, so the same cemetery never reads the same way twice.

And then there is **the Stranger**. We didn't write them. At the start of each game, Gemma gets the story context and one question: *"Someone is here tonight who no one in the Hollow has ever seen before. Who are they?"* Whoever it invents steps out of the fog, and the rest of the cast has to deal with them. In one test run Gemma created Astrid Nylund, a woman with a rifle, who walked straight up to the lamplighter and started questioning him about what had changed in the Hollow. Nobody scripted that.

That's my take on *Ghost in the Machine*: a ghost that literally comes from the machine.

## Demo

<!-- TODO: video link -->

## Code

{% github tobese/hallow-mud %}

The game engine is a fork of [LlamaTale](https://github.com/neph1/LlamaTale) by neph1, itself built on [Tale](https://github.com/irmen/Tale) by Irmen de Jong. Our changes live on the [`hallow-mud` branch of tobese/LlamaTale](https://github.com/tobese/LlamaTale/tree/hallow-mud).

## How I Built It

**Gemma, two ways.**

- **Local:** `gemma3:12b` on Ollama, on a gaming laptop (RTX 4080, 12 GB VRAM) reached over Tailscale. I benchmarked Gemma 3 12B, Gemma 4 12B and Gemma 4 26B-A4B; Gemma 3 12B with an 8k context fits fully on the GPU at about 40 tokens/s, which is fast enough that NPCs answer while the scene is still fresh.
- **Hosted:** `gemma-4-31b-it` through Google's Gemini API (OpenAI-compatible endpoint). Slower, but noticeably better prose, so it's the backend for demos.

Switching between them is one line in `llm_config.yaml`.

**The engine.** LlamaTale is a MUD engine where the LLM narrates, plays NPCs, and builds world content through JSON-schema structured output. The story itself (zone, NPCs, quests, Swedish 1800s items such as the *lie* scythe and the *folkdräkt*) is plain Python in `story/`.

**What I had to fix along the way** (all on the fork, each with tests):

- `say to <npc>` never reached the NPC, and NPC names matched case-sensitively
- Gemma 4 always "thinks", and its `<thought>` blocks leaked into the game text; they're now stripped
- When an NPC's dialogue couldn't be parsed, the player got `ERROR IN DRIVER MAINLOOP`; now the NPC just stares, lips moving, and no words come
- An option to show only the generated text, instead of the original description followed by its rewrite
- A save-path check that could be bypassed on macOS through `/private/etc`, plus test fixes for Python 3.11+

The first two fixes went upstream as PRs ([#145](https://github.com/neph1/LlamaTale/pull/145), [#146](https://github.com/neph1/LlamaTale/pull/146)).

## Why Does Open Innovation Matter?

<!-- TODO: in your own words. Points to draw from:
- The whole stack is open: Tale (2010s MUD framework) → LlamaTale (LLM layer) → our fork. We could fix the engine instead of working around it, and send the fixes back.
- Open weights mean the game runs on a laptop in the house, offline, with no per-token bill: NPCs can chatter to each other all night.
- The same Gemma model family runs locally and hosted, so moving between them is a config line, not a rewrite.
- Swede Hollow's history is a local story that no product team would build a game about; open tools let a hobbyist do it in a week. -->

## My Agent Session

<!-- Optional: DevRelay session, or remove -->

## The Spirit of It

<!-- Optional: Swede Hollow was cleared in 1956 and is a park now. Why this place, for you? -->

## Prize Categories

**Best Use of Gemma**: every NPC, every room description, and the Stranger are Gemma, run locally on Ollama or hosted via the Gemini API.
