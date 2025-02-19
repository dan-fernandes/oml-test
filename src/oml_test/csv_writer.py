from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import cast

from event_model.documents import DocumentType, Event, EventDescriptor
from ophyd_async.core import PathProvider, StaticFilenameProvider, StaticPathProvider


def cast_and_validate_path(directory_path: str) -> Path:
    path = Path(directory_path)

    if not path.exists():
        raise Exception(f"Path does not exist: {directory_path}")

    if not path.is_dir():
        raise Exception(f"Path is not directory: {directory_path}")

    return path


def get_static_path_provider(directory_path: Path, filename: str | None = None):
    filename = filename or "oml-test.csv" + datetime.now().strftime("%d-%m-%Y-%H-%M")
    filename_provider = StaticFilenameProvider(filename)
    return StaticPathProvider(filename_provider, directory_path)


def write_csv(csv_string: str, path_provider: PathProvider) -> None:
    path = path_provider().directory_path / path_provider().filename
    with open(path, "w") as file:
        file.write(csv_string)


def make_csv_string(
    event_descriptor_docs: list[DocumentType], event_docs: list[DocumentType]
) -> str:
    """
    Takes a list of RunEngine output docs and converts to CSV format

    Args:
        docs: A list of RunEngine docs

    Returms:
        A string of given list's csv equivalent
    """
    csv_dict = {"stream": []}
    headers = []
    streams = {}

    for doc in event_descriptor_docs:
        doc = cast(EventDescriptor, doc)
        headers = list(doc.get("data_keys"))
        headers.sort()
        for header in headers:
            csv_dict[header] = []
        headers.insert(0, "stream")
        streams[doc.get("uid")] = doc.get("name")

    for doc in event_docs:
        doc = cast(Event, doc)
        for header in doc["data"]:
            csv_dict[header].append(str(doc["data"][header]))
        csv_dict["stream"].append(streams[doc.get("descriptor")])

    csv_str = ",".join(headers) + "\n"

    csv_str += "\n".join(
        [
            ",".join(row)
            for row in zip(*[csv_dict[header] for header in headers], strict=True)
        ]
    )

    return csv_str


def csv_writer_subscription_builder(
    path_provider: PathProvider,
) -> tuple[Callable, Callable]:
    event_descriptor_docs = []
    event_docs = []

    def aggregate_event_descriptors(_, doc):
        event_descriptor_docs.append(doc)
        csv_string = make_csv_string(event_descriptor_docs, event_docs)

        write_csv(csv_string, path_provider)

    def aggregate_events(_, doc):
        event_docs.append(doc)
        csv_string = make_csv_string(event_descriptor_docs, event_docs)

        write_csv(csv_string, path_provider)

    return aggregate_event_descriptors, aggregate_events
