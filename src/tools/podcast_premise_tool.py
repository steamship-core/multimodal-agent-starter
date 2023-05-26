from typing import List
from steamship import Steamship
from steamship.utils.repl import ToolREPL
from steamship.agents.schema import AgentContext, Tool
from steamship.agents.utils import get_llm, with_llm
from steamship.agents.llms import OpenAI

DESCRIPTION = "podcasts"
HEADER = ["Podcast Name", "Podcast Description"]
EXAMPLE_ROWS = [
    ["Animal Planet", "The world is an amazing place. We'll tell you its stories every day."],
    ["Banking News", "All the updates you need to track the banking world."],
    ["Hollywood Gab", "The latest stories from inside Hollywood."],
    ["The MIT Tech Review", "The latest in science and technology, explained."],
    ["Politico", "Hear the opinions and analysis that shapes capitol hill."],
    ["Car Talk", "Call-in show with automotive mysteries, fix-it help, and laughter."],
]


from tools.tsv_row_generator_tool import TsvRowGeneratorTool

class PodcastPremiseTool(TsvRowGeneratorTool):    
    table_description: str = DESCRIPTION
    header_fields: List[str] = HEADER
    example_rows: List[List[str]] = EXAMPLE_ROWS


if __name__ == "__main__":
    with Steamship.temporary_workspace() as client:
        ToolREPL(PodcastPremiseTool()).run_with_client(
            client=client, context=with_llm(llm=OpenAI(client=client))
        )
