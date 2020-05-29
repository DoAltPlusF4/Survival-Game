import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(
    packages=[
        "source",
        "noise",
        "pymunk",
        "pyglet"
    ],
    excludes=[
    ]
)

base = "Win32GUI" if sys.platform == "win32" else None

executables = [
    Executable("client.py", base=base, targetName='Survival Client')
]

setup(
    name="Survival Prototype Client",
    version="0.1a",
    description="A top-down survival game. (CLIENT BINARY)",
    options=dict(build_exe=buildOptions),
    executables=executables
)
