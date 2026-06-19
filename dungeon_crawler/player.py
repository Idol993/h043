import pygame
from dataclasses import dataclass, field
from constants import (
    TILE_SIZE, PLAYER_SPEED, PLAYER_MAX_HP,
    TILE_WALL, TILE_DOOR, TILE_FLOOR, TILE_STAIRS,
    BUFF_HP, BUFF_SPEED, BUFF_KEY_KEEP, BUFF_INVINCIBLE
)


@dataclass
class Player:
    x: int = 0
    y: int = 0
    hp: int = PLAYER_MAX_HP
    max_hp: int = PLAYER_MAX_HP
    keys: int = 0
    vx: int = 0
    vy: int = 0
    invincible_timer: int = 0
    speed_bonus: int = 0
    invincible_bonus: int = 0
    key_keep: bool = False
    buffs: list = field(default_factory=list)
    rect: pygame.Rect = field(init=False)

    def __post_init__(self):
        self.rect = pygame.Rect(
            self.x * TILE_SIZE + 4, self.y * TILE_SIZE + 4,
            TILE_SIZE - 8, TILE_SIZE - 8)

    def spawn(self, tile_x, tile_y):
        self.x = tile_x * TILE_SIZE
        self.y = tile_y * TILE_SIZE
        self.rect.x = self.x + 4
        self.rect.y = self.y + 4
        self.hp = self.max_hp
        self.keys = 0
        self.invincible_timer = 0

    def apply_buff(self, buff_type):
        self.buffs.append(buff_type)
        if buff_type == BUFF_HP:
            self.max_hp += 1
            self.hp += 1
        elif buff_type == BUFF_SPEED:
            self.speed_bonus += 1
        elif buff_type == BUFF_KEY_KEEP:
            self.key_keep = True
        elif buff_type == BUFF_INVINCIBLE:
            self.invincible_bonus += 30

    def handle_input(self, keys):
        spd = PLAYER_SPEED + self.speed_bonus
        self.vx = 0
        self.vy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.vx = -spd
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.vx = spd
        if keys[pygame.K_UP] or keys[pygame.K_w]: self.vy = -spd
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: self.vy = spd

    def _is_wall(self, m, tx, ty):
        if tx < 0 or ty < 0 or tx >= len(m[0]) or ty >= len(m): return True
        return m[ty][tx] == TILE_WALL

    def _is_door(self, m, tx, ty):
        if tx < 0 or ty < 0 or tx >= len(m[0]) or ty >= len(m): return False
        return m[ty][tx] == TILE_DOOR

    def _check_collision(self, m, nr):
        l, r, t, b = nr.left // TILE_SIZE, nr.right // TILE_SIZE, nr.top // TILE_SIZE, nr.bottom // TILE_SIZE
        for ty in range(t, b + 1):
            for tx in range(l, r + 1):
                if self._is_wall(m, tx, ty): return True
                if self._is_door(m, tx, ty) and self.keys <= 0: return True
        return False

    def _try_open_doors(self, m, opened):
        if self.keys <= 0: return
        l, r, t, b = self.rect.left // TILE_SIZE, self.rect.right // TILE_SIZE, self.rect.top // TILE_SIZE, self.rect.bottom // TILE_SIZE
        for ty in range(t, b + 1):
            for tx in range(l, r + 1):
                if self._is_door(m, tx, ty) and (tx, ty) not in opened:
                    opened.add((tx, ty))
                    m[ty][tx] = TILE_FLOOR
                    if not self.key_keep:
                        self.keys -= 1

    def update(self, game_map, doors_opened):
        if self.vx != 0 and self.vy != 0:
            self.vx = int(self.vx * 0.707)
            self.vy = int(self.vy * 0.707)
        nr = self.rect.copy()
        nr.x += self.vx
        if not self._check_collision(game_map, nr): self.rect.x = nr.x
        self._try_open_doors(game_map, doors_opened)
        nr = self.rect.copy()
        nr.y += self.vy
        if not self._check_collision(game_map, nr): self.rect.y = nr.y
        self._try_open_doors(game_map, doors_opened)
        self.x = self.rect.x - 4
        self.y = self.rect.y - 4
        if self.invincible_timer > 0: self.invincible_timer -= 1

    def take_damage(self, amount=1):
        if self.invincible_timer > 0: return False
        self.hp -= amount
        self.invincible_timer = 60 + self.invincible_bonus
        return self.hp <= 0

    def add_key(self):
        self.keys += 1

    def get_tile_pos(self):
        return self.rect.centerx // TILE_SIZE, self.rect.centery // TILE_SIZE

    def is_on_stairs(self, game_map):
        tx, ty = self.get_tile_pos()
        if 0 <= ty < len(game_map) and 0 <= tx < len(game_map[0]):
            return game_map[ty][tx] == TILE_STAIRS
        return False
