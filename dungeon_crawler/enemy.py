import pygame
import random
from dataclasses import dataclass, field
from constants import (
    TILE_SIZE, TILE_WALL, TILE_DOOR,
    ENEMY_PATROL, ENEMY_TRACKER, ENEMY_GUARD,
    ENEMY_MOVE_INTERVAL, TRACKER_MOVE_INTERVAL, GUARD_MOVE_INTERVAL
)


@dataclass
class Enemy:
    tile_x: int = 0
    tile_y: int = 0
    etype: int = ENEMY_PATROL
    move_timer: int = 0
    home_x: int = 0
    home_y: int = 0
    rect: pygame.Rect = field(init=False)

    def __post_init__(self):
        self.rect = pygame.Rect(
            self.tile_x * TILE_SIZE + 6, self.tile_y * TILE_SIZE + 6,
            TILE_SIZE - 12, TILE_SIZE - 12)

    def spawn(self, tile_x, tile_y, etype=ENEMY_PATROL):
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.etype = etype
        self.home_x = tile_x
        self.home_y = tile_y
        self.rect.x = tile_x * TILE_SIZE + 6
        self.rect.y = tile_y * TILE_SIZE + 6
        interval = {ENEMY_PATROL: ENEMY_MOVE_INTERVAL,
                    ENEMY_TRACKER: TRACKER_MOVE_INTERVAL,
                    ENEMY_GUARD: GUARD_MOVE_INTERVAL}
        self.move_timer = random.randint(0, interval.get(etype, ENEMY_MOVE_INTERVAL))

    def _is_blocked(self, game_map, tx, ty):
        if tx < 0 or ty < 0 or tx >= len(game_map[0]) or ty >= len(game_map):
            return True
        t = game_map[ty][tx]
        return t == TILE_WALL or t == TILE_DOOR

    def _move_patrol(self, game_map):
        dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = self.tile_x + dx, self.tile_y + dy
            if not self._is_blocked(game_map, nx, ny):
                self.tile_x, self.tile_y = nx, ny
                break

    def _move_tracker(self, game_map, player_rect):
        pcx = player_rect.centerx // TILE_SIZE
        pcy = player_rect.centery // TILE_SIZE
        dx = (1 if pcx > self.tile_x else -1 if pcx < self.tile_x else 0)
        dy = (1 if pcy > self.tile_y else -1 if pcy < self.tile_y else 0)
        moves = []
        if dx != 0 and dy != 0:
            moves = [(dx, 0), (0, dy)] if abs(pcx - self.tile_x) >= abs(pcy - self.tile_y) else [(0, dy), (dx, 0)]
        elif dx != 0:
            moves = [(dx, 0)]
        elif dy != 0:
            moves = [(0, dy)]
        random.shuffle(moves) if random.random() < 0.2 else None
        for mx, my in moves:
            nx, ny = self.tile_x + mx, self.tile_y + my
            if not self._is_blocked(game_map, nx, ny):
                self.tile_x, self.tile_y = nx, ny
                break
        else:
            self._move_patrol(game_map)

    def _move_guard(self, game_map):
        dx = self.tile_x - self.home_x
        dy = self.tile_y - self.home_y
        if abs(dx) + abs(dy) >= 3:
            dirs = [(-1 if dx > 0 else 1 if dx < 0 else 0, 0),
                    (0, -1 if dy > 0 else 1 if dy < 0 else 0)]
        else:
            dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
            random.shuffle(dirs)
        for mx, my in dirs:
            nx, ny = self.tile_x + mx, self.tile_y + my
            if not self._is_blocked(game_map, nx, ny):
                self.tile_x, self.tile_y = nx, ny
                break

    def update(self, game_map, player_rect=None):
        interval = {ENEMY_PATROL: ENEMY_MOVE_INTERVAL,
                    ENEMY_TRACKER: TRACKER_MOVE_INTERVAL,
                    ENEMY_GUARD: GUARD_MOVE_INTERVAL}
        self.move_timer += 1
        if self.move_timer < interval.get(self.etype, ENEMY_MOVE_INTERVAL):
            return
        self.move_timer = 0
        if self.etype == ENEMY_TRACKER and player_rect:
            self._move_tracker(game_map, player_rect)
        elif self.etype == ENEMY_GUARD:
            self._move_guard(game_map)
        else:
            self._move_patrol(game_map)
        self.rect.x = self.tile_x * TILE_SIZE + 6
        self.rect.y = self.tile_y * TILE_SIZE + 6

    def check_player_collision(self, player_rect):
        return self.rect.colliderect(player_rect)
