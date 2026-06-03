import math
from .config import COXIA_L, FEMUR_L, TIBIA_L, JOINT_LIMITS


def _coxia_dir(angle_rad, side_sign):
    if side_sign > 0:
        return (math.sin(angle_rad), math.cos(angle_rad))
    return (math.sin(angle_rad), -math.cos(angle_rad))


class Leg:
    def __init__(self, name, base_pos, side_sign):
        self.name = name
        self.base_pos = base_pos
        self.side_sign = side_sign
        self.coxia = 0.0
        self.femur = 0.0
        self.tibia = 0.0
        self.foot_pos = (0.0, 0.0, 0.0)
        self.target_foot = None

    def clamp(self):
        lo, hi = JOINT_LIMITS['coxia']
        self.coxia = max(lo, min(hi, self.coxia))
        lo, hi = JOINT_LIMITS['femur']
        self.femur = max(lo, min(hi, self.femur))
        lo, hi = JOINT_LIMITS['tibia']
        self.tibia = max(lo, min(hi, self.tibia))

    def ik(self, target_pos):
        bx, by, bz = self.base_pos
        tx, ty, tz = target_pos
        dx = tx - bx
        dy = ty - by
        dz = tz - bz

        hip_xy = math.hypot(dx, dy)
        if hip_xy < 0.5:
            self.coxia = 0.0
        else:
            self.coxia = math.degrees(math.atan2(dx, dy * self.side_sign))
        self.clamp()

        rad_c = math.radians(self.coxia)
        cdir = _coxia_dir(rad_c, self.side_sign)
        hx = bx + cdir[0] * COXIA_L
        hy = by + cdir[1] * COXIA_L
        hz = bz

        dx2 = tx - hx
        dy2 = ty - hy
        dz2 = tz - hz
        reach = dx2 * cdir[0] + dy2 * cdir[1]
        h_dist = -dz2

        if abs(reach) < 0.5 and abs(h_dist) < 0.5:
            self.foot_pos = target_pos
            self.target_foot = target_pos
            return

        L1, L2 = FEMUR_L, TIBIA_L
        x = abs(reach)
        y = -h_dist
        d_sq = x * x + y * y
        d = math.sqrt(d_sq)

        if d > L1 + L2 - 1 or d < abs(L1 - L2) + 1:
            return

        cos_t2 = (d_sq - L1 * L1 - L2 * L2) / (2 * L1 * L2)
        cos_t2 = max(-1, min(1, cos_t2))
        sin_t2 = -math.sqrt(1 - cos_t2 * cos_t2)
        theta2 = math.atan2(sin_t2, cos_t2)
        self.tibia = math.degrees(theta2)

        k1 = L1 + L2 * cos_t2
        k2 = L2 * sin_t2
        theta1 = math.atan2(y, x) - math.atan2(k2, k1)
        self.femur = math.degrees(theta1)

        self.clamp()
        self.foot_pos = target_pos
        self.target_foot = target_pos

    def get_hip_pos(self):
        bx, by, bz = self.base_pos
        rad_c = math.radians(self.coxia)
        cdir = _coxia_dir(rad_c, self.side_sign)
        return (bx + cdir[0] * COXIA_L, by + cdir[1] * COXIA_L, bz)

    def get_foot_pos(self):
        rad_c = math.radians(self.coxia)
        rad_f = math.radians(self.femur)
        rad_t = math.radians(self.tibia)
        bx, by, bz = self.base_pos
        cdir = _coxia_dir(rad_c, self.side_sign)

        hx = bx + cdir[0] * COXIA_L
        hy = by + cdir[1] * COXIA_L
        hz = bz

        total = rad_f + rad_t
        cos_f = math.cos(rad_f)
        cos_t = math.cos(total)
        sin_f = math.sin(rad_f)
        sin_t = math.sin(total)

        fx = hx + cdir[0] * (FEMUR_L * cos_f + TIBIA_L * cos_t)
        fy = hy + cdir[1] * (FEMUR_L * cos_f + TIBIA_L * cos_t)
        fz = hz + FEMUR_L * sin_f + TIBIA_L * sin_t

        return (fx, fy, fz)

    def get_joint_angles(self):
        return {
            f'{self.name}_coxia': round(self.coxia, 1),
            f'{self.name}_femur': round(self.femur, 1),
            f'{self.name}_tibia': round(self.tibia, 1),
        }

    def get_angles_deg(self):
        return self.coxia, self.femur, self.tibia
