import logging
import sys
from typing import List

from steamship.experimental.transports.chat import ChatMessage

sys.path.insert(0, "src")
from steamship import Steamship, SteamshipError
from steamship.cli.ship_spinner import ship_spinner
from termcolor import colored

from api import MyAgent
from tools import MyTool


def show_results(response_messages: List[ChatMessage]):
    print(colored("\nResults: ", "blue", attrs=["bold"]))
    for message in response_messages:
        if message.mime_type and message.mime_type.startswith("image"):
            print(
                f"LLM response ('{message.text}') contained an image: \n {message.url}",
                end="\n\n",
            )
        else:
            print(message.text, end="\n\n")


class LoggingDisabled:
    """Context manager that turns off logging within context."""

    def __enter__(self):
        logging.disable(logging.CRITICAL)

    def __exit__(self, exit_type, exit_value, exit_traceback):
        logging.disable(logging.NOTSET)


def main():
    Steamship()
    # questions = [
    #     inquirer.List(
    #         "action",
    #         message="Do you want to run your agent or your tool?",
    #         choices=["Agent", "Tool"],
    #         carousel=True,
    #     ),
    # ]
    # answers = inquirer.prompt(questions)
    answers = {"action": "Agent"}
    is_tool = answers["action"] == "Tool"

    with Steamship.temporary_workspace() as client:
        if is_tool:
            run = run_tool
            print(f"Starting {answers['action']} {MyTool(client=client).name}...")
        else:
            run = run_agent
            print(f"Starting {answers['action']}...")

        print(
            f"If you make code changes, you will need to restart this client. Press CTRL+C to exit at any time.\n"
        )

        count = 1

        while True:
            print(f"----- {answers['action']} Run {count} -----")
            prompt = input(colored(f"Prompt: ", "blue"))
            run(
                client,
                prompt,
            )
            count += 1


def run_tool(client: Steamship, prompt: str, **kwargs) -> None:
    tool = MyTool(client=client)
    print(tool.run(prompt=prompt), end="\n\n")


def run_agent(client: Steamship, prompt: str, as_api: bool = False) -> None:
    agent = MyAgent(client=client, config={"bot_token": "test"})

    # For Debugging
    if as_api:
        # Web client simulation
        response = agent.answer(question=prompt)

        # Telegram client simulation
        # return agent.telegram_respond(message={"chat": {"id": 123}, "message_id": 123, "text": prompt})
    if not agent.is_verbose_logging_enabled():  # display progress when verbose is False
        print("Running: ", end="")
        with ship_spinner():
            response = agent.create_response(incoming_message=ChatMessage(text="test"))
    else:
        response = agent.create_response(incoming_message=ChatMessage(text="test"))

    show_results(response)


if __name__ == "__main__":
    # when running locally, we can use print statements to capture logs / info.
    # as a result, we will disable python logging to run. this will keep the output cleaner.
    with LoggingDisabled():
        try:
            main()
        except SteamshipError as e:
            print(colored("Aborting! ", "red"), end="")
            print(f"There was an error encountered when running: {e}")
