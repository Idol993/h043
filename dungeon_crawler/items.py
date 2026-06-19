import math
import pygame
from dataclasses import dataclass, field
from constants import TILE_SIZE, KEY_MAGNET_RANGE


@dataclass
class Key:
    tile_x: int = 0; tile_y: int = 0; collected: bool = False
    magnet_target: object = None; magnet_speed: float = 4.0
    rect: pygame.Rect = field(init=False)

    def __post_init__(self):
        self.rect = pygame.Rect(
            self.tile_x*TILE_SIZE+8, self.tile_y*TILE_SIZE+8,
            TILE_SIZE-16, TILE_SIZE-16)

    def spawn(self, tile_x, tile_y):
        self.tile_x = tile_x; self.tile_y = tile_y
        self.collected = False; self.magnet_target = None
        self.rect.x = tile_x*TILE_SIZE+8; self.rect.y = tile_y*TILE_SIZE+8

    def check_pickup(self, player_rect):
        if self.collected: return False
        if self.rect.colliderect(player_rect):
            self.collected = True; return True
        return False

    def try_magnet(self, player_rect, is_first_key):
        if self.collected or self.magnet_target: return
        if not is_first_key: return
        pcx, pcy = player_rect.centerx, player_rect.centery
        kcx, kcy = self.rect.centerx, self.rect.centery
        dist = math.hypot(pcx - kcx, pcy - kcy)
        if dist <= KEY_MAGNET_RANGE * TILE_SIZE:
            self.magnet_target = (pcx, pcy)

    def update_magnet(self, player_rect):
        if self.collected or not self.magnet_target: return
        kcx, kcy = self.rect.centerx, self.rect.centery
        pcx, pcy = player_rect.centerx, player_rect.centery
        dx, dy = pcx - kcx, pcy - kcy
        dist = math.hypot(dx, dy)
        if dist < self.magnet_speed * 2:
            self.rect.centerx = pcx; self.rect.centery = pcy
            return
        if dist > 0:
            self.rect.x += int(dx / dist * self.magnet_speed)
            self.rect.y += int(dy / dist * self.magnet_speed)
