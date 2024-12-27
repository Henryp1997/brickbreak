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

            if not brick_obj.is_alive:
                # Only generate powerup if brick was destroyed
                brick_obj.generate_powerup(all_powerups)


    def __brick_hit_bottom(
        self,
        b,
        neighbours_alive,
        negate_speed
    ) -> bool:
        if not neighbours_alive[0]:
            if self.velocity[1] < 0: # Can only hit bottom if moving upwards
                # Hit bottom. Snap ball to bottom of brick. See self.ceiling_collide for same logic
                self.x += (self.velocity[0] / -self.velocity[1]) * (self.y - b)
                self.y = b
                self.velocity = (self.velocity[0], negate_speed * self.velocity[1])
                return True
        return False
    
    
    def __brick_hit_top(
        self,
        t,
        neighbours_alive,
        negate_speed
    ) -> bool:
        if not neighbours_alive[1]:
            if self.velocity[1] > 0: # Can only hit the top if moving downwards
                # Hit top. Snap ball to top of brick. See self.ceiling_collide for same logic
                self.x += (self.velocity[0] / -self.velocity[1]) * (self.y + self.height - t)
                self.y = t - self.height
                self.velocity = (self.velocity[0], negate_speed * self.velocity[1])
                return True
        return False

    
    def __brick_hit_right(
        self,
        r,
        neighbours_alive,
        negate_speed
    ) -> bool:
        if not neighbours_alive[3]:
            if self.velocity[0] < 0: # Can only hit right if moving left
                # Hit right. Snap ball to right of brick. See self.ceiling_collide for same logic
                self.y += (self.velocity[1] / self.velocity[0]) * (r - self.x)
                self.x = r
                self.velocity = (negate_speed * self.velocity[0], self.velocity[1])
                return True
        return False


    def __brick_hit_left(
        self,
        l,
        neighbours_alive,
        negate_speed
    ) -> bool:
        if not neighbours_alive[2]:
            if self.velocity[0] > 0: # Can only hit the left if moving to the right/
                # Hit left. Snap ball to left of brick. See self.ceiling_collide for same logic
                self.y += (self.velocity[1] / self.velocity[0]) * (l - self.x - self.height)
                self.x = l - self.height
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


    def check_collision(self, player, all_bricks, all_powerups, max_brick_y, artist) -> tuple:
        ball_v_mag = self.v_mag()

        # Collision with brick. Only check if close enough to the lowest brick
        if self.y < max_brick_y + 30:
            # Only check the bricks within a certain distance of the ball
            bricks_to_check = [i for i in all_bricks if math.sqrt((self.x - i.x)**2 + (self.y - i.y)**2) < 1.25*BRICK_DEFAULT_WIDTH]
            all_bricks_coords = [(brick_obj.x, brick_obj.y) for brick_obj in all_bricks]

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
                    True if (l, b) in all_bricks_coords else False,                        # Neighbour below
                    True if (l, t - BRICK_DEFAULT_HEIGHT) in all_bricks_coords else False, # Neighbour above
                    True if (l - BRICK_DEFAULT_WIDTH, t) in all_bricks_coords else False,  # Neighbour to the left
                    True if (r, t) in all_bricks_coords else False                         # Neighbour to the right
                )

                brick_hit = False

                # Calculate coordinates of ball on next frame
                interpolated_x1 = self.x + self.velocity[0]
                interpolated_y1 = self.y + self.velocity[1]
                interpolated_x2 = self.x + self.height + self.velocity[0]
                interpolated_y2 = self.y + self.height + self.velocity[1]

                ball_in_brick_next_frame = ((l <= interpolated_x1 < r) and (t <= interpolated_y1 < b)) or ((l <= interpolated_x2 < r) and (t <= interpolated_y2 < b))
                if ball_in_brick_next_frame:
                    ball_center = (interpolated_x1 + 0.5*self.height, interpolated_y1 + 0.5*self.height)
                    
                    bc, wc = ball_center, brick_obj.center
                    m = BRICK_DEFAULT_HEIGHT / BRICK_DEFAULT_WIDTH # Gradient of diagonal lines connecting brick's corners
                    grad = abs((bc[1] - wc[1]) / (bc[0] - wc[0]))  # Use the gradient of the line connecting the ball and brick centers to determine which face was hit
                    if bc[0] > wc[0]:
                        # Ball to the right of brick center
                        if bc[1] > wc[1]:
                            # Ball below brick center
                            if grad <= m:
                                brick_hit = self.__brick_hit_right(r, neighbours_alive, negate_speed)
                            elif grad > m:
                                brick_hit = self.__brick_hit_bottom(b, neighbours_alive, negate_speed)
                        elif bc[1] < wc[1]:
                            # Ball above brick center
                            if grad <= m:
                                brick_hit = self.__brick_hit_right(r, neighbours_alive, negate_speed)
                            elif grad > m:
                                brick_hit = self.__brick_hit_top(t, neighbours_alive, negate_speed)
                    
                    elif bc[0] < wc[0]:
                        # Ball to the left of brick center
                        if bc[1] > wc[1]:
                            # Ball below brick center
                            if grad <= m:
                                brick_hit = self.__brick_hit_left(l, neighbours_alive, negate_speed)
                            elif grad > m:
                                brick_hit = self.__brick_hit_bottom(b, neighbours_alive, negate_speed)
                        elif bc[1] < wc[1]:
                            # Ball above center
                            if grad <= m:
                                brick_hit = self.__brick_hit_left(l, neighbours_alive, negate_speed)
                            elif grad > m:
                                brick_hit = self.__brick_hit_top(t, neighbours_alive, negate_speed)

                if brick_hit:
                    self.update_bricks(all_bricks, all_powerups, brick_obj, brick_hit)
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
