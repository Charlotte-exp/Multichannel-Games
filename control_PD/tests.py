from otree.api import Currency as c, currency_range
from . import pages
from ._builtin import Bot
from .models import Constants


class PlayerBot(Bot):
    def play_round(self):
        if self.round_number <= self.participant.vars['last_round']:
            if self.participant.vars['subgroup'] == 'high':
                yield pages.Decision, dict(decision_high=1)
            else:
                if self.participant.vars['subgroup'] == 'low':
                    yield pages.Decision, dict(decision_low=1)
        #     if self.round_number % 2 == 0:
        #         if self.participant.vars['subgroup'] == 'high':
        #             yield pages.Decision, dict(decision_high=1)
        #         else:
        #             if self.participant.vars['subgroup'] == 'low':
        #                 yield pages.Decision, dict(decision_low=1)
        #     else:
        #         if self.participant.vars['subgroup'] == 'high':
        #             yield pages.Decision, dict(decision_high=0)
        #         else:
        #             if self.participant.vars['subgroup'] == 'low':
        #                 yield pages.Decision, dict(decision_low=0)
            yield pages.Results

        if self.round_number == self.participant.vars['last_round']:
            yield pages.End
            yield pages.Demographics, {"age": '22', "gender": 'Female', "income": '£10.000 - £29.999',
                                       "education": 'Postgraduate degree', "ethnicity": 'White'}
            yield pages.Payment
            yield pages.ProlificLink
