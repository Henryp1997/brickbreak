import pygame as pg
from pygame.locals import KEYDOWN, KMOD_SHIFT, K_ESCAPE, K_SPACE, K_k, QUIT
import sys
import time
from consts import *
from levels import generate_brick_coords
from utils import play_sound
from objects.artist import Artist
from objects.player import Paddle
from objects.ball import Ball
from objects.brick import Brick

pg.init()
pg.display.set_caption("Brickbreaker")


def generate_level(artist, level):
    brick_coords, max_brick_y = generate_brick_coords(level)
    all_bricks = [
        Brick(
            artist,
            coords[0], 
            coords[1], 
            width=BRICK_DEFAULT_WIDTH, 
            height=BRICK_DEFAULT_HEIGHT, 
            health=coords[2], 
        ) for coords in brick_coords
    ]
    all_balls = [
        Ball(
            x=BALL_INIT_POS[level][0], 
            y=BALL_INIT_POS[level][1], 
            velocity=BALL_INIT_VELOCITY[level], 
            passthrough=False
        )
    ]

    return all_bricks, all_balls, max_brick_y


def initialise_objects(artist, level):  
    # Create objects
    player = Paddle(
        artist=artist,
        x=PLAYER_INIT_X,
        y=PLAYER_INIT_Y,
        width=PLAYER_DEFAULT_WIDTH,
        powerups=[],
        lives=3
    )
    ball_obj = Ball(
        x=BALL_INIT_POS[level][0],
        y=BALL_INIT_POS[level][1],
        velocity=BALL_INIT_VELOCITY[level],
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


def remain_paused(key, artist, draw_screen=None) -> None:
    keys = {"ESCAPE": K_ESCAPE, "SPACE": K_SPACE}
    if draw_screen:
        artist.draw_start_text()
        pg.display.update()
    while True:
        for event in pg.event.get():
            if event.type == KEYDOWN and event.key == keys[key]:
                return
            elif event.type == QUIT:
                pg.quit()
                sys.exit()


def start_game():
    init_everything = True

    # Create object for drawing things to the screen
    artist = Artist(
        SCREEN_X=SCREEN_X,
        SCREEN_Y=SCREEN_Y,
        start_or_retry="start"
    )

    # Main game loop
    while True:
        clock = pg.time.Clock()
        clock.tick(60)
        
        # Reset screen contents
        artist.fill_screen(colour=COLOURS["BLACK"])

        if init_everything:
            all_lasers, all_bricks, all_powerups = [], [], []
            level, levels_cleared = 0, 0
            revive_ball, restart, init_everything = False, False, False
            player, ball_obj = initialise_objects(artist, level)
            artist.start_or_retry = "start"
            draw_screen = True
            pg.display.update()
       
        elif not init_everything:
            artist.draw_border(colour=COLOURS['GREY2'])

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
                    artist.start_or_retry = "retry"
                    player.lives -= 1
                    if player.lives > 0:
                        play_sound("lose_life")
                        revive_ball = True

                # Delete all currently moving powerups
                all_powerups = []

                # Reset player position to center, reset player speed and size and
                # remove powerups if lost a life OR beat level
                player.reset_attributes()
                player.draw_paddle()

                artist.draw_info_bar(player.lives, player.powerups, player.width)
                
                # Draw brick objects that are still active before entering paused loop
                for brick_obj in all_bricks:
                    if brick_obj.is_alive:
                        brick_obj.draw_brick_sprite()
                
                # Draw a dummy ball on the screen. Level defines position of dummy ball
                artist.draw_dummy_ball(level)
        
                exit_key = "SPACE"

                # Cancel out all the drawing to the screen we just did if game over
                if player.lives == 0:
                    play_sound("game_over")
                    revive_ball = False
                    artist.start_or_retry = "start"

                    # Update screen before entering loop
                    artist.draw_game_over_screen()
                    restart, init_everything = True, True # Simulate a full restart
                    exit_key = "ESCAPE"
                    draw_screen = False

                # Update screen once before entering pause loop
                pg.display.update()
                remain_paused(key=exit_key, artist=artist, draw_screen=draw_screen)

            elif not lost_life and not completed_level:
                player.draw_paddle()
                for brick_obj in all_bricks:
                    if brick_obj.is_alive:
                        brick_obj.draw_brick_sprite()

            ### MAIN GAME LOOP ###
            if revive_ball or restart:
                ball_obj.x, ball_obj.y = BALL_INIT_POS[level]
                ball_obj.velocity = BALL_INIT_VELOCITY[level]
                ball_obj.passthrough = False
                all_balls.append(ball_obj)
                revive_ball, restart = False, False

            if "laser" in player.powerups:
                # Check if the laser powerup has timed out
                if time.time() - player.time_got_laser > 10:
                    player.powerups.pop(player.powerups.index("laser"))
                    artist.draw_info_bar(player.lives, player.powerups, player.width)
                    pg.display.update()

                # Move paddle and check for spacebar presses for laser bolts
                laser_bolt = player.check_laser_press(all_lasers)
                if laser_bolt is not None:
                    all_lasers.append(laser_bolt)

                # Move laser bolts
                for i, bolt in enumerate(all_lasers):
                    bolt.draw_laser()
                    bolt.move()
                    dead = bolt.check_collision(all_bricks, all_powerups, max_brick_y)
                    if dead == "dead":
                        all_lasers.pop(i)
                
            # Check if moving paddle
            player.check_movement()

            # Move powerups. Must do this before moving the balls because we check for width modifying powerups here too
            # If the paddle width changes AFTER checking collisions with the ball, the collisions will always be off
            for power_up in all_powerups:
                if power_up.is_alive:
                    power_up.move(artist, all_powerups)
                    player, all_balls = power_up.check_gained_powerup(player, all_balls, all_powerups)

            # Move balls
            for ball_obj in all_balls:
                ball_obj.draw_ball(artist)
                ball_obj.move()
                dead, all_bricks = ball_obj.check_collision(player, all_bricks, all_powerups, max_brick_y, artist)
                if dead == "dead":
                    all_balls.pop(all_balls.index(ball_obj))

            # Remove multi powerup if only one ball left              
            if len(all_balls) == 1 and "multi" in player.powerups:
                player.powerups.pop(player.powerups.index("multi"))
                artist.draw_info_bar(player.lives, player.powerups, player.width)

            # Only update playable area. Info bar will be updated in relevant sections if required
            pg.display.update((0, 0, artist.SCREEN_X, INFO_BAR_START))

            # Check for special key combinations
            restart, init_everything, all_bricks = check_system_keys(restart, init_everything, all_bricks)

if __name__ == "__main__":
    start_game()
