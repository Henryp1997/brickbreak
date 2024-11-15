import time
import pygame as pg
from variables import(
    assets_path,
    player_default_speed,
    screen_x,
    laser_cooldown_time,
    laser_bolt_init_width,
    laser_bolt_init_height,
    player_init_x,
    player_init_y,
    player_default_width
)
from utils import play_sound
from objects.laser_bolt import Laser

class Paddle():
    __slots__ = [
        "artist",
        "x",
        "y",
        "width",
        "height", 
        "rect_center",
        "lives",
        "speed", 
        "height",
        "powerups", 
        "rect", 
        "sprite_dict", 
        "image", 
        "time_got_laser",
        "time_shot_laser"
    ]
    def __init__(self, artist, x, y, width, powerups, lives) -> None:
        self.artist = artist
        self.x, self.y = x, y
        self.width, self.height = width, 15
        self.rect_center = (self.x + self.width / 2, self.y + self.height / 2)
        self.lives = lives
        self.speed = player_default_speed
        self.height = 15
        self.powerups = powerups
        self.rect = pg.Rect((self.x, self.y), (self.width, self.height))
        self.sprite_dict = {
            150: "paddle",
            225: "paddle_long",
            100: "paddle_short"
        }
        self.image = pg.image.load(f"{assets_path}/player_sprites/paddle.png").convert_alpha()
        self.time_got_laser = 0
        self.time_shot_laser = 0
    
    def check_movement(self) -> None:
        key = pg.key.get_pressed()
        # Move paddle left or right depending on key press
        # and whether paddle is in bounds or not
        if key[pg.K_LEFT]:
            if self.x + self.width/2 > 5:
                self.x -= self.speed
                self.rect.move_ip(-self.speed, 0)
        if key[pg.K_RIGHT]:
            if self.x + self.width/2 < screen_x - 5:
                self.x += self.speed
                self.rect.move_ip(self.speed, 0)

    def check_laser_press(self, all_lasers) -> "Laser":
        # Generate a laser object if laser key pressed and has powerup
        key = pg.key.get_pressed()
        generate_bolt = False

        # No laser bolts, always generate one
        if len(all_lasers) == 0:
            generate_bolt = True
        else:
            # Only generate another bolt if cooldown period has passed
            if time.time() - self.time_shot_laser > 0.75:
                generate_bolt = True

        # Generate bolt if all conditions are met
        if key[pg.K_UP] and generate_bolt:
            play_sound("laser_shot")
            laser_x = self.x + (self.width - laser_bolt_init_width)/2
            laser_y = self.y - laser_bolt_init_height
            laser_bolt = Laser(laser_x, laser_y)
            self.time_shot_laser = time.time() # Update for cooldown time
            return laser_bolt

    def draw_paddle(self) -> None:
        self.artist.screen.blit(self.image, (self.x, self.y))
    
    def change_sprite(self) -> None:
        new_sprite = self.sprite_dict.get(self.width, None)
        self.image = pg.image.load(f"{assets_path}/player_sprites/{new_sprite}.png").convert_alpha()

    def update_powerups(self, powerup) -> None:
        self.powerups.append(powerup)
        self.powerups = list(set(self.powerups))

    def reset_attributes(self) -> None:
        self.x, self.y = player_init_x, player_init_y
        self.powerups = []
        self.width = player_default_width
        self.speed = player_default_speed
        self.change_sprite()