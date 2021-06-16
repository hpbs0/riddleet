from threading import Thread, Event
from typing import List

from .Question import Question


class Game(Thread):
    """
    Timer for questions
    """

    def __init__(self, questions: List[Question], room) -> None:
        from riddleetserver import sendData
        super(Game, self).__init__()
        self.sendData = sendData
        self.questions: List[Question] = questions
        self.question: Question = None
        self.currentMax = len(self.questions)
        self.currentNumber = 1
        """
        room:
            owner: str
            status: WAIT | STARTED
            maxSize: int
            currentSize: int
            players:
                ID:socket
            playerNames:
                ID:str
            playerScores:
                ID:int   
        """
        self.room = room
        self.daemon = True
        self._stop_event = Event()

    def run(self):
        self.question = self.questions.pop()
        self.sendQuestion()
        self.currentNumber += 1
        while not self._stop_event.wait(15+3) and not len(self.questions) == 0:
            self.question = self.questions.pop()
            self.sendQuestion()
            self.currentNumber += 1
        self.setScores()

    def stop(self):
        self._stop_event.set()

    def sendQuestion(self):
        self.setScores()
        for player in self.room["players"]:
            self.sendData(self.room["players"]
                          [player], "set", "question", "{0}/{1} ".format(self.currentNumber, self.currentMax) + self.question.question)

    def stopped(self):
        return self._stop_event.is_set()

    def setScores(self):
        for player in self.room["players"]:
            self.sendData(self.room["players"]
                          [player], "set", "score", str(self.room["playerScores"][player]))
