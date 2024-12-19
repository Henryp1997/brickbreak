import pygame as pg
from consts import ASSETS_PATH

def play_sound(sound) -> None:
    pg.mixer.Sound.play(pg.mixer.Sound(f"{ASSETS_PATH}/{sound}.wav"))
