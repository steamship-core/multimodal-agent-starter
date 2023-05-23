"""Base Agent implementation to add missing pieces"""
from abc import ABC, abstractmethod
from typing import List, Optional

from steamship import Block
from steamship.agents.base import Metadata
from steamship.agents.context.context import AgentContext
from steamship.agents.llm.openai import OpenAI
from steamship.agents.planner.react import ReACTPlanner
from steamship.agents.service.agent_service import AgentService
from steamship.agents.tool import Tool
from steamship.experimental.package_starters.telegram_bot import TelegramBot
from steamship.experimental.transports.chat import ChatMessage

from core.personality import Personality

AGENT_PROMPT = """You are {agent_name}, {agent_byline}.

Who you are:
{agent_identity}

How you behave: 
{agent_behavior}

TOOLS:
------

You have access to the following tools:
{{tool_index}}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{{tool_names}}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a final response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
AI: [your final response here which ALWAYS includes UUID of generated images]

Make sure to use all observations to come up with your final response. 
If an observation included a media UUID, ALWAYS copy it into the final response.
If an observation included a media UUID, ALWAYS come up with a final response along with an explanation.
If an observation did not include a media UUID, to not return a placeholder message.
```

Begin!


New input: {{input}}
{{scratchpad}}
"""


class BaseAgent(AgentService, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.planner = ReACTPlanner(
            tools=self.get_tools(),
            llm=OpenAI(self.client),
        )
        self.planner.PROMPT = self.construct_react_prompt(self.get_personality())

    def voice_tool(self) -> Optional[Tool]:
        return None

    def send_message(self, blocks: List[Block], meta: Metadata):  # TODO: Push down in Telegrambot
        """Send a message to Telegram.

        Note: This is a private endpoint that requires authentication."""
        print(f"\n\nTELEGRAM SENDING MESSAGES:\n{blocks}")
        # self.telegram_transport.send([ChatMessage.from_block(block) for block in blocks])

    def respond(
            self, incoming_message: ChatMessage
    ) -> None:  # TODO: Push down into TelegramBot & SteamshipWidgetBot
        context = AgentContext.get_or_create(
            self.client,
            context_keys={
                "chat_id": incoming_message.get_chat_id()
                # No message id here; we don't want a new context per message
            },
        )
        if len(context.emit_funcs) == 0:
            context.emit_funcs.append(self.send_message)

        if len(context.chat_history.messages) == 0:
            context.chat_history.append_system_message()

        return self.create_response(context)

    def create_response(self, context: AgentContext) -> None:

        if len(context.emit_funcs) == 0:
            context.emit_funcs.append(self.send_message)

        if len(context.chat_history.messages) == 0:
            context.chat_history.append_system_message()

        self.run(context)

    @abstractmethod
    def get_personality(self):
        raise NotImplementedError()

    @abstractmethod
    def get_tools(self) -> List[Tool]:
        return []

    def construct_react_prompt(
            self,
            personality: Personality
    ):
        identity = "\n".join([f"- {item}" for item in personality.identity])
        behavior = "\n".join([f"- {item}" for item in personality.behavior])

        return AGENT_PROMPT.format(
            agent_name=personality.name,
            agent_byline=personality.byline,
            agent_identity=identity,
            agent_behavior=behavior
        )
