import pygame
import random
from dataclasses import dataclass, field
from constants import TILE_SIZE, TILE_WALL, ENEMY_MOVE_INTERVAL


@dataclass
class Enemy:
    tile_x: int = 0
    tile_y: int = 0
    move_timer: int = 0
    rect: pygame.Rect = field(init=False)

    def __post_init__(self):
        self.rect = pygame.Rect(
            self.tile_x * TILE_SIZE + 6,
            self.tile_y * TILE_SIZE + 6,
            TILE_SIZE - 12,
            TILE_SIZE - 12
        )

    def spawn(self, tile_x, tile_y):
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.rect.x = tile_x * TILE_SIZE + 6
        self.rect.y = tile_y * TILE_SIZE + 6
        self.move_timer = random.randint(0, ENEMY_MOVE_INTERVAL)

    def is_wall_at(self, game_map, tx, ty):
        if tx < 0 or ty < 0 or tx >= len(game_map[0]) or ty >= len(game_map):
            return True
        return game_map[ty][tx] == TILE_WALL

    def update(self, game_map):
        self.move_timer += 1
        if self.move_timer >= ENEMY_MOVE_INTERVAL:
            self.move_timer = 0
            directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx = self.tile_x + dx
                ny = self.tile_y + dy
                if not self.is_wall_at(game_map, nx, ny):
                    self.tile_x = nx
                    self.tile_y = ny
                    self.rect.x = self.tile_x * TILE_SIZE + 6
                    self.rect.y = self.tile_y * TILE_SIZE + 6
                    break


    def check_player_collision(self, player_rect):
        return self.rect.colliderect(player_rect)
