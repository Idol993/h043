import pygame
from dataclasses import dataclass
from constants import (
    TILE_SIZE, MAP_WIDTH, MAP_HEIGHT,
    TILE_FLOOR, TILE_WALL, TILE_DOOR, TILE_STAIRS,
    COLOR_FLOOR, COLOR_WALL, COLOR_WALL_TOP, COLOR_DOOR,
    COLOR_KEY, COLOR_ENEMY, COLOR_STAIRS,
    COLOR_PLAYER, COLOR_PLAYER_TOP,
    COLOR_HP_BG, COLOR_HP_FILL, COLOR_TEXT, COLOR_BG,
    PLAYER_MAX_HP
)


@dataclass
class Camera:
    x: int = 0
    y: int = 0
    view_w: int = 0
    view_h: int = 0

    def update(self, tx, ty, ts):
        self.x = tx + ts // 2 - self.view_w // 2
        self.y = ty + ts // 2 - self.view_h // 2
        mx = MAP_WIDTH * TILE_SIZE - self.view_w
        my = MAP_HEIGHT * TILE_SIZE - self.view_h
        self.x = max(0, min(self.x, mx))
        self.y = max(0, min(self.y, my))


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.camera = Camera()
        try:
            self.font = pygame.font.SysFont("arial", 20, bold=True)
            self.sfont = pygame.font.SysFont("arial", 14)
        except Exception:
            self.font = pygame.font.Font(None, 24)
            self.sfont = pygame.font.Font(None, 18)

    def resize(self, w, h):
        self.camera.view_w = w
        self.camera.view_h = h

    def _in_view(self, r):
        return pygame.Rect(0, 0, self.camera.view_w, self.camera.view_h).colliderect(r)

    def _draw_eyes(self, rect, ey):
        pygame.draw.rect(self.screen, (255,255,255), (rect.x+4, ey, 4, 4))
        pygame.draw.rect(self.screen, (255,255,255), (rect.right-8, ey, 4, 4))

    def draw_map(self, game_map):
        vx = self.camera.x // TILE_SIZE - 1
        vy = self.camera.y // TILE_SIZE - 1
        vw = self.camera.view_w // TILE_SIZE + 2
        vh = self.camera.view_h // TILE_SIZE + 2
        for ty in range(vy, vy + vh):
            for tx in range(vx, vx + vw):
                if tx < 0 or ty < 0 or tx >= MAP_WIDTH or ty >= MAP_HEIGHT:
                    continue
                tile = game_map[ty][tx]
                px = tx * TILE_SIZE - self.camera.x
                py = ty * TILE_SIZE - self.camera.y
                tr = pygame.Rect(px, py, TILE_SIZE, TILE_SIZE)
                if not self._in_view(tr):
                    continue
                if tile == TILE_FLOOR:
                    pygame.draw.rect(self.screen, COLOR_FLOOR, tr)
                elif tile == TILE_WALL:
                    pygame.draw.rect(self.screen, COLOR_WALL, tr)
                    pygame.draw.rect(self.screen, COLOR_WALL_TOP,
                                     (px+2, py+2, TILE_SIZE-4, TILE_SIZE-8))
                elif tile == TILE_DOOR:
                    pygame.draw.rect(self.screen, COLOR_FLOOR, tr)
                    pygame.draw.rect(self.screen, COLOR_DOOR,
                                     (px+4, py+2, TILE_SIZE-8, TILE_SIZE-4))
                    pygame.draw.rect(self.screen, (150,130,30),
                                     (px+TILE_SIZE//2-3, py+TILE_SIZE//2, 6, 6))
                elif tile == TILE_STAIRS:
                    pygame.draw.rect(self.screen, COLOR_FLOOR, tr)
                    pygame.draw.rect(self.screen, COLOR_STAIRS,
                                     (px+6, py+6, TILE_SIZE-12, TILE_SIZE-12))
                    if self.sfont:
                        t = self.sfont.render("↓", True, (20,80,20))
                        self.screen.blit(t, t.get_rect(center=tr.center))

    def draw_keys(self, keys):
        for k in keys:
            if k.collected: continue
            kr = k.rect.move(-self.camera.x, -self.camera.y)
            if not self._in_view(kr): continue
            pygame.draw.rect(self.screen, COLOR_KEY, kr)
            pygame.draw.rect(self.screen, (255,255,150),
                             (kr.x+2, kr.y+2, kr.w-4, kr.h-8))

    def draw_enemies(self, enemies):
        for e in enemies:
            er = e.rect.move(-self.camera.x, -self.camera.y)
            if not self._in_view(er): continue
            pygame.draw.rect(self.screen, COLOR_ENEMY, er)
            pygame.draw.rect(self.screen, (255,100,100),
                             (er.x+2, er.y+2, er.w-4, er.h-8))
            self._draw_eyes(er, er.y + 6)

    def draw_player(self, player):
        pr = player.rect.move(-self.camera.x, -self.camera.y)
        if player.invincible_timer > 0 and player.invincible_timer % 8 < 4:
            return
        pygame.draw.rect(self.screen, COLOR_PLAYER, pr)
        pygame.draw.rect(self.screen, COLOR_PLAYER_TOP,
                         (pr.x+2, pr.y+2, pr.w-4, pr.h-8))
        self._draw_eyes(pr, pr.y + 6)

    def draw_hud(self, player, level):
        bw, bh, bx, by = 120, 16, 10, 10
        pygame.draw.rect(self.screen, COLOR_HP_BG, (bx, by, bw, bh))
        pygame.draw.rect(self.screen, COLOR_HP_FILL,
                         (bx, by, int(bw * (player.hp / PLAYER_MAX_HP)), bh))
        pygame.draw.rect(self.screen, (255,255,255), (bx, by, bw, bh), 2)
        if self.font:
            self.screen.blit(self.font.render(
                f"HP: {player.hp}/{PLAYER_MAX_HP}", True, COLOR_TEXT), (bx+bw+10, by-2))
        pygame.draw.rect(self.screen, COLOR_KEY, (10, by+bh+10, 20, 20))
        if self.font:
            self.screen.blit(self.font.render(
                f"x {player.keys}", True, COLOR_TEXT), (36, by+bh+8))
            lt = self.font.render(f"第 {level} 层", True, COLOR_TEXT)
            self.screen.blit(lt, lt.get_rect(topright=(self.camera.view_w-10, 10)))

    def draw_game_over(self, level):
        ov = pygame.Surface((self.camera.view_w, self.camera.view_h), pygame.SRCALPHA)
        ov.fill((0,0,0,180))
        self.screen.blit(ov, (0,0))
        if self.font:
            cx, cy = self.camera.view_w//2, self.camera.view_h//2
            t1 = self.font.render("游戏结束", True, (255,80,80))
            t2 = self.font.render(f"到达第 {level} 层", True, COLOR_TEXT)
            t3 = self.font.render("按 R 键重新开始", True, COLOR_TEXT)
            self.screen.blit(t1, t1.get_rect(center=(cx, cy-40)))
            self.screen.blit(t2, t2.get_rect(center=(cx, cy)))
            self.screen.blit(t3, t3.get_rect(center=(cx, cy+40)))

    def clear(self):
        self.screen.fill(COLOR_BG)
