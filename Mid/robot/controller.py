import math
from .config import LEG_LAYOUT, LEG_ORDER, DEFAULT_BODY_HEIGHT, COXIA_L
from .leg import Leg
from .gait import TrotGait


class QuadrupedController:
    def __init__(self):
        self.body_x = 0.0
        self.body_y = 0.0
        self.body_z = DEFAULT_BODY_HEIGHT
        self.rotation = 0.0

        self.legs = {}
        for name, cfg in LEG_LAYOUT.items():
            px, py = cfg['pos']
            base = (px, py, 0)
            self.legs[name] = Leg(name, base, cfg['side_sign'])

        self.gait = TrotGait()
        self.speed = 0.0
        self.turn_rate = 0.0

    def set_speed(self, forward, turn=0.0):
        self.speed = max(-1.0, min(1.0, forward))
        self.turn_rate = max(-1.0, min(1.0, turn))

    def stand(self):
        body_z = self.body_z
        for name, leg in self.legs.items():
            bx, by, bz = leg.base_pos
            s = leg.side_sign
            foot_target = (bx, by + s * COXIA_L, -body_z)
            leg.ik(foot_target)

    def update(self, dt=1.0):
        if abs(self.speed) > 0.01:
            self.gait.update(self.speed, dt)
            self.body_x += math.cos(self.rotation) * self.speed * 0.5
            self.body_y += math.sin(self.rotation) * self.speed * 0.5
        else:
            self.gait.update(0, dt)

        body_z = self.body_z
        offsets = self.gait.get_all_offsets()

        for name, leg in self.legs.items():
            bx, by, bz = leg.base_pos
            s = leg.side_sign
            off = offsets.get(name, (0, 0, 0))
            foot_target = (bx + off[0], by + s * COXIA_L + off[1], -body_z + off[2])
            leg.ik(foot_target)

        if abs(self.turn_rate) > 0.01:
            self.rotation += self.turn_rate * 0.02

    def get_all_angles(self):
        result = {}
        for name in LEG_ORDER:
            if name in self.legs:
                result.update(self.legs[name].get_joint_angles())
        return result

    def get_leg_angles(self, leg_name):
        if leg_name in self.legs:
            return self.legs[leg_name].get_angles_deg()
        return (0, 0, 0)

    def print_angles(self):
        angles = self.get_all_angles()
        for name in sorted(angles.keys()):
            print(f"  {name}: {angles[name]:7.2f}")
