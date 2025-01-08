import cx_Freeze
from consts import ASSETS_PATH
import os
import sys
from glob import glob
import zipfile

here = os.path.dirname(os.path.realpath(__file__))

build_num = 1.0

# Force build mode
if len(sys.argv) == 1:
    sys.argv.append("build")

if sys.argv[1] != "release":
    # Arg for release only not included
    executables = [
        cx_Freeze.Executable(
            f"{here}/brickbreak.py",
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

build_folder = glob(f"{here}/build/*")[0]
with zipfile.ZipFile(f"{here}/release{build_num}.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(build_folder):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, build_folder)
            zipf.write(file_path, arcname)
