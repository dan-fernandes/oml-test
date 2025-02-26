import bluesky.plan_stubs as bps
from dodal.beamlines import optics_metrology_lab
from ophyd_async.core import init_devices

from oml_test.runengine import RE

with init_devices():
    mirror = optics_metrology_lab.mirror_one()


def check_valid_bimorph_state(
    voltage_list: list[float], abs_range: float, abs_diff: float
) -> bool:
    """Checks that a set of bimorph voltages is valid.
    Args:
        voltage_list: float amount each actuator will be increased by per scan
        abs_range: float absolute value of maximum possible voltage of each actuator
        abs_diff: float absolute maximum difference between two consecutive actuators

    Returns:
        Bool representing state validity
    """
    for voltage in voltage_list:
        if abs(voltage) > abs_range:
            return False

    for i in range(len(voltage_list) - 1):
        if abs(voltage_list[i] - voltage_list[i - 1]) > abs_diff:
            return False

    return True


def validate_bimorph_plan(
    initial_voltage_list: list[float],
    voltage_increment: float,
    abs_range: float,
    abs_diff: float,
) -> bool:
    """Checks that every position the bimorph will move through will not error.

    Args:
        initial_voltage_list: float list starting position
        voltage_increment: float amount each actuator will be increased by per scan
        abs_range: float absolute value of maximum possible voltage of each actuator
        abs_diff: float absolute maximum difference between two consecutive actuators

    Raises:
        Exception if the plan will lead to an error state"""
    voltage_list = initial_voltage_list.copy()

    if not check_valid_bimorph_state(voltage_list, abs_range, abs_diff):
        raise Exception(f"Bimorph plan reaches invalid state at: {voltage_list}")

    for i in range(len(initial_voltage_list)):
        voltage_list[i] += voltage_increment

        if not check_valid_bimorph_state(voltage_list, abs_range, abs_diff):
            raise Exception(f"Bimorph plan reaches invalid state at: {voltage_list}")

    return True


def plan(mirror):
    voltage_increment = 200

    # get start position:
    original_voltage_list = []

    for channel in mirror.channels.values():
        position = yield from bps.rd(channel.output_voltage)
        original_voltage_list.append(position)

    current_voltage_list = original_voltage_list.copy()

    validate_bimorph_plan(original_voltage_list, voltage_increment, 1000, 500)

    # move to each bimorph position:
    for i in range(len(mirror.channels)):
        current_voltage_list[i] += voltage_increment
        yield from bps.mv(mirror, current_voltage_list
        )
        # sleep 10 seconds:
        print("Sleeping...")
        yield from bps.sleep(10)
        print(
            f"In position {[voltage + (voltage_increment * (j <= i)) for j, voltage in enumerate(original_voltage_list)]}"  # noqa: E501
        )

    # return to start position:
    yield from bps.mv(mirror, original_voltage_list)


RE(plan(mirror))
