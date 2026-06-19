import pygame
from dataclasses import dataclass, field
from constants import TILE_SIZE


@dataclass
class Key:
    tile_x: int = 0
    tile_y: int = 0
    collected: bool = False
    rect: pygame.Rect = field(init=False)

    def __post_init__(self):
        self.rect = pygame.Rect(
            self.tile_x * TILE_SIZE + 8,
            self.tile_y * TILE_SIZE + 8,
            TILE_SIZE - 16,
            TILE_SIZE - 16
        )

    def spawn(self, tile_x, tile_y):
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.collected = False
        self.rect.x = tile_x * TILE_SIZE + 8
        self.rect.y = tile_y * TILE_SIZE + 8

    def check_pickup(self, player_rect):
        if self.collected:
            return False
        if self.rect.colliderect(player_rect):
            self.collected = True
            return True
        return False
