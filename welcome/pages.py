from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
from decimal import *
getcontext().rounding = ROUND_CEILING # is this for rounding up the payment?


class Introduction(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2']

    def is_displayed(self):
        return self.round_number == 1  # Exclude this page in the loop

    def error_message(self, values):
        if values['q1'] != 2:
            return 'Answer to question 1 is incorrect. Check the instructions again and give a new answer'
        if values['q2'] != 3:
            return 'Answer to question 2 is incorrect. Check the instructions again and give a new answer'

#    timeout_seconds = 100


class Instructions1(Page):
    form_model = 'player'
    form_fields = ['q3', 'q4', 'q5']

    def is_displayed(self):
        return self.round_number == 1  # Exclude this page in the loop

    def error_message(self, values):
        if values['q3'] != 1:
            return 'Answer to question 1 is incorrect. Check the instructions again and give a new answer'
        if values['q4'] != 2:
            return 'Answer to question 2 is incorrect. Check the instructions again and give a new answer'
        if values['q5'] != 2:
            return 'Answer to question 3 is incorrect. Check the instructions again and give a new answer'


class Instructions2(Page):
    form_model = 'player'
    form_fields = ['q6', 'q7', 'q8']

    def is_displayed(self):
        return self.round_number == 1  # Exclude this page in the loop

    def error_message(self, values):
        if values['q6'] != 2:
            return 'Answer to question 1 is incorrect. Check the instructions again and give a new answer'
        if values['q7'] != 3:
            return 'Answer to question 2 is incorrect. Check the instructions again and give a new answer'
        if values['q8'] != 3:
            return 'Answer to question 3 is incorrect. Check the instructions again and give a new answer'


class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'gender']

    def is_displayed(self):
        return self.round_number == 1  # Exclude this page in the loop


class Consent(Page):
    def is_displayed(self):
        return self.round_number == 1  # Exclude this page in the loop




page_sequence = [
    Introduction,
    Instructions1,
    Instructions2,
    Demographics,
    Consent,
]