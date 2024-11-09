import pygame as pg
import math
import random
import numpy as np
from variables import *
import time

class Artist():
    def __init__(self, screen_x, screen_y, start_or_retry) -> None:
        self.screen = pg.display.set_mode((screen_x, screen_y))
        self.screen_x = screen_x
        self.screen_y = screen_y
        self.start_or_retry = start_or_retry
 
    def fill_screen(self, colour) -> None:
        self.screen.fill(colour)

    def draw_border(self, colour) -> None:
        pg.draw.rect(self.screen, colour, pg.Rect((0, 0), (screen_x, info_bar_start + round(screen_x*0.002))), width=5)

    def draw_start_text(self) -> None:
        text_pos = (self.screen_x/2 - round(self.screen_x*0.13), self.screen_y/2 - (self.screen_y/9))
        font = pg.font.SysFont('Arial', 30)
        self.screen.blit(font.render(f'Press Space to {self.start_or_retry}', True, colours['RED']), text_pos)

    def draw_game_over_screen(self) -> None:
        text1_pos = (self.screen_x/2 - round(self.screen_x/10), self.screen_y/2 - (self.screen_y/9))
        text2_pos = (text1_pos[0] - round(self.screen_x*0.03), text1_pos[1] + round(self.screen_y*(5/90)))
        font = pg.font.SysFont('Arial', 30)
        self.screen.blit(font.render('GAME OVER', True, colours['RED']), text1_pos)
        self.screen.blit(font.render('Press Esc to restart', True, colours['RED']), text2_pos)

    def draw_info_bar(self, lives, player_powerups, player_width) -> None:
        pg.draw.rect(self.screen, colours['GREY2'], pg.Rect((0, info_bar_start), (self.screen_x,self.screen_y - info_bar_start)), width=5)
        font = pg.font.SysFont('Arial', 30)
        self.screen.blit(font.render(f'Lives:', True, colours['RED']), (round(self.screen_x*0.02), info_bar_start + round(self.screen_x*0.02)))
        font = pg.font.SysFont('Arial', 25)
        self.screen.blit(font.render(f'{lives}', True, colours['GREY1']), (round(self.screen_x*(45/1000)), info_bar_start + round(self.screen_x*(58/1000))))
        font = pg.font.SysFont('Arial', 30)
        self.screen.blit(font.render(f'Active modifiers:', True, colours['RED']),(175, info_bar_start + 20))

        font = pg.font.SysFont('Arial', 15)
        for i, j in enumerate(list(all_powerup_types.keys())):
            power_name = all_powerup_types[j][0]
            if power_name != 'extra_life':
                col = colours['GREY1']
                if 'paddle_size' in power_name:
                    if player_width == player_default_width:
                        col = colours['GREY1']
                    elif 'up' in power_name and player_width == player_long:
                        col = colours['RED']
                    elif 'down' in power_name and player_width == player_short:
                        col = colours['RED']
                else:
                    if power_name in player_powerups:
                        col = colours['RED']
                    else:
                        col = colours['GREY1']
                self.screen.blit(font.render(j, True, col),(all_powerup_types[j][1], info_bar_start + self.screen_x*(65/850)))

    def draw_dummy_ball(self, level) -> None:
        self.screen.blit(
            pg.image.load(f'{assets_path}/player_sprites/ball_default.png').convert_alpha(),
            (ball_init_pos[level][0], ball_init_pos[level][1])
        )


class Paddle():
    def __init__(self, x, y, width, powerups, lives) -> None:
        self.x, self.y = x, y
        self.width, self.height = width, 15
        self.rect_center = (self.x + self.width / 2, self.y + self.height / 2)
        self.lives = lives
        self.speed = 10
        if 'paddle_speed' in powerups:
            self.speed = 15
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

    def check_laser_press(self, all_lasers, frame_count) -> "Laser":
        # Generate a laser object if laser key pressed and has powerup
        key = pg.key.get_pressed()
        generate_bolt = False

        # No laser bolts, always generate one
        if len(all_lasers) == 0:
            generate_bolt = True
        else:
            # Only generate another bolt if cooldown period has passed
            frames = [i[1] for i in all_lasers]
            if abs(frame_count - max(frames)) > laser_cooldown_time:
                generate_bolt = True

        # Generate bolt if all conditions are met
        if key[pg.K_UP] and generate_bolt:
            play_sound("laser_shot")
            laser_x = self.x + (self.width - laser_bolt_init_width)/2
            laser_y = self.y - laser_bolt_init_height
            laser_bolt = Laser(laser_x, laser_y)
            return laser_bolt

    def draw_paddle(self, artist) -> None:
        artist.screen.blit(self.image, (self.x, self.y))
    
    def change_sprite(self) -> None:
        new_sprite = self.sprite_dict.get(self.width, None)
        self.image = pg.image.load(f"{assets_path}/player_sprites/{new_sprite}.png").convert_alpha()


class Ball():
    def __init__(self, x, y, velocity, passthrough):
        self.velocity = velocity
        self.height = 10
        self.x, self.y = x, y
        self.passthrough = passthrough # Can the ball delete bricks without bouncing (requires powerup)
        self.image = pg.image.load(f"{assets_path}/player_sprites/ball_default.png").convert_alpha()
        self.unstop_image = pg.image.load(f"{assets_path}/player_sprites/ball_unstop.png").convert_alpha()
        return
    
    def move(self):
        self.x += self.velocity[0]; self.y += self.velocity[1]
        return

    def draw_ball(self, artist):
        img = self.image
        if self.passthrough:
            img = self.unstop_image          
        if (self.y + self.height) > (player_init_y + round(screen_y / 30)): # Don't draw if in the info bar section of the screen
            return
        artist.screen.blit(img, (self.x, self.y))
        return
        
    def change_speed_upon_brick_collide(
            self,
            brick_obj, 
            all_bricks, 
            all_powerups, 
            brick_boundaries, 
            direction, 
            dont_change_ball_speed, 
            negate_speed_x, 
            negate_speed_y
        ):
        # Coords to check boundaries
        coords = (
            (self.y,               self.x + self.height, self.x),
            (self.x + self.height, self.y + self.height, self.y),
            (self.y + self.height, self.x + self.height, self.x),
            (self.x,               self.y + self.height, self.y)
        )
        # Speeds to check direction of ball
        speeds = (
            (+self.velocity[1]), 
            (-self.velocity[0]), 
            (-self.velocity[1]), 
            (+self.velocity[0])
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
                
            if len(all_bricks) == 1:
                locked_brick = all_bricks[0]
                if locked_brick.health == 3:
                    # turn the padlocked brick into a normal 2-health brick
                    locked_brick.health -= 1

            brick_obj.generate_powerup(all_powerups)
        return brick_hit, all_bricks

    def check_collision(self, player, all_bricks, all_powerups, max_brick_y):
        ball_v_mag = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)

        # collision with paddle
        if abs(self.y + self.height - player.y) < 10:
            # calculate what the angle of reflection should be when hitting the paddle
            # this should vary from 90 deg if the ball hits the centre to almost zero if the ball hits the edges
            relative_x = self.x - player.x + self.height
            if -10 <= relative_x <= player.width + 10: # does it hit the paddle at this y coord
                angle_min = 20
                grad = 2 * ((90 - angle_min) / player.width)
                intercept = angle_min
                negate_speed = -1
                if relative_x > 0.5*(player.width - self.height):
                    relative_x = player.width - relative_x
                    negate_speed = 1

                if self.velocity[1] > 0: # This prevents collision glitches
                    angle = ((grad * relative_x) + intercept) * np.pi/180
                    if self.velocity[0] > 0:
                        play_sound("bounce")
                        self.velocity = (negate_speed*ball_v_mag*np.cos(angle), -ball_v_mag*np.sin(angle))
                        return None, all_bricks
                    elif self.velocity[0] < 0:
                        play_sound("bounce")
                        self.velocity = (negate_speed*ball_v_mag*np.cos(angle), -ball_v_mag*np.sin(angle))
                        return None, all_bricks

        # collision with brick
        if self.y < max_brick_y + 20:
            # Only check the bricks within a certain distance of the ball
            bricks_to_check = [i for i in all_bricks if math.sqrt((self.x - i.x)**2 + (self.y - i.y)**2) < 1.25*brick_default_width]
            all_bricks_coords = [(brick_obj.x, brick_obj.y) for brick_obj in bricks_to_check]

            if 'ball_pass_through' in player.powerups:
                negate_speed = 1
            else:
                negate_speed = -1
                
            for i, brick_obj in enumerate(bricks_to_check):
                dont_change_ball_speed = False
                if len(all_bricks) == 1:
                    if all_bricks[0].health < 3:      # Only change this variable if the brick is destructable (i.e., health 1 or 2)
                        dont_change_ball_speed = True # This variable prevents bugs when the ball is carried through to a new level

                # Left, right, top and bottom coords of the brick
                l, r, t, b = (
                    brick_obj.x, 
                    brick_obj.x + brick_default_width, 
                    brick_obj.y, 
                    brick_obj.y + brick_default_height
                )

                # Check whether there is a brick blocking the current one
                blocking_alive = (
                    True if (l, b) in all_bricks_coords else False,
                    True if (l - brick_default_width, t) in all_bricks_coords else False,
                    True if (l, t - brick_default_height) in all_bricks_coords else False,
                    True if (r, t) in all_bricks_coords else False,
                )

                # Hit brick from below
                if not blocking_alive[0]:
                    brick_hit, all_bricks = self.change_speed_upon_brick_collide(brick_obj, all_bricks, all_powerups, [b, l, r], 0, dont_change_ball_speed, 1, negate_speed)
                    if brick_hit:
                        break

                # Hit brick from left side
                if not blocking_alive[1]:
                    brick_hit, all_bricks = self.change_speed_upon_brick_collide(brick_obj, all_bricks, all_powerups, [l, t, b], 1, dont_change_ball_speed, negate_speed, 1)
                    if brick_hit:
                        break

                # Hit brick from above
                if not blocking_alive[2]:
                    brick_hit, all_bricks = self.change_speed_upon_brick_collide(brick_obj, all_bricks, all_powerups, [t, l, r], 2, dont_change_ball_speed, 1, negate_speed)
                    if brick_hit: 
                        break

                # Hit brick from right side
                if not blocking_alive[3]:
                    brick_hit, all_bricks = self.change_speed_upon_brick_collide(brick_obj, all_bricks, all_powerups, [r, t, b], 3, dont_change_ball_speed, negate_speed, 1)
                    if brick_hit:
                        break

        # Collision with walls
        if self.y < 5:
            if self.velocity[1] < 0: # Prevents getting stuck out of bounds
                self.velocity = (self.velocity[0], -self.velocity[1])
                play_sound("wall")
        
        if self.y + self.height > player_init_y + 20:
            return "dead", all_bricks

        # If close to either the left or right wall, reflect back
        in_bounds = 10 <= self.x <= screen_x - 10
        close_to_left = self.x < 5
        close_to_right = self.x + self.height > screen_x - 5
        if not in_bounds:
            if close_to_left:
                if self.velocity[0] < 0: # Prevents getting stuck out of bounds
                    play_sound("wall")
                    self.velocity = (-self.velocity[0], self.velocity[1])
            
            if close_to_right:
                if self.velocity[0] > 0: # Prevents getting stuck out of bounds
                    play_sound("wall")
                    self.velocity = (-self.velocity[0], self.velocity[1])

        return None, all_bricks


class Brick():
    def __init__(self, x, y, width, height, health):
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

    def draw_brick_sprite(self, artist):
        artist.screen.blit(getattr(self, f"image_h{self.health}"), (self.x, self.y))
        return

    def generate_powerup(self, all_powerups):
        pos = (self.x, self.y)
        generate_powerup = random.randint(0, 2)
        if generate_powerup == 0 and self.health < 3:
            power_type = all_powerup_types[list(all_powerup_types.keys())[random.randint(0, len(all_powerup_types.keys()) - 1)]][0]
            # power_type = 'laser' # for debug
            power_up = Powerup(pos[0], pos[1], True, power_type)
            all_powerups.append(power_up)
        return
    

class Powerup():
    def __init__(self, x, y, is_alive, power_type):
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
            if (self.x + self.width) >= player.x and self.x <= (player.x + player.width):
            
                # ball velocity magnitude
                b_v_mag_store = [math.sqrt(i[0]**2 + i[1]**2) for i in [ball_obj.velocity for ball_obj in old_balls_list]]

                # powerups changing paddle properties
                if self.power_type == 'paddle_size_up':
                    width_delta = 0
                    if player.width != player_long:
                        next_size = all_widths[all_widths.index(player.width) + 1]
                        width_delta = abs(player.width - next_size)

                    # new_x = player.x - width_delta/2
                    # new_width = player.width + width_delta
                    # player = Paddle(x=new_x, y=player.y, width=new_width, powerups=player.powerups, lives=player.lives)

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

                    # width_delta = abs(player.width - all_widths[all_widths.index(player.width) - 1]) if player.width != player_short else 0
                    # new_x = player.x + width_delta/2
                    # new_width = player.width - width_delta
                    # player = Paddle(x=new_x, y=player.y, width=new_width, powerups=player.powerups, lives=player.lives)

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

def play_sound(sound) -> None:
    pg.mixer.Sound.play(pg.mixer.Sound(f"{assets_path}/{sound}.wav"))

def update_powerups(powerup, player) -> None:
    player.powerups.append(powerup)
    player.powerups = list(set(player.powerups))
