from .Display import Display
from .Connection import Connection
from .Timer import Timer


class Client(Display):
    """
    Contains the main game loop and Game UI
    Sends requests to the server via socket with the appopiate user commands
    """

    def __init__(self, screen):
        Display.__init__(self, screen)
        self.isRunning: bool = True
        self.isGameRuning: bool = False
        self.needConnection: bool = False
        self.isConnected: bool = False
        self.socket = None
        self.timer = None

        try:
            self.server = Connection(self)
            self.server.start()
            self.run()

        except:
            pass

    def _help(self):
        commands = ["/h \t\t\t: print help",
                    "/q \t\t\t: quit the game",
                    "/r <''|group|server> \t: clean the view",
                    "/n <name>\t\t: set your name!",
                    "/o \t\t\t: open a room!",
                    "/k <playerID> \t\t: Kick a player!",
                    "/j <id>\t\t\t: joins to a playroom!",
                    "/d \t\t\t: leave the room!",
                    "/s \t\t\t: Start the game!",
                    "/p \t\t\t: Print the players/leaderboard!",
                    "/!<msg>\t\t\t: send a message to your room!"]

        self._prompt_draw("")
        self._prompt_draw("\t!SOME WORKS ONLINE ONLY", "RED")
        self._prompt_draw("\tOptions:", "GREEN")
        for comm in commands:
            self._prompt_draw("\t"+comm, "YELLOW")
        self._prompt_draw("")

    def _prompt_draw(self, props, colour="WHITE"):
        """
        Draw to the prompt screen
        """
        self.promptContext.append(props, colour)
        self.promptContext.redrawMultiColour()
        self.prompt.redraw()

    def _group_draw(self, props, colour="WHITE", name="Client", time=""):
        """
        Draw to the group screen
        """
        self.groupContext.append(
            "{0} [{1}]: {2}".format(time, name, props), colour)
        self.groupContext.redrawMultiColour()

    def _server_draw(self, props, colour="WHITE"):
        """
        Draw to the server screen
        """
        self.serverContext.append(props, colour)
        self.serverContext.redrawMultiColour()

    def startTimer(self):
        """
        Starts the timer for the question
        """
        self.timer = Timer(self)
        self.timer.start()

    def stopTimer(self):
        """
        Ends the timer for the question if timer is not already stopped
        """
        if self.timer != None:
            self.timer.stop()
        self.timer = None

    def run(self):
        try:
            self._help()
            while True:
                self.redraw()
                msg = self.getInput()
                try:
                    if msg == '':
                        continue
                    elif msg == "/h":
                        self._help()
                    elif msg == "/q":
                        self.isRunning = False
                        break
                    elif msg == "/r":
                        self.promptContext.clearAnswers()
                    elif msg == "/r group":
                        self.groupContext.clearAnswers()
                    elif msg == "/r server":
                        self.serverContext.clearAnswers()
                    elif msg[:3] == "/n ":
                        self.waitServerConnection(self.setNameRequest, msg[3:])
                    elif msg == "/o":
                        self.waitServerConnection(self.openRoom)
                    elif msg[:3] == "/j ":
                        self.waitServerConnection(self.joinRoom, msg[3:])
                    elif msg[:1] == "!":
                        self.waitServerConnection(self.sendMessage, msg[1:])
                    elif msg == "/d":
                        self.waitServerConnection(self.leaveRoom)
                    elif msg == "/s":
                        self.waitServerConnection(self.startGame)
                    elif msg == "/p":
                        self.waitServerConnection(self.getPlayers)
                    elif msg[:1] == "/":
                        self._prompt_draw(
                            "{0}:Command not found".format(msg), "RED")
                    elif msg != '':
                        if self.isGameRuning:
                            self.waitServerConnection(self.sendAnswer, msg)
                        self._prompt_draw(msg, "WHITE")
                    else:
                        self._prompt_draw("-->!Server not connected", "YELLOW")
                except Exception as e:
                    print(e)

        except KeyboardInterrupt:
            pass

    def waitServerConnection(self, func, arg=None):
        """
        Wrapper for functions in need of server connection
        Prints a warning in prompt if there is no connection to server
        """
        if arg != None:
            func(arg) if self.socket != None else self._prompt_draw(
                "Wait for server connection...", "YELLOW")
        else:
            func() if self.socket != None else self._prompt_draw(
                "Wait for server connection...", "YELLOW")

    def setNameRequest(self, name: str):
        """
        Set name request
        Sends the name wanted to be used to the server
        Names can not be longer than 15 characters and contain whitespaces
        """
        if len(name) > 5 and len(name) < 15 and " " not in name:
            self.socket.sendall(bytes("set:name:{0}".format(name), 'UTF-8'))
            # self.header.setName(answer[3:])
        elif " " in name:
            self._prompt_draw(
                "-->!Whitespaces not allowed in a name", "YELLOW")
        else:
            self._prompt_draw(
                "-->!Please enter a string maximum length is less than 15 and minimum length 6", "YELLOW")

    def openRoom(self):
        """
        Sends an open room request
        Cannot open a room in another room
        """
        self.socket.sendall(bytes("open:room:", 'UTF-8'))

    def sendAnswer(self, answer: str):
        """
        Sends the given answer to the server
        If Player answer before was correct prints an error message
        """
        self.socket.sendall(bytes("send:answer:{0}".format(answer), 'UTF-8'))

    def joinRoom(self, roomID):
        """
        Sends an join room request
        Length of the roomID's are 6
        Prints an error message if can not join a room for some reason
        """
        if len(roomID) < 7:
            self.socket.sendall(bytes("join:room:{0}".format(roomID), 'UTF-8'))
        else:
            self._prompt_draw(
                "-->!Room id length cant be greater than 6", "YELLOW")

    def sendMessage(self, msg):
        """
        Sends an join room request
        Length of the roomID's are 6
        Player needs to be in a room to be able to send a message
        """
        if len(msg) > 0:
            self.socket.sendall(bytes("send:message:{0}".format(msg), 'UTF-8'))

    def leaveRoom(self):
        """
        Sends a leave room request
        Leaves the current room afterward
        """
        self.socket.sendall(bytes("leave:room:", 'UTF-8'))

    def startGame(self):
        """
        Sends a start game request
        If game is not startable prints an error message
        """
        self.socket.sendall(bytes("start:game:", 'UTF-8'))

    def getPlayers(self):
        """
        Sends a request for player table
        Prints the players in the room as a table
        If not in the table prints an error message
        """
        self.socket.sendall(bytes("get:players:", 'UTF-8'))
