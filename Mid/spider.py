import math
import random
import pygame
from constants import *
from leg import Leg

class Spider:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.rotation = 0.0
        self.target_fwd = 0
        self.target_strafe = 0
        self.target_rotation = 0.0
        self.terrain_factor = 1.0

        self.legs = []
        for i, deg in enumerate(LEG_BASE_DEG):
            self.legs.append(Leg(deg, self, i))
        for leg in self.legs:
            leg.target_knee = math.radians(-70) * leg.knee_sign

        self.gait_cycle = 0.0
        self.is_jumping = False
        self.jump_progress = 0.0
        self.jump_cooldown = 0
        self.body_bob = 0.0
        self.body_height = 0.0
        self.target_body_height = 0.0

        self.current_terrain = TERRAIN_TYPES[0]
        self.on_slope = False
        self.slope_angle = 0.0
        self.is_autopilot = False
        self.autopilot_target = None
        self.autopilot_timer = 0

        self.lidar = None
        self.cannon = None

    def attach_lidar(self, lidar):
        self.lidar = lidar

    def attach_cannon(self, cannon):
        self.cannon = cannon

    def set_move(self, forward, strafe, rotate):
        if not self.is_jumping:
            self.target_fwd = forward * MAX_SPEED
            self.target_strafe = strafe * MAX_SPEED
            self.target_rotation = self.rotation + rotate * 0.05

    def start_jump(self):
        if not self.is_jumping and self.jump_cooldown <= 0:
            self.is_jumping = True
            self.jump_progress = 0.0
            self.body_bob = 0

    def find_best_foothold(self, foot_x, foot_y, obstacles):
        if not obstacles:
            return foot_x, foot_y

        for obs in obstacles:
            dx = foot_x - obs.x
            dy = foot_y - obs.y
            dist = math.hypot(dx, dy)
            if dist < obs.radius + 8:
                angle = math.atan2(dy, dx)
                new_dist = obs.radius + 12
                foot_x = obs.x + math.cos(angle) * new_dist
                foot_y = obs.y + math.sin(angle) * new_dist
        return foot_x, foot_y

    def update(self, obstacles, terrain_tiles):
        prev_x, prev_y = self.x, self.y

        if self.is_autopilot:
            self._update_autopilot(obstacles)

        # Terrain detection (must run before velocity calc)
        self.terrain_factor = 1.0
        self.on_slope = False
        self.slope_angle = 0
        for tile in terrain_tiles:
            if tile.rect.collidepoint(self.x, self.y):
                self.current_terrain = tile.terrain_type
                self.terrain_factor = tile.terrain_type["speed_factor"]
                if tile.terrain_type["name"] == "斜坡":
                    self.on_slope = True
                    self.slope_angle = 0.15
                break

        if self.is_jumping:
            self.jump_progress += 1.0 / JUMP_FRAMES
            if self.jump_progress >= 1.0:
                self.is_jumping = False
                self.jump_cooldown = 15
                self.body_height = 0

            jump_phase = self.jump_progress
            jh = math.sin(jump_phase * math.pi) * 1.5
            self.body_height = jh
            self.target_body_height = jh

            for leg in self.legs:
                leg.apply_jump_pose(jump_phase)

            if jump_phase >= 0.45 and jump_phase <= 0.7:
                t = (jump_phase - 0.45) / 0.25
                power = math.sin(t * math.pi) * JUMP_POWER
                self.vx += math.cos(self.rotation) * power * 0.03
                self.vy += math.sin(self.rotation) * power * 0.03
        else:
            self.body_height += (self.target_body_height - self.body_height) * 0.15

            fwd_speed = abs(self.target_fwd)
            if fwd_speed > 0.1:
                self.gait_cycle += fwd_speed * 0.015
                if self.on_slope:
                    for leg in self.legs:
                        leg.apply_climb_pose(self.gait_cycle, self.slope_angle, 0.6)
                else:
                    for leg in self.legs:
                        leg.apply_gait(self.gait_cycle, fwd_speed / MAX_SPEED)
            else:
                for leg in self.legs:
                    leg.apply_gait(self.gait_cycle, 0.0)

        self.rotation += (self.target_rotation - self.rotation) * 0.2

        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1

        fwd_v = self.target_fwd * self.terrain_factor
        strafe_v = self.target_strafe * self.terrain_factor
        target_vx = fwd_v * math.cos(self.rotation) - strafe_v * math.sin(self.rotation)
        target_vy = fwd_v * math.sin(self.rotation) + strafe_v * math.cos(self.rotation)

        self.vx += (target_vx - self.vx) * 0.15
        self.vy += (target_vy - self.vy) * 0.15

        self.x += self.vx
        self.y += self.vy

        speed = math.hypot(self.vx, self.vy)

        # Foothold optimization
        for leg in self.legs:
            if speed > 0.5:
                fx, fy = leg.foot_pos
                nfx, nfy = self.find_best_foothold(fx, fy, obstacles)
                if abs(nfx - fx) > 1 or abs(nfy - fy) > 1:
                    leg.solve_ik(nfx, nfy)

        # Obstacle collision
        for obs in obstacles:
            if obs.collides_with(self.x, self.y, BODY_RADIUS):
                dx = self.x - obs.x
                dy = self.y - obs.y
                dist = math.hypot(dx, dy)
                if dist < 1:
                    dist = 1
                overlap = obs.radius + BODY_RADIUS - dist
                self.x += dx / dist * overlap
                self.y += dy / dist * overlap

        for leg in self.legs:
            leg.update()

        return self.x - prev_x, self.y - prev_y

    def _update_autopilot(self, obstacles):
        self.autopilot_timer -= 1
        if self.autopilot_timer <= 0 or self.autopilot_target is None:
            rx = random.uniform(-600, 600)
            ry = random.uniform(-600, 600)
            self.autopilot_target = (rx, ry)
            self.autopilot_timer = 180 + random.randint(0, 120)

        tx, ty = self.autopilot_target
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)

        if dist < 30:
            self.autopilot_timer = 0
            return

        target_rot = math.atan2(dy, dx)
        dr = target_rot - self.rotation
        while dr > math.pi:
            dr -= 2 * math.pi
        while dr < -math.pi:
            dr += 2 * math.pi

        self.target_rotation = self.rotation + dr * 0.1

        if self.lidar and self.lidar.distances:
            obs_angle, obs_dist = self.lidar.get_obstacle_direction()
            if obs_dist < 150:
                avoid_turn = math.radians(obs_angle * 0.5)
                self.target_rotation += avoid_turn
                if obs_dist < 80 and not self.is_jumping and self.jump_cooldown <= 0:
                    self.start_jump()
                self.target_fwd = MAX_SPEED * 0.5
            else:
                self.target_fwd = MAX_SPEED * (0.7 + 0.3 * min(1.0, dist / 400))
            self.target_strafe = 0
        else:
            self.target_fwd = MAX_SPEED * min(1.0, dist / 300)
            self.target_strafe = 0

    def draw(self, screen, offset_x, offset_y):
        ox = int(self.x - offset_x + SCREEN_W // 2)
        oy = int(self.y - offset_y + SCREEN_H // 2)
        body_scale = 1.0 + self.body_height * 0.08

        # Shadow
        shadow_r = int(BODY_RADIUS * body_scale * 1.4)
        shadow_alpha = max(30, 80 - int(self.body_height * 30))
        shadow = pygame.Surface((shadow_r * 2, shadow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(shadow, (0, 0, 0, shadow_alpha), (shadow_r, shadow_r), shadow_r)
        screen.blit(shadow, (ox - shadow_r, oy - shadow_r + 8), special_flags=pygame.BLEND_ALPHA_SDL2)

        # Legs
        for leg in self.legs:
            leg.draw(screen, offset_x, offset_y)

        # Body
        body_color = (60 + int(self.body_height * 20),
                      65 + int(self.body_height * 15),
                      75 + int(self.body_height * 10))
        br = BODY_RADIUS * body_scale
        body_len = int(br * 1.6)
        body_wid = int(br * 0.9)

        # Elliptical body oriented with rotation
        body_surf = pygame.Surface((body_len * 2 + 4, body_wid * 2 + 4), pygame.SRCALPHA)
        rect = pygame.Rect(2, 2, body_len * 2, body_wid * 2)
        pygame.draw.ellipse(body_surf, body_color, rect)
        pygame.draw.ellipse(body_surf, (120, 130, 140), rect, 2)

        inner_rect = pygame.Rect(2 + body_len * 0.3, 2 + body_wid * 0.3,
                                 body_len * 1.4, body_wid * 1.4)
        pygame.draw.ellipse(body_surf, (90, 100, 110), inner_rect)

        rotated = pygame.transform.rotate(body_surf, -math.degrees(self.rotation))
        screen.blit(rotated, (ox - rotated.get_width() // 2, oy - rotated.get_height() // 2))

        # Eye / sensor
        eye_x = ox + math.cos(self.rotation) * br * 0.3
        eye_y = oy + math.sin(self.rotation) * br * 0.3
        pygame.draw.circle(screen, (0, 200, 255), (int(eye_x), int(eye_y)), 5)
        pygame.draw.circle(screen, (255, 255, 255), (int(eye_x), int(eye_y)), 3)

        # Cannon
        if self.cannon:
            self.cannon.draw(screen, offset_x, offset_y)
