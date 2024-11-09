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
    # Create objects
    player = objects.Paddle(
        x=player_init_x,
        y=player_init_y,
        width=player_default_width,
        powerups=[],
        lives=3
    )
    ball_obj = objects.Ball(
        x=ball_init_pos[level][0],
        y=ball_init_pos[level][1],
        velocity=ball_init_velocity,
        passthrough=False
    )

    powerups_memory = player.powerups
    width_memory = player.width
    lives_memory = player.lives

    return player, ball_obj, powerups_memory, width_memory, lives_memory


def check_keypresses(restart, init_everything, all_bricks):
    for event in pg.event.get():
        if event.type == KEYDOWN and event.key == K_k and pg.key.get_mods() & KMOD_SHIFT:
            all_bricks = [all_bricks[0]]
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            restart = True
            init_everything = True
        if event.type == QUIT:
            pg.quit()
            sys.exit()

    return restart, init_everything, all_bricks


def remain_paused(key) -> None:
    keys = {"ESCAPE": K_ESCAPE, "SPACE": K_SPACE}
    while True:
        for event in pg.event.get():
            if event.type == KEYDOWN and event.key == keys[key]:
                return
            elif event.type == QUIT:
                pg.quit()
                sys.exit()


def start_game():
    init_everything = True
    frame_count = 0 # For delaying laser pulses
    frames = [0, 0]

    # Create object for drawing things to the screen
    artist = objects.Artist(
        screen_x=screen_x,
        screen_y=screen_y,
        start_or_retry="start"
    )

    # Main game loop
    while True:
        clock = pg.time.Clock()
        clock.tick(60)
        frame_count += 1
        
        # Reset screen contents
        artist.fill_screen(colour=colours["BLACK"])

        if init_everything:
            all_lasers, all_bricks, all_powerups = [], [], []
            level, levels_cleared = 0, 0
            revive_ball, restart, init_everything = False, False, False
            player, ball_obj, powerups_memory, width_memory, lives_memory = initialise_objects(level)
            pg.display.update()
       
        elif not init_everything:
            artist.draw_border(colour=colours['GREY2'])

            died_or_finished = len(all_bricks) == 0 or len(all_balls) == 0
            if died_or_finished: # Completed level or lost a life
                if len(all_bricks) == 0:
                    # Completed level, update variables
                    if levels_cleared > 0:
                        level += 1
                        artist.start_or_retry = "start"
                    levels_cleared += 1
                    all_bricks, all_balls, max_brick_y = generate_level(level) # Generate next level
                    all_powerups = []               
                else:
                    # This block is entered if the player lost a life. In which case, we need to reset the powerups
                    player.powerups = []

                # Reset player position to center, and remove powerups if lost a life OR beat level
                player.x, player.y = player_init_x, player_init_y
                player.powerups = []
    
                artist.draw_info_bar(player.lives, player.powerups, player.width)
                artist.draw_start_text()
                player.draw_paddle(artist)
                for brick_obj in all_bricks:
                    if brick_obj.is_alive:
                        brick_obj.draw_brick_sprite(artist)
                
                # Draw a dummy ball on the screen
                artist.draw_dummy_ball(level)

                # Draw static objects once before entering loop
                pg.display.update()
                remain_paused(key="SPACE")
            elif not died_or_finished:
                player.draw_paddle(artist)
                for brick_obj in all_bricks:
                    if brick_obj.is_alive:
                        brick_obj.draw_brick_sprite(artist)

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
                for i, laser_data in enumerate(all_lasers):
                    bolt = laser_data[0] # laser_data[1] is the frame number for that laser
                    bolt.draw_laser(artist)
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

            # Move powerups. Must do this before moving the balls because we check for width modifying powerups here too
            # If the paddle width changes AFTER checking collisions with the ball, the collisions will always be off
            for power_up in all_powerups:
                if power_up.is_alive:
                    power_up.update_position(artist)
                    player, all_balls = power_up.check_collisions(player, all_balls, all_powerups)

            # Move balls
            for ball_obj in all_balls:
                ball_obj.draw_ball(artist)
                ball_obj.move()
                dead, all_bricks = ball_obj.check_collision(player, all_bricks, all_powerups, max_brick_y)
                if dead == "dead":
                    all_balls.pop(all_balls.index(ball_obj))
                if len(all_balls) == 0:
                    # Player lost a life
                    all_powerups = []
                    player.powerups = []
                    player.width = player_default_width
                    player.lives -= 1
                    artist.start_or_retry = "retry"
                    if player.lives == 0:
                        pg.mixer.Sound.play(pg.mixer.Sound(f"{assets_path}/game_over.wav"))
                        artist.start_or_retry = "start"

                        # Update screen before entering loop
                        artist.fill_screen(colour=colours["BLACK"])
                        artist.draw_border(colour=colours['GREY2'])
                        artist.draw_game_over_screen()
                        pg.display.update()

                        # Stay in a loop until the player has pressed escape to restart 
                        remain_paused(key="ESCAPE")
                        restart, init_everything = True, True # Simulate a full restart
                    else:
                        pg.mixer.Sound.play(pg.mixer.Sound(f"{assets_path}/lose_life.wav"))
                        revive_ball = True

            # Remove multi powerup if only one ball left              
            if len(all_balls) == 1 and "multi" in player.powerups:
                player.powerups.pop(player.powerups.index("multi"))

            if player.width != width_memory or player.powerups != powerups_memory or player.lives != lives_memory:
                # Only update info bar if the player gains/loses a powerup or gains a life
                artist.draw_info_bar(player.lives, player.powerups, player.width)
                pg.display.update()
            else:
                pg.display.update((0, 0, artist.screen_x, info_bar_start))

            powerups_memory = player.powerups
            width_memory = player.width
            lives_memory = player.lives

            frames[1] = frame_count

            # Check for special key combinations
            restart, init_everything, all_bricks = check_keypresses(restart, init_everything, all_bricks)

if __name__ == "__main__":
    start_game()
