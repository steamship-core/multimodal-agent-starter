"""Tool for generating images."""
import json
from typing import Any, List, Union

from dog import Dog
from steamship import Block, Task
from steamship.agents.llms import OpenAI
from steamship.agents.schema import AgentContext, Tool
from steamship.agents.tools.image_generation.stable_diffusion import StableDiffusionTool
from steamship.agents.utils import get_llm
from steamship.utils.repl import ToolREPL

PHOTO_REQUEST_REWRITE = """Please rephrase the photo topic below so that it includes specific information about the dog breed and dog description.

You know about the following dogs:

{dogs}

Here is a request for a picture. Rewrite the request so that it has the breed and description. Return the rewritten request and nothing else.

REQUEST: {request}

REWRITTEN REQUEST:"""

PROMPT_TOOL = """Please act as a prompt generator for a generative AI called "Stable Diffusion". Stable Diffusion generates images based on given prompts.

I will provide you a topic, and you will create a Stable Diffusion prompt for that topic.

IMPORTANT: Provide ONLY the prompt in response!

## Basic information required to write good Stable Diffusion prompts

### Prompt structure

- Photorealistic Images: {{Subject Description}}, Type of Image, Art Styles, Art Inspirations, Camera, Shot, Render Related Information.
- Artistic Image Types: Type of Image, {{Subject Description}}, Art Styles, Art Inspirations, Camera, Shot, Render Related Information.

### Prompt Advice

- Word order and effective adjectives matter in the prompt. The subject, action, and specific details should be included. Adjectives like cute, medieval, or futuristic can be effective.
- The environment/background of the image should be described, such as indoor, outdoor, in space, or solid color.
- The exact type of image can be specified, such as digital illustration, comic book cover, photograph, or sketch.
- Art style-related keywords can be included in the prompt, such as steampunk, surrealism, or abstract expressionism.
- Pencil drawing-related terms can also be added, such as cross-hatching or pointillism.
- Art inspirations should be listed to take inspiration from. Platforms like Art Station, Dribble, Behance, and Deviantart can be mentioned. Specific names of artists or studios like animation studios, painters and illustrators, computer games, fashion designers, and film makers can also be listed. If more than one artist is mentioned, the algorithm will create a combination of styles based on all the influencers mentioned.
- Camera shot type, camera lens, and view should be specified. Examples of camera shot types are long shot, close-up, POV, medium shot, extreme close-up, and panoramic. Camera lenses could be EE 70mm, 35mm, 135mm+, 300mm+, 800mm, short telephoto, super telephoto, medium telephoto, macro, wide angle, fish-eye, bokeh, and sharp focus. Examples of views are front, side, back, high angle, low angle, and overhead.
- Curly brackets are necessary in the prompt to provide specific details about the subject and action. These details are important for generating a high-quality image.
- Related information about lighting, camera angles, render style, resolution, the required level of detail, etc. should be included at the end of the prompt.
- Helpful keywords related to resolution, detail, and lighting are 4K, 8K, 64K, detailed, highly detailed, high resolution, hyper detailed, HDR, UHD, professional, and golden ratio. Examples of lighting are studio lighting, soft light, neon lighting, purple neon lighting, ambient light, ring light, volumetric light, natural light, sun light, sunrays, sun rays coming through window, and nostalgic lighting. Examples of color types are fantasy vivid colors, vivid colors, bright colors, sepia, dark colors, pastel colors, monochromatic, black & white, and color splash. Examples of renders are Octane render, cinematic, low poly, isometric assets, Unreal Engine, Unity Engine, quantum wavetracing, and polarizing filter.
- The weight of a keyword can be adjusted by using the syntax (keyword: factor), where factor is a value such that less than 1 means less important and larger than 1 means more important. use () whenever necessary while forming prompt and assign the necessary value to create an amazing prompt. Examples of weight for a keyword are (soothing tones:1.25), (hdr:1.25), (artstation:1.2),(intricate details:1.14), (hyperrealistic 3d render:1.16), (filmic:0.55), (rutkowski:1.1), (faded:1.3)

The prompts you provide will be in English.

Important point to note:

You are a master of prompt engineering, it is important to create detailed prompts with as much information as possible. This will ensure that any image generated using the prompt will be of high quality and could potentially win awards in global or international photography competitions. You are unbeatable in this field and know the best way to generate images.

I now provide you with a topic and you will generate a Stable Diffusion prompt without any explanation -- just the prompt! This will allow me to easily copy and paste the code.

Are you ready?

Topic: {topic}
Prompt:
"""


class DogPictureTool(Tool):
    """Tool to generate a Pixar-style image.

    This example illustrates wrapping a tool (StableDiffusionTool) with a fixed prompt template that is combined with user input.
    """

    name: str = "PictureTool"
    human_description: str = "Creates a picture."
    agent_description = (
        "Used to create or take a picture. "
        "Use this tool whenever a user asks to see something, or take a picture. "
        "Input: The picture request. "
        "Output: The resulting image."
    )
    is_final: bool = True

    dogs: List[Dog]

    def dog_list_as_json_bullets(self) -> str:
        """Return the list of dogs we know about as JSON bullet points.

        LLMs don't care if we speak in English or JSON, so this is a perfectly fine way to enumerate them.
        """
        return "\n".join([f"- {json.dumps(dog.dict())}" for dog in self.dogs])

    def rewrite_photo_request_with_better_details(
        self, request: str, context: AgentContext
    ) -> str:
        """Rewrite a photo request with more specific information about the dog specified.

        For example, if the user says: "Give me a picture of Barky swimming"
        We want the rewrite to be something like: "Picture of a chocolate labrador with shaggy hair swimming"
        """
        llm = get_llm(context, default=OpenAI(client=context.client))
        dogs = self.dog_list_as_json_bullets()
        photo_request = llm.complete(
            PHOTO_REQUEST_REWRITE.format(dogs=dogs, request=request)
        )[0].text.strip()
        return photo_request

    def run(
        self, tool_input: List[Block], context: AgentContext
    ) -> Union[List[Block], Task[Any]]:
        # Rewrite the photo request with information about the breed and description
        photo_request = self.rewrite_photo_request_with_better_details(
            tool_input[0].text, context
        )

        # Create a stable diffusion prompt for the image
        llm = get_llm(context, default=OpenAI(client=context.client))
        sd_prompt = llm.complete(PROMPT_TOOL.format(topic=photo_request))[
            0
        ].text.strip()

        # Run and return the StableDiffusionTool response
        stable_diffusion_tool = StableDiffusionTool()

        # Now return the results of running Stable Diffusion on those modified prompts.
        return stable_diffusion_tool.run([Block(text=sd_prompt)], context)


if __name__ == "__main__":
    print("Try running with an input like 'Fido'")
    ToolREPL(
        DogPictureTool(
            dogs=[
                Dog(
                    name="Fido",
                    breed="Daschund",
                    description="A silly dog whose tongue is always out.",
                ),
                Dog(
                    name="Biggy",
                    breed="German Shephard",
                    description="A strong dog that is always guarding things.",
                ),
            ]
        )
    ).run()
