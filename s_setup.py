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

base = 'Console'

executables = [
    Executable('server.py', base=base, targetName='Survival Server')
]

setup(
    name='Survival Prototype Server',
    version='0.1a',
    description='A top-down survival game. (SERVER BINARY)',
    options=dict(build_exe=buildOptions),
    executables=executables
)
