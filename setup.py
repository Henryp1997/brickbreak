import cx_Freeze
import os
executables = [cx_Freeze.Executable("brickbreak.py")]
cwd = os.getcwd()
cx_Freeze.setup(
    name="Brickbreaker",
    options={"build_exe": {"packages":["pygame"],
                           "include_files":['assets/bounce.wav', 'assets/smash.wav', 'assets/tosh.jpg', 'assets/wall.wav']}},
    executables = executables
    )