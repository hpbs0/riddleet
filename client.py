from curses import wrapper
from riddleetclient import Client 

def main(stdscr):
    Client(stdscr)


if __name__ == "__main__":
    wrapper(main)