from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
from decimal import *
getcontext().rounding = ROUND_CEILING # is this for rounding up the payment?


class Consent(Page):
    def is_displayed(self):
        return self.round_number == 1  # Exclude this page in the loop

    def vars_for_template(self):
        return {
            'participation_fee': self.session.config['participation_fee'],
        }


class Welcome(Page):
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
        if values['q3'] != 3:
            return 'Answer to question 1 is incorrect. Check the instructions again and give a new answer'
        if values['q4'] != 2:
            return 'Answer to question 2 is incorrect. Check the instructions again and give a new answer'
        if values['q5'] != 2:
            return 'Answer to question 3 is incorrect. Check the instructions again and give a new answer'

    def vars_for_template(self):
        return{
            'initial_endowment_high': Constants.endowment_high * Constants.min_rounds,
            'initial_endowment_low': Constants.endowment_low * Constants.min_rounds,
            'initial_endowment_joint': (Constants.endowment_high + Constants.endowment_low) * Constants.min_rounds,
        }


class Instructions2(Page):
    form_model = 'player'
    form_fields = ['q6', 'q7', 'q8']

    def is_displayed(self):
        return self.round_number == 1  # Exclude this page in the loop

    def error_message(self, values):
        if values['q6'] != 1:
            return 'Answer to question 1 is incorrect. Check the instructions again and give a new answer'
        if values['q7'] != 3:
            return 'Answer to question 2 is incorrect. Check the instructions again and give a new answer'
        if values['q8'] != 2:
            return 'Answer to question 3 is incorrect. Check the instructions again and give a new answer'

    def vars_for_template(self):
        reward_low = Constants.endowment_low + Constants.b_low - Constants.c_low
        temptation_high = Constants.endowment_high + Constants.b_high
        sucker_high = Constants.endowment_high - Constants.c_high
        # punishment = Constants.endowment_low + Constants.dd_low
        return{
            'cost_high': Constants.c_high,
            'cost_low': Constants.c_low,
            'benefit_high': Constants.b_high,
            'benefit_low': Constants.b_low,

            'sucker_high': -Constants.c_high,
            'temptation_high': Constants.b_high,
            'reward_high': Constants.b_high - Constants.c_high,

            'sucker_low': -Constants.c_low,
            'temptation_low': Constants.b_low,
            'reward_low': Constants.b_low - Constants.c_low,

            'sum_p1': Constants.sucker_high + Constants.reward_low,
            'sum_p2': Constants.temptation_high + Constants.reward_low,
        }


page_sequence = [
    Consent,
    # Welcome,
    # Instructions1,
    # Instructions2,
]
