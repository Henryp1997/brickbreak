import pygame as pg
from variables import *
from utils import play_sound

class Laser():
    def __init__(self, x, y) -> None:
        self.x, self.y = x, y
        self.speed = -20
        self.width, self.height = laser_bolt_init_width, laser_bolt_init_height
    
    def draw_laser(self, artist) -> None:
        pg.draw.rect(artist.screen, colours["ELEC_BLUE"], (self.x, self.y, self.width, self.height))

    def move(self) -> None:
        self.y += self.speed
    
    def check_collision(self, all_bricks, all_powerups, max_brick_y) -> None:
        if self.y > max_brick_y + 20:
            return
        bricks_hit = 0
        for i, brick_obj in enumerate(all_bricks):
            if bricks_hit != 1:
                l, r, b = (brick_obj.x, brick_obj.x + brick_default_width, brick_obj.y + brick_default_height) # left, right and bottom coords of the brick
                if abs(self.y - b) < 10:
                    if l <= self.x <= r:
                        bricks_hit = 1
                        if brick_obj.health < 3:
                            brick_obj.health -= 1
                            if brick_obj.health == 0:
                                play_sound("smash")
                                brick_obj.is_alive = False
                                brick_obj.generate_powerup(all_powerups)
                                all_bricks.pop(i)
                            else:
                                play_sound("wall")
                            return "dead"
                        elif brick_obj.health == 3:
                            play_sound("wall")
                            return "dead"
                        if len(all_bricks) == 1:
                            locked_brick = all_bricks[0]
                            if locked_brick.health == 3:
                                # turn the padlocked brick into a normal 2-health brick
                                locked_brick.health -= 1
