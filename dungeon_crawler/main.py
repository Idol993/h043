import pygame
import time
import random
import sys
from constants import (WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TILE_SIZE,
    BUFF_HP, BUFF_SPEED, BUFF_KEY_KEEP, BUFF_INVINCIBLE,
    BUFF_LOW_HP_SPEED, BUFF_DOOR_SHIELD, BUFF_KEY_MAGNET, BUFF_HURT_KNOCK,
    LEVEL_UP_INTERVAL)
from player import Player
from enemy import Enemy
from items import Key
from map_gen import generate_map
from renderer import Renderer

ALL_BUFFS = [BUFF_HP, BUFF_SPEED, BUFF_KEY_KEEP, BUFF_INVINCIBLE,
             BUFF_LOW_HP_SPEED, BUFF_DOOR_SHIELD, BUFF_KEY_MAGNET, BUFF_HURT_KNOCK]


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("像素地牢闯关")
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen)
        self.renderer.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.player = Player()
        self.enemies=[]; self.keys=[]; self.game_map=[]; self.doors_opened=set()
        self.level=1; self.game_over=False; self.paused=False
        self.level_up_active=False; self.level_up_options=[]; self.level_up_selected=0
        self.logic_time=0.0; self.frame_count=0
        self.load_level(1)

    def load_level(self, level):
        data = generate_map(level)
        self.game_map = data['map']; self.doors_opened = set()
        self.player.level_keys_collected = 0
        if level == 1:
            self.player.spawn(*data['player_spawn'])
        else:
            px, py = data['player_spawn']
            self.player.rect.x=px*TILE_SIZE+4; self.player.rect.y=py*TILE_SIZE+4
            self.player.x=self.player.rect.x-4; self.player.y=self.player.rect.y-4
        self.keys = [Key() for _ in data['keys']]
        for k, (kx, ky) in zip(self.keys, data['keys']): k.spawn(kx, ky)
        self.enemies = [Enemy() for _ in data['enemies']]
        for e, (ex, ey, et) in zip(self.enemies, data['enemies']): e.spawn(ex, ey, et)

    def _check_level_up(self):
        if self.level > 1 and (self.level-1) % LEVEL_UP_INTERVAL == 0:
            self.level_up_active=True; self.level_up_selected=0
            self.level_up_options = random.sample(ALL_BUFFS, min(3, len(ALL_BUFFS)))

    def _do_knockback(self):
        if not self.player.has_buff(BUFF_HURT_KNOCK): return
        ptx, pty = self.player.get_tile_pos()
        for e in self.enemies:
            dist = abs(e.tile_x-ptx)+abs(e.tile_y-pty)
            if dist <= 4:
                e.push_away(self.game_map, ptx, pty)

    def _handle_key_magnet(self):
        if not self.player.has_buff(BUFF_KEY_MAGNET): return
        for k in self.keys:
            is_first = (self.player.level_keys_collected == 0 and not k.collected)
            k.try_magnet(self.player.rect, is_first)
            k.update_magnet(self.player.rect)

    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: return False
            if ev.type == pygame.VIDEORESIZE:
                self.screen=pygame.display.set_mode((ev.w,ev.h),pygame.RESIZABLE)
                self.renderer.resize(ev.w,ev.h)
            if ev.type == pygame.KEYDOWN:
                if self.level_up_active:
                    if ev.key in (pygame.K_UP,pygame.K_w): self.level_up_selected=(self.level_up_selected-1)%len(self.level_up_options)
                    elif ev.key in (pygame.K_DOWN,pygame.K_s): self.level_up_selected=(self.level_up_selected+1)%len(self.level_up_options)
                    elif ev.key == pygame.K_RETURN:
                        self.player.apply_buff(self.level_up_options[self.level_up_selected])
                        self.level_up_active = False
                elif self.game_over:
                    if ev.key == pygame.K_r: self.restart()
                elif ev.key == pygame.K_p: self.paused = not self.paused
                elif ev.key == pygame.K_ESCAPE: return False
        return True

    def restart(self):
        self.level=1; self.game_over=False; self.paused=False; self.level_up_active=False
        self.player = Player(); self.load_level(1)

    def update(self):
        if self.game_over or self.paused or self.level_up_active: return
        self.player.handle_input(pygame.key.get_pressed())
        self.player.update(self.game_map, self.doors_opened)
        self._handle_key_magnet()
        for k in self.keys:
            if k.check_pickup(self.player.rect): self.player.add_key()
        for e in self.enemies: e.update(self.game_map, self.player.rect)
        for e in self.enemies:
            if e.check_player_collision(self.player.rect):
                if self.player.take_damage(1):
                    self.game_over = True
                self._do_knockback()
        if self.player.is_on_stairs(self.game_map):
            self.level += 1; self.load_level(self.level); self._check_level_up()
        self.renderer.camera.update(self.player.x, self.player.y, TILE_SIZE)

    def render(self):
        r=self.renderer; r.clear(); r.draw_map(self.game_map)
        r.draw_keys(self.keys); r.draw_enemies(self.enemies); r.draw_player(self.player)
        r.draw_hud(self.player, self.level)
        if self.game_over: r.draw_game_over(self.level)
        elif self.paused: r.draw_pause(self.player, self.level)
        elif self.level_up_active: r.draw_level_up(self.level_up_options, self.level_up_selected)
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            t0 = time.perf_counter(); self.update()
            self.logic_time += time.perf_counter()-t0; self.frame_count += 1
            self.render(); self.clock.tick(FPS)
            if self.frame_count >= FPS:
                avg = (self.logic_time/self.frame_count)*1000
                pygame.display.set_caption(f"像素地牢闯关 - 第{self.level}层 | 逻辑: {avg:.2f}ms")
                self.frame_count=0; self.logic_time=0.0
        pygame.quit(); sys.exit()


def main(): Game().run()
if __name__ == "__main__": main()
