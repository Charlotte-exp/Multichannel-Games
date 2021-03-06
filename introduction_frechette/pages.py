from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants

import math


class Consent(Page):
    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):
        return {
            'participation_fee': self.session.config['participation_fee'],
        }


class Instructions(Page):
    form_model = 'player'

    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):
        """"
        The currency per point and participation fee are set in settings.py.
        """
        return {
            'currency_per_points': self.session.config['real_world_currency_per_point'],
            'delta': math.ceil(Constants.proba_next_round * 100)
        }


class Results(Page):
    pass


page_sequence = [
    Consent,
    Instructions,
]
