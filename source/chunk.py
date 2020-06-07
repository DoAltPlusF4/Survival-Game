import noise
import pyglet

from . import constants as c


class Chunk:
    def __init__(self, matrix, position):
        self.matrix = matrix
        self.position = position

    def generateTiles(self, application, batch=None):
        self.application = application

        self.batch = batch
        if self.batch is None:
            self.batch = pyglet.graphics.Batch()

        self.tiles = {}

        for x in range(16):
            for y in range(16):
                id = self.matrix[y][x]
                colour = c.TILES[id]
                self.tiles[(x, y)] = pyglet.shapes.Rectangle(
                    x=(
                        x*c.TILE_SIZE +
                        self.position[0]*c.CHUNK_SIZE*c.TILE_SIZE
                    ),
                    y=(
                        y*c.TILE_SIZE +
                        self.position[1]*c.CHUNK_SIZE*c.TILE_SIZE
                    ),
                    width=c.TILE_SIZE,
                    height=c.TILE_SIZE,
                    color=tuple(int(colour[i+1:i+3], 16) for i in (0, 2, 4)),
                    group=self.application.world_layers["ground"]
                )

    def delete(self):
        for pos in self.tiles.keys():
            self.tiles[pos].delete()

    def draw(self):
        if hasattr(self, "batch"):
            self.batch.draw()
        else:
            print("WARN: Batch not found, check that you have run generateTiles.")

    @staticmethod
    def createBlank(position):
        matrix = [[0 for _ in range(16)] for _ in range(16)]

        return Chunk(matrix, position)

    @staticmethod
    def createFromNoise(seed, position):

        matrix = [[0 for _ in range(16)] for _ in range(16)]
        for x in range(16):
            for y in range(16):
                value = (noise.snoise3(
                    (position[0]*c.CHUNK_SIZE + x)*0.01,
                    (position[1]*c.CHUNK_SIZE + y)*0.01,
                    seed,
                    octaves=8
                )+1)/2
                if value < 0.4:
                    id = 0
                elif value < 0.5:
                    id = 1
                elif value < 0.55:
                    id = 2
                elif value < 0.65:
                    id = 3
                elif value < 0.75:
                    id = 4
                elif value < 0.83:
                    id = 5
                elif value < 1:
                    id = 6

                matrix[y][x] = id

        return Chunk(matrix, position)
