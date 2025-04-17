import math
STATICFRICTION = 2.480847866
GRAVACCELLERATIONCONST = 9.8  ##m/s^2


class RaceTrack:
    def __init__(self, track_length, track_turn_radius=-1, max_speed=-1):
        self.track_length = abs(track_length)
        self.track_turn_radius = track_turn_radius
        self.max_speed = max_speed
        if track_turn_radius != -1:
            self.max_speed = math.sqrt(STATICFRICTION * GRAVACCELLERATIONCONST * track_turn_radius)
            
