import bluesky.plan_stubs as bps
from dodal.beamlines import optics_metrology_lab
from dodal.plans.bimorph import bimorph_optimisation
from ophyd_async.core import init_devices

from oml_test.runengine import RE
import oml_test.bimorph_config

with init_devices():
    mirror = optics_metrology_lab.mirror_one()
    slits = optics_metrology_lab.slits()
    autocollimator = optics_metrology_lab.autocollimator()


RE(bimorph_optimisation((autocollimator,), mirror, slits, *oml_test.bimorph_config.config))
