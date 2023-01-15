import pygame as pg
import os

colours = {
    'BLUE': (0, 100, 200),
    'DARK_BLUE': (0,55,255),
    'RED' : (225, 25, 25),
    'YELLOW': (255, 255, 0),
    'GREEN': (0, 220, 40),
    'BLACK': (15, 15, 15),
    'WHITE': '#ffffff',
    'GREY1': '#d1d1d1',
    'GREY2': '#a1a1a1',
    'PINK': '#fc03f8',
    'PURPLE': '#7734eb',
    'ORANGE': '#f5a742',
    'ELEC_BLUE': '#59CBE8'
}

assets_path = f'{os.path.dirname(os.path.abspath(__file__))}/assets'

screen_x = 1000
screen_y = screen_x*(9/10)
player_default_width = 150
player_short = 100
player_long = 225
all_widths = [player_short,player_default_width,player_long]
player_init_x = (screen_x-player_default_width)/2
player_init_y = screen_y*(15/18)
ball_init_x = screen_x*0.7
ball_init_y = screen_y/3
ball_init_height = 10
ball_init_velocity = (-7,7)
laser_bolt_init_width = 5
laser_bolt_init_height = 25
laser_cooldown_time = 50 # time in frames
brick_default_width = 70
brick_default_height = 30

info_bar_start = player_init_y + 40
all_powerup_types = {
    'Multi': ('multi',175,'multi_powerup'),
    'Fast ball': ('ball_speed',220,'fast_ball_powerup'),
    'Unstoppable ball': ('ball_pass_through',288,'unstop_powerup'),
    'Laser': ('laser',400,'laser_powerup'),
    'Fast paddle': ('paddle_speed',450,'fast_pad_powerup'),
    'Large paddle': ('paddle_size_up',540,'large_powerup'),
    'Small paddle': ('paddle_size_down',635,'small_powerup'),
    'Extra Life': ('extra_life',None,'life_powerup')
}

screen = pg.display.set_mode((screen_x,screen_y))