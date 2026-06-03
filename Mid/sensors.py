import math
import pygame
from constants import *

class Lidar:
    def __init__(self, owner):
        self.owner = owner
        self.rays = []
        self.ray_hits = []
        self.distances = []

    def scan(self, obstacles):
        self.rays = []
        self.ray_hits = []
        self.distances = []

        ox, oy = self.owner.x, self.owner.y

        for i in range(LIDAR_RAYS):
            angle = self.owner.rotation + math.radians(i * 360.0 / LIDAR_RAYS)
            end_x = ox + math.cos(angle) * LIDAR_RANGE
            end_y = oy + math.sin(angle) * LIDAR_RANGE

            closest_dist = LIDAR_RANGE
            hit_x, hit_y = end_x, end_y

            for obs in obstacles:
                ex, ey, r = obs
                dx = ox - ex
                dy = oy - ey
                a = (end_x - ox)**2 + (end_y - oy)**2
                b = 2 * (dx * (end_x - ox) + dy * (end_y - oy))
                c = dx**2 + dy**2 - r**2
                disc = b*b - 4*a*c
                if disc >= 0:
                    t1 = (-b - math.sqrt(disc)) / (2*a) if a != 0 else -1
                    t2 = (-b + math.sqrt(disc)) / (2*a) if a != 0 else -1
                    for t in [t1, t2]:
                        if 0 <= t <= 1:
                            hx = ox + t * (end_x - ox)
                            hy = oy + t * (end_y - oy)
                            d = math.hypot(hx - ox, hy - oy)
                            if d < closest_dist:
                                closest_dist = d
                                hit_x, hit_y = hx, hy

            self.rays.append((ox, oy, hit_x, hit_y))
            self.ray_hits.append((hit_x, hit_y))
            self.distances.append(closest_dist)

        return self.distances

    def get_obstacle_direction(self):
        if not self.distances or len(self.distances) < LIDAR_RAYS:
            return 0, LIDAR_RANGE
        front_indices = []
        for i in range(LIDAR_RAYS):
            angle_deg = i * 360.0 / LIDAR_RAYS
            if angle_deg > 315 or angle_deg < 45:
                front_indices.append(i)
        if not front_indices:
            return 0, LIDAR_RANGE
        min_dist = LIDAR_RANGE
        min_i = front_indices[0]
        for i in front_indices:
            if i < len(self.distances) and self.distances[i] < min_dist:
                min_dist = self.distances[i]
                min_i = i
        angle = min_i * 360.0 / LIDAR_RAYS
        if angle > 180:
            angle -= 360
        return angle, min_dist

    def get_ground_height(self, world_x):
        noise = math.sin(world_x * 0.02) * 10 + math.sin(world_x * 0.05) * 5
        return noise

    def get_slope_at(self, world_x):
        return math.cos(world_x * 0.03) * 0.15

    def draw(self, screen, offset_x, offset_y, show_all=True):
        if not self.rays:
            return

        surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        for ray in self.rays:
            sx, sy, ex, ey = ray
            px1 = int(sx - offset_x + SCREEN_W // 2)
            py1 = int(sy - offset_y + SCREEN_H // 2)
            px2 = int(ex - offset_x + SCREEN_W // 2)
            py2 = int(ey - offset_y + SCREEN_H // 2)

            d = math.hypot(ex - sx, ey - sy)
            if d > LIDAR_RANGE * 0.8 and not show_all:
                continue

            if d < LIDAR_RANGE * 0.5:
                color = (0, 255, 200, 180)
            elif d < LIDAR_RANGE * 0.8:
                color = (0, 200, 200, 120)
            else:
                color = (0, 150, 200, 60)

            pygame.draw.line(surf, color, (px1, py1), (px2, py2), 1)

            if d < LIDAR_RANGE * 0.9:
                pygame.draw.circle(surf, (255, 100, 50, 200), (px2, py2), 3)

        screen.blit(surf, (0, 0))
