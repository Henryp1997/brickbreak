

import random
import pygame as pg
from consts import ASSETS_PATH, ALL_POWERUP_TYPES, NUM_POWERUPS, BRICK_DEFAULT_WIDTH, BRICK_DEFAULT_HEIGHT
from objects.powerup import Powerup

class Brick():
    __slots__ = [
        "artist",
        "x",
        "y",
        "center",
        "gridx",
        "gridy",
        "width",
        "height",
        "health",
        "is_alive",
        "image_h3",
        "image_h2",
        "image_h1",
        "image_h3_rect",
        "image_h2_rect",
        "image_h1_rect"
    ]
    def __init__(self, artist, gridx, gridy, width, height, health) -> None:
        self.artist = artist
        self.gridx, self.gridy = gridx, gridy
        self.x, self.y = self.convert_grid_to_coords()
        self.center = (self.x + 0.5*BRICK_DEFAULT_WIDTH, self.y + 0.5*BRICK_DEFAULT_HEIGHT)
        self.width, self.height = width, height
        self.health, self.is_alive = health, True
        self.image_h3 = pg.image.load(f"{ASSETS_PATH}/brick_h3.png").convert_alpha()
        self.image_h2 = pg.image.load(f"{ASSETS_PATH}/brick_h2.png").convert_alpha()
        self.image_h1 = pg.image.load(f"{ASSETS_PATH}/brick_h1.png").convert_alpha()
        self.image_h3_rect = self.image_h3.get_rect(topleft=(self.x, self.y))
        self.image_h2_rect = self.image_h2.get_rect(topleft=(self.x, self.y))
        self.image_h1_rect = self.image_h1.get_rect(topleft=(self.x, self.y))


    def convert_grid_to_coords(self) -> tuple:
        # Add 5 to account for wall and ceiling thickness
        return (self.gridx * BRICK_DEFAULT_WIDTH + 5, self.gridy * BRICK_DEFAULT_HEIGHT + 5)


    def draw_brick_sprite(self) -> None:
        self.artist.screen.blit(getattr(self, f"image_h{self.health}"), (self.x, self.y))


    def generate_powerup(self, all_powerups) -> None:
        generate_powerup = random.randint(0, 2)
        if generate_powerup == 0 and self.health < 3:
            seed = random.randint(0, NUM_POWERUPS - 1)
            power_type = list(ALL_POWERUP_TYPES.values())[seed][0]
            power_name = list(ALL_POWERUP_TYPES.keys())[seed]
            # power_type, power_name = "laser", "Laser" # for debug
            power_up = Powerup(self.artist, self.x, self.y, True, power_name, power_type)
            all_powerups.append(power_up)
