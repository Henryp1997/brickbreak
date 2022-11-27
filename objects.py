import pygame as pg
import math
import random
import numpy as np

colours = {
    'BLUE': (0, 100, 200),
    'DARK_BLUE': (0,55,255),
    'RED' : (225, 25, 25),
    'YELLOW': (255, 255, 0),
    'GREEN': (0, 220, 40),
    'BLACK': (15, 15, 15),
    'WHITE': '#ffffff',
    'GREY1': '#d1d1d1',
    'GREY2': '#a1a1a1',
    'PINK': '#fc03f8',
    'PURPLE': '#7734eb',
    'ORANGE': '#f5a742',
    'ELEC_BLUE': '#59CBE8'
}

screen_x = 1000
screen_y = screen_x*(9/10)
player_default_width = 150
player_short = 100
player_long = 225
all_widths = [player_short,player_default_width,player_long]
player_init_x = (screen_x-player_default_width)/2
player_init_y = screen_y - 150
ball_init_x = 700
ball_init_y = screen_y - 600
ball_init_height = 10
ball_init_velocity = (-8,8)
laser_bolt_init_width = 5
laser_bolt_init_height = 25
brick_default_width = 70
brick_default_height = 30

info_bar_start = player_init_y + 40
all_powerup_types = {
    'Multi': ('multi',175),
    'Fast ball': ('ball_speed',220),
    'Unstoppable ball': ('ball_pass_through',288),
    'Laser': ('laser',400),
    'Fast paddle': ('paddle_speed',450),
    'Large paddle': ('paddle_size_up',540),
    'Small paddle': ('paddle_size_down',635),
    'Extra Life': ('extra_life',None)
}

screen = pg.display.set_mode((screen_x,screen_y))


class paddle(pg.sprite.Sprite):
    def __init__(self,x,y,width,powerups,lives):
        pg.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.width = width
        self.lives = lives
        if 'paddle_speed' in powerups:
            self.speed = 18
        else:
            self.speed = 12
        self.height = 15
        self.powerups = powerups
        self.rect = pg.Rect((self.x, self.y), (self.width, self.height))
        # self.image = pg.image.load('tosh.jpg')
        # self.size = self.image.get_size()
        # self.image = pg.transform.scale(self.image, ((int(self.size[0]/5.372)), int(self.size[1]/6.525)))
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
                if abs(frame_count - max(frames)) > 40:
                    generate_bolt = True
            if key[pg.K_UP] and generate_bolt:
                pg.mixer.Sound.play(pg.mixer.Sound('assets/laser_shot.wav'))
                laser_x = self.x + (self.width - laser_bolt_init_width)/2
                laser_y = self.y - laser_bolt_init_height
                laser_bolt = laser(laser_x, laser_y)
                return laser_bolt

    def draw_paddle(self):
        pg.draw.rect(screen, colours['RED'], self.rect, width=4, border_top_left_radius=4, border_top_right_radius=4, border_bottom_left_radius=4, border_bottom_right_radius=4)
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
        self.draw_ball()
        return

    def draw_ball(self):
        if self.passthrough:
            col = colours['PINK']
        else:
            col = colours['GREEN']
        if self.y + self.height > player_init_y + 30: # don't draw if in the info bar section of the screen
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
                        pg.mixer.Sound.play(pg.mixer.Sound("assets/bounce.wav"))
                        self.velocity = (negate_speed*ball_velocity_magnitude*np.cos(angle), -ball_velocity_magnitude*np.sin(angle))
                        return
                    elif self.velocity[0] < 0:
                        pg.mixer.Sound.play(pg.mixer.Sound("assets/bounce.wav"))
                        self.velocity = (negate_speed*ball_velocity_magnitude*np.cos(angle), -ball_velocity_magnitude*np.sin(angle))
                        return

        # collision with brick
        if not (self.y > max_brick_y + 20):
            # if ball_obj.passthrough:
            if 'ball_pass_through' in player.powerups:
                negate_speed = 1
            else:
                negate_speed = -1
            bricks_hit = 0
            for i, brick_obj in enumerate(all_bricks):
                if bricks_hit != 1:
                    brick_hit = False
                    l, r, t, b = (brick_obj.x, brick_obj.x + brick_default_width, brick_obj.y, brick_obj.y + brick_default_height) # left, right, top and bottom coords of the brick

                    # hit brick from below
                    if abs(int(self.y) - b) < 10:
                        if l <= ball_right and self.x <= r:
                            if self.velocity[1] < 0:
                                pg.mixer.Sound.play(pg.mixer.Sound("assets/smash.wav"))
                                self.velocity = (self.velocity[0], negate_speed*self.velocity[1])
                                bricks_hit = 1
                                brick_hit = True

                    # hit brick from left side
                    elif abs(int(ball_right) - l) < 10:
                        if t <= ball_bottom and self.y <= b:
                            if self.velocity[0] > 0:
                                pg.mixer.Sound.play(pg.mixer.Sound("assets/smash.wav"))
                                self.velocity = (negate_speed*self.velocity[0], self.velocity[1])
                                bricks_hit = 1
                                brick_hit = True
                            
                    # hit brick from above
                    elif abs(int(ball_bottom) - t) < 10:
                        if l <= ball_right and self.x <= r:
                            if self.velocity[1] > 0:
                                pg.mixer.Sound.play(pg.mixer.Sound("assets/smash.wav"))
                                self.velocity = (self.velocity[0], negate_speed*self.velocity[1])
                                bricks_hit = 1
                                brick_hit = True

                    # hit brick from right side
                    elif abs(int(self.x) - r) < 10: 
                        if t <= ball_bottom and self.y <= b:
                            if self.velocity[0] < 0:
                                pg.mixer.Sound.play(pg.mixer.Sound("assets/smash.wav"))
                                self.velocity = (negate_speed*self.velocity[0], self.velocity[1])
                                bricks_hit = 1
                                brick_hit = True                  

                    if brick_hit:
                        brick_obj.is_alive = False
                        brick_obj.generate_powerup(all_powerups)
                        all_bricks.pop(i)

        # collision with walls
        if self.y < 5:
            if self.velocity[1] < 0: # prevents getting stuck out of bounds
                self.velocity = (self.velocity[0], -self.velocity[1])
                pg.mixer.Sound.play(pg.mixer.Sound("assets/wall.wav"))
        
        if ball_bottom > player_init_y + 20:
            return "dead"

        if not 10 <= self.x <= screen_x - 10:
            if self.x < 5:
                if self.velocity[0] < 0: # prevents getting stuck out of bounds
                    pg.mixer.Sound.play(pg.mixer.Sound("assets/wall.wav"))
                    self.velocity = (-self.velocity[0], self.velocity[1])
            
            if ball_right > screen_x - 5:
                if self.velocity[0] > 0: # prevents getting stuck out of bounds
                    pg.mixer.Sound.play(pg.mixer.Sound("assets/wall.wav"))
                    self.velocity = (-self.velocity[0], self.velocity[1])

        return

class brick():
    def __init__(self,x,y,width,height,is_alive):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_alive = is_alive
        return

    def draw_brick_sprite(self):
        x = self.x
        y = self.y
        brick_default_width = self.width
        brick_default_height = self.height
        # draw main rectangle
        pg.draw.rect(screen, colours['GREY1'], pg.Rect((x,y),(brick_default_width,brick_default_height)), width=0)
        # draw brick border
        pg.draw.rect(screen, colours['BLACK'], pg.Rect((x,y),(brick_default_width,brick_default_height)), width=2)
        # draw lines for brick pattern
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
        pos = (int(self.x + (self.width/4)), int(self.y + (self.height/4)))
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
        self.width = brick_default_width/2
        self.height = brick_default_height/2
        self.is_alive = is_alive
        self.power_type = power_type
        return

    def update_position(self):
        self.y += self.speed
        if self.power_type == 'paddle_size_up':
            pg.draw.rect(screen, colours['GREEN'], (self.x, self.y, self.width, self.height))
        elif self.power_type == 'paddle_size_down':
            pg.draw.rect(screen, colours['BLUE'], (self.x, self.y, self.width, self.height))
        elif self.power_type == 'paddle_speed':
            pg.draw.rect(screen, colours['YELLOW'], (self.x, self.y, self.width, self.height))
        elif self.power_type == 'ball_speed':
            pg.draw.rect(screen, colours['PINK'], (self.x, self.y, self.width, self.height))
        elif self.power_type == 'ball_pass_through':
            pg.draw.rect(screen, colours['GREY1'], (self.x, self.y, self.width, self.height))
        elif self.power_type == 'multi':
            pg.draw.rect(screen, colours['PURPLE'], (self.x, self.y, self.width, self.height))
        elif self.power_type == 'laser':
            pg.draw.rect(screen, colours['ORANGE'], (self.x, self.y, self.width, self.height))
        else:
            pg.draw.rect(screen, colours['RED'], (self.x, self.y, self.width, self.height))
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
                        # 242 comes from the sum of 11**2 and 11**2 --> increasing speed from initial (8,8) to (11,11)
                        new_velocity = (math.sqrt(242/128)*b_v_store[k][0], math.sqrt(242/128)*b_v_store[k][1]) if abs(b_v_mag_store[k]**2 - 128) < 1 else b_v_store[k]
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
                        pg.mixer.Sound.play(pg.mixer.Sound("assets/smash.wav"))
                        bricks_hit = 1
                        brick_obj.is_alive = False
                        brick_obj.generate_powerup(all_powerups)
                        all_bricks.pop(i)        
                        return "dead"
