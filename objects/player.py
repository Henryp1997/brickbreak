import time
import pygame as pg
from consts import(
    ASSETS_PATH,
    PLAYER_DEFAULT_SPEED,
    SCREEN_X,
    LASER_BOLT_INIT_WIDTH,
    LASER_BOLT_INIT_HEIGHT,
    PLAYER_INIT_X,
    PLAYER_INIT_Y,
    PLAYER_DEFAULT_WIDTH,
    ALL_PLAYER_WIDTHS
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
        "powerup_gained",
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
        self.speed = PLAYER_DEFAULT_SPEED
        self.height = 15
        self.powerups = powerups
        self.powerup_gained = False
        self.rect = pg.Rect((self.x, self.y), (self.width, self.height))
        self.sprite_dict = {
            150: "paddle",
            225: "paddle_long",
            100: "paddle_short"
        }
        self.image = pg.image.load(f"{ASSETS_PATH}/player_sprites/paddle.png").convert_alpha()
        self.time_got_laser = 0
        self.time_shot_laser = 0
    

    def move(self, dt) -> None:
        key = pg.key.get_pressed()
        # Move paddle left or right depending on key press
        # and whether paddle is in bounds or not
        if key[pg.K_LEFT]:
            if self.x + self.width/2 > 5:
                self.x -= self.speed * dt
                self.rect.move_ip(-self.speed*dt, 0)
        if key[pg.K_RIGHT]:
            if self.x + self.width/2 < SCREEN_X - 5:
                self.x += self.speed * dt
                self.rect.move_ip(self.speed*dt, 0)


    def check_laser_press(self, all_lasers) -> "Laser":
        # Generate a laser object if laser key pressed and has powerup
        key = pg.key.get_pressed()
        generate_bolt = False

        # No laser bolts, always generate one
        if len(all_lasers) == 0:
            generate_bolt = True
        else:
            # Only generate another bolt if cooldown period has passed
            if time.perf_counter() - self.time_shot_laser > 0.75:
                generate_bolt = True

        # Generate bolt if all conditions are met
        if key[pg.K_UP] and generate_bolt:
            play_sound("laser_shot")
            laser_x = self.x + (self.width - LASER_BOLT_INIT_WIDTH)/2
            laser_y = self.y - LASER_BOLT_INIT_HEIGHT
            laser_bolt = Laser(laser_x, laser_y, artist=self.artist)
            self.time_shot_laser = time.perf_counter() # Update for cooldown time
            return laser_bolt


    def draw_paddle(self) -> None:
        self.artist.screen.blit(self.image, (self.x, self.y))
    

    def change_sprite(self) -> None:
        new_sprite = self.sprite_dict.get(self.width, None)
        self.image = pg.image.load(f"{ASSETS_PATH}/player_sprites/{new_sprite}.png").convert_alpha()


    def update_powerups(self, powerup) -> None:
        self.powerups.append(powerup)
        self.powerups = list(set(self.powerups))


    def reset_attributes(self) -> None:
        self.x, self.y = PLAYER_INIT_X, PLAYER_INIT_Y
        self.powerups = []
        self.width = PLAYER_DEFAULT_WIDTH
        self.speed = PLAYER_DEFAULT_SPEED
        self.change_sprite()


    def change_width(self, width, min_plus_1) -> None:
        width_delta = 0
        if self.width != width:
            next_size = ALL_PLAYER_WIDTHS[ALL_PLAYER_WIDTHS.index(self.width) + min_plus_1]
            width_delta = abs(self.width - next_size)

        # Update player properties
        self.x = self.x - (min_plus_1 * width_delta/2)
        self.width = self.width + (min_plus_1 * width_delta)
        self.change_sprite()


    def has_laser(self) -> bool:
        return "laser" in self.powerups


    def remove_powerup(self, powerup) -> None:
        self.powerups.pop(self.powerups.index(powerup))
