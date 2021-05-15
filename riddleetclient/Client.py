
from riddleetcommon.Display import Display
from riddleetclient.ResponseThread import ResponseThread
from curses import wrapper


class Client(Display):
    def __init__(self, screen):
        Display.__init__(self, screen)
        self.isRunning = True
        self.needConnection = False
        self.isConnected = False
        self.socket = None

        try:
            self.server = ResponseThread(self)
            self.server.start()
            self.run()

        except:
            pass

    def _help(self):
        commands = ["/h \t\t\t: print help",
                    "/q \t\t\t: quit the game",
                    "/r null/group/server \t: clean the view",
                    "/n <name>\t\t: set your name!",
                    "/o \t\t\t: open a room!",
                    "/j <id>\t\t\t: joins to a playroom!",
                    "/!<msg>\t\t\t: send a message to your room!",
                    "/d \t\t\t: leave the room!"]

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
                        self.waitServerConnection(
                            self.setNameRequest, msg[3:])
                    elif msg == "/o":
                        self.waitServerConnection(self.openRoomRequest)
                    elif msg[:3] == "/j ":
                        self.waitServerConnection(
                            self.joinRoomRequest, msg[3:])
                    elif msg[:1] == "!":
                        self.waitServerConnection(
                            self.sendMessage, msg[1:])
                    elif msg == "/d":
                        self.waitServerConnection(self.leaveRoomRequest)
                    elif msg[:1] == "/":
                        self._prompt_draw(
                            "{0}:Command not found".format(msg), "RED")
                    elif msg != '':
                        self._prompt_draw(msg, "RED")
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

    def openRoomRequest(self):
        """
        Sends an open room request
        """
        self.socket.sendall(bytes("open:room:", 'UTF-8'))

    def joinRoomRequest(self, roomID):
        """
        Sends an join room request
        Length of the roomID's are 6
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
        """
        if len(msg) > 0:
            self.socket.sendall(bytes("send:message:{0}".format(msg), 'UTF-8'))

    def leaveRoomRequest(self):
        """
        Sends a leave room request
        """
        self.socket.sendall(bytes("leave:room:", 'UTF-8'))


def main(stdscr):
    display = Client(stdscr)


if __name__ == "__main__":
    wrapper(main)
