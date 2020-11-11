from otree.api import Currency as c, currency_range
from . import pages
from ._builtin import Bot
from .models import Constants


class PlayerBot(Bot):
    def play_round(self):
        if self.round_number <= Constants.num_rounds:
            if self.participant.vars['treatment'] == 'high':
                yield pages.Decision, dict(decision_high=1)
            else:
                if self.participant.vars['treatment'] == 'low':
                    yield pages.Decision, dict(decision_low=3)
            yield pages.Results

        if self.round_number == Constants.num_rounds:
            yield pages.End
            # yield pages.Demographics, {"age": '22', "gender": 'Female', "income": '£10.000 - £29.999',
            #                            "education": 'Postgraduate degree', "ethnicity": 'White'}
            yield pages.Payment
            # yield pages.ProlificLink
