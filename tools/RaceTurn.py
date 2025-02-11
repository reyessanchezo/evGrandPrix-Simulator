class RaceTurn:
    def __init__(self, turn=False, length=0, max_speed=-1):
        self.turn = turn
        self.length = length
        self.max_speed = max_speed
        if not turn:
            max_speed = -1