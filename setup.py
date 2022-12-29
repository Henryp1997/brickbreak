import cx_Freeze
import os
from variables import *
executables = [cx_Freeze.Executable("brickbreak.py")]
cwd = os.getcwd()
cx_Freeze.setup(
    name="Brickbreaker",
    options={"build_exe": {"packages":["pygame"],
                           "include_files":[
                            f'{assets_path}/bounce.wav', 
                            f'{assets_path}/smash.wav', 
                            f'{assets_path}/tosh.jpg', 
                            f'{assets_path}/wall.wav',
                            f'{assets_path}/laser_shot.wav',
                            f'{assets_path}/game_over.wav',
                            f'{assets_path}/lose_life.wav',
                            f'{assets_path}/brick_cracked.png',
                            f'{assets_path}/brick_h1.png',
                            f'{assets_path}/brick_h2.png',
                            f'{assets_path}/player_sprites/paddle.png',
                            f'{assets_path}/player_sprites/paddle_short.png',
                            f'{assets_path}/player_sprites/paddle_long.png',
                            f'{assets_path}/powerup_sprites/fast_ball_powerup.png',
                            f'{assets_path}/powerup_sprites/fast_pad_powerup.png',
                            f'{assets_path}/powerup_sprites/large_powerup.png',
                            f'{assets_path}/powerup_sprites/small_powerup.png',
                            f'{assets_path}/powerup_sprites/laser_powerup.png',
                            f'{assets_path}/powerup_sprites/life_powerup.png',
                            f'{assets_path}/powerup_sprites/small_powerup.png',
                            f'{assets_path}/powerup_sprites/unstop_powerup.png',

                           ]}},
    executables = executables
    )