import pygame as pg
import math
import numpy as np
from variables import (
    assets_path,
    player_init_y,
    screen_x,
    screen_y,
    brick_default_width,
    brick_default_height
)
from utils import play_sound

class Ball():
    def __init__(self, x, y, velocity, passthrough) -> None:
        self.velocity = velocity
        self.height = 10
        self.x, self.y = x, y
        self.passthrough = passthrough # Can the ball delete bricks without bouncing (requires powerup)
        self.image = pg.image.load(f"{assets_path}/player_sprites/ball_default.png").convert_alpha()
        self.unstop_image = pg.image.load(f"{assets_path}/player_sprites/ball_unstop.png").convert_alpha()
    
    def move(self) -> None:
        self.x += self.velocity[0]; self.y += self.velocity[1]

    def v_mag(self) -> float:
        """ Calculate the magnitude of the ball's velocity """
        return math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)
    
    def v_comps(self, vmag, theta) -> tuple:
        """ Calculate the velocity components from magnitude """
        vx = +vmag * np.cos(theta)
        vy = -vmag * np.sin(theta) # Down is increasing y, hence -ve sign
        return vx, vy
    
    def v_angle(self) -> float:
        vx, vy = self.velocity
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

    def draw_ball(self, artist) -> None:
        img = self.image
        if self.passthrough:
            img = self.unstop_image          
        if (self.y + self.height) > (player_init_y + round(screen_y / 30)): # Don't draw if in the info bar section of the screen
            return
        artist.screen.blit(img, (self.x, self.y))
        
    def change_speed_upon_brick_collide(
            self,
            brick_obj, 
            all_bricks, 
            all_powerups, 
            brick_boundaries, 
            direction,              # 0: up 1: right 2: down 3: left
            dont_change_ball_speed, 
            negate_speed_x, 
            negate_speed_y
        ) -> None:
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
        if abs(coords[direction][0] - brick_boundaries[0]) < 10: # Currently uses buffer size of 10 to check collisions. TODO
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
                    # Turn the padlocked brick into a normal 2-health brick if there is one
                    locked_brick.health -= 1

            brick_obj.generate_powerup(all_powerups)
        return brick_hit, all_bricks

    def check_collision(self, player, all_bricks, all_powerups, max_brick_y):
        ball_v_mag = self.v_mag()

        # collision with paddle
        if abs(self.y + self.height - player.y) < 5:
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

                angle = ((grad * relative_x) + intercept) * np.pi/180
                if self.velocity[0] > 0:
                    play_sound("bounce")
                    self.velocity = (
                        negate_speed*ball_v_mag*np.cos(angle),
                        -ball_v_mag*np.sin(angle)
                    )
                    return None, all_bricks
                elif self.velocity[0] < 0:
                    play_sound("bounce")
                    self.velocity = (
                        negate_speed*ball_v_mag*np.cos(angle),
                        -ball_v_mag*np.sin(angle)
                    )
                    return None, all_bricks

        # Collision with brick. Only check if close enough to the lowest brick
        if self.y < max_brick_y + 10:
            # Only check the bricks within a certain distance of the ball
            bricks_to_check = [i for i in all_bricks if math.sqrt((self.x - i.x)**2 + (self.y - i.y)**2) < 1.25*brick_default_width]

            if 'ball_pass_through' in player.powerups:
                negate_speed = 1
            else:
                negate_speed = -1
                
            for brick_obj in bricks_to_check:
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

                brick_hit, all_bricks = self.change_speed_upon_brick_collide(brick_obj, all_bricks, all_powerups, [b, l, r], 0, dont_change_ball_speed, 1, negate_speed)
                if brick_hit:
                    break

                # Hit brick from left side
                brick_hit, all_bricks = self.change_speed_upon_brick_collide(brick_obj, all_bricks, all_powerups, [l, t, b], 1, dont_change_ball_speed, negate_speed, 1)
                if brick_hit:
                    break

                # Hit brick from above
                brick_hit, all_bricks = self.change_speed_upon_brick_collide(brick_obj, all_bricks, all_powerups, [t, l, r], 2, dont_change_ball_speed, 1, negate_speed)
                if brick_hit: 
                    break

                # Hit brick from right side
                brick_hit, all_bricks = self.change_speed_upon_brick_collide(brick_obj, all_bricks, all_powerups, [r, t, b], 3, dont_change_ball_speed, negate_speed, 1)
                if brick_hit:
                    break

        # Collision with walls
        if self.y < 5:
            if self.velocity[1] < 0: # Prevents getting stuck out of bounds
                self.velocity = (self.velocity[0], -self.velocity[1])
                play_sound("wall")

        # If close to either the left or right wall
        close_to_left = self.x < 5
        close_to_right = self.x + self.height > screen_x - 5

        if close_to_left:
            wall_pos = 5
            # Check if x coordinate will be beyond the wall on next frame
            if (self.x + self.velocity[0]) < wall_pos:
                # If so, snap ball to the wall and negate x velocity. Move ball along the y direction
                # the required amount to remain along the same vector that the ball was travelling
                self.y += (self.velocity[1] / self.velocity[0]) * (wall_pos - self.x)
                self.x = wall_pos
                play_sound("wall")
                self.velocity = (-self.velocity[0], self.velocity[1])

        elif close_to_right:
            wall_pos = screen_x - 5
            # Check if x coordinate will be beyond the wall on next frame.
            # For the right wall we need to check the right edge of the ball
            if (self.x + self.height + self.velocity[0]) > wall_pos:
                # If so, snap ball to the wall and negate x velocity. Move ball along the y direction
                # the required amount to remain along the same vector that the ball was travelling
                self.y += (self.velocity[1] / self.velocity[0]) * (wall_pos - self.x - self.height)
                self.x = wall_pos - self.height
                play_sound("wall")
                self.velocity = (-self.velocity[0], self.velocity[1])
        
        # Ball died
        if self.y + self.height > player_init_y + 30:
            return "dead", all_bricks

        return None, all_bricks
