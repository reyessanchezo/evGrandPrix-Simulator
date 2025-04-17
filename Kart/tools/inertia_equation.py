import numpy as np

AIR_DENSITY = 1.2  # Air density (kg/m^3)
DRAG_COEFF = 0.8  # Drag Coefficient (unitless)
GRAV_ACCELLERATION = 9.8  # Gravity acceleration constant (m/s^2)
GEARING_RATIO = 1.0  # Gearing Ratio (Tire revolutions / Motor revolutions)
MASS = 100.0  # Kart mass (kg)
MAX_CROSSSECTIONAL_AREA = 0.5  # Maximum cross-sectional area (m^2)
TIRE_DIAMETER = 0.3  # Kart tire diameter (m)
TIRE_PRESSURE = 2.0  # Tire pressure (barr)
TRANSMISSION_EFFICIENCY = 0.9  # Need clarification!!!
ROLLING_RESISTANCE = 1.0  # Nm. Need clarification!!!


def rpm_to_rps(rpm):
    """Converting RPM to RPS"""
    return rpm / 60


def rpm_to_v(rpm):
    """Converting RPM to velocity"""
    return GEARING_RATIO * rpm_to_rps(rpm) * TIRE_DIAMETER * np.pi


def acceleration_torque(rpm, dvdt):
    """
    Calculates the acceleration torque given an rpm and a difference of speeds across time.

    Returns the torque in watts.

    Formula = 0.005 + (1/P) (0.01 + 0.0095 ((3.6) v / 100)^2)) m g + (1/2) C_d p A v^2 + m * (dv/dt) = (2 * T * n / Dt) (w_motor / w_wheel)
                    | First Term                                   | Second Term       | Third Term  |
    """
    v = rpm_to_v(rpm)
    first_term = (
        (
            (1 / TIRE_PRESSURE)
            * (0.01 + 0.0095 * (3.6 * v / 100) ** 2)
            * MASS
            * GRAV_ACCELLERATION
        )
        * MASS
        * GRAV_ACCELLERATION
    )
    second_term = 0.5 * DRAG_COEFF * MAX_CROSSSECTIONAL_AREA * AIR_DENSITY * (v**2)
    third_term = MASS * dvdt

    return 0.005 + first_term + second_term + third_term
