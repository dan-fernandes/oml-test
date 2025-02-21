import bluesky.plan_stubs as bps
from dodal.beamlines import optics_metrology_lab
from ophyd_async.core import init_devices

with init_devices():
    mirror = optics_metrology_lab.mirror_one()


def plan(mirror):
    voltage_increment = 200

    # get start position:
    original_voltage_list = []
    for channel in mirror.channels.values():
        position = yield from bps.rd(channel.output_voltage)
        original_voltage_list.append(position)

    # move to each bimorph position:
    for i, channel in enumerate(mirror.channels.values()):
        yield from bps.mv(channel, original_voltage_list[i] + voltage_increment)
        # sleep 10 seconds:
        bps.sleep(10)

    # return to start position:
    for value, channel in zip(
        original_voltage_list, mirror.channels.values(), strict=True
    ):
        yield from bps.mv(channel, value)  # type: ignore
