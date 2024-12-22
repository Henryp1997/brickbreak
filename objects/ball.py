import pygame as pg
import math
import numpy as np
from consts import (
    ASSETS_PATH,
    PLAYER_INIT_Y,
    SCREEN_X,
    SCREEN_Y,
    LEFT_WALL_X,
    RIGHT_WALL_X,
    BRICK_DEFAULT_WIDTH,
    BRICK_DEFAULT_HEIGHT
)
from utils import play_sound

class Ball():
    def __init__(self, x, y, velocity, passthrough) -> None:
        self.velocity = velocity
        self.height = 10
        self.x, self.y = x, y
        self.passthrough = passthrough # Can the ball delete bricks without bouncing (requires powerup)
        self.image = pg.image.load(f"{ASSETS_PATH}/player_sprites/ball_default.png").convert_alpha()
        self.unstop_image = pg.image.load(f"{ASSETS_PATH}/player_sprites/ball_unstop.png").convert_alpha()
    

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
        if (self.y + self.height) > (PLAYER_INIT_Y + round(SCREEN_Y / 30)): # Don't draw if in the info bar section of the screen
            return
        artist.screen.blit(img, (self.x, self.y))
    

    def update_bricks(self, all_bricks, all_powerups, brick_obj, brick_hit) -> None:
        """ brick_obj is the brick object that was hit """
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


    def brick_collide_vertical(
        self,
        brick_obj,
        y_lim,
        x_lim1,
        x_lim2, 
        negate_speed,
        height_adjustment=0
    ) -> bool:
        if abs(self.y + height_adjustment - y_lim) < 10:
            if x_lim1 <= (self.x + self.height) and self.x <= x_lim2:
                if negate_speed == 1 and brick_obj.health > 1:
                    negate_speed *= -1
                self.velocity = (self.velocity[0], negate_speed * self.velocity[1])
                return True
        return False
    

    def brick_collide_horizontal(
        self,
        brick_obj,
        x_lim,
        y_lim1,
        y_lim2,
        negate_speed,
        width_adjustment=0,
    ) -> bool:
        if abs(self.x + width_adjustment - x_lim) < 10:
            # Check y positioning. Downwards is negative y
            if y_lim1 >= (self.y + self.height) and self.y >= y_lim2:
                if negate_speed == 1 and brick_obj.health > 1:
                    negate_speed *= -1
                self.velocity = (negate_speed * self.velocity[0], self.velocity[1])
                return True
        return False

    def paddle_collide(self, ball_v_mag, player) -> None:
        """ Calculate what the angle of reflection should be when hitting the paddle.
            This should vary from 90 deg if the ball hits the centre to 20 degrees if the ball hits the edges """
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
            elif self.velocity[0] < 0:
                play_sound("bounce")
                self.velocity = (
                    negate_speed*ball_v_mag*np.cos(angle),
                    -ball_v_mag*np.sin(angle)
                )


    def wall_collide(self, wall_x, sign=1, width_adjustment=0):
        """ Control collisions with the left or right wall """
        # Check if x coordinate will be beyond the wall on next frame
        if sign * (self.x + self.velocity[0] + width_adjustment) < (sign * wall_x):
            # If so, snap ball to the wall and negate x velocity. Move ball along the y direction
            # the required amount to remain along the same vector that the ball was travelling
            self.y += (self.velocity[1] / self.velocity[0]) * (wall_x - self.x - width_adjustment)
            self.x = wall_x - width_adjustment
            play_sound("wall")
            self.velocity = (-self.velocity[0], self.velocity[1])


    def ceiling_collide(self, ceiling_y=5):
        """ Control collisions with the ceiling """
        # Check if y coordinate will be above the ceiling on next frame. Upwards is negative y
        if (self.y + self.velocity[1]) < ceiling_y:
            # If so, snap ball to the ceiling and negate y velocity. Move ball along the x direction
            # the required amount to remain along the same vector that the ball was travelling
            self.x += (self.velocity[0] / -self.velocity[1]) * (self.y - ceiling_y)
            self.y = ceiling_y
            play_sound("wall")
            self.velocity = (self.velocity[0], -self.velocity[1])


    def check_collision(self, player, all_bricks, all_powerups, max_brick_y) -> tuple:
        ball_v_mag = self.v_mag()

        # Collision with brick. Only check if close enough to the lowest brick
        if self.y < max_brick_y + 10:
            # Only check the bricks within a certain distance of the ball
            bricks_to_check = [i for i in all_bricks if math.sqrt((self.x - i.x)**2 + (self.y - i.y)**2) < 1.25*BRICK_DEFAULT_WIDTH]
            all_bricks_coords = [(brick_obj.x, brick_obj.y) for brick_obj in bricks_to_check]

            if 'ball_pass_through' in player.powerups:
                negate_speed = 1
            else:
                negate_speed = -1
                
            for brick_obj in bricks_to_check:
                # Left, right, top and bottom coords of the brick
                l, r, t, b = (
                    brick_obj.x, 
                    brick_obj.x + BRICK_DEFAULT_WIDTH, 
                    brick_obj.y, 
                    brick_obj.y + BRICK_DEFAULT_HEIGHT
                )

                # Check whether there is a brick blocking the current one
                neighbours_alive = (
                    True if (l, b) in all_bricks_coords else False,
                    True if (l, t - BRICK_DEFAULT_HEIGHT) in all_bricks_coords else False,
                    True if (l - BRICK_DEFAULT_WIDTH, t) in all_bricks_coords else False,
                    True if (r, t) in all_bricks_coords else False
                )

                brick_hit = False
                # Hit brick from bottom. Only check if moving upwards
                if not neighbours_alive[0] and self.velocity[1] < 0:
                    brick_hit = self.brick_collide_vertical(brick_obj, b, l, r, negate_speed)

                # Hit brick from above. Only check if moving downwards
                if not neighbours_alive[1] and not brick_hit and self.velocity[1] > 0:
                    brick_hit = self.brick_collide_vertical(brick_obj, t, l, r, negate_speed, height_adjustment=self.height)

                # Hit brick from left side. Only check if moving right
                if not neighbours_alive[2] and not brick_hit and self.velocity[0] > 0:
                    brick_hit = self.brick_collide_horizontal(brick_obj, l, b, t, negate_speed, width_adjustment=self.height)

                if not neighbours_alive[3] and not brick_hit and self.velocity[0] < 0:
                    # Hit brick from right side
                    brick_hit = self.brick_collide_horizontal(brick_obj, r, b, t, negate_speed)
                
                if brick_hit:
                    self.update_bricks(all_bricks, all_powerups, brick_obj, brick_hit)
                    return None, all_bricks

        # Collision with paddle
        if (self.y + self.height) > (player.y - 5):
            if self.velocity[1] > 0:
                # Only check for paddle collisions if moving downards (prevents weird multi collisions)    
                self.paddle_collide(ball_v_mag, player)

        # Collision with walls
        close_to_top = self.y < 5
        if close_to_top:
            self.ceiling_collide()

        # If close to either the left or right wall
        close_to_left = self.x < 5
        close_to_right = self.x + self.height > SCREEN_X - 5
        if close_to_left:
            self.wall_collide(wall_x=LEFT_WALL_X)
        elif close_to_right:
            self.wall_collide(wall_x=RIGHT_WALL_X, width_adjustment=self.height, sign=-1)
        
        # Ball died
        if self.y + self.height > PLAYER_INIT_Y + 30:
            return "dead", all_bricks

        return None, all_bricks
