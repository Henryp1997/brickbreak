import pygame as pg
from pygame.locals import *
import sys
from objects import *
import objects
import time

pg.init()
pg.display.set_caption("Brickbreaker")

def generate_brick_coords(level):
    brick_default_width = 70
    brick_default_height = 30
    if level == -1:
        brick_coords = []
        brick_coords.append((400,400,470,430,'h3'))
    if level == 0:
        brick_coords = []
        y_start = 80
        x_start = round((screen_x - 700)/2)
        n_rows = 3
        for y in range(y_start,y_start + brick_default_height*(n_rows),brick_default_height):
            for x in range(x_start,x_start+700,brick_default_width):
                brick_coords.append([x, y, x + brick_default_width, y + brick_default_height, 'h1']) # left, top, right, bottom
    if level == 1:
        brick_coords = []
        y_start = 60
        x_start = round((screen_x - 700)/4)
        x_start_from_right = screen_x - x_start - brick_default_width
        n_rows = 10
        for y in range(y_start,y_start + brick_default_height*(n_rows),brick_default_height):
            for i, x in enumerate(range(x_start,x_start+175,brick_default_width)):
                if i == 0:
                    continue
                brick_coords.append([x, y, x + brick_default_width, y + brick_default_height]) # left, top, right, bottom
            for i, x in enumerate(range(x_start_from_right,x_start_from_right-175,-brick_default_width)):
                if i == 0:
                    continue
                brick_coords.append([x, y, x + brick_default_width, y + brick_default_height]) # left, top, right, bottom
        
        l = [i[0] for i in brick_coords][0:4]
        l.sort()
        
        for coords in brick_coords:
            if coords[0] == l[1] or coords[0] == l[2]:
                coords.append('h2')
            else:
                coords.append('h1')

    max_brick_y = max([i[3] for i in brick_coords])
    return brick_coords, brick_default_width, brick_default_height, max_brick_y

def draw_start_text(start_or_retry):
    text_pos = (screen_x/2 - round(screen_x*0.13), screen_y/2 - (screen_y/9))
    font = pg.font.SysFont('Arial', 30)
    screen.blit(font.render(f'Press Space to {start_or_retry}', True, colours['RED']), text_pos)
    return

def draw_game_over_screen():
    text1_pos = (screen_x/2 - round(screen_x/10), screen_y/2 - (screen_y/9))
    text2_pos = (text1_pos[0] - round(screen_x*0.03), text1_pos[1] + round(screen_y*(5/90)))
    font = pg.font.SysFont('Arial', 30)
    screen.blit(font.render('GAME OVER', True, colours['RED']), text1_pos)
    screen.blit(font.render('Press Esc to restart', True, colours['RED']), text2_pos)
    return

def draw_info_bar(lives,player_powerups,player_width):
    pg.draw.rect(screen, colours['GREY2'], pg.Rect((0,info_bar_start),(screen_x,screen_y - info_bar_start)),width=5)
    font = pg.font.SysFont('Arial', 30)
    screen.blit(font.render(f'Lives:', True, colours['RED']), (round(screen_x*0.02), info_bar_start + round(screen_x*0.02)))
    font = pg.font.SysFont('Arial', 25)
    screen.blit(font.render(f'{lives}', True, colours['GREY1']), (round(screen_x*(45/1000)), info_bar_start + round(screen_x*(58/1000))))
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
            screen.blit(font.render(j, True, col),(all_powerup_types[j][1], info_bar_start + screen_x*(65/850)))

initialise_everything = True
frame_count = 0
frames = [0,0]
got_laser = False
# game code
while True:
    clock = pg.time.Clock()
    clock.tick(60)
    frame_count += 1
    screen.fill(colours['BLACK'])
    
    if initialise_everything:
        level = -1
        all_lasers = []
        all_bricks = []
        all_powerups = []

        player = objects.paddle(x=player_init_x, y=player_init_y, width=player_default_width, powerups=[], lives=3)
        ball_obj = objects.ball(x=ball_init_pos[level][0],y=ball_init_pos[level][1],velocity=ball_init_velocity,passthrough=False)

        powerups_memory = player.powerups
        width_memory = player.width
        lives_memory = player.lives

        revive_ball = False
        restart = False
        generate_level = True
        game_over = False
        begin = False
        start_or_retry = 'start'

        use_toshiba = False
        group = pg.sprite.RenderPlain()
        group.add(player)

        draw_info_bar(player.lives,player.powerups,player.width)

        pg.display.update()

        initialise_everything = False

        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
    
    elif not initialise_everything:
        if game_over:
            pg.draw.rect(screen, colours['GREY2'], pg.Rect((0,0),(screen_x,info_bar_start + round(screen_x*0.002))),width=5)
            draw_game_over_screen()

        elif not game_over:

            pg.draw.rect(screen, colours['GREY2'], pg.Rect((0,0),(screen_x,info_bar_start + round(screen_x*0.002))),width=5)

            if len(all_bricks) == 0:
                level += 1
                generate_level = True
                begin = False
            else:
                for brick_obj in all_bricks:
                    if brick_obj.is_alive:
                        brick_obj.draw_brick_sprite()
            
            if generate_level:
                all_balls = []
                brick_coords, brick_default_width, brick_default_height, max_brick_y = generate_brick_coords(level-1)
                [all_bricks.append(objects.brick(coords[0],coords[1],width=brick_default_width,height=brick_default_height,health=coords[4],is_alive=True)) for coords in brick_coords]
                ball_obj = objects.ball(x=ball_init_pos[level-1][0],y=ball_init_pos[level-1][1],velocity=ball_init_velocity,passthrough=False)
                all_balls.append(ball_obj)
                generate_level = False

            if use_toshiba:
                group.draw(screen)
            else:
                player.draw_paddle()

            if not begin:
                all_powerups = []
                width_memory = player.width
                new_x = player_init_x
                player = objects.paddle(x=new_x, y=player_init_y, width=width_memory, powerups=[], lives=player.lives)
                draw_start_text(start_or_retry)
                # pg.draw.circle(screen, colours['FIRE'], (ball_init_x + 0.5*ball_init_height, ball_init_y + 0.5*ball_init_height), radius=10)
                screen.blit(pg.image.load(f'{assets_path}/player_sprites/ball_default.png').convert_alpha(), (ball_init_pos[level-1][0], ball_init_pos[level-1][1]))
                for event in pg.event.get():
                    if event.type == KEYDOWN and event.key == K_SPACE:
                        begin = True
                    elif event.type == QUIT:
                        pg.quit()
                        sys.exit()
            elif begin:
                ### MAIN GAME LOOP ###
                if revive_ball or restart:
                    ball_obj.x = ball_init_pos[level-1][0]
                    ball_obj.y = ball_init_pos[level-1][1]
                    ball_obj.velocity = ball_init_velocity
                    ball_obj.passthrough = False
                    all_balls.append(ball_obj)
                    revive_ball = False
                    restart = False

                if 'laser' in player.powerups:
                    with open(f'{assets_path}/got_laser.txt', 'r') as f:
                        data = f.readlines()
                    tm = float(data[0])
                    if time.time() - tm > 10:
                        player.powerups = [pwr for pwr in player.powerups if pwr != 'laser']

                # move paddle and check for spacebar presses for laser bolts
                laser_bolt = player.check_keys(all_lasers,frame_count)
                if laser_bolt is not None:
                    all_lasers.append((laser_bolt, frame_count))
                # move ball
                for ball_obj in all_balls:
                    ball_obj.draw_ball()
                    ball_obj.move()
                    dead = ball_obj.check_collision(player,all_bricks,all_powerups,max_brick_y)
                    if dead == "dead":
                        all_balls.pop(all_balls.index(ball_obj))
                    if len(all_balls) == 0:
                        player.powerups = []
                        player.width = player_default_width
                        player.lives -= 1
                        begin = False
                        start_or_retry = 'retry'
                        if player.lives == 0:
                            pg.mixer.Sound.play(pg.mixer.Sound(f"{assets_path}/game_over.wav"))
                            game_over = True
                            start_or_retry = 'start'
                        else:
                            pg.mixer.Sound.play(pg.mixer.Sound(f"{assets_path}/lose_life.wav"))
                            revive_ball = True
                
                # move laser bolts
                if 'laser' in player.powerups:
                    bolt_objects = [i[0] for i in all_lasers]
                    for i, bolt in enumerate(bolt_objects):
                        bolt.draw_laser()
                        bolt.move()
                        dead = bolt.check_collision(all_bricks,all_powerups,max_brick_y)
                        if dead == "dead":
                            all_lasers.pop(i)
                        
                if len(all_balls) == 1 and 'multi' in player.powerups:
                    player.powerups = [i for i in player.powerups if i != 'multi']

                for power_up in all_powerups:
                    if power_up.is_alive:
                        power_up.update_position()
                        player, all_balls = power_up.check_collisions(player,all_balls,all_powerups)

        if player.width != width_memory or player.powerups != powerups_memory or player.lives != lives_memory:
            draw_info_bar(player.lives,player.powerups,player.width)
            pg.display.update()
        else:
            pg.display.update((0,0,screen_x,info_bar_start))

        powerups_memory = player.powerups
        width_memory = player.width
        lives_memory = player.lives

        frames[1] = frame_count

        for event in pg.event.get():
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                restart = True
                game_over = False
                initialise_everything = True
            if event.type == QUIT:
                pg.quit()
                sys.exit()
