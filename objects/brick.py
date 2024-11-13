

import random
import pygame as pg
from variables import assets_path, all_powerup_types
from objects.powerup import Powerup

class Brick():
    def __init__(self, artist, x, y, width, height, health):
        self.artist = artist
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.health, self.is_alive = health, True
        self.image_h3 = pg.image.load(f"{assets_path}/brick_h3.png").convert_alpha()
        self.image_h2 = pg.image.load(f"{assets_path}/brick_h2.png").convert_alpha()
        self.image_h1 = pg.image.load(f"{assets_path}/brick_h1.png").convert_alpha()
        self.image_h3_rect = self.image_h3.get_rect(topleft=(self.x, self.y))
        self.image_h2_rect = self.image_h2.get_rect(topleft=(self.x, self.y))
        self.image_h1_rect = self.image_h1.get_rect(topleft=(self.x, self.y))
        return

    def draw_brick_sprite(self):
        self.artist.screen.blit(getattr(self, f"image_h{self.health}"), (self.x, self.y))
        return

    def generate_powerup(self, all_powerups):
        pos = (self.x, self.y)
        generate_powerup = random.randint(0, 2)
        if generate_powerup == 0 and self.health < 3:
            power_type = all_powerup_types[list(all_powerup_types.keys())[random.randint(0, len(all_powerup_types.keys()) - 1)]][0]
            # power_type = 'paddle_speed' # for debug
            power_up = Powerup(self.artist, pos[0], pos[1], True, power_type)
            all_powerups.append(power_up)
        return
