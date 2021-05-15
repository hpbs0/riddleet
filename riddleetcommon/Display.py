import curses
from .Components import getColour, Layout, Header, Context, Prompt


class Display:
    def __init__(self, screen):
        curses.curs_set(False)
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)
        self.screen = screen
        self.height, self.width = self.screen.getmaxyx()
        self.layout = Layout(self.height, self.width)
        self.header = Header(self.layout, self.screen)
        self.promptContext = Context(self.layout, self.screen, 6, 12)
        self.groupContext = Context(
            self.layout, self.screen, 6, 6, self.layout.contextCols//2)
        self.serverContext = Context(
            self.layout, self.screen, 6, 6, self.layout.contextCols//2, self.layout.contextRows//2)
        self.prompt = Prompt(self.layout, self.screen)
        self.player_input = None
        self.screen.keypad(1)
        self.colourIndex = 0

    def redraw(self):
        if self.height > 5:
            self.screen.refresh()
            self.header.redraw()
            self.promptContext.redrawMultiColour()
            self.groupContext.redrawMultiColour()
            self.serverContext.redrawMultiColour()
            self.prompt.redraw()
        else:
            self.screen.clear()

    def resize(self):
        self.height, self.width = self.screen.getmaxyx()
        if self.height > 5:
            self.layout = Layout(self.height, self.width)
            self.header.resize(self.layout, self.screen)
            self.promptContext.resize(self.layout, self.screen, 6, 12)
            self.groupContext.resize(
                self.layout, self.screen, 6, 6, self.layout.contextCols//2)
            self.serverContext.resize(
                self.layout, self.screen, 6, 6, self.layout.contextCols//2, self.layout.contextRows//2)
            self.prompt.resize(self.layout, self.screen)
        else:
            self.screen.clear()

    def getInput(self):
        buffer = []
        self.prompt.redraw("".join(buffer))
        char = ''
        while char != ord("\n"):
            char = self.prompt.getchar()
            if len(buffer) > 0 and (char == curses.KEY_BACKSPACE or char == 127):
                buffer.pop()
            elif char == curses.KEY_RESIZE:
                self.resize()
            elif 32 <= char <= 126 and len(buffer) < 50:
                buffer.append(chr(char))
            self.prompt.redraw("".join(buffer[0:self.prompt.promptLimit]))

        return ''.join(buffer)
