import pygame as pg
from consts import (
    ASSETS_PATH,
    SCREEN_X,
    SCREEN_Y,
    COLOURS,
    INFO_BAR_START,
    ALL_POWERUP_TYPES,
    PLAYER_DEFAULT_WIDTH,
    PLAYER_LONG,
    PLAYER_SHORT,
    BALL_INIT_POS
)

class Artist():
    def __init__(self, SCREEN_X, SCREEN_Y, start_or_retry) -> None:
        self.screen = pg.display.set_mode((SCREEN_X, SCREEN_Y))
        self.SCREEN_X = SCREEN_X
        self.SCREEN_Y = SCREEN_Y
        self.start_or_retry = start_or_retry
 

    def fill_screen(self, colour) -> None:
        self.screen.fill(colour)


    def draw_border(self, colour, full=False) -> None:
        if full:
            rect = pg.Rect((0, 0), (SCREEN_X, SCREEN_Y))
        else:
            rect = pg.Rect((0, 0), (SCREEN_X, INFO_BAR_START + round(SCREEN_X*0.002)))
        pg.draw.rect(self.screen, colour, rect, width=5)


    def draw_start_text(self) -> None:
        rect_width = 600
        rect_height = 200
        rect_coords = (self.SCREEN_X/2 - rect_width/2, self.SCREEN_Y/4)
        text_pos = (rect_coords[0] + rect_width/11, rect_coords[1] + rect_height/2.5)
        font = pg.font.Font(f"{ASSETS_PATH}/fonts/arcade.ttf", 25)

        pg.draw.rect(
            self.screen,
            "#666666",
            pg.Rect(
                (rect_coords[0], rect_coords[1], rect_width, rect_height)
            ),
            border_radius=4
        )
        self.screen.blit(
            font.render(f"Press Space to {self.start_or_retry}", True, COLOURS["ELEC_BLUE"]), text_pos
        )


    def draw_game_over_screen(self) -> None:
        self.fill_screen(colour=COLOURS["BLACK"])
        self.draw_border(colour=COLOURS["GREY2"], full=True)
        text1_pos = (self.SCREEN_X/2 - round(self.SCREEN_X/10), self.SCREEN_Y/2 - (self.SCREEN_Y/9))
        text2_pos = (text1_pos[0] - round(self.SCREEN_X*0.03), text1_pos[1] + round(self.SCREEN_Y*(5/90)))
        font = pg.font.SysFont("Arial", 30)
        self.screen.blit(
            font.render("GAME OVER", True, COLOURS["ELEC_BLUE"]), text1_pos
        )
        self.screen.blit(
            font.render("Press Esc to restart", True, COLOURS["ELEC_BLUE"]), text2_pos
        )


    def draw_info_bar(self, lives, player_powerups, player_width) -> None:
        pg.draw.rect(self.screen, COLOURS["GREY2"], pg.Rect((0, INFO_BAR_START), (self.SCREEN_X, self.SCREEN_Y - INFO_BAR_START)), width=5)
        font = pg.font.Font(f"{ASSETS_PATH}/fonts/arcade.ttf", 20)
        self.screen.blit(
            font.render(f"Lives", True, COLOURS["ELEC_BLUE"]), (SCREEN_X*0.02, SCREEN_Y*0.88)
        )
        font = pg.font.Font(f"{ASSETS_PATH}/fonts/arcade.ttf", 20)
        self.screen.blit(
            font.render(f"{lives}", True, COLOURS["GREY1"]), (SCREEN_X*0.06, SCREEN_Y*0.93)
        )
        font = pg.font.Font(f"{ASSETS_PATH}/fonts/arcade.ttf", 20)
        self.screen.blit(
            font.render(f"Active modifiers", True, COLOURS["ELEC_BLUE"]), (SCREEN_X*0.17, SCREEN_Y*0.88)
        )

        font = pg.font.Font(f"{ASSETS_PATH}/fonts/arcade.ttf", 8)
        for i, j in enumerate(list(ALL_POWERUP_TYPES.keys())):
            power_name = ALL_POWERUP_TYPES[j][0]
            if power_name != "extra_life":
                col = COLOURS["GREY1"]
                if "paddle_size" in power_name:
                    if player_width == PLAYER_DEFAULT_WIDTH:
                        col = COLOURS["GREY1"]
                    elif "up" in power_name and player_width == PLAYER_LONG:
                        col = COLOURS["FIRE"]
                    elif "down" in power_name and player_width == PLAYER_SHORT:
                        col = COLOURS["FIRE"]
                else:
                    col = COLOURS["GREY1"]
                    if power_name in player_powerups:
                        col = COLOURS["FIRE"]

                self.screen.blit(font.render(j, True, col), (ALL_POWERUP_TYPES[j][1], SCREEN_Y*0.935))


    def draw_dummy_ball(self, level) -> None:
        self.screen.blit(
            pg.image.load(f"{ASSETS_PATH}/player_sprites/ball_default.png").convert_alpha(),
            (BALL_INIT_POS[level][0], BALL_INIT_POS[level][1])
        )
