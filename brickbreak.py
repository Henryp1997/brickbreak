import pygame as pg
from pygame.locals import *
import sys
import math
import random
import numpy as np

pg.init()
# Setting up colour objects
colours = {
    'BLUE': (0, 100, 200),
    'DARK_BLUE': (0,55,255),
    'RED' : (225, 25, 25),
    'YELLOW': (255, 255, 0),
    'GREEN': (0, 220, 40),
    'BLACK': (15, 15, 15),
    'WHITE': (255, 255, 255),
    'GREY1': '#d1d1d1',
    'GREY2': '#a1a1a1',
    'PINK': '#fc03f8',
    'PURPLE': '#7734eb'
}

screen_x = 1000
screen_y = 900
player_default_width = 200
player_short = 100
player_long = 300
player_init_x = (screen_x-player_default_width)/2
player_init_y = screen_y - 150
ball_init_x = 600
ball_init_y = screen_y - 500
ball_init_velocity = (-8,8)
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
pg.display.set_caption("Brickbreaker")

class paddle(pg.sprite.Sprite):
    def __init__(self,x,y,width,powerups):
        pg.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.width = width
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
    
    def check_keys(self):
        key = pg.key.get_pressed()
        if key[pg.K_LEFT]:
            if self.x + self.width/2 > 5:
                self.x -= self.speed
                self.rect.move_ip(-self.speed, 0)
        if key[pg.K_RIGHT]:
            if self.x + self.width/2 < screen_x - 5:
                self.x += self.speed
                self.rect.move_ip(self.speed, 0)

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
        ball_obj.x += ball_obj.velocity[0]
        ball_obj.y += ball_obj.velocity[1]
        ball_obj.right += ball_obj.velocity[0]
        ball_obj.bottom += ball_obj.velocity[1]
        ball_obj.draw_ball()
        return

    def draw_ball(self):
        if self.passthrough:
            col = colours['PINK']
        else:
            col = colours['GREEN']
        if self.y + self.height > player_init_y + 30:
            return
        pg.draw.rect(screen, col, pg.Rect((self.x, self.y), (self.height,self.height)))
        return
        
    def check_collision(self,player,all_bricks):
        ball_right = self.x + self.height
        ball_bottom = self.y + self.height
        ball_velocity_magnitude = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)

        # collision with paddle
        if abs(ball_bottom - player.y) < 10:
            # calculate what the angle of reflection should be when hitting the paddle
            # this should vary from 90 deg if the ball hits the centre to almost zero if the ball hits the edges
            relative_x = self.x - player.x + self.height
            if 0 <= relative_x <= player.width: # does it hit the paddle at this y coord
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
        if ball_obj.passthrough:
            negate_speed = 1
        else:
            negate_speed = -1
        bricks_hit = 0
        for i, brick_obj in enumerate(all_bricks):
            if bricks_hit != 1:
                brick_hit = False
                l, r, t, b = (brick_obj.x, brick_obj.x + brick_width, brick_obj.y, brick_obj.y + brick_height) # left, right, top and bottom coords of the brick
                # hit brick from left side
                if abs(int(ball_right) - l) < 10:
                    if t <= ball_bottom and self.y <= b:
                        if self.velocity[0] > 0:
                            pg.mixer.Sound.play(pg.mixer.Sound("assets/smash.wav"))
                            self.velocity = (negate_speed*self.velocity[0], self.velocity[1])
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

                # hit brick from above
                elif abs(int(ball_bottom) - t) < 10:
                    if l <= ball_right and self.x <= r:
                        if self.velocity[1] > 0:
                            pg.mixer.Sound.play(pg.mixer.Sound("assets/smash.wav"))
                            self.velocity = (self.velocity[0], negate_speed*self.velocity[1])
                            bricks_hit = 1
                            brick_hit = True

                # hit brick from below
                elif abs(int(self.y) - b) < 10:
                    if l <= ball_right and self.x <= r:
                        if self.velocity[1] < 0:
                            pg.mixer.Sound.play(pg.mixer.Sound("assets/smash.wav"))
                            self.velocity = (self.velocity[0], negate_speed*self.velocity[1])
                            bricks_hit = 1
                            brick_hit = True

                if brick_hit:
                    brick_obj.is_alive = False
                    brick_obj.generate_powerup()
                    all_bricks.pop(i)

        # collision with walls
        if self.y < 5:
            if self.velocity[1] < 0: # prevents getting stuck out of bounds
                self.velocity = (self.velocity[0], -self.velocity[1])
                pg.mixer.Sound.play(pg.mixer.Sound("assets/wall.wav"))
        
        if ball_bottom > player_init_y + 20:
            return "dead"

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
        brick_width = self.width
        brick_height = self.height
        # draw main rectangle
        pg.draw.rect(screen, colours['GREY1'], pg.Rect((x,y),(brick_width,brick_height)), width=0)
        # draw brick border
        pg.draw.rect(screen, colours['BLACK'], pg.Rect((x,y),(brick_width,brick_height)), width=2)
        # draw lines for brick pattern
        for j in range(3):
            y_start = y + (brick_height*j)/3
            y_end = y_start + (brick_height)/3
            if j != 0:
                pg.draw.line(screen, colours['BLACK'], (x, y_start), (x + brick_width, y_start))
            if j % 2 == 1:
                for i in range(1,6):
                    if i % 2 == 1:
                        x_line = x + (brick_width*i)/6
                        pg.draw.line(screen, colours['BLACK'], (x_line, y_start), (x_line, y_end))
            elif j % 2 == 0:
                if j == 0:
                    y_start += 2
                    y_end -= 1
                elif j == 2:
                    y_end -=3
                for i in range(1,3):
                    x_line = x + (brick_width*i)/3
                    pg.draw.line(screen, colours['BLACK'], (x_line, y_start), (x_line, y_end))
        return

    def generate_powerup(self):
        pos = (int(self.x + (self.width/4)), int(self.y + (self.height/4)))
        generate_powerup = random.randint(0,2)
        if generate_powerup == 0:
            power_type = all_powerup_types[list(all_powerup_types.keys())[random.randint(0,len(all_powerup_types.keys())-1)]][0]
            power_up = powerup(pos[0],pos[1],True,power_type)
            all_powerups.append(power_up)
        return

class powerup():
    def __init__(self,x,y,is_alive,power_type):
        self.speed = 3
        self.x = x
        self.y = y
        self.width = brick_width/2
        self.height = brick_height/2
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
        else:
            pg.draw.rect(screen, colours['RED'], (self.x, self.y, self.width, self.height))
        return
    
    def check_collisions(self,player,old_balls_list):
        new_balls_list = []
        if self.y > player_init_y - 20:
            if (self.x + self.width) >= player.x and self.x <= (player.x + player.width):

                # old parameter values
                player_x_old = player.x
                player_y_old = player.y
                player_width_old = player.width

                ball_x_old = [i.x for i in old_balls_list]
                ball_y_old = [i.y for i in old_balls_list]
                ball_velocity_old = [i.velocity for i in old_balls_list]
                ball_passthrough_old = [i.passthrough for i in old_balls_list]
                ball_velocity_mag_old = [(i[0]**2 + i[1]**2) for i in ball_velocity_old]

                # powerups changing paddle properties
                if self.power_type == 'paddle_size_up':
                    new_x = player_x_old - 50 if player_width_old != player_long else player_x_old
                    new_width = player_width_old + 100 if player_width_old != player_long else player_width_old
                    player = paddle(x=new_x, y=player_y_old, width=new_width, powerups=player.powerups)
                    new_balls_list = old_balls_list
                elif self.power_type == 'paddle_size_down':
                    new_x = player_x_old + 50 if player_width_old != player_short else player_x_old
                    new_width = player_width_old - 100 if player_width_old != player_short else player_width_old
                    player = paddle(x=new_x, y=player_y_old, width=new_width,powerups=player.powerups)
                    new_balls_list = old_balls_list
                elif self.power_type == 'paddle_speed':
                    powerups = [i for i in player.powerups if i != "paddle_speed"]
                    powerups.append("paddle_speed")
                    player = paddle(x=player_x_old, y=player_y_old, width=player_width_old, powerups=powerups)
                    new_balls_list = old_balls_list

                # powerups changing ball properties
                # even though we're considering the ball here, still store powerups in the player object
                elif self.power_type == 'ball_speed':
                    for k, ball_obj in enumerate(old_balls_list):
                        # 242 comes from the sum of 11**2 and 11**2 --> increasing speed from initial (8,8) to (11,11)
                        new_velocity = (math.sqrt(242/128)*ball_velocity_old[k][0], math.sqrt(242/128)*ball_velocity_old[k][1]) if abs(ball_velocity_mag_old[k] - 128) < 1 else ball_velocity_old[k]
                        ball_obj = ball(x=ball_x_old[k], y=ball_x_old[k], velocity=new_velocity, passthrough=ball_passthrough_old[k])
                        new_balls_list.append(ball_obj)
                    powerups = [i for i in player.powerups if i != "ball_speed"]
                    powerups.append("ball_speed")
                    player.powerups = powerups

                elif self.power_type == 'ball_pass_through':
                    for k, ball_obj in enumerate(old_balls_list):
                        ball_obj = ball(x=ball_x_old[k], y=ball_x_old[k], velocity=ball_velocity_old[k], passthrough=True)            
                        new_balls_list.append(ball_obj)
                    powerups = [i for i in player.powerups if i != "ball_pass_through"]
                    powerups.append("ball_pass_through")
                    player.powerups = powerups 

                elif self.power_type == 'multi':

                    for k, ball_obj in enumerate(old_balls_list):
                        # split one ball into three
                        # x_memory = ball_obj.x
                        # y_memory = ball_obj.y
                        # velocity_memory = ball_obj.velocity
                        # passthrough_memory = ball_obj.passthrough

                        ball_velocity_mag_old = math.sqrt(ball_velocity_mag_old[k])

                        velocity_mag_memory = math.sqrt(ball_velocity_old[k][0]**2 + ball_velocity_old[k][1]**2)
                        vx_dir, vy_dir = ball_velocity_old[k][0]/abs(ball_velocity_old[k][0]), ball_velocity_old[k][1]/abs(ball_velocity_old[k][1])
                        angle = np.arccos(ball_velocity_old[k][0]/velocity_mag_memory)
                        new_balls_list.append(ball_obj)

                        for angle in [angle - np.pi/6, angle + np.pi/3]:
                            angle1 = angle - np.pi/6
                            vx, vy = abs(ball_velocity_mag_old*(np.cos(angle1)))*vx_dir, abs(ball_velocity_mag_old*(np.sin(angle1)))*vy_dir
                            if abs(vx) < 1:
                                vx = vx/abs(vx) # set the velocity component to 1 if it's less than 1
                                vy = (vy/abs(vy)) * (math.sqrt(ball_velocity_mag_old**2 - 1))

                            elif abs(vy) < 1:
                                vy = vy/abs(vy) # set the velocity component to 1 if it's less than 1
                                vx = (vx/abs(vx)) * (math.sqrt(ball_velocity_mag_old**2 - 0))
          
                            ball_obj1 = ball(x=ball_x_old[k], y=ball_y_old[k], velocity=(vx,vy), passthrough=ball_passthrough_old[k])
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

def generate_brick_coords(level):
    if level == -1:
        brick_coords = []
        brick_width = 70
        brick_height = 30
        brick_coords.append((400,400,470,430))
    if level == 0:
        brick_coords = []
        brick_width = 70
        brick_height = 30
        y_start = 80
        n_rows = 3
        for y in range(y_start,y_start + brick_height*(n_rows),brick_height):
            for x in range(120,screen_x-120,brick_width):
                brick_coords.append((x, y, x + brick_width, y + brick_height)) # left, top, right, bottom
    return brick_coords, brick_width, brick_height

def draw_start_text(start_or_continue):
    text1_pos = (screen_x/2 - 115, screen_y/2 - 100)
    font = pg.font.SysFont('Arial', 30)
    screen.blit(font.render(f'Press Space to {start_or_continue}', True, colours['RED']), text1_pos)
    return

def draw_game_over_screen():
    text1_pos = (screen_x/2 - 100, screen_y/2 - 100)
    text2_pos = (text1_pos[0] - 30, text1_pos[1] + 50)
    font = pg.font.SysFont('Arial', 30)
    screen.blit(font.render('GAME OVER', True, colours['RED']), text1_pos)
    screen.blit(font.render('Press Esc to restart', True, colours['RED']), text2_pos)
    return

def draw_info_bar(lives,player_powerups,player_width):
    pg.draw.rect(screen, colours['GREY2'], pg.Rect((0,info_bar_start),(screen_x,screen_y)),width=5)
    font = pg.font.SysFont('Arial', 30)
    screen.blit(font.render(f'Lives:', True, colours['RED']), (20, info_bar_start + 20))
    font = pg.font.SysFont('Arial', 25)
    screen.blit(font.render(f'{lives}', True, colours['GREY1']), (45, info_bar_start + 58))
    font = pg.font.SysFont('Arial', 30)
    screen.blit(font.render(f'Active modifiers:', True, colours['RED']),(175, info_bar_start + 20))

    font = pg.font.SysFont('Arial', 15)
    for i, j in enumerate(list(all_powerup_types.keys())):
        if all_powerup_types[j][0] != 'extra_life':
            col = colours['GREY1']
            if 'paddle_size' in all_powerup_types[j][0]:
                if player_width == player_default_width:
                    col = colours['GREY1']
                elif 'up' in all_powerup_types[j][0] and player_width == player_long:
                    col = colours['RED']
                elif 'down' in all_powerup_types[j][0] and player_width == player_short:
                    col = colours['RED']
            else:
                if all_powerup_types[j][0] in player_powerups:
                    col = colours['RED']
                else:
                    col = colours['GREY1']
            screen.blit(font.render(j, True, col),(all_powerup_types[j][1], info_bar_start + 65))

initialise_everything = True
# game code
while True:
    clock = pg.time.Clock()
    clock.tick(60)
    screen.fill(colours['BLACK'])

    if initialise_everything:
        all_balls = [] # list because there is a powerup that adds more balls
        all_bricks = []
        all_powerups = []

        player = paddle(x=player_init_x, y=player_init_y, width=player_default_width, powerups=[])
        ball_obj = ball(x=ball_init_x,y=ball_init_y,velocity=ball_init_velocity,passthrough=False)

        revive_ball = False
        restart = False
        generate_level = True
        level = 0
        lives = 3
        game_over = False
        begin = False
        start_or_continue = 'start'

        use_toshiba = False
        group = pg.sprite.RenderPlain()
        group.add(player)

        initialise_everything = False

        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
    
    elif not initialise_everything:
        if game_over:
            draw_game_over_screen()

        elif not game_over:

            pg.draw.rect(screen, colours['GREY2'], pg.Rect((0,0),(screen_x,screen_y)),width=5)
            draw_info_bar(lives,player.powerups,player.width)

            if generate_level:
                brick_coords, brick_width, brick_height = generate_brick_coords(level)
                [all_bricks.append(brick(coords[0],coords[1],width=brick_width,height=brick_height,is_alive=True)) for coords in brick_coords]
                all_balls.append(ball_obj)
                generate_level = False
            
            if len(all_bricks) == 0:
                level += 1
                generate_level = True
            else:
                for brick_obj in all_bricks:
                    if brick_obj.is_alive:
                        brick_obj.draw_brick_sprite()
 
            if use_toshiba:
                group.draw(screen)
            else:
                player.draw_paddle()

            if not begin:
                all_powerups = []
                width_memory = player.width
                new_x = (screen_x - width_memory)/2
                player = paddle(x=new_x, y=player_init_y, width=width_memory, powerups=[])
                draw_start_text(start_or_continue)
                for event in pg.event.get():
                    if event.type == KEYDOWN and event.key == K_SPACE:
                        begin = True
                    elif event.type == QUIT:
                        pg.quit()
                        sys.exit()
            elif begin:
                # move paddle if key pressed
                player.check_keys()
                if revive_ball or restart:
                    ball_obj.x = ball_init_x
                    ball_obj.y = ball_init_y
                    ball_obj.velocity = ball_init_velocity
                    ball_obj.passthrough = False
                    all_balls.append(ball_obj)
                    revive_ball = False
                    restart = False

                # move ball
                for ball_obj in all_balls:
                    ball_obj.move()
                    dead = ball_obj.check_collision(player,all_bricks)
                    if dead == "dead":
                        all_balls.pop(all_balls.index(ball_obj))
                    if len(all_balls) == 0:
                        if 'ball_speed' in player.powerups:
                            player.powerups = [i for i in player.powerups if i != 'ball_speed'] # revert ball speed back to default when losing a life
                        if 'ball_pass_through' in player.powerups:
                            player.powerups = [i for i in player.powerups if i != 'ball_pass_through'] # revert ball 'unstoppable' state back to default
                        if 'multi' in player.powerups:
                            player.powerups = [i for i in player.powerups if i != 'ball_pass_through'] # get rid of multi ball
                        lives -= 1
                        begin = False
                        start_or_continue = 'continue'
                        if lives == 0:
                            game_over = True
                            start_or_continue = 'start'
                        else:
                            revive_ball = True

                for power_up in all_powerups:
                    if power_up.is_alive:
                        power_up.update_position()
                        player, all_balls = power_up.check_collisions(player,all_balls)
                
        for event in pg.event.get():
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                restart = True
                game_over = False
                initialise_everything = True
            if event.type == QUIT:
                pg.quit()
                sys.exit()
    
    pg.display.update()