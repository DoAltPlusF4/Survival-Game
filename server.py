import pickle
import socket
import threading

import source
from source import constants as c

import random


class Server:
    def __init__(self, address, port):
        self.address = address
        self.port = port

        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )
        self.socket.bind((self.address, self.port))

        self.clients = {}

        self.seed = random.random()
        self.chunks = {}

    def socketThread(self):
        self.socket.listen()
        print(f"Listening on {self.address}:{self.port}.")

        while True:
            c_socket, c_address = self.socket.accept()

            c_thread = threading.Thread(
                target=self.threadedClient,
                args=(c_socket, c_address),
                daemon=True
            )
            c_thread.start()

    def threadedClient(self, c_socket, c_address):
        print(f"Accepted new connection from {c_address[0]}:{c_address[1]}.")
        self.clients[c_address] = c_socket
        while True:
            try:
                header_bytes = c_socket.recv(c.HEADER_SIZE)
                header = header_bytes.decode("utf-8")

                length = int(header.strip())
                message = c_socket.recv(length)

                broken = False
                while True:
                    try:
                        data = pickle.loads(message)
                        break
                    except pickle.UnpicklingError:
                        broken = True
                        message += c_socket.recv(1)
                if broken:
                    print("Resolved broken packet.")

                if "type" not in data.keys():
                    print(f"Received invalid request:\n{data}")

                elif data["type"] == "log":
                    print(data["message"])
                elif data["type"] == "chunk_request":
                    if data["position"] not in self.chunks.keys():
                        self.chunks[data["position"]] = source.chunk.Chunk.createFromNoise(
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

            except (ConnectionAbortedError, ConnectionResetError) as e:
                print(
                    f"Connection from {c_address[0]}:{c_address[1]} was reset."
                )
                del self.clients[c_address]
                break

    def send(self, socket, data):
        message = pickle.dumps(data)
        header = bytes(f"{len(message):<{c.HEADER_SIZE}}", "utf-8")
        return socket.sendall(header + message)

    def run(self):
        socket_thread = threading.Thread(
            target=self.socketThread,
            daemon=False  # NOTE: Change this to True when adding physics loop!
        )
        socket_thread.start()


if __name__ == "__main__":
    server = Server("", 25565)
    server.run()