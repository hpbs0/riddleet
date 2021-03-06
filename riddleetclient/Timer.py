from threading import Thread, Event
from .Display import Display


class Timer(Thread):
    """
    Timer for questions
    """
    def __init__(self, display: Display) -> None:
        super(Timer, self).__init__()
        self.daemon = True
        self.count = 15
        self.display = display
        self._stop_event = Event()

    def run(self):
        """
        Timer main loop, decreases from 15 one by one each second
        """
        while not self._stop_event.wait(1):
            if self.count == -1:
                break
            else:
                self.display.header.setTimer(str(self.count))
                self.count -= 1

    def stop(self):
        """
        Stops the timer, used by server
        """
        self._stop_event.set()
        self.display.header.setTimer("-")

    def stopped(self):
        """
        Checks if timer is stopped
        """
        return self._stop_event.is_set()
