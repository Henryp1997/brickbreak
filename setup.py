import cx_Freeze
from variables import assets_path
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
            "include_files": [(assets_path, "assets")]
        }
    },
    executables=executables
)