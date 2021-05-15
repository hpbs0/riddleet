import socket
import time
from curses import wrapper
from threading import Thread
from datetime import datetime


class ResponseThread(Thread):
    def __init__(self, Client):
        super(ResponseThread, self).__init__()
        self.client = Client
        self.daemon = True

    def printWithTime(self, props, color):
        now = datetime.now().strftime('%H:%M:%S')
        self.client._server_draw(
            "[{0}] {1}...".format(now, props), color)

    def run(self):
        """
        Start running the connection to the server
        """
        SERVER = "127.0.0.1"
        PORT = 65125
        while self.client.isRunning:
            try:
                _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                while not self.client.isConnected:
                    try:
                        self.printWithTime(
                            "Trying to connect to server", "YELLOW")
                        time.sleep(3)
                        _socket.connect((SERVER, PORT))
                        self.client.isConnected = True
                        self.printWithTime(
                            "Connection has been established", "GREEN")
                    except:
                        self.client.header.setServer("NaN")
                        self.printWithTime("Connection Failed", "RED")
                self.client.header.setServer("CONNECTED")
                self.client.socket = _socket
                self.responseClient()

            except Exception as e:
                self.client.socket = None
                self.client.isConnected = False
                self.client.header.setName("Player")
                self.client.header.setRoom("NaN")
                self.client._server_draw(str(e), "RED")
                self.client.header.setServer("NaN")
                self.printWithTime("Connection Failed", "RED")
                _socket.close()
                pass

    def responseClient(self):
        """
        Handles the response coming from the server
        Currently handles:
            set name
            open room
            join room

        prints the errors if returned one to the server section.
        """
        while True:
            data = self.client.socket.recv(1024).decode()
            typ, request, data = data.split(":", 2)

            if typ == "set" and request == "name":
                self.setNameResponse(data)

            elif typ == "open" and request == "room":
                self.openRoomResponse(data)

            elif typ == "join" and request == "room":
                self.joinRoomResponse(data)

            elif typ == "leave" and request == "room":
                self.leaveRoomResponse(data)

            elif typ == "send" and request == "notify":
                self.notifications(data)

            elif typ == "send" and request == "message":
                self.message(data)
            elif typ == "set" and request == "error":
                self.printError(data)

    def setNameResponse(self, data: str):
        self.client.header.setName(data)
        self.printWithTime(
            "Name has been set successfully", "GREEN")

    def openRoomResponse(self, data: str):
        self.client.header.setRoom(data)
        self.printWithTime(
            "Room created with ID: "+data, "GREEN")

    def joinRoomResponse(self, data: str):
        self.client.header.setRoom(data)
        self.printWithTime(
            "Joined the room with ID: "+data, "GREEN")

    def leaveRoomResponse(self, data: str):
        self.client.header.setRoom("NaN")
        self.printWithTime(
            "Leaved current room with ID: "+data, "YELLOW")

    def notifications(self, data: str):
        player, msg, time = data.split(":", 2)
        self.client._group_draw(
            msg, "YELLOW", "Room", time)

    def message(self, data: str):
        player, msg, time = data.split(":", 2)
        self.client._group_draw(
            msg, "WHITE", player, time)

    def printError(self, data: str):
        self.printWithTime(
            data, "RED")
