import csv


class Question:
    def __init__(self, question: str, answer: str) -> None:
        self.question:str = question
        self.ans:str = answer

    def compareAnswer(self, ans):
        return self.ans == ans


def readRiddles(riddles: dict):
    with open('riddles.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='|')
        for row in csv_reader:
            riddles.append(Question(row[0], row[1]))
