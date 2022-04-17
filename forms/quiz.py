from random import shuffle


class QuizForm:
    def __init__(self, question, answers, correct_answer):
        self.question = question
        self.answers_list = [(i, 0) for i in answers if i != correct_answer]
        self.answers_list.append((correct_answer, 1))
        shuffle(self.answers_list)
