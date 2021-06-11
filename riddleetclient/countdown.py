import socket
import time
from curses import wrapper
from threading import Thread
from datetime import datetime


class Countdown(Thread):
    def __init__(self, Client):
        super(Countdown, self).__init__()
        self.client = Client
        self.daemon = True

    def run(self):
        """
        Start running the connection to the server
        """
        SERVER = "127.0.0.1"
        PORT = 65125
