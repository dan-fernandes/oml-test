from bluesky.plans import count
from dodal.beamlines import optics_metrology_lab
from ophyd_async.core import init_devices

from oml_test.runengine import RE

with init_devices():
    mirror = optics_metrology_lab.mirror_one()
    slits = optics_metrology_lab.slits()
    detector = optics_metrology_lab.autocollimator()

RE(count((mirror, slits, detector)))
