import pygame as pg
import math
import random
import numpy as np
from variables import *
import time

class paddle(pg.sprite.Sprite):
    def __init__(self,x,y,width,powerups,lives):
        pg.sprite.Sprite.__init__(self)
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
        self.rect.center = (self.x+self.width/2,self.y+self.height/2)
        return
    
    def check_keys(self,all_lasers,frame_count):
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
                pg.mixer.Sound.play(pg.mixer.Sound(f'{assets_path}/laser_shot.wav'))
                laser_x = self.x + (self.width - laser_bolt_init_width)/2
                laser_y = self.y - laser_bolt_init_height
                laser_bolt = laser(laser_x, laser_y)
                return laser_bolt

    def draw_paddle(self):
        screen.blit(self.image, (self.x, self.y))
        # pg.draw.rect(screen, colours['RED'], self.rect, width=4, border_top_left_radius=4, border_top_right_radius=4, border_bottom_left_radius=4, border_bottom_right_radius=4)
        return
    
class ball():
    def __init__(self,x,y,velocity,passthrough):
        self.velocity = velocity
        self.height = 10
        self.x = x
        self.y = y
        self.passthrough = passthrough
        self.right = self.x + self.height # width and height the same because it's a square
        self.bottom = self.y + self.height
        return
    
    def move(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.right += self.velocity[0]
        self.bottom += self.velocity[1]
        return

    def draw_ball(self):
        if self.passthrough:
            col = colours['PINK']
        else:
            col = colours['GREEN']
        if self.y + self.height > player_init_y + round(screen_y/30): # don't draw if in the info bar section of the screen
            return
        ball_centre = (self.x + 0.5*self.height, self.y + 0.5*self.height)
        pg.draw.circle(screen, col, ball_centre, radius=0.5*self.height)
        return
        
    def check_collision(self,player,all_bricks,all_powerups,max_brick_y):
        ball_right = self.x + self.height
        ball_bottom = self.y + self.height
        ball_velocity_magnitude = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)

        # collision with paddle
        if abs(ball_bottom - player.y) < 10:
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
                        pg.mixer.Sound.play(pg.mixer.Sound(f"{assets_path}/bounce.wav"))
                        self.velocity = (negate_speed*ball_velocity_magnitude*np.cos(angle), -ball_velocity_magnitude*np.sin(angle))
                        return
                    elif self.velocity[0] < 0:
                        pg.mixer.Sound.play(pg.mixer.Sound(f"{assets_path}/bounce.wav"))
                        self.velocity = (negate_speed*ball_velocity_magnitude*np.cos(angle), -ball_velocity_magnitude*np.sin(angle))
                        return

        # collision with brick
        if not (self.y > max_brick_y + 20):
            if 'ball_pass_through' in player.powerups:
                negate_speed = 1
            else:
                negate_speed = -1
            bricks_hit = 0
            for i, brick_obj in enumerate(all_bricks):
                dont_change_ball_speed = False
                if len(all_bricks) == 1:
                    dont_change_ball_speed = True # this variable prevents bugs when the ball is carried through to a new level
                if bricks_hit != 1:
                    brick_hit = False
                    l, r, t, b = (brick_obj.x, brick_obj.x + brick_default_width, brick_obj.y, brick_obj.y + brick_default_height) # left, right, top and bottom coords of the brick

                    # hit brick from below
                    if abs(int(self.y) - b) < 10:
                        if l <= ball_right and self.x <= r:
                            if self.velocity[1] < 0:
                                if not dont_change_ball_speed:
                                    self.velocity = (self.velocity[0], negate_speed*self.velocity[1])
                                else:
                                    self.velocity = (self.velocity[0], self.velocity[1])
                                bricks_hit = 1
                                brick_hit = True

                    # hit brick from left side
                    elif abs(int(ball_right) - l) < 10:
                        if t <= ball_bottom and self.y <= b:
                            if self.velocity[0] > 0:
                                if not dont_change_ball_speed:
                                    self.velocity = (negate_speed*self.velocity[0], self.velocity[1])
                                else:
                                    self.velocity = (self.velocity[0], self.velocity[1])
                                bricks_hit = 1
                                brick_hit = True
                            
                    # hit brick from above
                    elif abs(int(ball_bottom) - t) < 10:
                        if l <= ball_right and self.x <= r:
                            if self.velocity[1] > 0:
                                if not dont_change_ball_speed:
                                    self.velocity = (self.velocity[0], negate_speed*self.velocity[1])
                                else:
                                    self.velocity = (self.velocity[0], self.velocity[1])
                                bricks_hit = 1
                                brick_hit = True

                    # hit brick from right side
                    elif abs(int(self.x) - r) < 10: 
                        if t <= ball_bottom and self.y <= b:
                            if self.velocity[0] < 0:
                                if not dont_change_ball_speed:
                                    self.velocity = (self.velocity[0], negate_speed*self.velocity[1])
                                else:
                                    self.velocity = (self.velocity[0], self.velocity[1])
                                bricks_hit = 1
                                brick_hit = True               

                    if brick_hit:
                        brick_obj.health -= 1
                        if brick_obj.health == 0:
                            pg.mixer.Sound.play(pg.mixer.Sound(f"{assets_path}/smash.wav"))
                            brick_obj.is_alive = False
                            all_bricks.pop(i)
                        else:
                            pg.mixer.Sound.play(pg.mixer.Sound(f"{assets_path}/wall.wav"))
                        brick_obj.generate_powerup(all_powerups)

        # collision with walls
        if self.y < 5:
            if self.velocity[1] < 0: # prevents getting stuck out of bounds
                self.velocity = (self.velocity[0], -self.velocity[1])
                pg.mixer.Sound.play(pg.mixer.Sound(f"{assets_path}/wall.wav"))
        
        if ball_bottom > player_init_y + 20:
            return "dead"

        if not 10 <= self.x <= screen_x - 10:
            if self.x < 5:
                if self.velocity[0] < 0: # prevents getting stuck out of bounds
                    pg.mixer.Sound.play(pg.mixer.Sound(f"{assets_path}/wall.wav"))
                    self.velocity = (-self.velocity[0], self.velocity[1])
            
            if ball_right > screen_x - 5:
                if self.velocity[0] > 0: # prevents getting stuck out of bounds
                    pg.mixer.Sound.play(pg.mixer.Sound(f"{assets_path}/wall.wav"))
                    self.velocity = (-self.velocity[0], self.velocity[1])

        return

class brick():
    def __init__(self,x,y,width,height,double_hit,health,is_alive):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.health = health
        self.is_alive = is_alive
        self.double_hit = double_hit
        if self.double_hit:
            default_image = 'brick_h2.png'
        else:
            default_image = 'brick_h1.png'
        self.image = pg.image.load(f'{assets_path}/{default_image}').convert_alpha()
        self.image_cracked = pg.image.load(f'{assets_path}/brick_h1.png').convert_alpha()
        return

    def draw_brick_sprite(self, cracked):
        sprite = True
        if cracked:
            screen.blit(self.image_cracked, (self.x, self.y))
            return
        screen.blit(self.image, (self.x, self.y))
        
        if not sprite:
            x = self.x
            y = self.y
            brick_default_width = self.width
            brick_default_height = self.height
            # draw main rectangle
            pg.draw.rect(screen, colours['GREY1'], pg.Rect((x,y),(brick_default_width,brick_default_height)), width=0)
            # draw brick border
            pg.draw.rect(screen, colours['BLACK'], pg.Rect((x,y),(brick_default_width,brick_default_height)), width=2)
            # draw lines for cracked pattern
            if cracked:
                arr = [(19, 29, 32, 6), (46, 8, 41, 3), (4, 15, 19, 7), (17, 2, 24, 5), (19, 15, 6, 28), (31, 16, 22, 14), (46, 8, 32, 7), (14, 2, 1, 4), (44, 14, 66, 6), (68, 27, 56, 1)]
                for i in range(10):
                    pg.draw.line(screen, colours['BLACK'], (x+arr[i][0],y+arr[i][1]),(x+arr[i][2],y+arr[i][3]))
            # brick pattern
            for j in range(3):
                y_start = y + (brick_default_height*j)/3
                y_end = y_start + (brick_default_height)/3
                if j != 0:
                    pg.draw.line(screen, colours['BLACK'], (x, y_start), (x + brick_default_width, y_start))
                if j % 2 == 1:
                    for i in range(1,6):
                        if i % 2 == 1:
                            x_line = x + (brick_default_width*i)/6
                            pg.draw.line(screen, colours['BLACK'], (x_line, y_start), (x_line, y_end))
                elif j % 2 == 0:
                    if j == 0:
                        y_start += 2
                        y_end -= 1
                    elif j == 2:
                        y_end -=3
                    for i in range(1,3):
                        x_line = x + (brick_default_width*i)/3
                        pg.draw.line(screen, colours['BLACK'], (x_line, y_start), (x_line, y_end))
        return

    def generate_powerup(self,all_powerups):
        # pos = (int(self.x + (self.width/4)), int(self.y + (self.height/4)))
        pos = (self.x, self.y)
        generate_powerup = random.randint(0,2)
        # generate_powerup = 0
        if generate_powerup == 0:
            power_type = all_powerup_types[list(all_powerup_types.keys())[random.randint(0,len(all_powerup_types.keys())-1)]][0]
            # power_type = 'laser'
            power_up = powerup(pos[0],pos[1],True,power_type)
            all_powerups.append(power_up)
        return

class powerup():
    def __init__(self,x,y,is_alive,power_type):
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
    
    def check_collisions(self,player,old_balls_list,all_powerups):
        new_balls_list = []
        if self.y > player_init_y - 20:
            if (self.x + self.width) >= player.x and self.x <= (player.x + player.width):
                
                # old parameter values
                p_x_store = player.x
                p_y_store = player.y
                p_w_store = player.width
                p_l_store = player.lives

                b_x_store = [i.x for i in old_balls_list]
                b_y_store = [i.y for i in old_balls_list]
                b_v_store = [i.velocity for i in old_balls_list]
                b_pass_store = [i.passthrough for i in old_balls_list]
                b_v_mag_store = [math.sqrt(i[0]**2 + i[1]**2) for i in b_v_store]

                # powerups changing paddle properties
                if self.power_type == 'paddle_size_up':
                    width_delta = abs(p_w_store - all_widths[all_widths.index(player.width) + 1]) if p_w_store != player_long else 0
                    new_x = p_x_store - width_delta/2
                    new_width = p_w_store + width_delta
                    player = paddle(x=new_x, y=p_y_store, width=new_width, powerups=player.powerups, lives=p_l_store)
                    new_balls_list = old_balls_list
                elif self.power_type == 'paddle_size_down':
                    width_delta = abs(p_w_store - all_widths[all_widths.index(player.width) - 1]) if p_w_store != player_short else 0
                    new_x = p_x_store + width_delta/2
                    new_width = p_w_store - width_delta
                    player = paddle(x=new_x, y=p_y_store, width=new_width, powerups=player.powerups, lives=p_l_store)
                    new_balls_list = old_balls_list
                elif self.power_type == 'paddle_speed':
                    powerups = [i for i in player.powerups if i != "paddle_speed"]
                    powerups.append("paddle_speed")
                    player = paddle(x=p_x_store, y=p_y_store, width=p_w_store, powerups=powerups, lives=p_l_store)
                    new_balls_list = old_balls_list
                elif self.power_type == 'laser':
                    with open(f'{assets_path}/got_laser.txt', 'w') as f:
                        f.write(f'{time.time()}')
                    powerups = [i for i in player.powerups if i != "laser"]
                    powerups.append("laser")
                    player = paddle(x=p_x_store, y=p_y_store, width=p_w_store, powerups=powerups, lives=p_l_store)
                    new_balls_list = old_balls_list
                elif self.power_type == 'extra_life':
                    powerups = [i for i in player.powerups if i != 'extra_life']
                    powerups.append('extra_life')
                    player = paddle(x=p_x_store, y=p_y_store, width=p_w_store, powerups=powerups, lives=p_l_store + 1)
                    new_balls_list = old_balls_list

                # powerups changing ball properties
                # even though we're considering the ball here, still store powerups in the player object
                elif self.power_type == 'ball_speed':
                    for k, ball_obj in enumerate(old_balls_list):
                        new_velocity = (math.sqrt(162/98)*b_v_store[k][0], math.sqrt(162/98)*b_v_store[k][1]) if abs(b_v_mag_store[k]**2 - 98) < 1 else b_v_store[k]
                        ball_obj = ball(x=b_x_store[k], y=b_y_store[k], velocity=new_velocity, passthrough=b_pass_store[k])
                        new_balls_list.append(ball_obj)
                    powerups = [i for i in player.powerups if i != "ball_speed"]
                    powerups.append("ball_speed")
                    player.powerups = powerups

                elif self.power_type == 'ball_pass_through':
                    for k, ball_obj in enumerate(old_balls_list):
                        ball_obj = ball(x=b_x_store[k], y=b_y_store[k], velocity=b_v_store[k], passthrough=True)            
                        new_balls_list.append(ball_obj)
                    powerups = [i for i in player.powerups if i != "ball_pass_through"]
                    powerups.append("ball_pass_through")
                    player.powerups = powerups 

                elif self.power_type == 'multi':

                    for k, ball_obj in enumerate(old_balls_list):
                        vx_dir, vy_dir = b_v_store[k][0]/abs(b_v_store[k][0]), b_v_store[k][1]/abs(b_v_store[k][1])
                        angle = np.arccos(b_v_store[k][0]/b_v_mag_store[k])
                        new_balls_list.append(ball_obj)

                        for angle in [angle - np.pi/6, angle + np.pi/3]:
                            angle1 = angle - np.pi/6
                            vx, vy = abs(b_v_mag_store[k]*(np.cos(angle1)))*vx_dir, abs(b_v_mag_store[k]*(np.sin(angle1)))*vy_dir
                            if abs(vx) < 1:
                                vx = vx/abs(vx) # set the velocity component to 1 if it's less than 1
                                vy = (vy/abs(vy)) * (math.sqrt(b_v_mag_store[k]**2 - 1))

                            elif abs(vy) < 1:
                                vy = vy/abs(vy) # set the velocity component to 1 if it's less than 1
                                vx = (vx/abs(vx)) * (math.sqrt(b_v_mag_store[k]**2 - 0))
          
                            ball_obj1 = ball(x=b_x_store[k], y=b_y_store[k], velocity=(vx,vy), passthrough=b_pass_store[k])
                            new_balls_list.append(ball_obj1)
                    
                    powerups = [i for i in player.powerups if i != "multi"]
                    powerups.append("multi")
                    player.powerups = powerups
        
            else: # player didn't grab powerup
                for ball_obj in old_balls_list:
                    new_balls_list.append(ball_obj)
            
            self.is_alive = False # kill the powerup object
            all_powerups.pop(all_powerups.index(self))

        else:
            for ball_obj in old_balls_list:
                new_balls_list.append(ball_obj)

        return player, new_balls_list

class laser():
    def __init__(self,x,y):
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
    
    def check_collision(self,all_bricks,all_powerups,max_brick_y):
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
                            pg.mixer.Sound.play(pg.mixer.Sound(f"{assets_path}/smash.wav"))
                            brick_obj.is_alive = False
                            brick_obj.generate_powerup(all_powerups)
                            all_bricks.pop(i)
                        else:
                            pg.mixer.Sound.play(pg.mixer.Sound(f"{assets_path}/wall.wav"))
                        return "dead"
