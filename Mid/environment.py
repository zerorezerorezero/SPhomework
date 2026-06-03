import math
import random
import pygame
from constants import *

class TerrainTile:
    def __init__(self, x, y, width, height, terrain_type):
        self.rect = pygame.Rect(x, y, width, height)
        self.terrain_type = terrain_type
        self.color = terrain_type["color"]
        self.height_variation = random.uniform(-3, 3)

    def draw(self, screen, offset_x, offset_y):
        sx = self.rect.x - offset_x + SCREEN_W // 2
        sy = self.rect.y - offset_y + SCREEN_H // 2
        if sx + self.rect.width < -50 or sx > SCREEN_W + 50:
            return
        if sy + self.rect.height < -50 or sy > SCREEN_H + 50:
            return

        r = pygame.Rect(int(sx), int(sy), self.rect.width, self.rect.height)
        c = self.color
        pygame.draw.rect(screen, c, r)
        pygame.draw.rect(screen, tuple(min(255, x + 20) for x in c), r, 1)

class Obstacle:
    def __init__(self, x, y, radius, height=1.0):
        self.x = x
        self.y = y
        self.radius = radius
        self.height = height
        self.color = (100 + random.randint(0, 40),
                      80 + random.randint(0, 30),
                      60 + random.randint(0, 20))

    def get_circle(self):
        return (self.x, self.y, self.radius)

    def collides_with(self, px, py, pr=10):
        dx = px - self.x
        dy = py - self.y
        return math.hypot(dx, dy) < self.radius + pr

    def draw(self, screen, offset_x, offset_y):
        sx = int(self.x - offset_x + SCREEN_W // 2)
        sy = int(self.y - offset_y + SCREEN_H // 2)

        if sx < -100 or sx > SCREEN_W + 100 or sy < -100 or sy > SCREEN_H + 100:
            return

        # Shadow
        shadow_off = 5 + int(self.height * 5)
        pygame.draw.circle(screen, (40, 40, 30, 80), (sx + shadow_off, sy + shadow_off),
                          int(self.radius * 0.9))

        # Main body
        c = self.color
        pygame.draw.circle(screen, c, (sx, sy), self.radius)
        pygame.draw.circle(screen, tuple(min(255, x + 30) for x in c), (sx, sy), self.radius, 2)

        # Height highlight
        if self.height > 0.5:
            highlight_r = int(self.radius * 0.6)
            highlight = pygame.Surface((highlight_r * 2, highlight_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(highlight, (255, 255, 200, 30), (highlight_r, highlight_r), highlight_r)
            screen.blit(highlight, (sx - highlight_r, sy - highlight_r), special_flags=pygame.BLEND_ALPHA_SDL2)

def generate_obstacles(world_size, count=OBSTACLE_COUNT, exclude_center_radius=100):
    obstacles = []
    for _ in range(count):
        for attempt in range(20):
            x = random.uniform(-world_size, world_size)
            y = random.uniform(-world_size, world_size)
            if math.hypot(x, y) < exclude_center_radius:
                continue
            valid = True
            for o in obstacles:
                if math.hypot(x - o.x, y - o.y) < o.radius + OBST_MIN_R + 15:
                    valid = False
                    break
            if valid:
                r = random.uniform(OBST_MIN_R, OBST_MAX_R)
                h = random.uniform(0.5, 2.0)
                obstacles.append(Obstacle(x, y, r, h))
                break
    return obstacles

def generate_terrain(world_size, tile_size=80):
    tiles = []
    num_tiles_x = int(world_size * 2 / tile_size) + 4
    num_tiles_y = int(world_size * 2 / tile_size) + 4

    for tx in range(-2, num_tiles_x - 2):
        for ty in range(-2, num_tiles_y - 2):
            wx = tx * tile_size - world_size
            wy = ty * tile_size - world_size

            dist = math.hypot(wx, wy)
            if dist > world_size + tile_size:
                continue

            if dist < world_size * 0.3:
                t = TERRAIN_TYPES[0]
            elif dist < world_size * 0.6:
                t = TERRAIN_TYPES[1] if random.random() < 0.4 else TERRAIN_TYPES[0]
            else:
                t = random.choice(TERRAIN_TYPES)

            tiles.append(TerrainTile(wx, wy, tile_size, tile_size, t))
    return tiles

def draw_minimap(screen, spider, obstacles, world_size, offset_x, offset_y):
    map_size = 150
    map_x = SCREEN_W - map_size - 15
    map_y = 15
    scale = map_size / (world_size * 2)

    bg = pygame.Surface((map_size + 4, map_size + 4))
    bg.fill((30, 30, 30))
    bg.set_alpha(180)
    screen.blit(bg, (map_x - 2, map_y - 2))

    pygame.draw.rect(screen, (50, 50, 50), (map_x, map_y, map_size, map_size), 1)

    for obs in obstacles:
        mx = map_x + (obs.x + world_size) * scale
        my = map_y + (obs.y + world_size) * scale
        r = max(2, int(obs.radius * scale))
        pygame.draw.circle(screen, (150, 100, 80), (int(mx), int(my)), r)

    sx = map_x + (spider.x + world_size) * scale
    sy = map_y + (spider.y + world_size) * scale
    pygame.draw.circle(screen, (0, 200, 255), (int(sx), int(sy)), 4)
    fwd_x = sx + math.cos(spider.rotation) * 8
    fwd_y = sy + math.sin(spider.rotation) * 8
    pygame.draw.line(screen, (255, 255, 255), (sx, sy), (fwd_x, fwd_y), 2)
