import pygame as pg
import math
import time
import numpy as np
from variables import *
from utils import update_powerups
from objects.ball import Ball

class Powerup():
    def __init__(self, artist, x, y, is_alive, power_type):
        self.artist = artist
        self.speed = 3
        self.x, self.y = x, y
        self.width, self.height = brick_default_width, brick_default_height
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
                # ball velocity magnitude
                b_v_mag_store = [math.sqrt(i[0]**2 + i[1]**2) for i in [ball_obj.velocity for ball_obj in old_balls_list]]

                # powerups changing paddle properties
                if self.power_type == 'paddle_size_up':
                    width_delta = 0
                    if player.width != player_long:
                        next_size = all_widths[all_widths.index(player.width) + 1]
                        width_delta = abs(player.width - next_size)

                    # Update player properties
                    player.x = player.x - width_delta/2
                    player.width = player.width + width_delta
                    player.change_sprite()

                    new_balls_list = old_balls_list

                elif self.power_type == 'paddle_size_down':
                    width_delta = 0
                    if player.width != player_short:
                        next_size = all_widths[all_widths.index(player.width) - 1]
                        width_delta = abs(player.width - next_size)

                    # Update player properties
                    player.x = player.x + width_delta/2
                    player.width = player.width - width_delta
                    player.change_sprite()

                    new_balls_list = old_balls_list

                elif self.power_type == 'paddle_speed':
                    update_powerups("paddle_speed", player)
                    new_balls_list = old_balls_list

                elif self.power_type == 'laser':
                    player.time_got_laser = time.time() # Record the time the player got the laser powerup
                    update_powerups("laser", player)
                    new_balls_list = old_balls_list

                elif self.power_type == 'extra_life':                   
                    player.lives += 1
                    new_balls_list = old_balls_list

                # powerups changing ball properties
                # even though we're considering the ball here, still store powerups in the player object
                elif self.power_type == 'ball_speed':
                    for k, ball_obj in enumerate(old_balls_list):
                        new_velocity = (math.sqrt(162/98)*ball_obj.velocity[0], math.sqrt(162/98)*ball_obj.velocity[1]) if abs(b_v_mag_store[k]**2 - 98) < 1 else ball_obj.velocity
                        ball_obj = Ball(x=ball_obj.x, y=ball_obj.y, velocity=new_velocity, passthrough=ball_obj.passthrough)
                        new_balls_list.append(ball_obj)
                    update_powerups("ball_speed", player)

                elif self.power_type == 'ball_pass_through':
                    for k, ball_obj in enumerate(old_balls_list):
                        ball_obj = Ball(x=ball_obj.x, y=ball_obj.y, velocity=ball_obj.velocity, passthrough=True)            
                        new_balls_list.append(ball_obj)
                    update_powerups("ball_pass_through", player) 

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

                            # need to negate vy since down is positive and up is negative
                            vx, vy = b_v_mag_store[k] * np.cos(angle), - b_v_mag_store[k] * np.sin(angle)
                            new_ball = Ball(x=ball_obj.x, y=ball_obj.y, velocity=(vx, vy), passthrough=ball_obj.passthrough)
                            new_balls_list.append(new_ball)
   
                    update_powerups("multi", player)
        
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
