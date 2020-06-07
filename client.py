import json
import math
import pickle
import socket
import threading

import pyglet
import pymunk
import pymunk.pyglet_util
from pyglet.window import key, mouse

import source
from source import constants as c

pyglet.image.Texture.default_mag_filter = pyglet.gl.GL_NEAREST
pyglet.image.Texture.default_min_filter = pyglet.gl.GL_NEAREST


class Client:
    def __init__(self, address, port):
        self.address = address
        self.port = port

        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )

        self.create_layers()

        self.window = pyglet.window.Window(
            width=1280,
            height=720,
            caption="Entity Test 1",
            resizable=True
        )
        self.window.set_minimum_size(*c.VIEWPORT_SIZE)
        self.window.push_handlers(self)

        self.fps_display = pyglet.window.FPSDisplay(window=self.window)
        self.fps_display.label.color = (255, 255, 255, 200)

        self.key_handler = key.KeyStateHandler()
        self.mouse_handler = mouse.MouseStateHandler()
        self.window.push_handlers(self.key_handler, self.mouse_handler)

        self.world_batch = pyglet.graphics.Batch()
        self.world_camera = source.camera.Camera(
            scroll_speed=0,
            min_zoom=0,
            max_zoom=float("inf")
        )
        self.ui_batch = pyglet.graphics.Batch()
        self.fps_display.label.batch = self.ui_batch

        self.debug_mode = False

        self.camera_position = pymunk.Vec2d.zero()
        self.camera_chunk = (0, 0)
        self.camera_zoom = 1

        self.physics_space = pymunk.Space()

        self.position_label = pyglet.text.Label(
            text=f"X: {round(self.camera_position.x/c.TILE_SIZE, 3)}, Y: {round(self.camera_position.y/c.TILE_SIZE, 3)}",
            batch=self.ui_batch,
            font_size=10,
            x=5,
            y=40
        )

        self.entities = []

        self.chunks = {}
        self.chunk_buffer = {}
        self.to_request = []
        self.to_unload = []

    def on_draw(self):
        self.window.clear()
        with self.world_camera:
            self.world_batch.draw()
            if self.debug_mode:
                debug_draw_options = pymunk.pyglet_util.DrawOptions()
                self.physics_space.debug_draw(debug_draw_options)
        self.ui_batch.draw()

    def on_key_press(self, button, modifiers):
        if button == key.F3:
            self.debug_mode = not self.debug_mode

    def update(self, dt):
        self.physics_space.step(dt)
        self.position_camera()
        self.camera_chunk = (
            math.floor(self.camera_position.x/c.TILE_SIZE/c.CHUNK_SIZE),
            math.floor(self.camera_position.y/c.TILE_SIZE/c.CHUNK_SIZE)
        )

        in_load_distance = [
            (x+self.camera_chunk[0], y+self.camera_chunk[1])
            for x, y in source.spiral(c.LOAD_DISTANCE)
        ]

        while True:
            if len(self.chunk_buffer) > 0:
                chunk = list(self.chunk_buffer.values())[0]
                del self.chunk_buffer[chunk.position]
                if chunk.position in in_load_distance:
                    chunk.generate_tiles(self, batch=self.world_batch)
                    self.chunks[chunk.position] = chunk
                    break
            else:
                break

        while True:
            if len(self.to_unload) > 0:
                position = self.to_unload[0]
                self.to_unload.remove(position)
                if (
                    position in self.chunks.keys() and
                    position not in in_load_distance
                ):
                    chunk = self.chunks[position]
                    chunk.delete()
                    del self.chunks[position]
                    break
            else:
                break

        while True:
            if len(self.to_request) > 0:
                position = self.to_request[0]
                self.to_request.remove(position)
                if position in in_load_distance:
                    data = {
                        "type": "chunk_request",
                        "position": position
                    }
                    self.send(data)
                    break
            else:
                break

        for pos in in_load_distance:
            if (
                pos not in self.chunks.keys() and
                pos not in self.to_request
            ):
                self.to_request.append(pos)

        for pos in self.chunks.keys():
            if pos not in in_load_distance:
                self.to_unload.append(pos)

        if self.key_handler[key.W]:
            self.camera_position.y += c.TILE_SIZE*dt*c.CAMERA_SPEED
        if self.key_handler[key.A]:
            self.camera_position.x -= c.TILE_SIZE*dt*c.CAMERA_SPEED
        if self.key_handler[key.S]:
            self.camera_position.y -= c.TILE_SIZE*dt*c.CAMERA_SPEED
        if self.key_handler[key.D]:
            self.camera_position.x += c.TILE_SIZE*dt*c.CAMERA_SPEED
        self.position_label.text = f"X: {round(self.camera_position.x/c.TILE_SIZE, 3)}, Y: {round(self.camera_position.y/c.TILE_SIZE, 3)}"

    def socket_thread(self):
        while True:
            try:
                header_bytes = b""
                while len(header_bytes) < c.HEADER_SIZE:
                    header_bytes += self.socket.recv(c.HEADER_SIZE)
                header = header_bytes.decode("utf-8")
                length = int(header.strip())

                message = b""
                while len(message) < length:
                    message += self.socket.recv(length - len(message))

                data = pickle.loads(message)

                if data["type"] == "log":
                    print(data["message"])
                elif data["type"] == "chunk":
                    if (
                        data["chunk"].position not in self.chunks.keys()
                    ):
                        self.chunk_buffer[data["chunk"].position] = data["chunk"]

            except (ConnectionAbortedError, ConnectionResetError) as e:
                print("Disconnected.")
                break

    def position_camera(self):
        zoom = min(
            self.window.width/c.VIEWPORT_SIZE[0],
            self.window.height/c.VIEWPORT_SIZE[1]
        )

        if self.world_camera.zoom != zoom:
            self.world_camera.zoom = zoom

        x = -self.window.width//2/zoom
        y = -self.window.height//2/zoom

        x += self.camera_position.x
        y += self.camera_position.y

        x, y = round(x), round(y)

        if self.world_camera.position != (x, y):
            self.world_camera.position = (x, y)

    def send(self, data):
        message = pickle.dumps(data)
        header = bytes(f"{len(message):<{c.HEADER_SIZE}}", "utf-8")
        return self.socket.sendall(header + message)

    def create_layers(self):
        self.world_layers = {}
        self.world_layers["master"] = pyglet.graphics.Group()
        for layer in c.WORLD_LAYERS:
            self.world_layers[layer] = pyglet.graphics.OrderedGroup(
                c.WORLD_LAYERS.index(layer)+1,
                parent=self.world_layers["master"]
            )

        self.ui_layers = {}
        self.ui_layers["master"] = pyglet.graphics.Group()
        for layer in c.UI_LAYERS:
            self.ui_layers[layer] = pyglet.graphics.OrderedGroup(
                c.UI_LAYERS.index(layer)+1,
                parent=self.ui_layers["master"]
            )

    def run(self):
        while True:
            try:
                self.socket.connect((self.address, self.port))
                break
            except TimeoutError:
                print("Server did not respond, retrying.")

        socket_thread = threading.Thread(
            target=self.socket_thread,
            daemon=True
        )
        socket_thread.start()

        pyglet.clock.schedule(self.update)
        pyglet.app.run()


if __name__ == "__main__":
    with open("client_config.json", "r") as f:
        config = json.load(f)
    client = Client(config["ip"], config["port"])
    client.run()
