"""Tool for generating images."""
from typing import Any, List, Union

from steamship import Block, Task
from steamship.agents.schema import AgentContext, Tool
from steamship.agents.tools.image_generation.stable_diffusion import StableDiffusionTool
from steamship.agents.tools.text_generation import TextRewritingTool
from steamship.utils.kv_store import KeyValueStore
from steamship.utils.repl import ToolREPL


class GameTurnTool(Tool):
    """Tool to generate a Pixar-style image.

    This example illustrates wrapping a tool (StableDiffusionTool) with a fixed prompt template that is combined with user input.
    """

    name: str = "GameTurnTool"
    human_description: str = "Modifies a prior prompt with instructions."
    agent_description = (
        "Used to accept instructions about how to modify the visual appearance of something. "
        'Use this tool whenever a user issues an instruction about visual modifications. For example: "Add blue hair." '
        "Input: Instructions for visual modification "
        "Output: An image resulting from those instructions."
    )

    rewrite_prompt = """Instructions:
Rewrite the following image generation prompt so that it reflects the changes requested.

ORIGINAL PROMPT:
{original}

CHANGES REQUESTED:
{{input}}

REWRITTEN PROMPT:"""

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

        starting_prompt = (key_value_store.get("prompt") or {}).get("prompt", None)
        if starting_prompt is None:
            starting_prompt = self.make_initial_prompt()

        # Create a tool for rewriting
        prompt_rewriting_tool = TextRewritingTool(
            rewrite_prompt=self.rewrite_prompt.format(original=starting_prompt)
        )

        # Rewrite the prompt
        rewritten_prompt = prompt_rewriting_tool.run(tool_input, context)

        # Save the new prompt - this is what makes it golf!
        key_value_store.set("prompt", {"prompt": rewritten_prompt})

        # Create the Stable Diffusion tool we want to wrap
        stable_diffusion_tool = StableDiffusionTool()

        # Now return the results of running Stable Diffusion on those modified prompts.
        return stable_diffusion_tool.run(rewritten_prompt, context)


if __name__ == "__main__":
    print("Try running with an input like 'penguin'")
    ToolREPL(GameTurnTool()).run()
