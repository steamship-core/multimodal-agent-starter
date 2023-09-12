# Question Answering Bot

Create a cloud-hosted LLM Agent with a vector-store memory and question-answering capabilities.

This repository is designed to pair with [this Agent Building Guidebook](https://docs/steamship.com/agent-guidebook)

## Getting Started

You can be up and running in under a minute. [A full setup walk-through is here](https://steamship.com/learn/agent-guidebook/project-setup).

Clone this repository, then set up a Python virtual environment with:

```bash
python3.8 -m venv .venv
source .venv/bin/activate
python3.8 -m pip install -r requirements.txt
python3.8 -m pip install -r requirements.dev.txt
```

> [!NOTE]
> Requirements you put in `requirements.txt` are what will be run along with the agent when you deploy. The dependencies
> in `requirements.dev.txt` have been prepopulated with packages you may need while developing on your machine.

## Running your agent

[A full guide to running is here](https://docs.steamship.com/agent-guidebook/getting-started/run-your-agent).

With the proper Python environment set up and your `STEAMSHIP_API_KEY` environment variable set, just run:

```bash
ship run local
```

## Modifying your agent

Modify your agent by editing `api.py`. 

You can:

- Change its personality (edit the SYSTEM_PROMPT)
- Add tools, allowing your agent's reasoning process to do new things (see tool list below)
- Add mixins, allowing your agent to connect to different channels (see mixin list below)

Other examples are found in the `example_agents` folder. Copy/paste one of these into `api.py` to use it.

## Deploying your agent

[A full guide to deploying is here](https://docs.steamship.com/agent-guidebook/getting-started/deploy-your-agent).

This project can be deployed straight to the cloud. Simply type:

```bash
ship deploy
```

and follow the prompts.

## What tools can I use with my agent?

Tools help your agent perform actions or fetch information from the outside world. 
The Steamship SDK includes [a large set of multi-modal & memory-aware tools you can use right away](https://docs.steamship.com/agent-guidebook/core-concepts/tools).
And you can import or find more open source tools in the [Steamship SDK](https://github.com/steamship-core/python-client):

## What mixins can I use with my agent?

Mixins provide additional API endpoints to your agent, which can connect your agent to a communication channel like Telegram, or provide additional data loading functionality.

Several mixins are provided out of the box in the Steamship SDK:

* Transports (Communication Channels)
  * [Steamship Web Widget](https://github.com/steamship-core/python-client/blob/main/src/steamship/agents/mixins/transports/steamship_widget.py) - For testing your agent in the Web UI
  * [Telegram](https://github.com/steamship-core/python-client/blob/main/src/steamship/agents/mixins/transports/telegram.py) - for communicating with your agent in Telegram
  * [Slack](https://github.com/steamship-core/python-client/blob/main/src/steamship/agents/mixins/transports/slack.py) - for communicating with your agent in Slack
* Data Loading
  * [Indexer Pipeline](https://github.com/steamship-core/python-client/blob/main/src/steamship/invocable/mixins/indexer_pipeline_mixin.py) - For loading documents into your agent's question-answer ability