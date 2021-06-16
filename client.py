from curses import wrapper as Display
from riddleetclient import Client 

def main(stdscr):
    Client(stdscr)


if __name__ == "__main__":
    Display(main)