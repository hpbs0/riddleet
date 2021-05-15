import socket
from threading import Thread
import random
import string
from datetime import datetime
HOST = "127.0.0.1"
PORT = 65125


rooms = {}
players = {}


def randomID(size: int = 6) -> str:
    """
    Creates an random 6 character ID
    """
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(random.choices(alphabet, k=size))


def sendData(socket, typ: str, request: str, data: str) -> None:
    """
    Sends response/data to player client
    """
    return socket.sendall(
        bytes("{0}:{1}:{2}".format(typ, request, data),  "utf-8"))


class PlayerThread(Thread):
    def __init__(self, playerSocket, playerAddress, id: str):
        print(playerAddress)
        Thread.__init__(self)
        self.socket = playerSocket
        self.address = playerAddress
        self.daemon = True
        self.id = id
        self.name = "Player#{0}".format(id)
        self.roomID = ""
        print("New player added: ", self.address)

    def run(self):
        """
        End points for the users
        Gets the requests and returns responses

        Convenvention used: (type:request:data)
            type: type of the request ex:set/open/join
            request: specify where request is to ex:name/room/chat
            data: body of the request

        Current opeartions:
            -Set name request
            -Open room request
            -Join room request
            -Leave room request
        """
        try:
            global rooms
            print("Player from : ", self.address)
            #self.socket.send(bytes("Connection established..", "utf-8"))

            msg = ""
            while True:
                data = self.socket.recv(1024)
                print
                typ, request, data = data.decode().split(":")

                # Set name request
                if typ == "set" and request == "name":
                    self.setName(data)

                # Open room request
                elif typ == "open" and request == "room":
                    self.createRoom()

                # Join room request
                elif typ == "join" and request == "room":
                    self.joinRoom(data)

                # Leave room request
                elif typ == "leave" and request == "room":
                    self.leaveRoom()

                # Leave room request
                elif typ == "send" and request == "message":
                    self.sendMessage(request, data)

        except Exception as e:

            print(e)
            pass
        self.leaveRoom()
        print("Player at ", self.address, " disconnected...")

    def setName(self, data: str) -> None:
        """
        Sets the name to the given data
        """
        print("Player at ", self.address, "set his name to:", data)
        if self.roomID != "":
            self.sendMessage("notify", self.name+" set his name to "+data)
        self.name = "{0}#{1}".format(data, self.id)
        return sendData(self.socket, "set", "name", data)

    def createRoom(self) -> None:
        """
        Creates a Room with the with the id of 6 char length random string
        Adds the room to the rooms dictionary and appends the player to the dictionary
        Player can not create another room if he/she is in one.
        """
        global rooms
        if self.roomID == "":
            self.roomID = randomID()
            rooms[self.roomID] = {}
            rooms[self.roomID]["players"] = {}
            rooms[self.roomID]["maxSize"] = 4
            rooms[self.roomID]["currentSize"] = 0
            rooms[self.roomID]["players"][self.id] = self.socket

            print("Player at ", self.address,
                  "opened a room of id ", self.roomID)
            return sendData(self.socket, "open", "room", self.roomID)
        else:
            return sendData(self.socket,
                            "set", "error", "You need to disconnect from the room before opening new room.")

    def joinRoom(self, roomID: str) -> None:
        """
        Joins to the room of another client
        Player cant join if:
            You are in a room
            The id you entered is wrong
        """
        global rooms
        if self.roomID == "" and roomID in rooms and rooms[roomID]["currentSize"] < rooms[roomID]["maxSize"]:
            rooms[roomID]["players"][self.id] = self.socket
            rooms[roomID]["currentSize"] += 1
            self.roomID = roomID
            print("Player at ", self.address,
                  "Joined a room with id ", self.roomID)
            self.sendMessage("notify", self.name+" joined the room.")
            sendData(self.socket, "join", "room", self.roomID)
        elif self.roomID != "":
            sendData(self.socket,
                     "set", "error", "You need to disconnect from the room before joining new room.")
        elif roomID not in rooms:
            sendData(self.socket,
                     "set", "error", "Room not found.")

    def leaveRoom(self) -> None:
        """
        Leaves the room currently in
        Removes the room if the las member leaved the room
        """
        global rooms
        try:
            if self.roomID != "":
                if rooms[self.roomID]["currentSize"] >= 0:
                    rooms[self.roomID]["players"].pop(self.id)
                    rooms[self.roomID]["currentSize"] -= 1
                    if rooms[self.roomID]["currentSize"] < 0:
                        print(
                            "Room deleted with id: ", self.roomID)
                        rooms.pop(self.roomID)
                    else:
                        self.sendMessage("notify", self.name+" left the room.")
                    print("Player at ", self.address,
                          "leaved a room with id ", self.roomID)
                    sendData(self.socket, "leave", "room", self.roomID)
                    self.roomID = ""
            else:
                sendData(self.socket,
                         "set", "error", "You need to be in a room to leave.")
        except Exception as e:
            print(e)
            pass

    def sendMessage(self, typ: str, msg: str) -> None:
        """
        Send messages to the client
        Can specify the type of the message
        Can send message only in a Room
        Current Types:
            notify: Notifications
            message: Player messages
        """

        if self.roomID != "":
            now = datetime.now().strftime('%H:%M')
            sendData(self.socket, "send", typ,
                     "{0}:{1}:{2}".format(self.name, msg, now))
            for player in rooms[self.roomID]["players"]:
                if player != self.id:
                    sendData(rooms[self.roomID]["players"]
                             [player], "send", typ, "{0}:{1}:{2}".format(self.name, msg, now))
        else:
            sendData(self.socket,
                     "set", "error", "You need to be in a room to send messsage.")


def main():
    """
    Opens a thread for each player/connection
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        try:
            while True:
                server.listen()
                playerSocket, playerAddress = server.accept()
                id = randomID(5)
                newPlayer = PlayerThread(
                    playerSocket, playerAddress, id)
                players[id] = playerSocket
                newPlayer.start()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
