import math
import pygame
from constants import *

class Projectile:
    def __init__(self, x, y, angle, speed, friendly=True):
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.radius = 6
        self.friendly = friendly
        self.alive = True
        self.trail = []
        self.damage = 30
        self.world_size = 1200

    def update(self):
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 12:
            self.trail.pop(0)
        self.x += self.vx
        self.y += self.vy
        margin = 200
        ws = self.world_size
        if (self.x < -ws or self.x > ws or
                self.y < -ws or self.y > ws):
            self.alive = False

    def draw(self, screen, offset_x, offset_y):
        ox = int(self.x - offset_x + SCREEN_W // 2)
        oy = int(self.y - offset_y + SCREEN_H // 2)

        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(200 * i / len(self.trail))
            r = int(self.radius * 0.3 * i / len(self.trail))
            px = int(tx - offset_x + SCREEN_W // 2)
            py = int(ty - offset_y + SCREEN_H // 2)
            pygame.draw.circle(screen, (255, 200, 50, alpha), (px, py), max(1, r))

        color = (255, 220, 50) if self.friendly else (255, 50, 50)
        pygame.draw.circle(screen, (255, 255, 200), (ox, oy), self.radius)
        pygame.draw.circle(screen, color, (ox, oy), self.radius - 1)
        pygame.draw.circle(screen, (255, 255, 255), (ox, oy), self.radius // 2)

class AutoLoader:
    def __init__(self):
        self.shells_in_mag = MAG_SIZE
        self.current_shell = None
        self.loading_progress = 0.0
        self.is_loading = False
        self.is_reloading_mag = False
        self.reload_progress = 0.0
        self.state = "idle"
        self.total_rounds_fired = 0

    def update(self):
        if self.state == "loading":
            self.loading_progress += 1.0 / AUTO_LOAD_TICKS
            if self.loading_progress >= 1.0:
                self.current_shell = True
                self.loading_progress = 0.0
                self.is_loading = False
                self.state = "ready"
        elif self.state == "reloading":
            self.reload_progress += 1.0 / MAG_RELOAD_TICKS
            if self.reload_progress >= 1.0:
                self.shells_in_mag = MAG_SIZE
                self.reload_progress = 0.0
                self.is_reloading_mag = False
                self.state = "idle"

    def request_fire(self):
        if self.state == "ready" and self.current_shell:
            self.current_shell = None
            self.total_rounds_fired += 1
            self.state = "idle"
            self.start_loading()
            return True
        return False

    def start_loading(self):
        if self.state != "loading" and self.shells_in_mag > 0:
            self.shells_in_mag -= 1
            self.is_loading = True
            self.loading_progress = 0.0
            self.state = "loading"

    def start_reload(self):
        if self.shells_in_mag < MAG_SIZE and not self.is_reloading_mag:
            self.is_reloading_mag = True
            self.reload_progress = 0.0
            self.state = "reloading"

class Cannon:
    def __init__(self, owner):
        self.owner = owner
        self.angle = 0.0
        self.target_angle = 0.0
        self.loader = AutoLoader()
        self.loader.start_loading()
        self.fire_cooldown = 0
        self.projectiles = []
        self.firing = False
        self.fire_anim = 0.0

    def aim_at(self, world_x, world_y):
        dx = world_x - self.owner.x
        dy = world_y - self.owner.y
        if dx != 0 or dy != 0:
            raw = math.atan2(dy, dx) - self.owner.rotation
            while raw > math.pi:
                raw -= 2 * math.pi
            while raw < -math.pi:
                raw += 2 * math.pi
            self.target_angle = raw

    def update(self):
        da = self.target_angle - self.angle
        while da > math.pi:
            da -= 2 * math.pi
        while da < -math.pi:
            da += 2 * math.pi
        self.angle += da * 0.2

        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1

        self.loader.update()

        if self.fire_anim > 0:
            self.fire_anim -= 0.05

        for p in self.projectiles[:]:
            p.update()
            if not p.alive:
                self.projectiles.remove(p)

    def fire(self):
        if self.fire_cooldown > 0:
            return False
        if not self.loader.request_fire():
            return False
        self.fire_cooldown = FIRE_COOLDOWN_TICKS
        self.fire_anim = 1.0

        cx = self.owner.x + math.cos(self.owner.rotation + self.angle) * CANNON_LEN
        cy = self.owner.y + math.sin(self.owner.rotation + self.angle) * CANNON_LEN

        p = Projectile(cx, cy, self.owner.rotation + self.angle, PROJ_SPEED)
        p.vx += self.owner.vx * 0.5
        p.vy += self.owner.vy * 0.5
        self.projectiles.append(p)
        return True

    def reload_magazine(self):
        self.loader.start_reload()

    def draw(self, screen, offset_x, offset_y):
        ox = int(self.owner.x - offset_x + SCREEN_W // 2)
        oy = int(self.owner.y - offset_y + SCREEN_H // 2)
        rot = self.owner.rotation

        # Barrel
        barrel_len = CANNON_LEN
        bx = ox + math.cos(rot + self.angle) * barrel_len
        by = oy + math.sin(rot + self.angle) * barrel_len

        # Barrel body
        perp_angle = rot + self.angle + math.pi / 2
        perp_x = math.cos(perp_angle) * CANNON_W
        perp_y = math.sin(perp_angle) * CANNON_W

        barrel_points = [
            (ox + perp_x, oy + perp_y),
            (bx + perp_x, by + perp_y),
            (bx - perp_x, by - perp_y),
            (ox - perp_x, oy - perp_y),
        ]
        barrel_points = [(int(px), int(py)) for px, py in barrel_points]
        pygame.draw.polygon(screen, (80, 80, 90), barrel_points)
        pygame.draw.polygon(screen, (60, 60, 70), barrel_points, 2)

        # Breech
        breech_len = 15
        bbx = ox - math.cos(rot + self.angle) * breech_len
        bby = oy - math.sin(rot + self.angle) * breech_len
        bp = perp_x * 1.3, perp_y * 1.3
        breech_pts = [
            (ox + bp[0], oy + bp[1]),
            (bbx + bp[0], bby + bp[1]),
            (bbx - bp[0], bby - bp[1]),
            (ox - bp[0], oy - bp[1]),
        ]
        breech_pts = [(int(px), int(py)) for px, py in breech_pts]
        pygame.draw.polygon(screen, (70, 70, 80), breech_pts)
        pygame.draw.polygon(screen, (50, 50, 60), breech_pts, 2)

        # Muzzle flash
        if self.fire_anim > 0:
            flash_len = 20 + int(self.fire_anim * 30)
            flash_w = 12 + int(self.fire_anim * 10)
            fx = ox + math.cos(rot + self.angle) * (barrel_len + 5)
            fy = oy + math.sin(rot + self.angle) * (barrel_len + 5)
            fpx = math.cos(perp_angle) * flash_w
            fpy = math.sin(perp_angle) * flash_w

            flash_pts = [
                (fx + fpx, fy + fpy),
                (fx + math.cos(rot + self.angle) * flash_len + fpx * 0.3,
                 fy + math.sin(rot + self.angle) * flash_len + fpy * 0.3),
                (fx - fpx, fy - fpy),
            ]
            flash_pts = [(int(px), int(py)) for px, py in flash_pts]
            pygame.draw.polygon(screen, (255, 255, 200), flash_pts)
            pygame.draw.polygon(screen, (255, 200, 50), flash_pts, 2)

            glow_r = 25 + int(self.fire_anim * 20)
            glow = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            for i in range(5):
                r = glow_r - i * 4
                a = int(80 * (1 - i / 5) * self.fire_anim)
                pygame.draw.circle(glow, (255, 200, 50, a), (glow_r, glow_r), r)
            screen.blit(glow, (fx - glow_r - offset_x + SCREEN_W // 2,
                               fy - glow_r - offset_y + SCREEN_H // 2),
                        special_flags=pygame.BLEND_ALPHA_SDL2)

        # Shell in chamber indicator
        if self.loader.current_shell:
            shell_x = ox - math.cos(rot + self.angle) * 8
            shell_y = oy - math.sin(rot + self.angle) * 8
            pygame.draw.circle(screen, (220, 180, 50), (int(shell_x), int(shell_y)), 4)

        for p in self.projectiles:
            p.draw(screen, offset_x, offset_y)
