import pathlib

from bluesky.run_engine import RunEngine

from oml_test import csv_writer

RE = RunEngine()

dir = pathlib.Path("/tmp/")

path_provider = csv_writer.get_static_path_provider(dir)

sub = csv_writer.csv_writer_subscription_builder(path_provider)

RE.subscribe(sub)
