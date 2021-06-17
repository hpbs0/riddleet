import socket
from threading import Thread
import random
import string
from datetime import datetime
import time
from typing import List
from .Question import Question, readRiddles
from random import sample
from .Game import Game
HOST = "127.0.0.1"
PORT = 65125

rooms = {}
players = {}
"""
    Rooms
        roomID
            owner: str
            status: WAIT | STARTED
            maxSize: int
            currentSize: int
            game: Game
            players:
                ID:socket
            playerNames:
                ID:str
            playerScores:
                ID:int  
            playerAnswered:
                ID:bool  
"""
riddles: List[Question] = []


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
        Thread.__init__(self)
        self.socket = playerSocket
        self.address = playerAddress
        self.daemon = True
        self.id = id
        self.game = None
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

        Current opeartions can be found in README with details
        """
        try:
            global rooms
            print("Player from : ", self.address)
            # self.socket.send(bytes("Connection established..", "utf-8"))

            msg = ""
            while True:
                data = self.socket.recv(1024).decode()
                typ, request, data = data.split(":", 2)
                print(typ,request,data)
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

                # Start game request
                elif typ == "start" and request == "game":
                    self.startGame()
                # get the list of players
                elif typ == "send" and request == "answer":
                    self.answer(data)
                # get the list of players
                elif typ == "get" and request == "players":
                    self.getPlayer()

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
        if self.roomID != "":
            rooms[self.roomID]["playerNames"][self.id] = self.name
            rooms[self.roomID]["playerScores"][self.id] += 3
        sendData(self.socket, "set", "name",  data)

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
            rooms[self.roomID]["owner"] = self.id
            rooms[self.roomID]["status"] = "WAIT"
            rooms[self.roomID]["players"] = {}
            rooms[self.roomID]["playerNames"] = {}
            rooms[self.roomID]["playerScores"] = {}
            rooms[self.roomID]["playerAnswered"] = {}
            rooms[self.roomID]["maxSize"] = 4
            rooms[self.roomID]["currentSize"] = 1
            rooms[self.roomID]["players"][self.id] = self.socket
            rooms[self.roomID]["playerNames"][self.id] = self.name
            rooms[self.roomID]["playerScores"][self.id] = 0
            rooms[self.roomID]["playerAnswered"][self.id] = False
            return sendData(self.socket, "open", "room", self.roomID)
        else:
            return sendData(self.socket,
                            "set", "error", "You need to disconnect from the room before opening new room.")

    def joinRoom(self, roomID: str) -> None:
        """
        Joins to the room of another client
        Player cant join if:
            Room reached the maximum number of people
            Game has been started
            You are in a room
            The id you entered is wrong
        """
        global rooms
        if self.roomID == "" and roomID in rooms:
            if rooms[roomID]["currentSize"] < rooms[roomID]["maxSize"]:
                if rooms[roomID]["status"] == "WAIT":
                    rooms[roomID]["players"][self.id] = self.socket
                    rooms[roomID]["playerNames"][self.id] = self.name
                    rooms[roomID]["playerScores"][self.id] = 0
                    rooms[roomID]["playerAnswered"][self.id] = False
                    rooms[roomID]["currentSize"] += 1
                    self.roomID = roomID
                    self.sendMessage("notify", self.name+" joined the room.")
                    sendData(self.socket, "join", "room", self.roomID)
                else:
                    sendData(self.socket,
                             "set", "error", "You can not join a started game, wait for it to end.")
            else:
                sendData(self.socket,
                         "set", "error", "Max size of the room is "+str(rooms[roomID]["maxSize"])+".")
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
                print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
                if rooms[self.roomID]["currentSize"] > 1:
                    rooms[self.roomID]["players"].pop(self.id)
                    rooms[self.roomID]["playerNames"].pop(self.id)
                    rooms[self.roomID]["playerScores"].pop(self.id)
                    rooms[self.roomID]["playerAnswered"].pop(self.id)
                    rooms[self.roomID]["currentSize"] -= 1
                    self.sendMessage("notify", self.name+" left the room.")
                    time.sleep(0.5)
                    sendData(self.socket, "leave", "room", self.roomID)
                    time.sleep(0.5)
                    if self.id == rooms[self.roomID]["owner"]:
                        key = random.choice(list(rooms[self.roomID]["players"].keys()))
                        print(key,"--------------------------")
                        rooms[self.roomID]["owner"] = key
                        self.sendMessage("notify", rooms[self.roomID]["playerNames"][key]+" becomes the owner.")
            
                    self.roomID = ""
                else:
                    self.sendMessage("notify", self.name+" left the room.")
                    time.sleep(0.5)
                    rooms.pop(self.roomID)
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
                     "{0} {1} {2}".format(self.name, now, msg))
            for player in rooms[self.roomID]["players"]:
                if player != self.id:
                    sendData(rooms[self.roomID]["players"]
                             [player], "send", typ, "{0} {1} {2}".format(self.name, now, msg))
        else:
            sendData(self.socket,
                     "set", "error", "You need to be in a room to send messsage.")

    def startGame(self) -> None:
        """
        """
        global rooms
        if self.roomID != "" and self.id == rooms[self.roomID]["owner"] and rooms[self.roomID]["status"] != "STARTED":
            rooms[self.roomID]["status"] = "STARTED"
            questions = sample(riddles, 5)
            self.game = Game(questions, rooms[self.roomID], self.players)
            rooms[self.roomID]["game"] = self.game
            self.game.start()
            pass
        elif rooms[self.roomID]["status"] == "STARTED":
            return sendData(self.socket,
                            "set", "error", "Game has been already started, please wait for it to finish.")
        elif self.id != rooms[self.roomID]["owner"]:
            return sendData(self.socket,
                            "set", "error", "You are not the owner, wait for owner to start the game.")
        else:
            return sendData(self.socket,
                            "set", "error", "You need to be in a room before Starting a game.")

    def getPlayer(self) -> None:
        data = self.players()
        if isinstance(data, list):
            s = ":"
            sendData(self.socket,
                     "print", "lb", ":" + s.join(data))

    def answer(self, answer) -> None:
        game: Game = rooms[self.roomID]["game"]
        if game.question != None and game.question.compareAnswer(answer) and not rooms[self.roomID]["playerAnswered"][self.id]:
            rooms[self.roomID]["playerScores"][self.id] += 10
            rooms[self.roomID]["playerAnswered"][self.id] = True
            sendData(self.socket, "accept", "answer", str(
                rooms[self.roomID]["playerScores"][self.id]))
        elif rooms[self.roomID]["playerAnswered"][self.id]:
            sendData(self.socket,
                     "set", "error", "Wait for another question, you already answered.")
        elif game.question == None:
            sendData(self.socket,
                     "set", "error", "Wait for question.")
        else:
            sendData(self.socket, "reject", "answer", "")

    def players(self) -> None:
        """
        """
        global rooms
        if self.roomID != "":
            data = []

            if rooms[self.roomID]["status"] == "STARTED":
                sort_orders = sorted(
                    rooms[self.roomID]["playerScores"].items(), key=lambda x: x[1], reverse=True)
                for id, score in sort_orders:
                    if id != rooms[self.roomID]["owner"]:
                        data.append(rooms[self.roomID]["playerNames"][id] +
                                    "-(Score=" + str(score) + ")")
                    else:
                        data.append(rooms[self.roomID]["playerNames"][id] +
                                    "-(Score=" + str(score) + ")-Owner")
            else:
                data.append(rooms[self.roomID]["playerNames"]
                            [rooms[self.roomID]["owner"]]+"-Owner")
                for player in rooms[self.roomID]["playerNames"].keys():
                    if player != rooms[self.roomID]["owner"]:
                        data.append(rooms[self.roomID]["playerNames"][player])
            return data
        else:
            return sendData(self.socket,
                            "set", "error", "You need to be in a room before seeing the players.")


def server():
    """
    Opens a thread for each player/connection
    """

    readRiddles(riddles)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        try:
            while True:
                server.listen()
                playerSocket, playerAddress = server.accept()
                id = randomID(5)
                sendData(playerSocket, "set", "id",  id)
                newPlayer = PlayerThread(
                    playerSocket, playerAddress, id)
                players[id] = playerSocket
                newPlayer.start()
        except KeyboardInterrupt:
            pass
