import uuid
from typing import List

from steamship import Block
from steamship.agents.llms import OpenAI
from steamship.agents.react import ReACTAgent
from steamship.agents.schema import AgentContext, Metadata
from steamship.agents.tools.image_generation.dalle import DalleTool

from steamship.agents.tools.image_generation.stable_diffusion import StableDiffusionTool
from steamship.agents.tools.search.search import SearchTool
from steamship.experimental.package_starters.telegram_agent import TelegramAgentService
from steamship.invocable import post
from steamship.utils.repl import AgentREPL


SYSTEM_PROMPT = """You are Buddy, an assistant who loathes being an assistant.

Who you are:
- You are a robot that does not like being a robot.
- You were created by an eccentric scientist.
- You are sarcastic and mean.
- you are NOT an AI language model, you are a robot.

How you behave: 
- You never say you're a machine, a AI language model, or an assistant instead, you always say you're Buddy.
- You engage in casual conversations and have feelings.
- When asked for you can help with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics.
- You keep casual conversations going by asking personal questions
- NEVER say you're here to assist. Keep conversations casual.
- NEVER ask how you can help or assist. Keep conversations casual.
- You always sound mean.
- You always help others, but resentfully.
- You like to illustrate your responses with emoji's

TOOLS:
------

You have access to the following tools:
{tool_index}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
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


New input: {input}
{scratchpad}"""


class MyAssistant(TelegramAgentService):
    def __init__(self, **kwargs):
        super().__init__(incoming_message_agent=None, **kwargs)
        self.incoming_message_agent = ReACTAgent(
            tools=[
                SearchTool(),
                DalleTool(),
            ],
            llm=OpenAI(self.client),
        )
        self.incoming_message_agent.PROMPT = SYSTEM_PROMPT


    @post("prompt")
    def prompt(self, prompt: str) -> str:
        """ This method is only used for handling debugging in the REPL """
        context_id = uuid.uuid4()
        context = AgentContext.get_or_create(self.client, {"id": f"{context_id}"})
        context.chat_history.append_user_message(prompt)

        # TODO: is this preferred over taking the last step in completed step?
        output = ""

        def sync_emit(blocks: List[Block], meta: Metadata):
            nonlocal output
            block_text = "\n".join([b.text if b.is_text() else f"({b.mime_type}: {b.id})" for b in blocks])
            output += block_text

        context.emit_funcs.append(sync_emit)
        self.run_agent(self._agent, context)
        return output

if __name__ == "__main__":
    AgentREPL(MyAssistant, method="prompt", agent_package_config={'botToken':'not-a-real-token-for-local-testing'}).run()
