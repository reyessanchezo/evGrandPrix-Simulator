import numpy as np
import math

DYNO_POWER_OUT = 0 #output
RPM = 4500  # kart motor rpm
CD = 0.6  # drag coefficient
RHO = 1.376E-6  # air density (slug/in^3)
C = 10 / 55  # gear ratio from motor to tire
D = 8  # tire diameter (in)
A = 700  # max cross-sectional area of kart (in^2) ~ about 24 * 32

def aerodynamic_drag_power(wm):
    over12 = np.divide(1, 12)
    rps = np.divide(wm, 60)
    part1 = np.multiply(np.multiply(np.multiply(C, rps), math.pi), D)
    section1 = np.multiply(part1,  over12)
    section2 = np.multiply(np.multiply(np.multiply(np.multiply(np.multiply(0.5, CD), A), RHO), np.power(part1, 2)), 1.355818)

    DYNO_POWER_OUT = np.multiply(section1, section2)
    return DYNO_POWER_OUT
