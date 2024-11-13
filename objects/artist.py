import pygame as pg
from variables import (
    assets_path,
    screen_x,
    colours,
    info_bar_start,
    all_powerup_types,
    player_default_width,
    player_long,
    player_short,
    ball_init_pos
)

class Artist():
    def __init__(self, screen_x, screen_y, start_or_retry) -> None:
        self.screen = pg.display.set_mode((screen_x, screen_y))
        self.screen_x = screen_x
        self.screen_y = screen_y
        self.start_or_retry = start_or_retry
 
    def fill_screen(self, colour) -> None:
        self.screen.fill(colour)

    def draw_border(self, colour) -> None:
        pg.draw.rect(self.screen, colour, pg.Rect((0, 0), (screen_x, info_bar_start + round(screen_x*0.002))), width=5)

    def draw_start_text(self) -> None:
        text_pos = (self.screen_x/2 - round(self.screen_x*0.13), self.screen_y/2 - (self.screen_y/9))
        font = pg.font.SysFont('Arial', 30)
        self.screen.blit(font.render(f'Press Space to {self.start_or_retry}', True, colours['RED']), text_pos)

    def draw_game_over_screen(self) -> None:
        self.fill_screen(colour=colours["BLACK"])
        self.draw_border(colour=colours["GREY2"])
        text1_pos = (self.screen_x/2 - round(self.screen_x/10), self.screen_y/2 - (self.screen_y/9))
        text2_pos = (text1_pos[0] - round(self.screen_x*0.03), text1_pos[1] + round(self.screen_y*(5/90)))
        font = pg.font.SysFont('Arial', 30)
        self.screen.blit(font.render('GAME OVER', True, colours['RED']), text1_pos)
        self.screen.blit(font.render('Press Esc to restart', True, colours['RED']), text2_pos)

    def draw_info_bar(self, lives, player_powerups, player_width) -> None:
        pg.draw.rect(self.screen, colours['GREY2'], pg.Rect((0, info_bar_start), (self.screen_x,self.screen_y - info_bar_start)), width=5)
        font = pg.font.SysFont('Arial', 30)
        self.screen.blit(font.render(f'Lives:', True, colours['RED']), (round(self.screen_x*0.02), info_bar_start + round(self.screen_x*0.02)))
        font = pg.font.SysFont('Arial', 25)
        self.screen.blit(font.render(f'{lives}', True, colours['GREY1']), (round(self.screen_x*(45/1000)), info_bar_start + round(self.screen_x*(58/1000))))
        font = pg.font.SysFont('Arial', 30)
        self.screen.blit(font.render(f'Active modifiers:', True, colours['RED']),(175, info_bar_start + 20))

        font = pg.font.SysFont('Arial', 15)
        for i, j in enumerate(list(all_powerup_types.keys())):
            power_name = all_powerup_types[j][0]
            if power_name != 'extra_life':
                col = colours['GREY1']
                if 'paddle_size' in power_name:
                    if player_width == player_default_width:
                        col = colours['GREY1']
                    elif 'up' in power_name and player_width == player_long:
                        col = colours['RED']
                    elif 'down' in power_name and player_width == player_short:
                        col = colours['RED']
                else:
                    if power_name in player_powerups:
                        col = colours['RED']
                    else:
                        col = colours['GREY1']
                self.screen.blit(font.render(j, True, col),(all_powerup_types[j][1], info_bar_start + self.screen_x*(65/850)))

    def draw_dummy_ball(self, level) -> None:
        self.screen.blit(
            pg.image.load(f'{assets_path}/player_sprites/ball_default.png').convert_alpha(),
            (ball_init_pos[level][0], ball_init_pos[level][1])
        )
