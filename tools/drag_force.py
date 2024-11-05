import math

import numpy as np

# use metric units
# DYNO_POWER_OUT = 0  # output (W)
# RPM = 4500  # kart motor rpm

CD = 0.8  # drag coefficient
RHO = 1.225  # air density (kg/m^3)
G = 13 / 55  # gear ratio from motor to tire
D = 0.254  # tire diameter (m)
A = 0.495483  # max cross-sectional area of kart (m^2) ~ about 24in * 32in

def aerodynamic_drag_power(wm):
    wm /= 3  # ERPM to actual RPM
    rps = np.divide(wm, 60)
    velocity = np.multiply(
        np.multiply(np.multiply(G, rps), np.pi), D
    )  # velocity of the kart in m/s
    velocity3 = np.power(velocity, 3)
    section1 = np.multiply(np.multiply(np.multiply(0.5, CD), A), RHO)

    DYNO_POWER_OUT = np.multiply(
        section1, velocity3
    )  # Drag power = 0.5 * CD * A * RHO * (kart velocity)^3
    return DYNO_POWER_OUT / 2
