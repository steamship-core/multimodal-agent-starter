"""Tool for generating images."""
from typing import Any, List, Union

from steamship import Block, Task
from steamship.agents.schema import AgentContext
from steamship.agents.tools.base_tools import ImageGeneratorTool
from steamship.agents.tools.image_generation.stable_diffusion import StableDiffusionTool
from steamship.utils.repl import ToolREPL


class PixarStyleTool(ImageGeneratorTool):
    """Tool to generate a Pixar-style image.

    This example illustrates wrapping a tool (StableDiffusionTool) with a fixed prompt template that is combined with user input.
    """

    name: str = "PixarStyleTool"
    human_description: str = "Generates a Pixar-style image from text."
    agent_description = (
        "Used to generate a Pixar-style image of something. "
        "Only use if the user has asked directly for a Pixar-style image of something. "
        "Input: the subject of the image "
        "Output: the Pixar-style image."
    )

    prompt_template = (
        "Pixar style {subject}, 4k, 8k, unreal engine, octane render photorealistic by cosmicwonder, "
        "hdr, photography by cosmicwonder, high definition, symmetrical face, volumetric lighting, dusty haze, "
        "photo, octane render, 24mm, 4k, 24mm, DSLR, high quality, 60 fps, ultra realistic"
    )

    def run(
        self, tool_input: List[Block], context: AgentContext
    ) -> Union[List[Block], Task[Any]]:
        # Modify the tool inputs by interpolating them with stored prompt here
        modified_inputs = [
            Block(text=self.prompt_template.format(subject=block.text))
            for block in tool_input
        ]

        # Create the Stable Diffusion tool we want to wrap
        stable_diffusion_tool = StableDiffusionTool()

        # Now return the results of running Stable Diffusion on those modified prompts.
        return stable_diffusion_tool.run(modified_inputs, context)


if __name__ == "__main__":
    print("Try running with an input like 'penguin'")
    ToolREPL(PixarStyleTool()).run()
