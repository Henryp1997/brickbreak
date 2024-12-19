import os
import sys

X_RES    = 1150
Y_RES    = int(16 * X_RES / 9)
SCREEN_X = int(0.75 * X_RES)
SCREEN_Y = int(SCREEN_X * (9 / 10))
 
COLOURS = {
    "BLUE":      "#0064C8",
    "DARK_BLUE": "#0037FF",
    "ELEC_BLUE": "#59CBE8", # 'Electric' blue
    "RED" :      "#E11919",
    "YELLOW":    "#FFFF00",
    "GREEN":     "#00DC28",
    "BLACK":     "#0F0F0F",
    "WHITE":     "#FFFFFF",
    "GREY1":     "#D1D1D1",
    "GREY2":     "#A1A1A1",
    "PINK":      "#FC03F8",
    "PURPLE":    "#7734EB",
    "ORANGE":    "#F5A742",
    "FIRE":      "#FC4903"
}

if getattr(sys, "frozen", False):
    # If the application is frozen (bundled by cx_Freeze)
    BASE_PATH = os.path.dirname(sys.executable)
else:
    # If running in a development environment
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

ASSETS_PATH = f"{BASE_PATH}/assets"

LEFT_WALL_X = 5
RIGHT_WALL_X = SCREEN_X - 5

PLAYER_DEFAULT_SPEED = 10
PLAYER_FAST_SPEED    = 15
PLAYER_DEFAULT_WIDTH = 150
PLAYER_SHORT         = 100
PLAYER_LONG          = 225

ALL_PLAYER_WIDTHS = [
    PLAYER_SHORT,
    PLAYER_DEFAULT_WIDTH,
    PLAYER_LONG
]

PLAYER_INIT_X = (SCREEN_X - PLAYER_DEFAULT_WIDTH) / 2
PLAYER_INIT_Y = SCREEN_Y * (15 / 18)

BALL_INIT_POS = {
    -1: (SCREEN_X*0.7, SCREEN_Y/3),
    0:  (SCREEN_X*0.7, SCREEN_Y/3),
    1:  (SCREEN_X*0.6, SCREEN_Y/3),
    2:  (SCREEN_X*0.9, SCREEN_Y/3),
}

BALL_INIT_VELOCITY     = (-7, 7)
LASER_BOLT_INIT_WIDTH  = 5
LASER_BOLT_INIT_HEIGHT = 25
LASER_COOLDOWN_TIME    = 50 # time in frames
BRICK_DEFAULT_WIDTH    = 70
BRICK_DEFAULT_HEIGHT   = 30

INFO_BAR_START = PLAYER_INIT_Y + 40
ALL_POWERUP_TYPES = {
    "Multi":            ("multi",             175,  "multi_powerup"),
    "Fast ball":        ("ball_speed",        220,  "fast_ball_powerup"),
    "Unstoppable ball": ("ball_pass_through", 288,  "unstop_powerup"),
    "Laser":            ("laser",             400,  "laser_powerup"),
    "Fast paddle":      ("paddle_speed",      450,  "fast_pad_powerup"),
    "Large paddle":     ("paddle_size_up",    540,  "large_powerup"),
    "Small paddle":     ("paddle_size_down",  635,  "small_powerup"),
    "Extra Life":       ("extra_life",        None, "life_powerup")
}
NUM_POWERUPS = len(ALL_POWERUP_TYPES)
