---
title: Hallow Mud: a Halloween MUD where Gemma invents the one ghost we didn't write
published: true
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

Every NPC is played by an open-weight model. You talk to them in plain language; they answer in character, remember you, react to each other, and some of them wander the Hollow on their own. The model rewrites every room description when the server starts, so each night's Hollow reads differently, and all players share it, so looking around never waits on the model.

And you can fight. Take the gravedigger's scythe from the cemetery or the brewery's sledgehammer from the cellar stairs, go down into the root cellar and `attack gengångare`. The dice decide who hits; Gemma tells it: *"Your sledgehammer connects with a sickening crunch against the gengångare's face…"* Fall, and you wake among the graves, because the veil won't let anyone go tonight. Kill the gengångare, and three minutes later it claws its way back up out of the earth; *gengångare* is Swedish for "one who walks again".

And then there is **the Stranger**. We didn't write them. At the start of each game, Gemma gets the story context and one question: *"Someone is here tonight who no one in the Hollow has ever seen before. Who are they?"* Whoever it invents steps out of the fog, and the rest of the cast has to deal with them. In one test run Gemma created Astrid Nylund, a woman with a rifle, who walked straight up to the lamplighter and started questioning him about what had changed in the Hollow. Nobody scripted that.

That's my take on *Ghost in the Machine*: a ghost that literally comes from the machine.

## Demo

**Play it** in three places. On the first two, pick a name, create a character, and you're in the Hollow with whoever else is online on that server.

- [q-bert.bearded-panga.ts.net](https://q-bert.bearded-panga.ts.net/tale/): the fast one. Gemma 3 12B runs on the laptop GPU in my home, and the game sits next to it, published with Tailscale Funnel. NPCs answer in seconds. It's a laptop, so it may be asleep.
- [hallow-mud.onrender.com](https://hallow-mud.onrender.com/tale/): always there. It runs on Render's free plan with Gemma on the Gemini API, so the first visit after a quiet spell takes about a minute to wake up, accounts reset whenever the server restarts, and NPCs take a while to think.
- [hallow-mud-terminal.onrender.com](https://hallow-mud-terminal.onrender.com/): the old way. A terminal in the browser, like the MUDs we telnetted to at university, with a game of your own in each tab: just you, the dead of the Hollow and the Stranger. Same Gemma on the Gemini API, room for three players at a time.

![Playing Hallow Mud: logging in, meeting Mor Brita in the cemetery and Näcken at the creek, with Gemma answering on the local GPU](https://raw.githubusercontent.com/tobese/hallow-mud/main/docs/hallow-mud-demo.gif)

*A minute in the Hollow on the local server: Brita and Näcken each answer within about fifteen seconds.*

I think it's really fascinating to see the generated conversations, but don't take my word for it, try it out!

## Code

{% github tobese/hallow-mud %}

The game engine is a fork of [LlamaTale](https://github.com/neph1/LlamaTale) by neph1, itself built on [Tale](https://github.com/irmen/Tale) by Irmen de Jong. Our changes live on the [`hallow-mud` branch of tobese/LlamaTale](https://github.com/tobese/LlamaTale/tree/hallow-mud).

## How I Built It

**Gemma, two ways.**

- **Local:** `gemma3:12b` on Ollama, on a gaming laptop (RTX 4080, 12 GB VRAM), with the game server running right next to it. I benchmarked Gemma 3 12B, Gemma 4 12B and Gemma 4 26B-A4B; Gemma 3 12B with an 8k context fits fully on the GPU at about 40 tokens/s, which is fast enough that NPCs answer while the scene is still fresh.
- **Hosted:** `gemma-4-31b-it` through Google's Gemini API (OpenAI-compatible endpoint). Slower, but noticeably better prose, and it needs no GPU, so it's the backend for the always-on server on Render.

Switching between them is one line in `llm_config.yaml`.

**The engine.** LlamaTale is a MUD engine where the LLM narrates, plays NPCs, and builds world content through JSON-schema structured output. The story itself (zone, NPCs, quests, Swedish 1800s items such as the *lie* scythe and the *folkdräkt*) is plain Python in `story/`.

**The look.** Each NPC has a portrait and each room a picture, in the style of hand-tinted 1870s tintypes. Gemini's image model painted them in advance, from the same descriptions Gemma plays the characters from (the script is in `tools/paint_resources.py`). The Stranger can't be painted in advance, so the game paints their portrait the moment Gemma invents them, before they step out of the fog. The web client is restyled in Hacktoberfest's colours and fonts.

**What I had to fix along the way** (all on the fork, each with tests):

- `say to <npc>` never reached the NPC, and NPC names matched case-sensitively
- Gemma 4 always "thinks", and its `<thought>` blocks leaked into the game text; they're now stripped
- When an NPC's dialogue couldn't be parsed, the player got `ERROR IN DRIVER MAINLOOP`; now the NPC just stares, lips moving, and no words come
- An option to show only the generated text, instead of the original description followed by its rewrite
- A save-path check that could be bypassed on macOS through `/private/etc`, plus test fixes for Python 3.11+
- Every `look` asked the model to rewrite the room for that one player, so players queued behind each other for 20 to 30 seconds; now each room is rewritten once when the server starts and shared, and looking around is instant
- In multiplayer, what you said reached the other players retold by the model; now they hear your words as you said them
- New players who took more than a minute to create a character were destroyed by the Grim Reaper in Limbo mid sign-up
- NPCs name each other when they talk, and every named NPC answered, so two of them could talk forever; now an NPC answers other NPCs once per player line
- Players started with no skill in any weapon, so they could never land a blow, and a slain player kept walking around at zero hit points
- Stories can now ship their own stylesheet, and their pictures are found wherever the game is started from

Two fixes went upstream as PRs: [#145](https://github.com/neph1/LlamaTale/pull/145), which neph1 has merged, and [#146](https://github.com/neph1/LlamaTale/pull/146).

## Why Does Open Innovation Matter?

**The whole stack is open, so I could fix it instead of working around it.** Tale is a MUD framework from the 2010s, LlamaTale adds the LLM layer on top, and Hallow Mud is a fork of that. When the engine got something wrong, like NPCs never hearing `say to`, I fixed it in the engine, with tests, and sent the fixes back upstream. One has already been merged.

**Open weights are faster here, not just cheaper.** Gemma 3 12B runs on the laptop next to the game server, so an NPC answers in about ten seconds. The same conversation through a hosted API took close to a minute. For a game, that's the difference between talking to someone and waiting for a letter.

**Open weights mean no bill per word.** Running locally there is no per-token cost, so the NPCs can gossip with each other, rewrite the rooms and react to everything all night long without anyone watching a meter.

**One model family, two places to run it.** The same Gemma runs on my own GPU and on Google's API, so moving between them is a line in a config file, not a rewrite. The always-on server uses the API; the fast one uses the laptop.

**Small stories get to exist.** Swede Hollow was a ravine of Swedish immigrant shacks in Saint Paul, cleared in 1956 and a park today. No product team would build a game about it. Open tools let one hobbyist do it in a few days.

## My Agent Session

The whole project started from this prompt to Claude Code:

> Hallow Mud
>
> This project is meant to be a contribution to Hacktoberfest:  
> https://dev.to/challenges/hacktoberfest-week4-2026-10-26
>
> My idea is to build a LLM Mud with Halloween Theme
>
> Mud LLM Base  
> https://github.com/neph1/LlamaTale  
> or  
> https://www.fluffos.info/  
> Try to figure out how the llm actually is involved.
>
> The back story:  
> https://en.wikipedia.org/wiki/Swede_Hollow,_Saint_Paul
>
> The NPCs I think should be based on the inhabitants from there that now are ghosts, zombies, werewolfs, vampires or similar. 
>
> Weapons and armour could be based on Swedish 1800s things:  
> Folkdräkter  
> Lie, Sledgehammer
>
> And other things along that line.
>
> In the challenge there are a number of prize categories, if we can find a match that would be a bonus.  
> The one that caught my eye is gemma.  
> For the local llm, we have q-bert, if MACHINES.md isn't in the global dirs, check sibling project systema-naturae.
>
> Lets dive into the MUD!  
> The Dungeon Master

Besides some python version issues, that basically made a running system.

From there the session kept going: the fixes to the engine listed above (two of them sent upstream as pull requests), the Stranger, the portraits, the theme, and the two public servers.

## The Spirit of It

When the autumn is advancing, the wind is howling and Halloween is nigh, then the mood is set for a real adventure with terrifying encounters...

When attending Uni, my friends and I were playing MUDs a lot. Today, I mostly play FFXIV, with stunning graphics and really advanced fighting. But it is the spirit of the game that matters, and MUDs still have it! 
Coding has been done in really advanced environments like Visual Studio or JetBrains' many tools. Visual Studio Code was sort of a step backwards to a text editor, of course with plugins and tools for almost anything.

Now, I am sitting with a command prompt again, but with agents it can do about anything! 
And the terminal cursor really calls for an entry of *hallow-mud*.

I recently stumbled on a MUD with an LLM, and this challenge felt like a perfect fit!
And for a Swede, I thought that Swede Hollow would be a good setting.

## Prize Categories

**Best Use of Gemma**: every NPC, every room description, and the Stranger are Gemma, run locally on Ollama or hosted via the Gemini API. (The pictures, including each night's portrait of the Stranger, come from Gemini's image model.)

**Best Use of Render**: Render is the game's AI runtime and hosts its front end. The multiplayer server runs there as a Docker web service, built from the repo and deployed on every push to `main`: it runs the game, calls Gemma through the Gemini API for every NPC, room and Stranger, paints each night's Stranger, and serves the web client players connect to. See the `Dockerfile`.
