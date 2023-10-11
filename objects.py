import pygame as pg
import math
import random
import numpy as np
from variables import *
import time

class paddle():
    def __init__(self, x, y, width, powerups, lives):
        self.x = x
        self.y = y
        self.width = width
        self.lives = lives
        if 'paddle_speed' in powerups:
            self.speed = 15
        else:
            self.speed = 10
        self.height = 15
        self.powerups = powerups
        self.rect = pg.Rect((self.x, self.y), (self.width, self.height))
        img_name = 'paddle' if self.width == 150 else 'paddle_long' if self.width == 225 else 'paddle_short' if self.width == 100 else None
        self.image = pg.image.load(f'{assets_path}/player_sprites/{img_name}.png').convert_alpha()
        self.rect.center = (self.x+self.width/2, self.y+self.height/2)
        return
    
    def check_keys(self, all_lasers, frame_count):
        key = pg.key.get_pressed()
        if key[pg.K_LEFT]:
            if self.x + self.width/2 > 5:
                self.x -= self.speed
                self.rect.move_ip(-self.speed, 0)
        if key[pg.K_RIGHT]:
            if self.x + self.width/2 < screen_x - 5:
                self.x += self.speed
                self.rect.move_ip(self.speed, 0)
        if 'laser' in self.powerups:
            generate_bolt = False
            if len(all_lasers) == 0:
                generate_bolt = True
            else:
                frames = [i[1] for i in all_lasers]
                if abs(frame_count - max(frames)) > laser_cooldown_time:
                    generate_bolt = True
            if key[pg.K_UP] and generate_bolt:
                play_sound("laser_shot")
                laser_x = self.x + (self.width - laser_bolt_init_width)/2
                laser_y = self.y - laser_bolt_init_height
                laser_bolt = laser(laser_x, laser_y)
                return laser_bolt

    def draw_paddle(self):
        screen.blit(self.image, (self.x, self.y))
        return
    
class ball():
    def __init__(self, x, y, velocity, passthrough):
        self.velocity = velocity
        self.height = 10
        self.x = x
        self.y = y
        self.passthrough = passthrough
        self.image = pg.image.load(f'{assets_path}/player_sprites/ball_default.png').convert_alpha()
        self.unstop_image = pg.image.load(f'{assets_path}/player_sprites/ball_unstop.png').convert_alpha()
        return
    
    def move(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        return

    def draw_ball(self):
        if self.passthrough:
            img = self.unstop_image
        else:
            img = self.image
        if self.y + self.height > player_init_y + round(screen_y/30): # don't draw if in the info bar section of the screen
            return
        screen.blit(img, (self.x, self.y))
        return
        
    def change_speed_upon_brick_collide(self, brick_obj, all_bricks, all_powerups, brick_boundaries, direction, dont_change_ball_speed, negate_speed_x, negate_speed_y):
        # coords to check boundaries
        coords = (
            (self.y, self.x + self.height, self.x),
            (self.x + self.height, self.y + self.height, self.y),
            (self.y + self.height, self.x + self.height, self.x),
            (self.x, self.y + self.height, self.y)
        )
        # speeds to check direction of ball
        speeds = (
            (self.velocity[1]), 
            (-self.velocity[0]), 
            (-self.velocity[1]), 
            (self.velocity[0])
        )
        brick_hit = False
        if abs(coords[direction][0] - brick_boundaries[0]) < 10:
            if brick_boundaries[1] <= coords[direction][1] and coords[direction][2] <= brick_boundaries[2]:
                if speeds[direction] < 0:
                    if not dont_change_ball_speed:
                        if direction in [0, 2]:
                            if negate_speed_y == 1 and brick_obj.health > 1:
                                negate_speed_y *= -1
                        elif direction in [1, 3]:
                            if negate_speed_x == 1 and brick_obj.health > 1:
                                negate_speed_x *= -1
                        self.velocity = (negate_speed_x*self.velocity[0], negate_speed_y*self.velocity[1])
                    brick_hit = True 
        if brick_hit:
            if brick_obj.health < 3:
                brick_obj.health -= 1
            if brick_obj.health == 0:
                play_sound("smash")
                brick_obj.is_alive = False
                all_bricks.pop(all_bricks.index(brick_obj))
            else:
                play_sound("wall")
            brick_obj.generate_powerup(all_powerups)
        return brick_hit

    def check_collision(self, player, all_bricks, all_powerups, max_brick_y):
        ball_velocity_magnitude = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)

        # collision with paddle
        if abs(self.y + self.height - player.y) < 10:
            # calculate what the angle of reflection should be when hitting the paddle
            # this should vary from 90 deg if the ball hits the centre to almost zero if the ball hits the edges
            relative_x = self.x - player.x + self.height
            if -10 <= relative_x <= player.width + 10: # does it hit the paddle at this y coord
                angle_min = 20
                grad = 2*((90-angle_min)/player.width)
                intercept = angle_min
                negate_speed = -1
                if relative_x > 0.5*(player.width - self.height):
                    relative_x = player.width - relative_x
                    negate_speed = 1

                if self.velocity[1] > 0: # prevent glitches
                    angle = ((grad * relative_x) + intercept) * np.pi/180
                    if self.velocity[0] > 0:
                        play_sound("bounce")
                        self.velocity = (negate_speed*ball_velocity_magnitude*np.cos(angle), -ball_velocity_magnitude*np.sin(angle))
                        return
                    elif self.velocity[0] < 0:
                        play_sound("bounce")
                        self.velocity = (negate_speed*ball_velocity_magnitude*np.cos(angle), -ball_velocity_magnitude*np.sin(angle))
                        return

        # collision with brick
        if self.y < max_brick_y + 20:
            bricks_to_check = [i for i in all_bricks if math.sqrt((self.x - i.x)**2 + (self.y - i.y)**2) < 1.25*brick_default_width]
            all_bricks_coords = [(brick_obj.x, brick_obj.y) for brick_obj in bricks_to_check]

            if 'ball_pass_through' in player.powerups:
                negate_speed = 1
            else:
                negate_speed = -1
                
            for i, brick_obj in enumerate(bricks_to_check):
                dont_change_ball_speed = False
                if len(all_bricks) == 1:
                    if all_bricks[0].health < 3: # only change this variable if the brick is destructable (i.e., health 1 or 2)
                        dont_change_ball_speed = True # this variable prevents bugs when the ball is carried through to a new level

                # left, right, top and bottom coords of the brick
                l, r, t, b = (
                    brick_obj.x, 
                    brick_obj.x + brick_default_width, 
                    brick_obj.y, 
                    brick_obj.y + brick_default_height
                )

                # check whether there is a brick blocking the current one
                blocking_alive = (
                    True if (l, b) in all_bricks_coords else False,
                    True if (l - brick_default_width, t) in all_bricks_coords else False,
                    True if (l, t - brick_default_height) in all_bricks_coords else False,
                    True if (r, t) in all_bricks_coords else False,
                )

                # hit brick from below
                if not blocking_alive[0]:
                    if self.change_speed_upon_brick_collide(brick_obj, all_bricks, all_powerups, [b, l, r], 0, dont_change_ball_speed, 1, negate_speed):
                        break

                # hit brick from left side
                if not blocking_alive[1]:
                    if self.change_speed_upon_brick_collide(brick_obj, all_bricks, all_powerups, [l, t, b], 1, dont_change_ball_speed, negate_speed, 1):
                        break

                # hit brick from above
                if not blocking_alive[2]:
                    if self.change_speed_upon_brick_collide(brick_obj, all_bricks, all_powerups, [t, l, r], 2, dont_change_ball_speed, 1, negate_speed): 
                        break

                # hit brick from right side
                if not blocking_alive[3]:
                    if self.change_speed_upon_brick_collide(brick_obj, all_bricks, all_powerups, [r, t, b], 3, dont_change_ball_speed, negate_speed, 1):
                        break

        # collision with walls
        if self.y < 5:
            if self.velocity[1] < 0: # prevents getting stuck out of bounds
                self.velocity = (self.velocity[0], -self.velocity[1])
                play_sound("wall")
        
        if self.y + self.height > player_init_y + 20:
            return "dead"

        if not 10 <= self.x <= screen_x - 10:
            if self.x < 5:
                if self.velocity[0] < 0: # prevents getting stuck out of bounds
                    play_sound("wall")
                    self.velocity = (-self.velocity[0], self.velocity[1])
            
            if self.x + self.height > screen_x - 5:
                if self.velocity[0] > 0: # prevents getting stuck out of bounds
                    play_sound("wall")
                    self.velocity = (-self.velocity[0], self.velocity[1])

        return

class brick():
    def __init__(self, x, y, width, height, health, is_alive):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.health = health
        self.is_alive = is_alive
        default_image = f'brick_h{self.health}.png'
        self.image = pg.image.load(f'{assets_path}/{default_image}').convert_alpha()
        self.image_cracked = pg.image.load(f'{assets_path}/brick_h1.png').convert_alpha()
        self.image_rect = self.image.get_rect(topleft=(self.x, self.y))
        self.image_cracked_rect = self.image_cracked.get_rect(topleft=(self.x, self.y))
        return

    def draw_brick_sprite(self):
        if self.health == 1:
            screen.blit(self.image_cracked, (self.x, self.y))
            return
        screen.blit(self.image, (self.x, self.y))
        return

    def generate_powerup(self, all_powerups):
        pos = (self.x, self.y)
        generate_powerup = random.randint(0, 2)
        # generate_powerup = 0
        if generate_powerup == 0 and self.health < 3:
            power_type = all_powerup_types[list(all_powerup_types.keys())[random.randint(0, len(all_powerup_types.keys()) - 1)]][0]
            # power_type = 'multi'
            power_up = powerup(pos[0], pos[1], True, power_type)
            all_powerups.append(power_up)
        return

class powerup():
    def __init__(self, x, y, is_alive, power_type):
        self.speed = 3
        self.x = x
        self.y = y
        self.width = brick_default_width
        self.height = brick_default_height
        self.is_alive = is_alive
        self.power_type = power_type
        img_name = all_powerup_types[list(all_powerup_types.keys())[[j[0] for i, j in enumerate(list(all_powerup_types.values()))].index(power_type)]][2]
        self.image = pg.image.load(f'{assets_path}/powerup_sprites/{img_name}.png').convert_alpha()
        return

    def update_position(self):
        self.y += self.speed
        screen.blit(self.image, (self.x, self.y))
        return
    
    def check_collisions(self, player, old_balls_list, all_powerups):
        new_balls_list = []
        if self.y > player_init_y - 20:
            if (self.x + self.width) >= player.x and self.x <= (player.x + player.width):
            
                # ball velocity magnitude
                b_v_mag_store = [math.sqrt(i[0]**2 + i[1]**2) for i in [ball_obj.velocity for ball_obj in old_balls_list]]

                # powerups changing paddle properties
                if self.power_type == 'paddle_size_up':
                    width_delta = abs(player.width - all_widths[all_widths.index(player.width) + 1]) if player.width != player_long else 0
                    new_x = player.x - width_delta/2
                    new_width = player.width + width_delta
                    player = paddle(x=new_x, y=player.y, width=new_width, powerups=player.powerups, lives=player.lives)
                    new_balls_list = old_balls_list

                elif self.power_type == 'paddle_size_down':
                    width_delta = abs(player.width - all_widths[all_widths.index(player.width) - 1]) if player.width != player_short else 0
                    new_x = player.x + width_delta/2
                    new_width = player.width - width_delta
                    player = paddle(x=new_x, y=player.y, width=new_width, powerups=player.powerups, lives=player.lives)
                    new_balls_list = old_balls_list

                elif self.power_type == 'paddle_speed':
                    update_powerups("paddle_speed", player)
                    new_balls_list = old_balls_list

                elif self.power_type == 'laser':
                    with open(f'{assets_path}/got_laser.txt', 'w') as f:
                        f.write(f'{time.time()}')
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
                        ball_obj = ball(x=ball_obj.x, y=ball_obj.y, velocity=new_velocity, passthrough=ball_obj.passthrough)
                        new_balls_list.append(ball_obj)
                    update_powerups("ball_speed", player)

                elif self.power_type == 'ball_pass_through':
                    for k, ball_obj in enumerate(old_balls_list):
                        ball_obj = ball(x=ball_obj.x, y=ball_obj.y, velocity=ball_obj.velocity, passthrough=True)            
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
                            new_ball = ball(x=ball_obj.x, y=ball_obj.y, velocity=(vx, vy), passthrough=ball_obj.passthrough)
                            new_balls_list.append(new_ball)
   
                    update_powerups("multi", player)
        
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

class laser():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = -20
        self.width = laser_bolt_init_width
        self.height = laser_bolt_init_height
    
    def draw_laser(self):
        pg.draw.rect(screen, colours['ELEC_BLUE'], (self.x, self.y, self.width, self.height))
        return

    def move(self):
        self.y += self.speed
        return
    
    def check_collision(self, all_bricks, all_powerups, max_brick_y):
        if self.y > max_brick_y + 20:
            return
        bricks_hit = 0
        for i, brick_obj in enumerate(all_bricks):
            if bricks_hit != 1:
                l, r, b = (brick_obj.x, brick_obj.x + brick_default_width, brick_obj.y + brick_default_height) # left, right and bottom coords of the brick
                if abs(self.y - b) < 10:
                    if l <= self.x <= r:
                        bricks_hit = 1
                        brick_obj.health -= 1
                        if brick_obj.health == 0:
                            play_sound("smash")
                            brick_obj.is_alive = False
                            brick_obj.generate_powerup(all_powerups)
                            all_bricks.pop(i)
                        else:
                            play_sound("wall")
                        return "dead"

def play_sound(sound):
    pg.mixer.Sound.play(pg.mixer.Sound(f"{assets_path}/{sound}.wav"))

def update_powerups(powerup, player):
    player.powerups.append(powerup)
    player.powerups = list(set(player.powerups))
    return