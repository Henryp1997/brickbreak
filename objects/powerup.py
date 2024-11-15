import pygame as pg
import math
import time
import numpy as np
from variables import(
    brick_default_width,
    brick_default_height,
    all_powerup_types,
    assets_path,
    player_init_y,
    player_long,
    player_short,
    player_fast_speed,
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
    def __init__(self, artist, x, y, is_alive, power_type):
        self.artist = artist
        self.x, self.y = x, y
        self.width, self.height = brick_default_width, brick_default_height
        self.speed = 3
        self.is_alive = is_alive
        self.power_type = power_type
        img_name = all_powerup_types[list(all_powerup_types.keys())[[j[0] for i, j in enumerate(list(all_powerup_types.values()))].index(power_type)]][2]
        self.image = pg.image.load(f"{assets_path}/powerup_sprites/{img_name}.png").convert_alpha()
        return

    def update_position(self, artist):
        self.y += self.speed
        artist.screen.blit(self.image, (self.x, self.y))
        return
    
    def check_collisions(self, player, old_balls_list, all_powerups):
        new_balls_list = []
        if self.y > player_init_y - 20:
            grabbed_powerup = (self.x + self.width) >= player.x and self.x <= (player.x + player.width)
            if grabbed_powerup:
                # powerups changing paddle properties
                if self.power_type == 'paddle_size_up':
                    player.change_width(width=player_long, min_plus_1=+1)
                    new_balls_list = old_balls_list

                elif self.power_type == 'paddle_size_down':
                    player.change_width(width=player_short, min_plus_1=-1)
                    new_balls_list = old_balls_list

                elif self.power_type == 'paddle_speed':
                    player.speed = player_fast_speed
                    player.update_powerups("paddle_speed")
                    new_balls_list = old_balls_list

                elif self.power_type == 'laser':
                    player.time_got_laser = time.time() # Record the time the player got the laser powerup
                    player.update_powerups("laser")
                    new_balls_list = old_balls_list

                elif self.power_type == 'extra_life':                   
                    player.lives += 1
                    new_balls_list = old_balls_list

                # powerups changing ball properties
                # even though we're considering the ball here, still store powerups in the player object
                elif self.power_type == 'ball_speed':
                    # Ball velocity magnitude
                    v_mag = [math.sqrt(i[0]**2 + i[1]**2) for i in [ball_obj.velocity for ball_obj in old_balls_list]]
                    for k, ball_obj in enumerate(old_balls_list):

                        new_velocity = (
                            math.sqrt(162/98)*ball_obj.velocity[0],
                            math.sqrt(162/98)*ball_obj.velocity[1]
                        ) if abs(v_mag[k]**2 - 98) < 1 else ball_obj.velocity

                        ball_obj.velocity = new_velocity
                        new_balls_list.append(ball_obj)
                    player.update_powerups("ball_speed")

                elif self.power_type == 'ball_pass_through':
                    for k, ball_obj in enumerate(old_balls_list):
                        ball_obj.passthrough = True
                        new_balls_list.append(ball_obj)
                    player.update_powerups("ball_pass_through") 

                elif self.power_type == 'multi':
                    for k, ball_obj in enumerate(old_balls_list):
                        new_balls_list.append(ball_obj)

                        theta = calculate_ball_angle(ball_obj.velocity)

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
                                velocity=(
                                    +v_mag[k] * np.cos(angle), 
                                    -v_mag[k] * np.sin(angle) # need to negate vy since down is positive and up is negative
                                ), 
                                passthrough=ball_obj.passthrough)
                            new_balls_list.append(new_ball)
   
                    player.update_powerups("multi")
        
                # Update info bar with newly obtained powerup
                self.artist.draw_info_bar(player.lives, player.powerups, player.width)
                pg.display.update()

            else: # player didn't grab powerup
                for ball_obj in old_balls_list:
                    new_balls_list.append(ball_obj)
            
            self.is_alive = False # kill the powerup object
            all_powerups.pop(all_powerups.index(self))

        else:
            for ball_obj in old_balls_list:
                new_balls_list.append(ball_obj)

        return player, new_balls_list

def calculate_ball_angle(vel):
    vx, vy = vel
    try:
        # upper right quadrant
        if vx > 0 and vy <= 0:
            theta = np.arctan(-vy / vx)
        # upper left quadrant
        elif vx < 0 and vy <= 0:
            theta = np.pi + np.arctan(-vy / vx)
        # lower left quadrant
        elif vx < 0 and vy > 0:
            theta = np.pi + np.arctan(-vy / vx)
        # lower right quadrant
        elif vx > 0 and vy > 0:
            theta = 2*np.pi + np.arctan(-vy / vx)

    except ZeroDivisionError:
        if vy < 0:
            theta = np.pi/2
        else:
            theta = 3*np.pi/2
    
    return theta
