import json
import pickle
import random
import socket
import threading
import time

import pymunk

import source
from source import constants as c


class Server:
    def __init__(self, address, port):
        self.address = address
        self.port = port

        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )
        self.socket.bind((self.address, self.port))

        self.clients = {}

        self.physics_space = pymunk.Space()

        self.entities = []
        self.players = {}

        self.seed = random.random()
        self.chunks = {}

    def update_loop(self, update_frequency):
        while True:
            self.physics_space.step(1/update_frequency)
            time.sleep(1/update_frequency)

    def socket_thread(self):
        self.socket.listen()
        print(f"Listening on {self.address}:{self.port}.")

        while True:
            c_socket, c_address = self.socket.accept()

            c_thread = threading.Thread(
                target=self.threaded_client,
                args=(c_socket, c_address),
                daemon=True
            )
            c_thread.start()

    def threaded_client(self, c_socket, c_address):
        print(f"Accepted new connection from {c_address[0]}:{c_address[1]}.")
        self.clients[c_address] = c_socket

        player = source.player.Player()
        self.entities.append(player)
        self.players[c_socket] = player

        player.active = False
        data = {
            "type": "player_assignment",
            "player": player
        }
        self.send(c_socket, data)
        player.active = True

        player.space = self.physics_space

        while True:
            try:
                header_bytes = b""
                while len(header_bytes) < c.HEADER_SIZE:
                    header_bytes += c_socket.recv(
                        c.HEADER_SIZE - len(header_bytes)
                    )
                header = header_bytes.decode("utf-8")
                length = int(header.strip())

                message = b""
                while len(message) < length:
                    message += c_socket.recv(length - len(message))

                data = pickle.loads(message)

                if "type" not in data.keys():
                    print(f"Received invalid request:\n{data}")

                elif data["type"] == "log":
                    print(data["message"])
                elif data["type"] == "chunk_request":
                    if data["position"] not in self.chunks.keys():
                        self.chunks[data["position"]] = source.chunk.Chunk.create_from_noise(
                            self.seed, data["position"]
                        )
                        # print(
                        #     f"Generated new chunk at {data['position']}."
                        # )
                    data = {
                        "type": "chunk",
                        "chunk": self.chunks[data["position"]]
                    }
                    self.send(c_socket, data)

                else:
                    print(f"Received invalid request:\n{data}")

            except (ConnectionAbortedError, ConnectionResetError, TimeoutError) as e:
                print(
                    f"Connection from {c_address[0]}:{c_address[1]} was reset."
                )
                c_socket.close()
                del self.clients[c_address]
                del self.players[c_socket]
                break

    def broadcast(self, data):
        for socket in self.clients.values():
            self.send(socket, data)

    def send(self, socket, data):
        message = pickle.dumps(data)
        header = bytes(f"{len(message):<{c.HEADER_SIZE}}", "utf-8")
        return socket.sendall(header + message)

    def run(self):
        socket_thread = threading.Thread(
            target=self.socket_thread,
            daemon=True
        )
        socket_thread.start()
        self.update_loop(60)


if __name__ == "__main__":
    with open("server_config.json", "r") as f:
        config = json.load(f)
    server = Server(config["ip"], config["port"])
    server.run()
