import curses


def getColour(color):

    if color == "RED":
        return 1
    elif color == "GREEN":
        return 2
    elif color == "BLUE":
        return 3
    elif color == "MAGENTA":
        return 4
    elif color == "YELLOW":
        return 5
    elif color == "CYAN":
        return 6
    elif color == "WHITE":
        return 7


class Layout:
    HEADER = 2
    PROMPT = 3

    def __init__(self, height, width):
        self.headerRows = Layout.HEADER
        self.headerCols = width
        self.headerPositionY = 2
        self.headerPositionX = 0

        self.contextRows = height - Layout.PROMPT - Layout.HEADER
        self.contextCols = width
        self.contextPositionY = Layout.PROMPT
        self.contextPositionX = 0

        self.promptRows = Layout.PROMPT
        self.promptCols = width
        self.promptPositionY = height - Layout.PROMPT
        self.promptPositionX = 0


class Header:

    def __init__(self, layout, screen):
        self.layout = layout
        self.screen = screen
        self.window = curses.newwin(
            layout.headerRows, layout.headerCols, layout.headerPositionY, layout.headerPositionX)
        self.status = {"Name:": "Player",
                       "Server:": "NaN", "Room:": "NaN"}
        self.redraw()

    def redraw(self):
        self.window.clear()
        limit = 0
        for key in self.status:
            limit += len(key)+len(self.status[key])+1
            self.window.addstr(key+"\t")
            if(limit < self.layout.headerCols):
                if(self.status[key] == "NaN"):

                    self.window.addstr(
                        self.status[key]+"\t", curses.color_pair(getColour("MAGENTA")))
                else:
                    self.window.addstr(
                        self.status[key]+"\t", curses.color_pair(getColour("GREEN")))

        self.window.refresh()

    def resize(self, layout, screen):
        self.layout = layout
        self.screen = screen
        self.window = curses.newwin(
            layout.headerRows, layout.headerCols, layout.headerPositionY, layout.headerPositionX)
        self.redraw()

    def setName(self, name):
        self.status["Name:"] = name
        self.redraw()

    def setServer(self, status):
        self.status["Server:"] = status
        self.redraw()

    def setRoom(self, roomId):
        self.status["Room:"] = roomId
        self.redraw()


class Context:
    def __init__(self, layout, screen, xFactor=6, yFactor=6, xOffset=0, yOffset=0):
        self.layout = layout
        self.screen = screen
        self.children = []
        self.window = curses.newwin(
            yFactor*layout.contextRows//12, xFactor*layout.contextCols//12, layout.contextPositionY+yOffset, layout.contextPositionX+xOffset)
        self.childrenBoxLimit = (yFactor*layout.contextRows//12)-4

    def resize(self, layout, screen, xFactor=6, yFactor=6, xOffset=0, yOffset=0):
        self.layout = layout
        self.screen = screen
        self.window = curses.newwin(
            yFactor*layout.contextRows//12, xFactor*layout.contextCols//12, layout.contextPositionY+yOffset, layout.contextPositionX+xOffset)
        self.childrenBoxLimit = (yFactor*layout.contextRows//12)-4
        self.redrawMultiColour()

    def setChildren(self, children):
        self.children = children

    def append(self, child, color="WHITE"):
        self.children.append((child, color))

    def redrawMultiColour(self):
        self.window.clear()
        currentRow = self.childrenBoxLimit+5
        if self.childrenBoxLimit > 0:
            for child in reversed(self.children[-self.childrenBoxLimit:]):
                self.window.move(currentRow-5, 1)
                self.window.addstr(
                    child[0], curses.color_pair(getColour(child[1])))
                currentRow -= 1
        self.window.refresh()

    def clearAnswers(self):
        self.children = []


class Prompt:
    def __init__(self, layout, screen):
        self.layout = layout
        self.screen = screen
        self.window = curses.newwin(
            layout.promptRows, layout.promptCols, layout.promptPositionY, layout.promptPositionX)
        self.window.keypad(1)
        self.window.addstr('> ')
        self.promptLimit = layout.promptRows*layout.promptCols-3

    def resize(self, layout, screen):
        self.layout = layout
        self.screen = screen
        self.window = curses.newwin(
            layout.promptRows, layout.promptCols, layout.promptPositionY, layout.promptPositionX)
        self.promptLimit = layout.promptRows*layout.promptCols-3
        self.redraw()

    def getchar(self):
        return self.window.getch()

    def redraw(self, msg=""):
        self.window.clear()
        self.window.addstr('> '+msg)
        self.window.refresh()