import pygame
from dataclasses import dataclass, field
from constants import (
    TILE_SIZE, PLAYER_SPEED, PLAYER_MAX_HP,
    TILE_WALL, TILE_DOOR, TILE_FLOOR, TILE_STAIRS
)


@dataclass
class Player:
    x: int = 0
    y: int = 0
    hp: int = PLAYER_MAX_HP
    keys: int = 0
    vx: int = 0
    vy: int = 0
    invincible_timer: int = 0
    rect: pygame.Rect = field(init=False)

    def __post_init__(self):
        self.rect = pygame.Rect(
            self.x * TILE_SIZE + 4,
            self.y * TILE_SIZE + 4,
            TILE_SIZE - 8,
            TILE_SIZE - 8
        )

    def spawn(self, tile_x, tile_y):
        self.x = tile_x * TILE_SIZE
        self.y = tile_y * TILE_SIZE
        self.rect.x = self.x + 4
        self.rect.y = self.y + 4
        self.hp = PLAYER_MAX_HP
        self.keys = 0
        self.invincible_timer = 0

    def handle_input(self, keys):
        self.vx = 0
        self.vy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vy = -PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vy = PLAYER_SPEED

    def is_wall_at(self, game_map, tile_x, tile_y):
        if tile_x < 0 or tile_y < 0 or tile_x >= len(game_map[0]) or tile_y >= len(game_map):
            return True
        return game_map[tile_y][tile_x] == TILE_WALL

    def is_door_at(self, game_map, tile_x, tile_y):
        if tile_x < 0 or tile_y < 0 or tile_x >= len(game_map[0]) or tile_y >= len(game_map):
            return False
        return game_map[tile_y][tile_x] == TILE_DOOR

    def check_collision(self, game_map, new_rect):
        left = new_rect.left // TILE_SIZE
        right = new_rect.right // TILE_SIZE
        top = new_rect.top // TILE_SIZE
        bottom = new_rect.bottom // TILE_SIZE

        for ty in range(top, bottom + 1):
            for tx in range(left, right + 1):
                if self.is_wall_at(game_map, tx, ty):
                    return True
                if self.is_door_at(game_map, tx, ty):
                    if self.keys <= 0:
                        return True
        return False

    def update(self, game_map, doors_opened):
        if self.vx != 0 and self.vy != 0:
            self.vx = int(self.vx * 0.707)
            self.vy = int(self.vy * 0.707)

        new_rect = self.rect.copy()
        new_rect.x += self.vx
        if not self.check_collision(game_map, new_rect):
            self.rect.x = new_rect.x
            self._try_open_doors(game_map, doors_opened, 'x')
        else:
            self._try_open_doors(game_map, doors_opened, 'x')

        new_rect = self.rect.copy()
        new_rect.y += self.vy
        if not self.check_collision(game_map, new_rect):
            self.rect.y = new_rect.y
            self._try_open_doors(game_map, doors_opened, 'y')
        else:
            self._try_open_doors(game_map, doors_opened, 'y')

        self.x = self.rect.x - 4
        self.y = self.rect.y - 4

        if self.invincible_timer > 0:
            self.invincible_timer -= 1

    def _try_open_doors(self, game_map, doors_opened, axis):
        if self.keys <= 0:
            return
        left = self.rect.left // TILE_SIZE
        right = self.rect.right // TILE_SIZE
        top = self.rect.top // TILE_SIZE
        bottom = self.rect.bottom // TILE_SIZE

        for ty in range(top, bottom + 1):
            for tx in range(left, right + 1):
                if self.is_door_at(game_map, tx, ty):
                    door_key = (tx, ty)
                    if door_key not in doors_opened:
                        doors_opened.add(door_key)
                        game_map[ty][tx] = TILE_FLOOR
                        self.keys -= 1

    def take_damage(self, amount=1):
        if self.invincible_timer > 0:
            return False
        self.hp -= amount
        self.invincible_timer = 60
        return self.hp <= 0

    def add_key(self):
        self.keys += 1

    def get_tile_pos(self):
        cx = self.rect.centerx // TILE_SIZE
        cy = self.rect.centery // TILE_SIZE
        return cx, cy

    def is_on_stairs(self, game_map):
        tx, ty = self.get_tile_pos()
        if 0 <= ty < len(game_map) and 0 <= tx < len(game_map[0]):
            return game_map[ty][tx] == TILE_STAIRS
        return False
