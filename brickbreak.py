import pygame as pg
from pygame.locals import *
import sys
import time
from variables import *
from levels import generate_brick_coords
from utils import play_sound
from objects.artist import Artist
from objects.player import Paddle
from objects.ball import Ball
from objects.brick import Brick

pg.init()
pg.display.set_caption("Brickbreaker")


def generate_level(artist, level):
    brick_coords, brick_default_width, brick_default_height, max_brick_y = generate_brick_coords(level)
    all_bricks = [
        Brick(
            artist,
            coords[0], 
            coords[1], 
            width=brick_default_width, 
            height=brick_default_height, 
            health=coords[4], 
        ) for coords in brick_coords
    ]
    all_balls = [
        Ball(
            x=ball_init_pos[level][0], 
            y=ball_init_pos[level][1], 
            velocity=ball_init_velocity, 
            passthrough=False
        )
    ]

    return all_bricks, all_balls, max_brick_y


def initialise_objects(artist, level):  
    # Create objects
    player = Paddle(
        artist=artist,
        x=player_init_x,
        y=player_init_y,
        width=player_default_width,
        powerups=[],
        lives=3
    )
    ball_obj = Ball(
        x=ball_init_pos[level][0],
        y=ball_init_pos[level][1],
        velocity=ball_init_velocity,
        passthrough=False
    )

    return player, ball_obj


def check_system_keys(restart, init_everything, all_bricks):
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
    artist = Artist(
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
            player, ball_obj = initialise_objects(artist, level)
            pg.display.update()
       
        elif not init_everything:
            artist.draw_border(colour=colours['GREY2'])

            completed_level = len(all_bricks) == 0
            try:
                lost_life = len(all_balls) == 0
            except UnboundLocalError:
                lost_life = False

            if completed_level or lost_life:
                # Generate next level
                if completed_level:
                    if levels_cleared > 0:
                        level += 1
                    levels_cleared += 1
                    all_bricks, all_balls, max_brick_y = generate_level(artist, level) 
                
                # Play sound and subtract from lives count
                if lost_life:
                    player.lives -= 1
                    if player.lives > 0:
                        play_sound("lose_life")
                        revive_ball = True

                # Delete all currently moving powerups
                all_powerups = []

                # Reset player position to center, reset player size and
                # remove powerups if lost a life OR beat level
                player.x, player.y = player_init_x, player_init_y
                player.powerups = []
                player.width = player_default_width
                player.change_sprite()

                artist.start_or_retry = "start"
                artist.draw_info_bar(player.lives, player.powerups, player.width)
                artist.draw_start_text()
                player.draw_paddle()
                

                # Draw brick objects that are still active before entering paused loop
                for brick_obj in all_bricks:
                    if brick_obj.is_alive:
                        brick_obj.draw_brick_sprite()
                
                # Draw a dummy ball on the screen
                artist.draw_dummy_ball(level)
        
                exit_key = "SPACE"

                # Cancel out all the drawing to the screen we just did if game over
                if player.lives == 0:
                    play_sound("game_over")
                    revive_ball = False
                    artist.start_or_retry = "start"

                    # Update screen before entering loop
                    artist.fill_screen(colour=colours["BLACK"])
                    artist.draw_border(colour=colours["GREY2"])
                    artist.draw_game_over_screen()
                    restart, init_everything = True, True # Simulate a full restart
                    exit_key = "ESCAPE"

                # Update screen once before entering pause loop
                pg.display.update()
                remain_paused(key=exit_key)

            elif not lost_life and not completed_level:
                player.draw_paddle()
                for brick_obj in all_bricks:
                    if brick_obj.is_alive:
                        brick_obj.draw_brick_sprite()

            ### MAIN GAME LOOP ###
            if revive_ball or restart:
                ball_obj.x, ball_obj.y = ball_init_pos[level]
                ball_obj.velocity = ball_init_velocity
                ball_obj.passthrough = False
                all_balls.append(ball_obj)
                revive_ball, restart = False, False

            if "laser" in player.powerups:
                # Check if the laser powerup has timed out
                if time.time() - player.time_got_laser > 10:
                    player.powerups.pop(player.powerups.index("laser"))
                    artist.draw_info_bar(player.lives, player.powerups, player.width)

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

            # Remove multi powerup if only one ball left              
            if len(all_balls) == 1 and "multi" in player.powerups:
                player.powerups.pop(player.powerups.index("multi"))
                artist.draw_info_bar(player.lives, player.powerups, player.width)

            # Only update playable area. Info bar will be updated in relevant sections if required
            pg.display.update((0, 0, artist.screen_x, info_bar_start))

            frames[1] = frame_count

            # Check for special key combinations
            restart, init_everything, all_bricks = check_system_keys(restart, init_everything, all_bricks)

if __name__ == "__main__":
    start_game()
