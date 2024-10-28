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
    DYNO_POWER_OUT = ((1 / 12) * (C * (wm / 60) * math.pi * D) * (0.5 * CD * A * RHO * (C * (wm / 60) * math.pi * D) ** 2)) * 1.355818
    return DYNO_POWER_OUT