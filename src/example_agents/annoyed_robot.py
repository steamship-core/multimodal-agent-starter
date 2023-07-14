from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.mixins.transports.steamship_widget import \
    SteamshipWidgetTransport
from steamship.agents.service.agent_service import AgentService
from steamship.agents.tools.image_generation.stable_diffusion import \
    StableDiffusionTool
from steamship.agents.tools.search.search import SearchTool
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

NOTE: Some functions return images, video, and audio files. These multimedia files will be represented in messages as
UUIDs for Steamship Blocks. When responding directly to a user, you SHOULD print the Steamship Blocks for the images,
video, or audio as follows: `Block(UUID for the block)`.

Example response for a request that generated an image:
Here is the image you requested: Block(288A2CA1-4753-4298-9716-53C1E42B726B).

Only use the functions you have been provided with."""

MODEL_NAME = "gpt-4"


class MyAssistant(AgentService):

    USED_MIXIN_CLASSES = [SteamshipWidgetTransport]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._agent = FunctionsBasedAgent(
            tools=[SearchTool(), StableDiffusionTool()],
            llm=ChatOpenAI(self.client, model_name=MODEL_NAME),
        )
        self._agent.PROMPT = SYSTEM_PROMPT

        # This Mixin provides HTTP endpoints that connects this agent to a web client
        self.add_mixin(
            SteamshipWidgetTransport(
                client=self.client, agent_service=self, agent=self._agent
            )
        )


if __name__ == "__main__":
    AgentREPL(
        MyAssistant,
        agent_package_config={},
    ).run()
