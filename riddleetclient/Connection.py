import socket
import time
from curses import wrapper
from threading import Thread
from datetime import datetime
from .Display import Display


class Connection(Thread):
    def __init__(self, Client: Display):
        super(Connection, self).__init__()
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
                self.client.header.setQuestion("-")
                self.client.header.setNumber("-")
                self.client.header.setAnswer("-")
                self.client.stopTimer()
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

            # set name <name:string>
            if typ == "set" and request == "name":
                self.setName(data)

            # set id <id:string>
            if typ == "set" and request == "id":
                self.setID(data)

            # open room <roomID:string>
            elif typ == "open" and request == "room":
                self.openRoom(data)

            # join room <roomID:string>
            elif typ == "join" and request == "room":
                self.joinRoom(data)

            # leave room <roomID:string>
            elif typ == "leave" and request == "room":
                self.leaveRoom(data)

            # send notify <notification:string>
            elif typ == "send" and request == "notify":
                self.notifications(data)

            # send message <message:string>
            elif typ == "send" and request == "message":
                self.message(data)

            # start game <>
            elif typ == "start" and request == "game":
                self.startGame()

            # end game <>
            elif typ == "end" and request == "game":
                self.endGame()

            # set question <question:string>
            elif typ == "set" and request == "question":
                self.setQuestion(data)

            # set score <score:string>
            elif typ == "set" and request == "score":
                self.setScore(data)

            # set error <error:string>
            elif typ == "set" and request == "error":
                self.error(data)

            # accept answer <score>
            elif typ == "accept" and request == "answer":
                self.acceptAnswer(data)

            # reject answer <>
            elif typ == "reject" and request == "answer":
                self.rejectAnswer()

            # print lb <players:[string:]*>
            elif typ == "print" and request == "lb":
                self.printPlayers(data)
    """
    Response Functions
    """

    def setName(self, data: str):
        self.client.header.setName(data)
        self.printWithTime(
            "Name has been set successfully", "GREEN")

    def setID(self, data: str):
        self.client.header.setID(data)

    def openRoom(self, data: str):
        self.client.header.setRoom(data)
        self.printWithTime(
            "Room created with ID: "+data, "GREEN")

    def joinRoom(self, data: str):
        self.client.header.setRoom(data)
        self.printWithTime(
            "Joined the room with ID: "+data, "GREEN")

    def leaveRoom(self, data: str):
        self.client.header.setRoom("NaN")
        self.client.header.setAnswer("-")
        self.client.header.setQuestion("-")
        self.client.header.setNumber("-")
        self.client.header.setScore("-")
        self.client.stopTimer()
        self.printWithTime(
            "Leaved current room with ID: "+data, "YELLOW")

    def notifications(self, data: str):
        """
        Draw notifications to the group chat
        """
        player, time, msg = data.split(" ", 2)
        self.client._group_draw(
            msg, "YELLOW", "Room", time)

    def message(self, data: str):
        """
        Draw message to the group chat
        """
        player, time, msg = data.split(" ", 2)
        self.client._group_draw(
            msg, "WHITE", player, "[{0}]".format(time))

    def setQuestion(self, data: str):
        number, currentScore, question = data.split(" ", 2)
        """
        Sets the current question
        """
        self.client.header.setQuestion(question)
        self.client.header.setAnswer("-")
        self.client.header.setNumber(number)
        self.client.header.setScore(currentScore)
        self.client.stopTimer()
        self.client.startTimer()

    def acceptAnswer(self, data: str):
        self.client.header.setAnswer("✓")
        self.client.header.setScore(data)

    def rejectAnswer(self):
        self.client.header.setAnswer("x")

    def error(self, data: str):
        """
        Draw errors to the connection box
        """
        self.printWithTime(
            data, "RED")

    def setScore(self, data: str):
        self.client.header.setScore(data)

    def startGame(self):
        self.printWithTime("Game started, Good luck!", "GREEN")
        self.client.isGameRuning = True

    def endGame(self):
        self.printWithTime(
            "Game ended, you can restart the game with '/s'", "GREEN")
        self.client.header.setQuestion("-")
        self.client.header.setAnswer("-")
        self.client.isGameRuning = False

    def printPlayers(self, data: str):
        players = data.split(":")
        self.client._group_draw(
            "", "RED", "PLAYERS (" + str(len(players)-1) + "/4)")
        count = 1
        for player in players:
            if player != "":
                self.client._group_draw(
                    player, "YELLOW", str(count))
                count += 1
