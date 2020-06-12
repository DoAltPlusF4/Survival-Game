import pyglet
import pymunk

from . import constants as c
from .entity import Entity


class Player(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(position=(8*c.TILE_SIZE, 8*c.TILE_SIZE))
        collider = {
            "type": "circle",
            "offset": (0, 0),
            "radius": 6,
            "collision_type": 0
        }
        self.add_collider(collider)

    def create_sprite(self, batch=None, group=None):
        self.sprite_offset = pymunk.Vec2d.zero()
        self.sprite = pyglet.shapes.Circle(
            x=self.position.x+self.sprite_offset.x,
            y=self.position.y+self.sprite_offset.y,
            radius=6,
            color=(96, 128, 255),
            segments=16,
            batch=batch,
            group=group
        )
