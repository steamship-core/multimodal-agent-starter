import sys

sys.path.insert(0, "src")
from steamship import Steamship, SteamshipError
from steamship.cli.ship_spinner import ship_spinner
from termcolor import colored

from api import MyAgent
from src.utils import show_results, LoggingDisabled
from tools import MyTool


def main():
    # questions = [
    #     inquirer.List('action',
    #                   message="Do you want to run your agent or your tool?",
    #                   choices=['Agent', 'Tool'],
    #                   carousel=True
    #                   ),
    # ]
    # answers = inquirer.prompt(questions)
    answers = {"action": "Agent"}
    is_tool = answers["action"] == "Tool"

    with Steamship.temporary_workspace() as client:
        if is_tool:
            tool = MyTool(client=client)
            print(f"Starting {answers['action']} {tool.name}...")
        else:
            print(f"Starting {answers['action']}...")

        print(
            f"If you make code changes, you will need to restart this client. Press CTRL+C to exit at any time.\n"
        )

        count = 1

        # Set to true to debug the Web Client / Telegram Client interfaces
        debug_web_endpoint_via_localhost = False

        while True:
            print(f"----- {answers['action']} Run {count} -----")
            prompt = input(colored(f"Prompt: ", "blue"))
            results = get_results(
                client,
                answers["action"],
                prompt,
                as_api=debug_web_endpoint_via_localhost,
            )
            show_results(client, results)
            count += 1


def get_results(client: Steamship, action: str, prompt: str, as_api: bool = False):
    if action == "Tool":
        tool = MyTool(client=client)
        return tool.run(prompt=prompt)
    else:
        agent = MyAgent(client=client)

        # For Debugging
        if as_api:
            # Web client simulation
            return agent.answer(question=prompt)

            # Telegram client simulation
            # return agent.telegram_respond(message={"chat": {"id": 123}, "message_id": 123, "text": prompt})
        if (
            not agent.is_verbose_logging_enabled()
        ):  # display progress when verbose is False
            print("Running: ", end="")
            with ship_spinner():
                return agent.run(prompt=prompt)
        else:
            return agent.run(prompt=prompt)


if __name__ == "__main__":
    # when running locally, we can use print statements to capture logs / info.
    # as a result, we will disable python logging to run. this will keep the output cleaner.
    with LoggingDisabled():
        try:
            main()
        except SteamshipError as e:
            print(colored("Aborting! ", "red"), end="")
            print(f"There was an error encountered when running: {e}")
