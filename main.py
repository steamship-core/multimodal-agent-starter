from steamship import Steamship

from my_agent import MyAgent
from src.utils import show_result
from tools import MyTool
from termcolor import colored

if __name__ == "__main__":
    with Steamship.temporary_workspace() as client:
        agent = MyAgent(client)
        if agent.is_ready():
            message = input(colored("Input: ", "grey"))
            results = agent.run(message)
            for result in results:
                show_result(client, result)
        else:
            my_tool = MyTool(client)
            message = input(colored("Input: ", "grey"))
            result = my_tool.run(message)
            print(result)
