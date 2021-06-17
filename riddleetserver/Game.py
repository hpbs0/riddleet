from threading import Thread, Event
import time
from typing import List

from .Question import Question


class Game(Thread):
    """
    Contains the game loop and current question
    Mounted to its own thread
    Started by the owner of the group, room has reference to the game instance
    """

    def __init__(self, questions: List[Question], room, playerList) -> None:
        from riddleetserver import sendData
        super(Game, self).__init__()
        self.sendData = sendData
        self.questions: List[Question] = questions
        self.question: Question = None
        self.currentMax = len(self.questions)
        self.currentNumber = 1
        self.playerList = playerList
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
        """
        Main loop of the game, sends questions and wait for 15 seconds 
        (+3 seconds for matching the time somewhat and answering overhead)
        Prints out the leaderboard before the questions and after game ended
        """
        for player in self.room["players"]:
            self.room["playerScores"][player] = 0
            self.sendData(self.room["players"][player], "start", "game", "")
        self.question = self.questions.pop()
        self.sendQuestion()
        self.currentNumber += 1
        while not self._stop_event.wait(15+3) and not len(self.questions) == 0:
            self.question = self.questions.pop()
            self.sendQuestion()
            self.currentNumber += 1
        self.question = None
        self.printPlayers()
        for player in self.room["players"]:
            self.sendData(self.room["players"]
                          [player], "end", "game", "")
        self.room["status"] = "WAIT"

    def stop(self):
        """
        Stops the loop, currently does not have any use but
        stopping from client can be implemented
        """
        self._stop_event.set()

    def sendQuestion(self):
        """
        Sends current question to ever player in the room
        Resets the playerAnswered dictionary for the new question
        """
        self.printPlayers()
        for player in self.room["players"]:
            self.room["playerAnswered"][player] = False
            self.sendData(self.room["players"]
                          [player], "set", "question", "{0}/{1}".format(
                              self.currentNumber, self.currentMax) +
                          " "+format(str(self.room["playerScores"][player]) + " " +
                                     self.question.question))
        time.sleep(1)

    def printPlayers(self):
        """
        Sends the leaderboard to all of the players in the room
        Used just before sending the questions
        """
        data = self.playerList()
        if isinstance(data, list):
            s = ":"
            s = ":"+s.join(data)
            for player in self.room["players"]:
                self.sendData(self.room["players"][player], "print", "lb", s)
            time.sleep(1)

    def stopped(self):
        """
        Checks if game is stopped
        """
        return self._stop_event.is_set()
