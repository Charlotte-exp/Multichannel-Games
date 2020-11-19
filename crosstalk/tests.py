from otree.api import Currency as c, currency_range
from . import pages
from ._builtin import Bot
from .models import Constants


class PlayerBot(Bot):
    def play_round(self):
        if self.round_number <= self.participant.vars['last_round']:
            yield pages.Decision, {"decision_high": 1, "decision_low": 3}
            # assert 'Both of you chose to Cooperate' in self.html  # no clue what this is
            # assert self.player.payoff == Constants.both_cooperate_payoff  # no clue what this is
            # if self.round_number % 2 == 0:
            #     if self.player.id_in_group == 1:
            #         yield pages.Decision, dict(decision_high="Cooperate", decision_low="Cooperate")
            # else:
            #     if self.player.id_in_group == 1:
            #         yield pages.Decision, dict(decision_high="Defect", decision_low="Defect")
            yield pages.Results

        if self.round_number == self.participant.vars['last_round']:
            yield pages.End
            # yield pages.Demographics, {"age": '22', "gender": 'Female', "income": '£10.000 - £29.999',
            #                            "education": 'Postgraduate degree', "ethnicity": 'White'}
            yield pages.Payment
            yield pages.ProlificLink
