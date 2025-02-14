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
    

    def move(self, dt) -> None:
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt


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
    

    def update_bricks(self, all_bricks, all_powerups, brick_obj) -> None:
        """ brick_obj is the brick object that was hit """
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

        if not brick_obj.is_alive:
            # Only generate powerup if brick was destroyed
            brick_obj.generate_powerup(all_powerups)


    def __brick_collide(
        self,
        neighbours_alive,
        l,
        r,
        t,
        b
    ) -> None:
        halfheight = 0.5*self.height

        # Get centre of ball one frame before ball entered brick
        cx, cy = self.x + halfheight - self.velocity[0], self.y + halfheight - self.velocity[1]

        # Gradient of velocity vector
        grad = self.velocity[1] / self.velocity[0]

        # Four intersection positions. The intersection between the ball's velocity vector and the brick edges
        collide_positions = [()]*4

        # Bottom
        x_collide_pos = (b - cy)/grad + cx
        # Check if result x position is between brick left and right (plus half ball's height)
        if (l - halfheight) <= x_collide_pos <= (r + halfheight):
            if not neighbours_alive[0] and self.velocity[1] < 0:
                collide_positions[0] = (x_collide_pos, b)

        # Top
        x_collide_pos = (t - cy)/grad + cx
        # Check if result x position is between brick left and right (plus half ball's height)
        if (l - halfheight) <= x_collide_pos <= (r + halfheight):
            if not neighbours_alive[1] and self.velocity[1] > 0:
                collide_positions[1] = (x_collide_pos, t)

        # Left
        y_collide_pos = grad*(l - cx) + cy
        # Check if result y position is between brick top and bottom (plus half ball's height)
        if (t - halfheight) <= y_collide_pos <= (b + halfheight):
            if not neighbours_alive[2] and self.velocity[0] > 0:
                collide_positions[2] = (l, y_collide_pos)

        # Right
        y_collide_pos = grad*(r - cx) + cy
        # Check if result y position is between brick top and bottom (plus half ball's height)
        if (t - halfheight) <= y_collide_pos <= (b + halfheight):
            if not neighbours_alive[3] and self.velocity[0] < 0:
                collide_positions[3] = (r, y_collide_pos)

        # Check which edge will be intersected first to conclude which side of the brick was hit
        distances = []
        for i in range(4):
            try:
                x, y = collide_positions[i]
                x_diff, y_diff = x - cx, y - cy
                distances.append(math.sqrt(x_diff**2 + y_diff**2))
            except:
                distances.append(10000)
        
        min_loc = distances.index(min(distances))
        collide_funcs = {
            0: self.__brick_hit_bottom,
            1: self.__brick_hit_top,
            2: self.__brick_hit_left,
            3: self.__brick_hit_right
        }
        return collide_funcs[min_loc](l, r, b, t)


    def __brick_hit_bottom(self, _l, _r, b, _t) -> None:
        # Hit bottom. Snap ball to bottom of brick. See self.ceiling_collide for same logic
        self.x += (self.velocity[0] / self.velocity[1]) * (b - self.y)
        self.y = b
        self.velocity = (self.velocity[0], -1 * self.velocity[1])

    
    def __brick_hit_top(self, _l, _r, _b, t) -> None:
        # Hit top. Snap ball to top of brick. See self.ceiling_collide for same logic
        self.x += (self.velocity[0] / self.velocity[1]) * (t - self.y - self.height)
        self.y = t - self.height
        self.velocity = (self.velocity[0], -1 * self.velocity[1])


    def __brick_hit_left(self, l, _r, _b, _t) -> None:
        # Hit left. Snap ball to left of brick. See self.wall_collide for same logic
        self.y += (self.velocity[1] / self.velocity[0]) * (l - self.x - self.height)
        self.x = l - self.height
        self.velocity = (-1 * self.velocity[0], self.velocity[1])

    
    def __brick_hit_right(self, _l, r, _b, _t) -> None:
        # Hit right. Snap ball to right of brick. See self.wall_collide for same logic
        self.y += (self.velocity[1] / self.velocity[0]) * (r - self.x)
        self.x = r
        self.velocity = (-1 * self.velocity[0], self.velocity[1])


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
        if self.y < max_brick_y + 30:
            # Only check the bricks within a certain distance of the ball
            bricks_to_check = [i for i in all_bricks if math.sqrt((self.x - i.x)**2 + (self.y - i.y)**2) < BRICK_DEFAULT_WIDTH]
            all_bricks_coords = [(brick_obj.x, brick_obj.y) for brick_obj in all_bricks]

            for brick_obj in bricks_to_check:
                # Left, right, top and bottom coords of the brick
                l, r, t, b = (
                    brick_obj.x, 
                    brick_obj.x + BRICK_DEFAULT_WIDTH, 
                    brick_obj.y, 
                    brick_obj.y + BRICK_DEFAULT_HEIGHT
                )

                # X and Y coordinates are within the current brick
                x_in_brick = (l <= self.x <= r) or (l <= (self.x + self.height) <= r)
                y_in_brick = (t <= self.y <= b) or (t <= (self.y + self.height) <= b)

                # Determine that the ball has collided if it is going to be in the brick on next frame
                ball_in_brick_next_frame = x_in_brick and y_in_brick
                if ball_in_brick_next_frame:
                    # To check whether there is a brick blocking the current one
                    neighbours_alive = (
                        True if (l, b) in all_bricks_coords else False,                        # Neighbour below
                        True if (l, t - BRICK_DEFAULT_HEIGHT) in all_bricks_coords else False, # Neighbour above
                        True if (l - BRICK_DEFAULT_WIDTH, t) in all_bricks_coords else False,  # Neighbour to the left
                        True if (r, t) in all_bricks_coords else False                         # Neighbour to the right
                    )

                    if ("ball_pass_through" not in player.powerups) or (brick_obj.health > 1):
                        # Health 2 and above bricks don't break instantly with unstoppable ball powerup
                        self.__brick_collide(neighbours_alive, l, r, t, b)

                    self.update_bricks(all_bricks, all_powerups, brick_obj)
                    return None, all_bricks

        # Collision with paddle
        near_paddle = (self.y + self.height) > (player.y - 10)
        past_paddle = (self.y + self.height) > player.y + 5
        if near_paddle and not past_paddle:
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
