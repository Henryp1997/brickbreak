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


class Game():
    def __init__(self, artist) -> None:
        self.frame_time = 0
        self.artist = artist
        self.game_state = "INIT"


    def frame_dur(self) -> float:
        """ Return the duration of a frame in milliseconds """
        current_time = time.perf_counter()
        dt = current_time - self.frame_time
        self.frame_time = current_time
        return dt
    

    def state_init(self) -> None:
        """ Initialisation game state """
        all_lasers, all_bricks, all_powerups = [], [], []
        level = -1
        revive_ball = False
        player, all_balls = self.__initialise_objects(self.artist, level)
        draw_screen = True

        # Set Attributes
        self.artist.start_or_retry = "start"
        self.game_state = "PLAYING"

        return all_lasers, all_bricks, all_powerups, level, revive_ball, player, all_balls, draw_screen


    def state_paused(self, key, draw_screen=None) -> None:
        """ Paused state. Don't perform any actions until the user has pressed the appropriate exit key """
        keys = {"ESCAPE": K_ESCAPE, "SPACE": K_SPACE}
        output_states = {"ESCAPE": "INIT", "SPACE": "PLAYING"}
        if draw_screen:
            self.artist.draw_start_text()

        self.frame_dur() # Make sure we're still measuring frame time
        for event in pg.event.get():
            if event.type == KEYDOWN and event.key == keys[key]:
                self.game_state = output_states[key]
                return
            elif event.type == QUIT:
                pg.quit()
                sys.exit()

    
    def check_system_keys(self, all_bricks):
        """ Check for special key combinations """
        for event in pg.event.get():
            if event.type == KEYDOWN and event.key == K_k and pg.key.get_mods() & KMOD_SHIFT:
                all_bricks = [all_bricks[0]]
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                self.game_state = "INIT"
            if event.type == QUIT:
                pg.quit()
                sys.exit()

        return all_bricks

    ### PRIVATE METHODS
    def __initialise_objects(self, artist, level) -> tuple:
        """ Create the player and ball objects """
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

        return player, [ball_obj]


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


def start_game():
    # Create object for drawing things to the screen
    artist = Artist(
        SCREEN_X=SCREEN_X,
        SCREEN_Y=SCREEN_Y,
        start_or_retry="start"
    )

    # Create game object for keeping track of global properties like game state and time
    game = Game(artist)

    # Main game loop
    while True:
        game.frame_time = time.perf_counter() # Keep track of frame time for speed calculations
        clock = pg.time.Clock()
        clock.tick(60)
        
        # Reset screen contents
        artist.fill_screen(colour=COLOURS["BLACK"])

        if game.game_state == "INIT":
            all_lasers, all_bricks, all_powerups, level, revive_ball, player, all_balls, draw_screen = game.state_init()
            pg.display.update()
       
        elif game.game_state == "PAUSED":
            artist.draw_border(colour=COLOURS['GREY2'])
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
                exit_key = "ESCAPE"
                draw_screen = False

            game.state_paused(key=exit_key, draw_screen=draw_screen)
            pg.display.update()

        ### STATE 2 - Playing game
        elif game.game_state == "PLAYING":
            # Check if completed level or lost life. Enter paused state if so
            completed_level = len(all_bricks) == 0
            lost_life = len(all_balls) == 0

            # Generate next level
            if completed_level:
                # Note this will also be entered on every reset
                level += 1
                all_bricks, all_balls, max_brick_y = generate_level(artist, level)
                game.game_state = "PAUSED"
            
            # Play sound and subtract from lives count
            if lost_life:
                artist.start_or_retry = "retry"
                player.lives -= 1
                if player.lives > 0:
                    play_sound("lose_life")
                    revive_ball = True
                game.game_state = "PAUSED"

            # Get frame time for motion calculations
            dt = game.frame_dur()

            ### OBJECT MOVEMENT
            player.move(dt)
            
            # Move powerups. Must do this before moving the balls because we check for width modifying powerups here too
            # If the paddle width changes AFTER checking collisions with the ball, the collisions will always be off
            for powerup in all_powerups:
                if powerup.is_alive:
                    powerup.move(dt)

                    # Kill the powerup object if hits bottom of screen
                    if powerup.y > (PLAYER_INIT_Y - 5):
                        powerup.is_alive = False
                        all_powerups.pop(all_powerups.index(powerup))

                    player, all_balls = powerup.check_gained_powerup(player, all_balls, all_powerups)

            # Move balls
            for ball_obj in all_balls:
                ball_obj.draw_ball(artist)
                ball_obj.move(dt)
                dead, all_bricks = ball_obj.check_collision(player, all_bricks, all_powerups, max_brick_y)
                if dead == "dead":
                    all_balls.pop(all_balls.index(ball_obj))

            if revive_ball:
                ball_obj.x, ball_obj.y = BALL_INIT_POS[level]
                ball_obj.velocity = BALL_INIT_VELOCITY[level]
                ball_obj.passthrough = False
                all_balls.append(ball_obj)
                revive_ball = False

            remove_laser_powerup = False
            if player.has_laser():
                # Check if the laser powerup has timed out
                if time.perf_counter() - player.time_got_laser > 10:
                    remove_laser_powerup = True

                # Move paddle and check for spacebar presses for laser bolts
                laser_bolt = player.check_laser_press(all_lasers)
                if laser_bolt is not None:
                    all_lasers.append(laser_bolt)

                # Move laser bolts
                for i, bolt in enumerate(all_lasers):
                    bolt.move(dt)
                    dead = bolt.check_collision(all_bricks, all_powerups, max_brick_y)
                    if dead == "dead":
                        all_lasers.pop(i)

            ### DRAWING
            artist.draw_border(colour=COLOURS['GREY2'])
            player.draw_paddle()
            for brick_obj in all_bricks:
                if brick_obj.is_alive:
                    brick_obj.draw_brick_sprite()
            
            if player.has_laser():
                for i, bolt in enumerate(all_lasers):
                    bolt.draw_laser()
                
            for powerup in all_powerups:
                powerup.draw()

            # Remove multi powerup if only one ball left
            remove_multi_powerup = len(all_balls) == 1 and "multi" in player.powerups
            powerups_changed = player.powerup_gained
            update_bar = remove_multi_powerup or remove_laser_powerup or powerups_changed
            if update_bar:
                if remove_multi_powerup:
                    player.remove_powerup("multi")
                if remove_laser_powerup:
                    player.remove_powerup("laser")

                artist.draw_info_bar(player.lives, player.powerups, player.width)
                player.powerup_gained = False # Must always set back to False as this flag should only last one frame
                pg.display.update()

            else:
                # Only update playable area. Info bar will be updated in relevant sections if required
                pg.display.update((0, 0, artist.SCREEN_X, INFO_BAR_START))

            # Check for special key combinations
            all_bricks = game.check_system_keys(all_bricks)

if __name__ == "__main__":
    start_game()
