import pygame
import time
import sys
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TILE_SIZE
from player import Player
from enemy import Enemy
from items import Key
from map_gen import generate_map
from renderer import Renderer


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("像素地牢闯关")
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen)
        self.renderer.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.player = Player()
        self.enemies = []
        self.keys = []
        self.game_map = []
        self.doors_opened = set()
        self.level = 1
        self.game_over = False
        self.logic_time = 0.0
        self.frame_count = 0
        self.load_level(1)

    def load_level(self, level):
        data = generate_map(level)
        self.game_map = data['map']
        self.doors_opened = set()
        if level == 1:
            self.player.spawn(*data['player_spawn'])
        else:
            px, py = data['player_spawn']
            self.player.rect.x = px * TILE_SIZE + 4
            self.player.rect.y = py * TILE_SIZE + 4
            self.player.x = self.player.rect.x - 4
            self.player.y = self.player.rect.y - 4
        self.keys = []
        for kx, ky in data['keys']:
            k = Key()
            k.spawn(kx, ky)
            self.keys.append(k)
        self.enemies = []
        for ex, ey in data['enemies']:
            e = Enemy()
            e.spawn(ex, ey)
            self.enemies.append(e)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode(
                    (event.w, event.h), pygame.RESIZABLE)
                self.renderer.resize(event.w, event.h)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.restart()
                if event.key == pygame.K_ESCAPE:
                    return False
        return True

    def restart(self):
        self.level = 1
        self.game_over = False
        self.load_level(1)

    def update(self):
        if self.game_over:
            return
        self.player.handle_input(pygame.key.get_pressed())
        self.player.update(self.game_map, self.doors_opened)
        for k in self.keys:
            if k.check_pickup(self.player.rect):
                self.player.add_key()
        for e in self.enemies:
            e.update(self.game_map)
        for e in self.enemies:
            if e.check_player_collision(self.player.rect):
                if self.player.take_damage(1):
                    self.game_over = True
        if self.player.is_on_stairs(self.game_map):
            self.level += 1
            self.load_level(self.level)
        self.renderer.camera.update(self.player.x, self.player.y, TILE_SIZE)

    def render(self):
        self.renderer.clear()
        self.renderer.draw_map(self.game_map)
        self.renderer.draw_keys(self.keys)
        self.renderer.draw_enemies(self.enemies)
        self.renderer.draw_player(self.player)
        self.renderer.draw_hud(self.player, self.level)
        if self.game_over:
            self.renderer.draw_game_over(self.level)
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            t0 = time.perf_counter()
            self.update()
            self.logic_time += time.perf_counter() - t0
            self.frame_count += 1
            self.render()
            self.clock.tick(FPS)
            if self.frame_count >= FPS:
                avg = (self.logic_time / self.frame_count) * 1000
                pygame.display.set_caption(
                    f"像素地牢闯关 - 第{self.level}层 | 逻辑: {avg:.2f}ms")
                self.frame_count = 0
                self.logic_time = 0.0
        pygame.quit()
        sys.exit()


def main():
    Game().run()


if __name__ == "__main__":
    main()
