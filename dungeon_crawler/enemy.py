import pygame
import random
from dataclasses import dataclass, field
from constants import (
    TILE_SIZE, TILE_WALL, TILE_DOOR,
    ENEMY_PATROL, ENEMY_TRACKER, ENEMY_GUARD,
    ENEMY_MOVE_INTERVAL, TRACKER_MOVE_INTERVAL, GUARD_MOVE_INTERVAL,
    KNOCKBACK_DIST
)


@dataclass
class Enemy:
    tile_x: int = 0; tile_y: int = 0
    etype: int = ENEMY_PATROL; move_timer: int = 0
    home_x: int = 0; home_y: int = 0
    rect: pygame.Rect = field(init=False)

    def __post_init__(self):
        self.rect = pygame.Rect(self.tile_x*TILE_SIZE+6, self.tile_y*TILE_SIZE+6,
                                TILE_SIZE-12, TILE_SIZE-12)

    def spawn(self, tile_x, tile_y, etype=ENEMY_PATROL):
        self.tile_x = tile_x; self.tile_y = tile_y; self.etype = etype
        self.home_x = tile_x; self.home_y = tile_y
        self.rect.x = tile_x*TILE_SIZE+6; self.rect.y = tile_y*TILE_SIZE+6
        iv = {ENEMY_PATROL:ENEMY_MOVE_INTERVAL, ENEMY_TRACKER:TRACKER_MOVE_INTERVAL,
              ENEMY_GUARD:GUARD_MOVE_INTERVAL}
        self.move_timer = random.randint(0, iv.get(etype, ENEMY_MOVE_INTERVAL))

    def _blocked(self, m, tx, ty):
        if tx<0 or ty<0 or tx>=len(m[0]) or ty>=len(m): return True
        return m[ty][tx] in (TILE_WALL, TILE_DOOR)

    def _move_patrol(self, m):
        dirs = [(0,-1),(0,1),(-1,0),(1,0)]; random.shuffle(dirs)
        for dx,dy in dirs:
            nx,ny = self.tile_x+dx, self.tile_y+dy
            if not self._blocked(m,nx,ny): self.tile_x=nx; self.tile_y=ny; break

    def _move_tracker(self, m, pr):
        pcx,pcy = pr.centerx//TILE_SIZE, pr.centery//TILE_SIZE
        dx = (1 if pcx>self.tile_x else -1 if pcx<self.tile_x else 0)
        dy = (1 if pcy>self.tile_y else -1 if pcy<self.tile_y else 0)
        moves = []
        if dx!=0 and dy!=0:
            moves = [(dx,0),(0,dy)] if abs(pcx-self.tile_x)>=abs(pcy-self.tile_y) else [(0,dy),(dx,0)]
        elif dx!=0: moves = [(dx,0)]
        elif dy!=0: moves = [(0,dy)]
        if random.random()<0.2: random.shuffle(moves)
        for mx,my in moves:
            nx,ny = self.tile_x+mx, self.tile_y+my
            if not self._blocked(m,nx,ny): self.tile_x=nx; self.tile_y=ny; break
        else: self._move_patrol(m)

    def _move_guard(self, m):
        dx,dy = self.tile_x-self.home_x, self.tile_y-self.home_y
        if abs(dx)+abs(dy)>=3:
            dirs = [(-1 if dx>0 else 1 if dx<0 else 0, 0),
                    (0, -1 if dy>0 else 1 if dy<0 else 0)]
        else:
            dirs = [(0,-1),(0,1),(-1,0),(1,0)]; random.shuffle(dirs)
        for mx,my in dirs:
            nx,ny = self.tile_x+mx, self.tile_y+my
            if not self._blocked(m,nx,ny): self.tile_x=nx; self.tile_y=ny; break

    def update(self, m, player_rect=None):
        iv = {ENEMY_PATROL:ENEMY_MOVE_INTERVAL, ENEMY_TRACKER:TRACKER_MOVE_INTERVAL,
              ENEMY_GUARD:GUARD_MOVE_INTERVAL}
        self.move_timer += 1
        if self.move_timer < iv.get(self.etype, ENEMY_MOVE_INTERVAL): return
        self.move_timer = 0
        if self.etype==ENEMY_TRACKER and player_rect: self._move_tracker(m, player_rect)
        elif self.etype==ENEMY_GUARD: self._move_guard(m)
        else: self._move_patrol(m)
        self.rect.x = self.tile_x*TILE_SIZE+6; self.rect.y = self.tile_y*TILE_SIZE+6

    def push_away(self, m, from_tile_x, from_tile_y, dist=KNOCKBACK_DIST):
        dx = self.tile_x - from_tile_x
        dy = self.tile_y - from_tile_y
        if dx==0 and dy==0: dx = random.choice([-1,1])
        step_x = (1 if dx>0 else -1 if dx<0 else 0)
        step_y = (1 if dy>0 else -1 if dy<0 else 0)
        for _ in range(dist):
            nx, ny = self.tile_x + step_x, self.tile_y + step_y
            if not self._blocked(m, nx, ny):
                self.tile_x = nx; self.tile_y = ny
            else:
                if step_x!=0 and not self._blocked(m, self.tile_x+step_x, self.tile_y):
                    self.tile_x += step_x
                elif step_y!=0 and not self._blocked(m, self.tile_x, self.tile_y+step_y):
                    self.tile_y += step_y
                break
        self.rect.x = self.tile_x*TILE_SIZE+6; self.rect.y = self.tile_y*TILE_SIZE+6

    def check_player_collision(self, player_rect):
        return self.rect.colliderect(player_rect)
