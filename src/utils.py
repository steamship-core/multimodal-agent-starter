import logging
import uuid

from steamship import Block, Steamship
from steamship.data.workspace import SignedUrl
from steamship.utils.signed_urls import upload_to_signed_url


def is_valid_uuid(uuid_to_test: str, version=4) -> bool:
    """Check a string to see if it is actually a UUID."""
    lowered = uuid_to_test.lower()
    try:
        uuid_obj = uuid.UUID(lowered, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == lowered


def show_result(client: Steamship, result: str):
    if is_valid_uuid(result):
        signed_url = _make_image_public(client, result)
        result = signed_url
    print(result, end="\n\n")


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
