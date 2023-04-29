import logging
import re
import uuid

from steamship import Block, Steamship
from steamship.data.workspace import SignedUrl
from steamship.utils.signed_urls import upload_to_signed_url
from termcolor import colored

UUID_PATTERN = re.compile(
    r"([0-9A-Za-z]{8}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{12})"
)


def is_valid_uuid(uuid_to_test: str, version=4) -> bool:
    """Check a string to see if it is actually a UUID."""
    lowered = uuid_to_test.lower()
    try:
        uuid_obj = uuid.UUID(lowered, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == lowered


def show_result(client: Steamship, result: str):
    maybe_block_id = UUID_PATTERN.search(result or "")
    if maybe_block_id:
        print(f"LLM response ('{result}') contained an image: ", end="")
        signed_url = _make_image_public(client, maybe_block_id.group())
        result = signed_url
    print(result, end="\n\n")


def show_results(client: Steamship, results):
    print(colored("\nResults: ", "blue", attrs=["bold"]))
    if isinstance(results, str):
        show_result(client, results)
    else:
        for result in results:
            show_result(client, result)


def _make_image_public(client, result):
    block = Block.get(client, _id=result)
    filepath = str(uuid.uuid4())
    signed_url = (
        client.get_workspace()
        .create_signed_url(
            SignedUrl.Request(
                bucket=SignedUrl.Bucket.PLUGIN_DATA,
                filepath=filepath,
                operation=SignedUrl.Operation.WRITE,
            )
        )
        .signed_url
    )
    logging.info(f"Got signed url for uploading block content: {signed_url}")
    read_signed_url = (
        client.get_workspace()
        .create_signed_url(
            SignedUrl.Request(
                bucket=SignedUrl.Bucket.PLUGIN_DATA,
                filepath=filepath,
                operation=SignedUrl.Operation.READ,
            )
        )
        .signed_url
    )
    upload_to_signed_url(signed_url, block.raw())
    return read_signed_url


class LoggingDisabled:
    """Context manager that turns off logging within context."""

    def __enter__(self):
        logging.disable(logging.CRITICAL)

    def __exit__(self, exit_type, exit_value, exit_traceback):
        logging.disable(logging.NOTSET)
