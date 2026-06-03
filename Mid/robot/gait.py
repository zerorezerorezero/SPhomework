import math
from .config import STEP_LENGTH, STEP_HEIGHT, DEFAULT_BODY_HEIGHT, TROT_PAIRS


class TrotGait:
    def __init__(self):
        self.cycle = 0.0
        self.speed = 0.0

    def reset(self):
        self.cycle = 0.0
        self.speed = 0.0

    def update(self, speed, dt=1.0):
        self.speed = speed
        self.cycle = (self.cycle + speed * 0.02 * dt) % 1.0

    def get_phase(self, leg_name):
        if leg_name in TROT_PAIRS[0]:
            return self.cycle
        else:
            return (self.cycle + 0.5) % 1.0

    def get_foot_offset(self, leg_name):
        phase = self.get_phase(leg_name)

        if phase < 0.5:
            t = phase / 0.5
            ox = STEP_LENGTH * 0.5 * (1 - 2 * t)
            oy = 0.0
            oz = 0.0
        else:
            t = (phase - 0.5) / 0.5
            ox = STEP_LENGTH * 0.5 * (2 * t - 1)
            oy = 0.0
            lift = math.sin(t * math.pi)
            oz = -STEP_HEIGHT * lift

        return (ox, oy, oz)

    def is_swing(self, leg_name):
        return self.get_phase(leg_name) >= 0.5

    def get_all_offsets(self):
        offsets = {}
        for pair in TROT_PAIRS:
            for leg in pair:
                offsets[leg] = self.get_foot_offset(leg)
        return offsets
