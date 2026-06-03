import math
import pygame
from constants import *

class Leg:
    def __init__(self, base_deg, body_ref, leg_id):
        self.base_angle = math.radians(base_deg)
        self.hip_angle = 0.0
        self.knee_angle = -0.5
        self.target_hip = 0.0
        self.target_knee = -0.5
        self.body = body_ref
        self.leg_id = leg_id
        self.knee_sign = -1 if leg_id < 2 else 1
        self.phase_offset = [0.0, 0.5, 0.0, 0.5][leg_id]
        self.lift_height = 0.0
        self.foot_target = None
        self.base_pos = (0, 0)
        self.hip_pos = (0, 0)
        self.foot_pos = (0, 0)

    def solve_ik(self, target_x, target_y):
        bx, by = self.base_pos
        dx = target_x - bx
        dy = target_y - by
        dist = math.hypot(dx, dy)
        if dist < 5:
            return
        angle_to_target = math.atan2(dy, dx)
        rel_angle = angle_to_target - (self.body.rotation + self.base_angle)
        clamped = max(-math.radians(HIP_RANGE), min(math.radians(HIP_RANGE), rel_angle))
        self.target_hip = clamped

        hip_global = self.body.rotation + self.base_angle + clamped
        hx = bx + math.cos(hip_global) * COXIA_L
        hy = by + math.sin(hip_global) * COXIA_L
        dx2 = target_x - hx
        dy2 = target_y - hy
        dist2 = math.hypot(dx2, dy2)
        if dist2 > LEG_SEG_LEN * 2 or dist2 < 1:
            return
        cos_knee = (LEG_SEG_LEN**2 + LEG_SEG_LEN**2 - dist2**2) / (2 * LEG_SEG_LEN * LEG_SEG_LEN)
        cos_knee = max(-1, min(1, cos_knee))
        self.target_knee = -math.acos(cos_knee) * self.knee_sign

    def update(self):
        self.hip_angle += (self.target_hip - self.hip_angle) * 0.5
        self.knee_angle += (self.target_knee - self.knee_angle) * 0.5

        bx, by = self.body.x, self.body.y
        rot = self.body.rotation
        ba = self.base_angle
        cx = bx + math.cos(rot + ba) * BODY_RADIUS
        cy = by + math.sin(rot + ba) * BODY_RADIUS
        self.base_pos = (cx, cy)

        hx = cx + math.cos(rot + ba + self.hip_angle) * COXIA_L
        hy = cy + math.sin(rot + ba + self.hip_angle) * COXIA_L
        self.hip_pos = (hx, hy)

        lift = self.lift_height if self.lift_height > 0 else 0
        effective_len = LEG_SEG_LEN * (1.0 - lift * 0.4)
        fx = hx + math.cos(rot + ba + self.hip_angle + self.knee_angle) * effective_len
        fy = hy + math.sin(rot + ba + self.hip_angle + self.knee_angle) * effective_len
        self.foot_pos = (fx, fy)

    def apply_gait(self, cycle_progress, speed_factor=1.0):
        phase = (cycle_progress + self.phase_offset) % 1.0
        spd = min(1.0, speed_factor)

        if phase < 0.5:
            t = phase / 0.5
            self.target_hip = math.radians(35 - 70 * t) * spd
            self.target_knee = math.radians(-60) * self.knee_sign
            self.lift_height = 0.0
        else:
            t = (phase - 0.5) / 0.5
            self.target_hip = math.radians(-35 + 70 * t) * spd
            lift_curve = math.sin(t * math.pi)
            self.target_knee = math.radians(-60 - 40 * lift_curve) * self.knee_sign
            self.lift_height = lift_curve

    def apply_jump_pose(self, jump_progress):
        if jump_progress < 0.25:
            self.target_hip = 0
            self.target_knee = math.radians(-70) * self.knee_sign
            self.lift_height = 0
        elif jump_progress < 0.45:
            self.target_hip = 0
            self.target_knee = math.radians(-120) * self.knee_sign
            self.lift_height = 1.0
        elif jump_progress < 0.7:
            t = (jump_progress - 0.45) / 0.25
            self.target_knee = math.radians(-120 + 60 * t) * self.knee_sign
            self.lift_height = 1.0 - t
        else:
            t = (jump_progress - 0.7) / 0.3
            self.target_knee = math.radians(-60 - 10 * t) * self.knee_sign
            self.lift_height = 0

    def apply_climb_pose(self, cycle_progress, slope_angle, speed_factor=0.6):
        phase = (cycle_progress + self.phase_offset) % 1.0
        spd = speed_factor

        climb_offset = math.sin(slope_angle) * 0.3
        if phase < 0.5:
            t = phase / 0.5
            self.target_hip = math.radians(30 - 60 * t) * spd
            self.target_knee = math.radians(-60) * self.knee_sign + climb_offset
            self.lift_height = 0.0
        else:
            t = (phase - 0.5) / 0.5
            self.target_hip = math.radians(-30 + 60 * t) * spd
            lift_curve = math.sin(t * math.pi)
            self.target_knee = math.radians(-60 - 40 * lift_curve) * self.knee_sign + climb_offset
            self.lift_height = lift_curve * 1.2

    def draw(self, screen, offset_x, offset_y, color=None):
        if color is None:
            color = (180, 160, 140)

        lift_color = tuple(min(255, c + 40) for c in color)
        foot_color = (200, 180, 100)

        def to_screen(px, py):
            return (int(px - offset_x + SCREEN_W//2), int(py - offset_y + SCREEN_H//2))

        b = to_screen(*self.base_pos)
        h = to_screen(*self.hip_pos)
        f = to_screen(*self.foot_pos)

        pygame.draw.line(screen, (100, 100, 100), b, h, 4)
        if self.lift_height > 0:
            pygame.draw.line(screen, lift_color, h, f, 3)
            pygame.draw.circle(screen, foot_color, f, 3)
            pygame.draw.line(screen, (255, 200, 0, 128), f,
                             (f[0] + int(self.lift_height * 20), f[1] + int(self.lift_height * 20)), 1)
        else:
            ground_color = color
            pygame.draw.line(screen, ground_color, h, f, 5)
            pygame.draw.circle(screen, (100, 100, 100), f, 4)

        pygame.draw.circle(screen, (120, 120, 120), h, 4)
