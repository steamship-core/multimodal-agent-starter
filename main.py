from steamship import Steamship

from my_agent import MyAgent
from src.utils import show_result
from tools import MyTool

if __name__ == "__main__":
    with Steamship.temporary_workspace() as client:
        agent = MyAgent(client)
        if agent.is_ready():
            results = agent.run("Generate a picture of boston")
            for result in results:
                show_result(client, result)
        else:
            my_tool = MyTool(client)
            result = my_tool.run("Find a hotel in Boston")
            print(result)
