from curses import wrapper
from riddleetclient import Client 

def main(stdscr):
    display = Client(stdscr)


if __name__ == "__main__":
    wrapper(main)