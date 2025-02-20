import pygame as pg
import math
import time
import numpy as np
from consts import(
    BALL_DEFAULT_VELOCITY,
    BALL_FAST_VELOCITY_MAG,
    BRICK_DEFAULT_WIDTH,
    BRICK_DEFAULT_HEIGHT,
    ALL_POWERUP_TYPES,
    ASSETS_PATH,
    PLAYER_INIT_Y,
    PLAYER_LONG,
    PLAYER_SHORT,
    PLAYER_FAST_SPEED,
    POWERUP_SPEED
)
from objects.ball import Ball

class Powerup():
    __slots__ = [
        "artist",
        "x",
        "y",
        "width",
        "height",
        "speed",
        "is_alive",
        "power_type",
        "image"
    ]
    def __init__(self, artist, x, y, is_alive, power_name, power_type) -> None:
        self.artist = artist
        self.x, self.y = x, y
        self.width, self.height = BRICK_DEFAULT_WIDTH, BRICK_DEFAULT_HEIGHT
        self.speed = POWERUP_SPEED
        self.is_alive = is_alive
        self.power_type = power_type
        img_name = ALL_POWERUP_TYPES[power_name][2]
        self.image = pg.image.load(f"{ASSETS_PATH}/powerup_sprites/{img_name}.png").convert_alpha()


    def move(self, artist, dt) -> None:
        self.y += self.speed * dt
        artist.screen.blit(self.image, (self.x, self.y))
    

    def check_gained_powerup(self, player, old_balls_list, all_powerups) -> tuple:
        new_balls_list = []

        # Only check collision with player if close to the paddle
        if self.y > PLAYER_INIT_Y - 20:
            grabbed_powerup = (self.x + self.width) >= player.x and self.x <= (player.x + player.width)
            if grabbed_powerup:
                # powerups changing paddle properties
                if self.power_type == "paddle_size_up":
                    player.change_width(width=PLAYER_LONG, min_plus_1=+1)
                    new_balls_list = old_balls_list

                elif self.power_type == "paddle_size_down":
                    player.change_width(width=PLAYER_SHORT, min_plus_1=-1)
                    new_balls_list = old_balls_list

                elif self.power_type == "paddle_speed":
                    player.speed = PLAYER_FAST_SPEED
                    player.update_powerups("paddle_speed")
                    new_balls_list = old_balls_list

                elif self.power_type == "laser":
                    player.time_got_laser = time.perf_counter() # Record the time the player got the laser powerup
                    player.update_powerups("laser")
                    new_balls_list = old_balls_list

                elif self.power_type == "extra_life":                   
                    player.lives += 1
                    new_balls_list = old_balls_list

                # powerups changing ball properties
                # even though we're considering the ball here, still store powerups in the player object
                elif self.power_type == "ball_speed":
                    bfm = BALL_FAST_VELOCITY_MAG
                    bdv = BALL_DEFAULT_VELOCITY[0] # Just get the Vx component as |Vx| = |Vy| for default V
                    bfm_mag = 2 * bfm**2
                    bdv_mag = 2 * bdv**2
                    # Ball velocity magnitude
                    for ball_obj in old_balls_list:

                        new_velocity = (
                            math.sqrt(bfm_mag/bdv_mag)*ball_obj.velocity[0], # Compare magnitude of fast speed to slow speed to change vector
                            math.sqrt(bfm_mag/bdv_mag)*ball_obj.velocity[1]
                        ) if abs(ball_obj.v_mag()**2 - bdv_mag) < 1 else ball_obj.velocity

                        ball_obj.velocity = new_velocity
                        new_balls_list.append(ball_obj)
                    player.update_powerups("ball_speed")

                elif self.power_type == "ball_pass_through":
                    for ball_obj in old_balls_list:
                        ball_obj.passthrough = True
                        new_balls_list.append(ball_obj)
                    player.update_powerups("ball_pass_through") 

                elif self.power_type == "multi":
                    for ball_obj in old_balls_list:
                        new_balls_list.append(ball_obj)

                        theta = ball_obj.v_angle()

                        # Produce two new balls 30 degrees to the left and right of current ball
                        for i, angle in enumerate((theta - np.pi/6, theta + np.pi/6)):
                            if i == 0:
                                if angle < 0:
                                    angle = 11*np.pi/6 - theta
                            elif i == 1:
                                if angle > 2*np.pi:
                                    angle -= 2*np.pi

                            new_ball = Ball(
                                x=ball_obj.x,
                                y=ball_obj.y,
                                velocity=ball_obj.v_comps(ball_obj.v_mag(), angle),
                                passthrough=ball_obj.passthrough)
                            new_balls_list.append(new_ball)
   
                    player.update_powerups("multi")

                self.is_alive = False # kill the powerup object
                all_powerups.pop(all_powerups.index(self))

                # Update info bar with newly obtained powerup
                self.artist.draw_info_bar(player.lives, player.powerups, player.width)
                pg.display.update()

            else: # player didn't grab powerup
                for ball_obj in old_balls_list:
                    new_balls_list.append(ball_obj)
            
        else:
            for ball_obj in old_balls_list:
                new_balls_list.append(ball_obj)

        return player, new_balls_list
