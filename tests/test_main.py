import pathlib
from collections.abc import Callable

import pytest
from bluesky.run_engine import RunEngine
from dodal.beamlines import optics_metrology_lab
from dodal.plans.bimorph import bimorph_optimisation
from ophyd_async.core import init_devices
from ophyd_async.testing import set_mock_value

from oml_test import bimorph_config, csv_writer

RE = RunEngine()


@pytest.fixture
def mirror():
    with init_devices(mock=True):
        mirror = optics_metrology_lab.mirror_one()
    return mirror


@pytest.fixture
def slits():
    with init_devices(mock=True):
        slits = optics_metrology_lab.slits()
    set_mock_value(slits.x_centre.velocity, 1)
    return slits


@pytest.fixture
def detector():
    with init_devices(mock=True):
        detector = optics_metrology_lab.autocollimator()
    return detector


@pytest.fixture
def csv_writer_subscriptions(tmp_path: pathlib.Path) -> tuple[Callable, Callable]:
    dir = pathlib.Path(tmp_path)

    path_provider = csv_writer.get_static_path_provider(dir)

    return csv_writer.csv_writer_subscription_builder(path_provider)


def test_1(tmp_path, csv_writer_subscriptions, detector, mirror, slits):
    RE(
        bimorph_optimisation(
            [detector],
            mirror,
            slits,  # type: ignore
            *bimorph_config.config,
        ),
        {
            "descriptor": csv_writer_subscriptions[0],
            "event": csv_writer_subscriptions[1],
        },
    )

    with open(tmp_path / "oml-test") as csv_file:
        csv_string = csv_file.read()

    assert csv_string != ""


def test_2(): ...
