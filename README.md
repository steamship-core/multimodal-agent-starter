# AI Podcaster

[![Open in a VS Code Dev Container](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/eob/ai-podcaster)

A cloud-deployable project to generate a podcast 100% with AI. Based on the [Multimodal Agent Starter](https://steamship.com/learn/agent-guidebook) repo.

Podcasts produced with this code:
* [LOLLM - AI Generated Standup Comedy](https://edwardbenson.com/lollm)


## Getting Started

Clone this repository, then set up a Python virtual environment with:

```bash
python3.8 -m venv .venv
source .venv/bin/activate
python3.8 -m pip install -r requirements.txt
```

## Deploying

[A full guide to deploying is here](https://steamship.com/learn/agent-guidebook/deploying/deploy-your-agent). The TL;DR is:

```bash
ship deploy
```

and follow the prompts.

