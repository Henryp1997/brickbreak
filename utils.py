import pygame as pg
from variables import assets_path

def play_sound(sound) -> None:
    pg.mixer.Sound.play(pg.mixer.Sound(f"{assets_path}/{sound}.wav"))
