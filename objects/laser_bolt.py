import pygame as pg
from consts import(
    LASER_BOLT_INIT_WIDTH,
    LASER_BOLT_INIT_HEIGHT,
    LASER_SPEED,
    COLOURS,
    BRICK_DEFAULT_WIDTH,
    BRICK_DEFAULT_HEIGHT
)
from utils import play_sound

class Laser():
    def __init__(self, x, y, artist) -> None:
        self.x, self.y = x, y
        self.artist = artist
        self.speed = LASER_SPEED
        self.width, self.height = LASER_BOLT_INIT_WIDTH, LASER_BOLT_INIT_HEIGHT
    

    def draw_laser(self) -> None:
        pg.draw.rect(self.artist.screen, COLOURS["ELEC_BLUE"], (self.x, self.y, self.width, self.height))


    def move(self, dt) -> None:
        self.y += self.speed * dt
    

    def check_collision(self, all_bricks, all_powerups, max_brick_y) -> None:
        if self.y > max_brick_y + 20:
            return
        bricks_hit = 0
        for i, brick_obj in enumerate(all_bricks):
            if bricks_hit != 1:
                # Left, right and bottom coords of the brick
                l, r, b = (brick_obj.x, brick_obj.x + BRICK_DEFAULT_WIDTH, brick_obj.y + BRICK_DEFAULT_HEIGHT)
                
                # Interpolate laser position to see if collision will happen on next frame
                if (self.y + self.speed) < b:
                    if l <= (self.x + self.width) and self.x <= r:
                        self.y = b # Snap laser to brick bottom
                        self.draw_laser()
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
                                # Turn the padlocked brick into a normal 2-health brick
                                locked_brick.health -= 1
