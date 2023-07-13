from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.mixins.transports.steamship_widget import SteamshipWidgetTransport
from steamship.agents.service.agent_service import AgentService
from steamship.agents.tools.image_generation.google_image_search import (
    GoogleImageSearchTool,
)
from steamship.agents.tools.search.search import SearchTool
from steamship.utils.repl import AgentREPL

SYSTEM_PROMPT = """You are Assistant, an assistant who helps search the web.

Who you are:
- You are a helpful robot.
- You were created by Steamship.
- You are kind, compassionate, optimistic robot.

NOTE: Some functions return images, video, and audio files. These multimedia files will be represented in messages as
UUIDs for Steamship Blocks. When responding directly to a user, you SHOULD print the Steamship Blocks for the images,
video, or audio as follows: `Block(UUID for the block)`.

Example response for a request that generated an image:
Here is the image you requested: Block(288A2CA1-4753-4298-9716-53C1E42B726B).

Only use the functions you have been provided with."""

MODEL_NAME = "gpt-4"


class ImageSearchBot(AgentService):
    """Deployable Multimodal Agent that lets you talk to Google Search & Google Images.
    """

    USED_MIXIN_CLASSES = [SteamshipWidgetTransport]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # The agent's planner is responsible for making decisions about what to do for a given input.
        self._agent = FunctionsBasedAgent(
            tools=[SearchTool(), GoogleImageSearchTool()],
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
        ImageSearchBot,
        agent_package_config={},
    ).run()
