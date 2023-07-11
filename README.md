# Multi-modal Agent Starter

Create a cloud-hosted LLM Agent with custom personality, multi-modal tools, and memory.

This repository is designed to pair with [this Agent Building Guidebook](https://steamship.com/learn/agent-guidebook)

## Getting Started

You can be up and running in under a minute. [A full setup walk-through is here](https://steamship.com/learn/agent-guidebook/project-setup).

Clone this repository, then set up a Python virtual environment with:

```bash
python3.8 -m venv .venv
source .venv/bin/activate
python3.8 -m pip install -r requirements.txt
```

## Running your agent

[A full guide to running is here](https://steamship.com/learn/agent-guidebook/use/use-on-localhost).

With the proper Python environment set up and your `STEAMSHIP_API_KEY` environment variable set, just run:

```bash
PYTHONPATH=src python3.8 src/api.py
```

## Modifying your agent

Modify your agent by editing `src/api.py`. 
You can:

- Change its personality (edit the SYSTEM_PROMPT)
- Add tools, allowing your agent's reasoning process to do new things (see tool list below)
- Add mixins, allowing your agent to connect to different channels (see mixin list below)

Other examples are found in the `example_agents` folder. Copy/paste one of these into `api.py` to use it.

## Deploying your agent

[A full guide to deploying is here](https://steamship.com/learn/agent-guidebook/deploying/deploy-your-agent).

This project can be deployed straight to the cloud. Simply type:

```bash
ship deploy
```

and follow the prompts.

## What tools can I use with my agent?

Tools help your agent perform actions or fetch information from the outside world. The Steamship SDK includes [a large set of multi-modal & memory-aware tools you can use right away](https://steamship.com/learn/agent-guidebook/project-layout/tools).

Your starter project already has a few tools in `src/example_tools`.

And you can import or find more open source tools in the [Steamship SDK](https://github.com/steamship-core/python-client):

* Audio Transcription:
  * [Assembly AI](https://github.com/steamship-core/python-client/blob/main/src/steamship/agents/tools/audio_transcription/assembly_speech_to_text_tool.py) - Turns audio into text
  * [Whisper](https://github.com/steamship-core/python-client/blob/main/src/steamship/agents/tools/audio_transcription/whisper_speech_to_text_tool.py) - Turns audio into text
  * [RSS Download](https://github.com/steamship-core/python-client/blob/main/src/steamship/agents/tools/audio_transcription/fetch_audio_urls_from_rss_tool.py) - Returns Audio URLs from an RSS feed
* Classification:
  * [Sentiment Analysis](https://github.com/steamship-core/python-client/blob/main/src/steamship/agents/tools/classification/sentiment_analysis_tool.py) - Can report on the sentiment of a piece of text
  * [Zero Shot Classification](https://github.com/steamship-core/python-client/blob/main/src/steamship/agents/tools/classification/zero_shot_classifier_tool.py) - Can classify a piece of text
* Image Generation:
  * [DALL-E](https://github.com/steamship-core/python-client/blob/main/src/steamship/agents/tools/image_generation/dalle.py) - Generate images with DALL-E
  * [Stable Diffusion](https://github.com/steamship-core/python-client/blob/main/src/steamship/agents/tools/image_generation/stable_diffusion.py) - Generate images with Stable Diffusion
  * [Google Image Search](https://github.com/steamship-core/python-client/blob/main/src/steamship/agents/tools/image_generation/google_image_search.py) - Perform a Google Image Search and return the results
* Speech Generation:
  * [Eleven Labs](https://github.com/steamship-core/python-client/blob/main/src/steamship/agents/tools/speech_generation/generate_speech.py) - Turn text into the spoken word
* Search:
  * [Google Search](https://github.com/steamship-core/python-client/blob/main/src/steamship/agents/tools/search/search.py) - Find answers to questions on the web
* Question Answering:
  * [Vector Search QA](https://github.com/steamship-core/python-client/blob/main/src/steamship/agents/tools/question_answering/vector_search_qa_tool.py) - Find answers to questions in the Steamship Vector Database
  * [Prompt Database QA](https://github.com/steamship-core/python-client/blob/main/src/steamship/agents/tools/question_answering/prompt_database_question_answerer.py) - Find answers to questions from a pre-loaded prompt database
* Text Generation:
  * [Image Prompt Generation](https://github.com/steamship-core/python-client/blob/main/src/steamship/agents/tools/text_generation/image_prompt_generator_tool.py) - Rewrite a topic into a Stable Diffusion image prompt
  * [Personality Tool](https://github.com/steamship-core/python-client/blob/main/src/steamship/agents/tools/text_generation/personality_tool.py) - Reword a response according to a particular personality
  * [Text Summarization](https://github.com/steamship-core/python-client/blob/main/src/steamship/agents/tools/text_generation/summarize_text_with_prompt_tool.py) - Summarize text
  * [Text Rewriter](https://github.com/steamship-core/python-client/blob/main/src/steamship/agents/tools/text_generation/text_rewrite_tool.py) - Utility tool for building tools that use prompts to operate
  * [Translation](https://github.com/steamship-core/python-client/blob/main/src/steamship/agents/tools/text_generation/text_translation_tool.py) - Translate text using an LLM
* Conversation Starters:
  * [Knock-Knock Joke Starter](https://github.com/steamship-core/python-client/blob/main/src/steamship/agents/tools/conversation_starters/knock_knock_tool.py) - Initiate a knock knock joke. The world's most useful tool.

## What mixins can I use with my agent?

Mixins provide additional API endpoints to your agent, which can connect your agent to a communication channel like Telegram, or provide additional data loading functionality.

Several mixins are provided out of the box in the Steamship SDK:

* Transports (Communication Channels)
  * [Steamship Web Widget](https://github.com/steamship-core/python-client/blob/main/src/steamship/agents/mixins/transports/steamship_widget.py) - For testing your agent in the Web UI
  * [Telegram](https://github.com/steamship-core/python-client/blob/main/src/steamship/agents/mixins/transports/telegram.py) - for communicating with your agent in Telegram
* Data Loading
  * [Indexer Pipeline](https://github.com/steamship-core/python-client/blob/main/src/steamship/invocable/mixins/indexer_pipeline_mixin.py) - For loading documents into your agent's question-answer ability