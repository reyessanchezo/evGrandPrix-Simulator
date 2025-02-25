import math
STATICFRICTION = 2.480847866
GRAV_ACCELLERATION = 9.8

class RaceTurn:
    def __init__(self, length, turn_radius=-1, max_speed = -1):
        self.length = abs(length)
        self.turn_radius = turn_radius
        if turn_radius > 0:
            self.calcMaxSpeed(turn_radius)
        
    def calcMaxSpeed(self, turn_radius):
        self.max_speed = math.sqrt(STATICFRICTION * GRAV_ACCELLERATION * turn_radius)

if __name__ == '__main__':
    TestTurn = RaceTurn(length=10, turn_radius = 7.62)
    print(TestTurn.max_speed)