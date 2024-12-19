import cx_Freeze
from consts import ASSETS_PATH
import os

executables = [
    cx_Freeze.Executable(
        f"{os.path.dirname(os.path.realpath(__file__))}/brickbreak.py",
        base="Win32GUI",
        target_name="Brickbreaker.exe"
    )
]

cx_Freeze.setup(
    name="Brickbreaker",
    options={
        "build_exe": {
            "include_files": [(ASSETS_PATH, "assets")]
        }
    },
    executables=executables
)