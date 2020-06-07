import math
import pickle

import pyglet
import pymunk

from . import constants as c
from .col_dicts import dict_to_collider


class Entity(pymunk.Body):
    _space = None

    def __init__(self, position=(0, 0), body_type=pymunk.Body.DYNAMIC, colliders: list = None):
        super().__init__(mass=1, moment=float("inf"), body_type=body_type)
        self.position = position
        self.colliders = []

        if colliders is not None:
            for collider in colliders:
                self.add_collider(collider)

    @property
    def chunk(self):
        return (
            self.position.x / c.TILE_SIZE // c.CHUNK_SIZE,
            self.position.y / c.TILE_SIZE // c.CHUNK_SIZE
        )

    @property
    def space(self):
        return self._space

    @space.setter
    def space(self, space):
        if self.space is not None:
            self.space.remove(self, *self.colliders)

        self._space = space
        self.space.add(self, *self.colliders)

    def add_collider(self, collider):
        col = dict_to_collider(collider)
        col.body = self

        if self.space is not None:
            self.space.add(col)

        self.colliders.append(col)

    def create_sprite(self, image, offset, batch=None, group=None):
        self.sprite_offset = pymunk.Vec2d(offset)
        self.sprite = pyglet.sprite.Sprite(
            image,
            x=self.position.x+self.sprite_offset.x,
            y=self.position.y+self.sprite_offset.y,
            batch=batch,
            group=group
        )

    def update_sprite(self):
        self.sprite.position = tuple(self.position+self.sprite_offset)

    def delete(self):
        self.sprite.delete()
