import pathlib

from bluesky.plans import count
from bluesky.run_engine import RunEngine
from dodal.beamlines import optics_metrology_lab
from ophyd_async.core import init_devices

from oml_test import csv_writer

RE = RunEngine()

with init_devices():
    mirror = optics_metrology_lab.mirror_one()
    slits = optics_metrology_lab.slits()
    detector = optics_metrology_lab.autocollimator()


dir = pathlib.Path("/tmp/")

path_provider = csv_writer.get_static_path_provider(dir)

sub = csv_writer.csv_writer_subscription_builder(path_provider)

RE.subscribe(sub)

RE(count((mirror, slits, detector)))
