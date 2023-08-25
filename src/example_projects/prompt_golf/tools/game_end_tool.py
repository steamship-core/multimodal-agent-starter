"""Tool for generating images."""
from typing import Any, List, Union

from steamship import Block, Task
from steamship.agents.schema import AgentContext, Tool
from steamship.agents.tools.image_generation.stable_diffusion import StableDiffusionTool
from steamship.utils.kv_store import KeyValueStore
from steamship.utils.repl import ToolREPL


class GameStartTool(Tool):
    """Tool to generate a Pixar-style image.

    This example illustrates wrapping a tool (StableDiffusionTool) with a fixed prompt template that is combined with user input.
    """

    game_name = "Prompt Golf"

    name: str = "GameEndTool"
    human_description: str = f"Ends a new game of {game_name}."
    agent_description = (
        f"Used to end a new game of {game_name}. "
        "Use this tool whenever a user remarks that someone or something has won. "
        "Input: The information that someone has won. "
        "Output: A congratulatory message to tell them."
    )

    def make_initial_prompt(self) -> str:
        starting_prompt = (
            "Pixar style {subject}, 4k, 8k, unreal engine, octane render photorealistic by cosmicwonder, "
            "hdr, photography by cosmicwonder, high definition, symmetrical face, volumetric lighting, dusty haze, "
            "photo, octane render, 24mm, 4k, 24mm, DSLR, high quality, 60 fps, ultra realistic"
        )
        return starting_prompt

    def run(
        self, tool_input: List[Block], context: AgentContext
    ) -> Union[List[Block], Task[Any]]:

        key_value_store = KeyValueStore(
            client=context.client, store_identifier=f"{self.name}"
        )

        starting_prompt = self.make_initial_prompt()

        # Save the new prompt - this is what makes it golf!
        key_value_store.set("prompt", {"prompt": starting_prompt})

        # Create the Stable Diffusion tool we want to wrap
        stable_diffusion_tool = StableDiffusionTool()

        # Now return the results of running Stable Diffusion on those modified prompts.
        image_results = stable_diffusion_tool.run(starting_prompt, context)

        return [
            Block(
                text="Are you ready?? The rules are simple: tell me how to modify this image and I will. Whoever successfully makes it a PINK SHARK wins."
            ),
            image_results[0],
        ]


if __name__ == "__main__":
    print("Try running with an input like 'penguin'")
    ToolREPL(GameStartTool()).run()
