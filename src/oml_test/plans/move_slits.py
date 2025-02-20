from bluesky.plans import scan
from dodal.beamlines import optics_metrology_lab
from ophyd_async.core import init_devices

from oml_test.runengine import RE

with init_devices():
    slits = optics_metrology_lab.slits()


RE(scan(slits, 0.0, 1.0))
