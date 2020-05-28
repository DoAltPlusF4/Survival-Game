# Size Settings
CHUNK_SIZE = 16
TILE_SIZE = 16

# Networking
HEADER_SIZE = 32

# Game Settings, should be configurable
CAMERA_SPEED = 50
LOAD_DISTANCE = 5
VIEWPORT_SIZE = (
    CHUNK_SIZE*TILE_SIZE*3,
    CHUNK_SIZE*TILE_SIZE*2
)

# Tile Colours, will be moved into the mods system
# TODO: Add actual tile resources.
TILES = {
    0: "#07259e",  # Deep Water
    1: "#2eb1cc",  # Shallow Water
    2: "#f4f484",  # Sand
    3: "#85e24f",  # Grass
    4: "#075405",  # Forest
    5: "#515151",  # Mountain/Rock
    6: "#ed5f0a",  # Magma
}
