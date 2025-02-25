from dodal.beamlines import optics_metrology_lab
from ophyd_async.core import init_devices

from oml_test.runengine import RE

with init_devices():
    autocollimator = optics_metrology_lab.autocollimator()


def plan(autocollimator):
    raise NotImplementedError()


RE(plan(autocollimator))
