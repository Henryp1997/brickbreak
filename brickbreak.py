import pygame as pg
from pygame.locals import *
import sys
from objects import *
from levels import generate_brick_coords
import objects
import time

pg.init()
pg.display.set_caption("Brickbreaker")


def generate_level(level):
    all_balls = []
    brick_coords, brick_default_width, brick_default_height, max_brick_y = generate_brick_coords(level)
    all_bricks = [
        objects.Brick(
            coords[0], 
            coords[1], 
            width=brick_default_width, 
            height=brick_default_height, 
            health=coords[4], 
            is_alive=True
        ) for coords in brick_coords
    ]
    ball_obj = objects.Ball(
        x=ball_init_pos[level][0], 
        y=ball_init_pos[level][1], 
        velocity=ball_init_velocity, 
        passthrough=False
    )
    all_balls.append(ball_obj)

    return all_bricks, all_balls, max_brick_y


def initialise_objects(level):
    level = 0
    
    # Create objects
    player = objects.Paddle(x=player_init_x, y=player_init_y, width=player_default_width, powerups=[], lives=3)
    ball_obj = objects.Ball(x=ball_init_pos[level][0], y=ball_init_pos[level][1], velocity=ball_init_velocity, passthrough=False)
    artist = objects.Artist(screen_x=screen_x, screen_y=screen_y, start_or_retry="start")

    powerups_memory = player.powerups
    width_memory = player.width
    lives_memory = player.lives

    return player, ball_obj, artist, powerups_memory, width_memory, lives_memory


def check_keypresses(all_bricks):
    restart, game_over, init_everything = None, None, None
    for event in pg.event.get():
        if event.type == KEYDOWN and event.key == K_k and pg.key.get_mods() & KMOD_SHIFT:
            all_bricks = [all_bricks[0]]
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            restart = True
            game_over = False
            init_everything = True
        if event.type == QUIT:
            pg.quit()
            sys.exit()

    return restart, game_over, init_everything, all_bricks


def start_game():
    init_everything = True
    frame_count = 0 # For delaying laser pulses
    frames = [0, 0]
    # game code
    while True:
        clock = pg.time.Clock()
        clock.tick(60)
        frame_count += 1
        screen.fill(colours['BLACK'])
        
        if init_everything:
            all_lasers = []
            all_bricks = []
            all_powerups = []
            levels_cleared = 0
            level = 0
            revive_ball, restart, gen_level, game_over, begin_level, init_everything = False, False, True, False, False, False
            player, ball_obj, artist, powerups_memory, width_memory, lives_memory = initialise_objects(level)
            artist.draw_info_bar(player.lives, player.powerups, player.width)
            pg.display.update()
       
        elif not init_everything:
            artist.draw_border(colour=colours['GREY2'])
            if game_over:
                artist.draw_game_over_screen()

            elif not game_over:
                if len(all_bricks) == 0: # Completed level
                    if levels_cleared > 0:
                        level += 1
                        artist.start_or_retry = "start"
                    levels_cleared += 1
                    all_bricks, all_balls, max_brick_y = generate_level(level) # Generate next level
                    
                    # Flag to force stay in the 'Press space to start'
                    # screen until the player has pressed space
                    begin_level = False
                else:
                    for brick_obj in all_bricks:
                        if brick_obj.is_alive:
                            brick_obj.draw_brick_sprite()

                if gen_level:
                    gen_level = False

                player.draw_paddle()

                # Player has not yet pressed space, this will always be entered
                if not begin_level:
                    all_powerups = []
                    width_memory = player.width
                    new_x = player_init_x
                    player = objects.Paddle(
                        x=new_x, 
                        y=player_init_y, 
                        width=width_memory,
                        powerups=[], 
                        lives=player.lives
                    )

                    artist.draw_start_text()
                    
                    # Draw a dummy ball on the screen
                    screen.blit(
                        pg.image.load(f'{assets_path}/player_sprites/ball_default.png').convert_alpha(),
                        (ball_init_pos[level][0], ball_init_pos[level][1])
                    )
                    for event in pg.event.get():
                        if event.type == KEYDOWN and event.key == K_SPACE:
                            begin_level = True
                        elif event.type == QUIT:
                            pg.quit()
                            sys.exit()

                # Player pressed space to begin level
                elif begin_level:
                    ### MAIN GAME LOOP ###
                    if revive_ball or restart:
                        ball_obj.x, ball_obj.y = ball_init_pos[level]
                        ball_obj.velocity = ball_init_velocity
                        ball_obj.passthrough = False
                        all_balls.append(ball_obj)
                        revive_ball = False
                        restart = False

                    if "laser" in player.powerups:
                        # Check if the laser powerup has timed out
                        if time.time() - player.time_got_laser > 10:
                            player.powerups.pop(player.powerups.index("laser"))

                        # Move laser bolts
                        bolt_objects = [i[0] for i in all_lasers]
                        for i, bolt in enumerate(bolt_objects):
                            bolt.draw_laser()
                            bolt.move()
                            dead = bolt.check_collision(all_bricks, all_powerups, max_brick_y)
                            if dead == "dead":
                                all_lasers.pop(i)

                        # Move paddle and check for spacebar presses for laser bolts
                        laser_bolt = player.check_laser_press(all_lasers, frame_count)
                        if laser_bolt is not None:
                            all_lasers.append((laser_bolt, frame_count))
                        
                    # Check if moving paddle
                    player.check_movement()

                    # Move balls
                    for ball_obj in all_balls:
                        ball_obj.draw_ball()
                        ball_obj.move()
                        dead, all_bricks = ball_obj.check_collision(player, all_bricks, all_powerups, max_brick_y)
                        if dead == "dead":
                            all_balls.pop(all_balls.index(ball_obj))
                        if len(all_balls) == 0:
                            # Player lost a life
                            player.powerups = []
                            player.width = player_default_width
                            player.lives -= 1
                            begin_level = False
                            artist.start_or_retry = "retry"
                            if player.lives == 0:
                                pg.mixer.Sound.play(pg.mixer.Sound(f"{assets_path}/game_over.wav"))
                                game_over = True
                                artist.start_or_retry = "start"
                            else:
                                pg.mixer.Sound.play(pg.mixer.Sound(f"{assets_path}/lose_life.wav"))
                                revive_ball = True
                                               
                    if len(all_balls) == 1 and "multi" in player.powerups:
                        player.powerups.pop(player.powerups.index("multi"))

                    for power_up in all_powerups:
                        if power_up.is_alive:
                            power_up.update_position()
                            player, all_balls = power_up.check_collisions(player, all_balls, all_powerups)

            if player.width != width_memory or player.powerups != powerups_memory or player.lives != lives_memory:
                # Only update info bar if the player gains a powerup or life
                artist.draw_info_bar(player.lives, player.powerups, player.width)
                pg.display.update()
            else:
                pg.display.update((0, 0, artist.screen_x, info_bar_start))

            powerups_memory = player.powerups
            width_memory = player.width
            lives_memory = player.lives

            frames[1] = frame_count

            # Check for special key combinations
            restart, game_over, init_everything, all_bricks = check_keypresses(all_bricks)

if __name__ == "__main__":
    start_game()
