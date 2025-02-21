import bluesky.plan_stubs as bps
from dodal.beamlines import optics_metrology_lab
from dodal.plans.bimorph import SlitDimension, move_slits
from numpy import linspace
from ophyd_async.core import init_devices

from oml_test.runengine import RE

with init_devices():
    slits = optics_metrology_lab.slits()


def plan(slits):
    slits_start_gap = yield from bps.rd(slits.x_gap)
    slits_start_centre = yield from bps.rd(slits.x_centre)

    for value in linspace(0.0, 100.0, 200):
        yield from move_slits(slits, SlitDimension.X, 0.25, value)

    yield from move_slits(slits, SlitDimension.X, slits_start_gap, slits_start_centre)


RE(plan(slits))
