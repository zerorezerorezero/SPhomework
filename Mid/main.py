import pygame
import math
import sys
import random

from constants import *
from leg import Leg
from spider import Spider
from cannon import Cannon, Projectile
from sensors import Lidar
from environment import TerrainTile, Obstacle, generate_obstacles, generate_terrain, draw_minimap

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("四足機械蜘蛛控制系統 | Quadruped Spider Control System")
        self.clock = pygame.time.Clock()
        font_names = ["simhei", "microsoftyahei", "notosanscjk", "arialunicodems", "arial"]
        self.font = None
        self.font_big = None
        self.font_huge = None
        self.font_hud = None

        for name in font_names:
            try:
                f = pygame.font.SysFont(name, 16, bold=True)
                if f is not None and f.render("test", True, (0,0,0)).get_width() > 0:
                    self.font = f
                    self.font_big = pygame.font.SysFont(name, 24, bold=True)
                    self.font_huge = pygame.font.SysFont(name, 48, bold=True)
                    self.font_hud = pygame.font.SysFont(name, 14)
                    break
            except:
                continue

        if self.font is None:
            self.font = pygame.font.Font(None, 16)
            self.font_big = pygame.font.Font(None, 24)
            self.font_huge = pygame.font.Font(None, 48)
            self.font_hud = pygame.font.Font(None, 14)

        self.running = True
        self.paused = False
        self.world_size = 800
        self.camera_x = 0
        self.camera_y = 0
        self.show_lidar = True
        self.show_minimap = True
        self.mouse_world = (0, 0)

        self.spider = Spider(0, 0)
        self.spider.rotation = -math.pi / 2
        self.lidar = Lidar(self.spider)
        self.cannon = Cannon(self.spider)
        self.spider.attach_lidar(self.lidar)
        self.spider.attach_cannon(self.cannon)

        self.obstacles = generate_obstacles(self.world_size)
        self.terrain_tiles = generate_terrain(self.world_size)

        self.modal_welcome = True
        self.modal_timer = 120

    def handle_events(self):
        mouse_buttons = pygame.mouse.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.spider.start_jump()
                elif event.key == pygame.K_e:
                    self.cannon.reload_magazine()
                elif event.key == pygame.K_TAB:
                    self.spider.is_autopilot = not self.spider.is_autopilot
                elif event.key == pygame.K_l:
                    self.show_lidar = not self.show_lidar
                elif event.key == pygame.K_m:
                    self.show_minimap = not self.show_minimap
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.reset_spider()
                elif event.key == pygame.K_RIGHT:
                    self.spider.target_rotation += 0.3
                elif event.key == pygame.K_LEFT:
                    self.spider.target_rotation -= 0.3
                elif event.key == pygame.K_UP:
                    self.spider.set_move(1, 0, 0)
                elif event.key == pygame.K_DOWN:
                    self.spider.set_move(-1, 0, 0)
            if self.modal_welcome:
                self.modal_welcome = False
                self.modal_timer = 0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.cannon.fire()
                elif event.button == 3:
                    self.cannon.reload_magazine()

        keys = pygame.key.get_pressed()
        fwd = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            fwd = 1
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            fwd = -1
        strafe = 0
        if keys[pygame.K_a]:
            strafe = -1
        elif keys[pygame.K_d]:
            strafe = 1
        rot = 0
        if keys[pygame.K_LEFT]:
            rot = -1
        elif keys[pygame.K_RIGHT]:
            rot = 1
        self.spider.set_move(fwd, strafe, rot)

        mx, my = pygame.mouse.get_pos()
        self.mouse_world = (
            mx - SCREEN_W // 2 + self.camera_x,
            my - SCREEN_H // 2 + self.camera_y,
        )
        self.cannon.aim_at(self.mouse_world[0], self.mouse_world[1])

    def reset_spider(self):
        self.spider.x = 0
        self.spider.y = 0
        self.spider.vx = 0
        self.spider.vy = 0
        self.spider.rotation = 0
        self.spider.target_fwd = 0
        self.spider.target_strafe = 0
        self.spider.is_autopilot = False
        self.cannon.projectiles.clear()

    def update(self):
        self.lidar.scan([o.get_circle() for o in self.obstacles])
        self.spider.update(self.obstacles, self.terrain_tiles)
        self.cannon.update()

        self.camera_x = self.spider.x
        self.camera_y = self.spider.y

        projectile_hits = []
        for p in self.cannon.projectiles:
            for obs in self.obstacles:
                if obs.collides_with(p.x, p.y, p.radius):
                    projectile_hits.append(p)
                    break
        for p in projectile_hits:
            if p in self.cannon.projectiles:
                self.cannon.projectiles.remove(p)

        if self.modal_welcome:
            self.modal_timer -= 1
            if self.modal_timer <= 0:
                self.modal_welcome = False

    def draw_hud(self):
        # Top bar
        bar = pygame.Surface((SCREEN_W, 36))
        bar.fill((20, 20, 30, 200))
        bar.set_alpha(200)
        self.screen.blit(bar, (0, 0))
        pygame.draw.line(self.screen, (80, 80, 100), (0, 36), (SCREEN_W, 36), 1)

        mode = "AUTO" if self.spider.is_autopilot else "手動"
        mode_color = (0, 255, 200) if self.spider.is_autopilot else (255, 200, 100)

        speed = math.hypot(self.spider.vx, self.spider.vy)
        terrain = self.spider.current_terrain["name"]
        pos_text = f"X:{self.spider.x:+.0f} Y:{self.spider.y:+.0f}"
        speed_text = f"速度:{speed:.1f}"
        terrain_text = f"地形:{terrain}"
        jump_text = f"跳躍:{'是' if self.spider.is_jumping else '否'}"

        y = 10
        x = 15
        for text, color in [
            (pos_text, (200, 200, 200)),
            (speed_text, (200, 200, 200)),
            (terrain_text, (160, 220, 160)),
            (jump_text, (255, 255, 100)),
        ]:
            surf = self.font_hud.render(text, True, color)
            self.screen.blit(surf, (x, y))
            x += surf.get_width() + 20

        mode_text = self.font.render(f"[{mode}]", True, mode_color)
        self.screen.blit(mode_text, (SCREEN_W - mode_text.get_width() - 15, 8))

        # Cannnon HUD - bottom right
        hud_x = SCREEN_W - 260
        hud_y = SCREEN_H - 130
        hud_bg = pygame.Surface((250, 120))
        hud_bg.fill((15, 15, 25, 200))
        hud_bg.set_alpha(200)
        self.screen.blit(hud_bg, (hud_x, hud_y))
        pygame.draw.rect(self.screen, (60, 60, 80), (hud_x, hud_y, 250, 120), 1)

        loader = self.cannon.loader
        shells = loader.shells_in_mag
        rounds = loader.total_rounds_fired
        state = loader.state
        state_names = {
            "idle": "待機",
            "loading": "裝填中...",
            "ready": "備便",
            "reloading": "更換彈匣...",
        }
        state_name = state_names.get(state, state)

        line_y = hud_y + 10
        ammo_text = self.font_hud.render(f"彈匣: {'●' * shells}{'○' * (MAG_SIZE - shells)}", True, (255, 220, 100))
        self.screen.blit(ammo_text, (hud_x + 10, line_y))

        line_y += 22
        state_surf = self.font_hud.render(f"狀態: {state_name}", True, (200, 200, 200))
        self.screen.blit(state_surf, (hud_x + 10, line_y))

        if state == "loading":
            prog = int(loader.loading_progress * 50)
            bar_color = (255, 200, 50)
            pygame.draw.rect(self.screen, (40, 40, 40), (hud_x + 10, line_y + 18, 150, 8))
            pygame.draw.rect(self.screen, bar_color, (hud_x + 10, line_y + 18, int(150 * loader.loading_progress), 8))
        elif state == "reloading":
            prog = int(loader.reload_progress * 50)
            pygame.draw.rect(self.screen, (40, 40, 40), (hud_x + 10, line_y + 18, 150, 8))
            pygame.draw.rect(self.screen, (100, 200, 255), (hud_x + 10, line_y + 18, int(150 * loader.reload_progress), 8))

        line_y += 36
        total_text = self.font_hud.render(f"累計射擊: {rounds} 發", True, (180, 180, 180))
        self.screen.blit(total_text, (hud_x + 10, line_y))

        line_y += 22
        if state == "ready" and loader.current_shell:
            ready_text = self.font_hud.render("> 左鍵開火 <", True, (255, 100, 100))
            self.screen.blit(ready_text, (hud_x + 75, line_y))

        # Controls hint
        hint_x = 15
        hint_y = SCREEN_H - 120
        hint_bg = pygame.Surface((280, 110))
        hint_bg.fill((15, 15, 25, 180))
        hint_bg.set_alpha(180)
        self.screen.blit(hint_bg, (hint_x, hint_y))
        pygame.draw.rect(self.screen, (60, 60, 80), (hint_x, hint_y, 280, 110), 1)

        hints = [
            "W/S/↑↓ 移動 | A/D 橫移 | ←→ 轉向",
            "滑鼠 瞄準 | 左鍵 開火 | 右鍵/E 換彈匣",
            "空白鍵 跳躍 | TAB 自動/手動切換",
            "L 顯示光達 | M 小地圖 | P 暫停 | R 重生",
        ]
        for i, hint in enumerate(hints):
            surf = self.font_hud.render(hint, True, (160, 160, 160))
            self.screen.blit(surf, (hint_x + 10, hint_y + 8 + i * 22))

        # FPS
        fps = int(self.clock.get_fps())
        fps_surf = self.font_hud.render(f"FPS: {fps}", True, (100, 200, 100))
        self.screen.blit(fps_surf, (SCREEN_W - 80, SCREEN_H - 20))

    def draw(self):
        self.screen.fill((25, 25, 35))
        ox, oy = self.camera_x, self.camera_y

        # Terrain
        for tile in self.terrain_tiles:
            tile.draw(self.screen, ox, oy)

        # Grid
        grid_size = 100
        grid_color = (45, 45, 55)
        start_x = int(-((ox - SCREEN_W // 2) % grid_size))
        start_y = int(-((oy - SCREEN_H // 2) % grid_size))
        for gx in range(start_x, SCREEN_W, grid_size):
            pygame.draw.line(self.screen, grid_color, (gx, 0), (gx, SCREEN_H), 1)
        for gy in range(start_y, SCREEN_H, grid_size):
            pygame.draw.line(self.screen, grid_color, (0, gy), (SCREEN_W, gy), 1)

        # Obstacles
        for obs in self.obstacles:
            obs.draw(self.screen, ox, oy)

        # LiDAR
        if self.show_lidar:
            self.lidar.draw(self.screen, ox, oy, show_all=False)

        # Spider
        self.spider.draw(self.screen, ox, oy)

        # Aiming crosshair
        mx, my = pygame.mouse.get_pos()
        ch = 12
        pygame.draw.line(self.screen, (255, 100, 100), (mx - ch, my), (mx + ch, my), 1)
        pygame.draw.line(self.screen, (255, 100, 100), (mx, my - ch), (mx, my + ch), 1)
        pygame.draw.circle(self.screen, (255, 100, 100, 80), (mx, my), 20, 1)

        # HUD
        self.draw_hud()

        # Minimap
        if self.show_minimap:
            draw_minimap(self.screen, self.spider, self.obstacles, self.world_size, ox, oy)

        # Welcome modal
        if self.modal_welcome:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(180)
            self.screen.blit(overlay, (0, 0))

            title = self.font_huge.render("四足機械蜘蛛控制系統", True, (0, 200, 255))
            subtitle = self.font_big.render("Quadruped Spider Control System", True, (200, 200, 200))
            instr = self.font.render("按任意方向鍵或 TAB 開始 | Press any key to start", True, (255, 255, 100))

            self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, SCREEN_H // 2 - 60))
            self.screen.blit(subtitle, (SCREEN_W // 2 - subtitle.get_width() // 2, SCREEN_H // 2))
            self.screen.blit(instr, (SCREEN_W // 2 - instr.get_width() // 2, SCREEN_H // 2 + 50))

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            if not self.paused:
                self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
