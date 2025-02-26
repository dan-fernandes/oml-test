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
    filename = filename or "oml-test-" + datetime.now().strftime(
        "%d-%m-%Y-%H-%M" + ".csv"
    )
    filename_provider = StaticFilenameProvider(filename)
    return StaticPathProvider(filename_provider, directory_path)


def write_csv(csv_string: str, path_provider: PathProvider) -> None:
    path = path_provider().directory_path / path_provider().filename
    with open(path, "w") as file:
        file.write(csv_string)


def make_csv_string(
    start_docs: list[DocumentType],
    event_descriptor_docs: list[DocumentType],
    event_docs: list[DocumentType],
    metadata: dict[str, str],
) -> str:
    """
    Takes a list of RunEngine output docs and converts to CSV format

    Args:
        docs: A list of RunEngine docs

    Returms:
        A string of given list's csv equivalent
    """
    start_time = None
    csv_dict = {"scan_index": [], "time": []}
    headers = []
    streams = {}

    for doc in start_docs:
        doc = cast(EventDescriptor, doc)
        start_time = start_time or doc["time"]

    for doc in event_descriptor_docs:
        doc = cast(EventDescriptor, doc)

        headers = list(doc.get("data_keys"))
        headers.sort()
        for header in headers:
            csv_dict[header] = []
        headers.insert(0, "scan_index")
        headers.insert(1, "time")
        streams[doc.get("uid")] = doc.get("name")

    start_time = start_time or 0.0

    for doc in event_docs:
        doc = cast(Event, doc)

        for header in doc["data"]:
            csv_dict[header].append(str(doc["data"][header]))
        csv_dict["scan_index"].append(streams[doc.get("descriptor")])
        csv_dict["time"].append(str(doc["time"] - start_time))

    csv_str = ""

    for name, value in metadata.items():
        csv_str += f"#{name} {value}\n"

    csv_str += ",".join(headers) + "\n"

    csv_str += "\n".join(
        [
            ",".join(row)
            for row in zip(*[csv_dict[header] for header in headers], strict=True)
        ]
    )

    return csv_str


def parse_metadata(metadata: dict[str, str], start_doc):
    if "voltage_increment" in start_doc.keys():
        metadata["voltage_increment"] = str(start_doc["voltage_increment"])

    if "dimension" in start_doc.keys():
        metadata["dimension"] = start_doc["dimension"].value

    if "slit_positions" in start_doc.keys():
        metadata["slit_positions"] = str(start_doc["slit_positions"])

    if "channels" in start_doc.keys():
        metadata["channels"] = str(start_doc["channels"])


def csv_writer_subscription_builder(
    path_provider: PathProvider,
) -> Callable:
    start_docs = []
    event_descriptor_docs = []
    event_docs = []
    metadata = {}

    def aggregate_docs(name, doc):
        if name == "descriptor":
            event_descriptor_docs.append(doc)
        elif name == "event":
            event_docs.append(doc)
        elif name == "start":
            parse_metadata(metadata, doc)
            start_docs.append(doc)
        csv_string = make_csv_string(
            start_docs, event_descriptor_docs, event_docs, metadata
        )

        write_csv(csv_string, path_provider)

    return aggregate_docs
