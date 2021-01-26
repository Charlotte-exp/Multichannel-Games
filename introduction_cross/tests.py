from otree.api import Currency as c, currency_range
from . import pages
from ._builtin import Bot
from .models import Constants


class PlayerBot(Bot):
    def play_round(self):
        if self.round_number == 1:
            yield pages.Consent
            yield pages.Welcome, {"q1": '3', "q2": '3'}
            yield pages.Instructions1, {"q3": '2', "q4": '2', "q5": '2'}
            yield pages.Instructions2, {"q6": '2', "q7": '3', "q8": '3'}

