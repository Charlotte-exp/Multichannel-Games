from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


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


class Results(Page):
    pass


page_sequence = [
    Consent,
    Instructions,
]
