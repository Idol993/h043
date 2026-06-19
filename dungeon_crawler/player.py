import pygame
from dataclasses import dataclass, field
from constants import (
    TILE_SIZE, PLAYER_SPEED, PLAYER_MAX_HP,
    TILE_WALL, TILE_DOOR, TILE_FLOOR, TILE_STAIRS,
    BUFF_HP, BUFF_SPEED, BUFF_KEY_KEEP, BUFF_INVINCIBLE,
    BUFF_LOW_HP_SPEED, BUFF_DOOR_SHIELD, BUFF_KEY_MAGNET, BUFF_HURT_KNOCK,
    DOOR_SHIELD_FRAMES
)


@dataclass
class Player:
    x: int = 0; y: int = 0
    hp: int = PLAYER_MAX_HP; max_hp: int = PLAYER_MAX_HP
    keys: int = 0; vx: int = 0; vy: int = 0
    invincible_timer: int = 0; speed_bonus: int = 0
    invincible_bonus: int = 0; key_keep: bool = False
    buffs: list = field(default_factory=list)
    door_shield_timer: int = 0
    level_keys_collected: int = 0
    rect: pygame.Rect = field(init=False)

    def __post_init__(self):
        self.rect = pygame.Rect(self.x*TILE_SIZE+4, self.y*TILE_SIZE+4, TILE_SIZE-8, TILE_SIZE-8)

    def spawn(self, tile_x, tile_y):
        self.x = tile_x*TILE_SIZE; self.y = tile_y*TILE_SIZE
        self.rect.x = self.x+4; self.rect.y = self.y+4
        self.hp = self.max_hp; self.keys = 0
        self.invincible_timer = 0; self.level_keys_collected = 0

    def apply_buff(self, bt):
        self.buffs.append(bt)
        if bt == BUFF_HP: self.max_hp += 1; self.hp += 1
        elif bt == BUFF_SPEED: self.speed_bonus += 1
        elif bt == BUFF_KEY_KEEP: self.key_keep = True
        elif bt == BUFF_INVINCIBLE: self.invincible_bonus += 30

    def has_buff(self, bt):
        return bt in self.buffs

    def get_combos(self):
        cs=[]
        if self.has_buff(BUFF_DOOR_SHIELD) and self.has_buff(BUFF_HURT_KNOCK): cs.append('开门即退')
        if self.has_buff(BUFF_LOW_HP_SPEED) and self.has_buff(BUFF_HURT_KNOCK): cs.append('绝境爆发')
        if self.has_buff(BUFF_KEY_KEEP) and self.has_buff(BUFF_KEY_MAGNET): cs.append('钥匙在手')
        if self.has_buff(BUFF_INVINCIBLE) and self.has_buff(BUFF_DOOR_SHIELD): cs.append('不死战神')
        return cs

    def get_combo_info(self):
        ci={}
        if self.has_buff(BUFF_DOOR_SHIELD) and self.has_buff(BUFF_HURT_KNOCK):
            ci['开门即退']='护盾期自动击退怪物'
        if self.has_buff(BUFF_LOW_HP_SPEED) and self.has_buff(BUFF_HURT_KNOCK):
            ci['绝境爆发']='低血时击退距离×2'
        if self.has_buff(BUFF_KEY_KEEP) and self.has_buff(BUFF_KEY_MAGNET):
            ci['钥匙在手']='磁铁范围+3 吸附更快'
        if self.has_buff(BUFF_INVINCIBLE) and self.has_buff(BUFF_DOOR_SHIELD):
            ci['不死战神']='护盾时间×1.5'
        return ci

    def get_magnet_bonus(self):
        extra_range=0; extra_speed=1.0
        if self.has_buff(BUFF_KEY_KEEP) and self.has_buff(BUFF_KEY_MAGNET):
            extra_range=3; extra_speed=1.5
        return extra_range, extra_speed

    def get_knockback_bonus(self):
        dist=0; auto=False
        if self.has_buff(BUFF_LOW_HP_SPEED) and self.has_buff(BUFF_HURT_KNOCK) and self.hp<=1: dist=3
        if self.has_buff(BUFF_DOOR_SHIELD) and self.has_buff(BUFF_HURT_KNOCK) and self.door_shield_timer>0: auto=True
        return dist, auto

    def get_speed(self):
        spd = PLAYER_SPEED + self.speed_bonus
        if self.has_buff(BUFF_LOW_HP_SPEED) and self.hp <= 1:
            spd += 3
        return spd

    def handle_input(self, keys):
        spd = self.get_speed()
        self.vx = 0; self.vy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.vx = -spd
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.vx = spd
        if keys[pygame.K_UP] or keys[pygame.K_w]: self.vy = -spd
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: self.vy = spd

    def _is_wall(self, m, tx, ty):
        if tx<0 or ty<0 or tx>=len(m[0]) or ty>=len(m): return True
        return m[ty][tx] == TILE_WALL

    def _is_door(self, m, tx, ty):
        if tx<0 or ty<0 or tx>=len(m[0]) or ty>=len(m): return False
        return m[ty][tx] == TILE_DOOR

    def _check_collision(self, m, nr):
        l,r,t,b = nr.left//TILE_SIZE, nr.right//TILE_SIZE, nr.top//TILE_SIZE, nr.bottom//TILE_SIZE
        for ty in range(t, b+1):
            for tx in range(l, r+1):
                if self._is_wall(m, tx, ty): return True
                if self._is_door(m, tx, ty) and self.keys <= 0: return True
        return False

    def _try_open_doors(self, m, opened):
        if self.keys <= 0: return False
        l,r,t,b = self.rect.left//TILE_SIZE, self.rect.right//TILE_SIZE, self.rect.top//TILE_SIZE, self.rect.bottom//TILE_SIZE
        opened_any = False
        for ty in range(t, b+1):
            for tx in range(l, r+1):
                if self._is_door(m, tx, ty) and (tx,ty) not in opened:
                    opened.add((tx,ty)); m[ty][tx] = TILE_FLOOR
                    if not self.key_keep: self.keys -= 1
                    opened_any = True
                    if self.has_buff(BUFF_DOOR_SHIELD):
                        sf = 1.5 if (self.has_buff(BUFF_INVINCIBLE)) else 1.0
                        self.door_shield_timer = int(DOOR_SHIELD_FRAMES * sf)
        return opened_any

    def update(self, game_map, doors_opened):
        if self.vx!=0 and self.vy!=0:
            self.vx = int(self.vx * 0.707); self.vy = int(self.vy * 0.707)
        nr = self.rect.copy(); nr.x += self.vx
        if not self._check_collision(game_map, nr): self.rect.x = nr.x
        self._try_open_doors(game_map, doors_opened)
        nr = self.rect.copy(); nr.y += self.vy
        if not self._check_collision(game_map, nr): self.rect.y = nr.y
        self._try_open_doors(game_map, doors_opened)
        self.x = self.rect.x-4; self.y = self.rect.y-4
        if self.invincible_timer > 0: self.invincible_timer -= 1
        if self.door_shield_timer > 0: self.door_shield_timer -= 1

    def take_damage(self, amount=1):
        if self.invincible_timer > 0 or self.door_shield_timer > 0: return False
        self.hp -= amount
        self.invincible_timer = 60 + self.invincible_bonus
        return self.hp <= 0

    def add_key(self):
        self.keys += 1; self.level_keys_collected += 1

    def get_tile_pos(self):
        return self.rect.centerx // TILE_SIZE, self.rect.centery // TILE_SIZE

    def is_on_stairs(self, game_map):
        tx, ty = self.get_tile_pos()
        if 0<=ty<len(game_map) and 0<=tx<len(game_map[0]):
            return game_map[ty][tx] == TILE_STAIRS
        return False
