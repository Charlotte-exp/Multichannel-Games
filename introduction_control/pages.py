from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
from decimal import *
getcontext().rounding = ROUND_CEILING  # is this for rounding up the payment?


class Consent(Page):
    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):
        return {
            'participation_fee': self.session.config['participation_fee'],
        }


class Welcome(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2']

    def is_displayed(self):
        return self.round_number == 1

    def error_message(self, values):
        if values['q1'] != 2:
            return 'Answer to question 1 is incorrect. Check the instructions again and give a new answer'
        if values['q2'] != 3:
            return 'Answer to question 2 is incorrect. Check the instructions again and give a new answer'


class Instructions1(Page):
    form_model = 'player'

    def is_displayed(self):
        return self.round_number == 1

    def get_form_fields(self):
        """ make one q3 for each subgroup that displays only to each to avoid empty field errors"""
        if self.participant.vars['subgroup'] == 'high':
            return ['q3a', 'q4', 'q5']
        else:
            return ['q3b', 'q4', 'q5']

    def error_message(self, values):
        if self.participant.vars['subgroup'] == 'high':
            if values['q3a'] != 2:
                return 'Answer to question 1 is incorrect. Check the instructions again and give a new answer'
        if self.participant.vars['subgroup'] == 'low':
            if values['q3b'] != 2:
                return 'Answer to question 1 is incorrect. Check the instructions again and give a new answer'
        if values['q4'] != 2:
            return 'Answer to question 2 is incorrect. Check the instructions again and give a new answer'
        if values['q5'] != 2:
            return 'Answer to question 3 is incorrect. Check the instructions again and give a new answer'

    def vars_for_template(self):
        return{
            'my_treatment': self.participant.vars['subgroup']
        }


class Instructions2(Page):
    form_model = 'player'
    form_fields = ['q6', 'q7', 'q8']

    def is_displayed(self):
        return self.round_number == 1

    def error_message(self, values):
        if values['q6'] != 1:
            return 'Answer to question 1 is incorrect. Check the instructions again and give a new answer'
        if self.participant.vars['subgroup'] == 'high':
            if values['q7'] != 3:
                return 'Answer to question 2 is incorrect. Check the instructions again and give a new answer'
            if values['q8'] != 3:
                return 'Answer to question 3 is incorrect. Check the instructions again and give a new answer'
        if self.participant.vars['subgroup'] == 'low':
            if values['q7'] != 2:
                return 'Answer to question 2 is incorrect. Check the instructions again and give a new answer'
            if values['q8'] != 2:
                return 'Answer to question 3 is incorrect. Check the instructions again and give a new answer'

    def vars_for_template(self):
        return{
            'my_treatment': self.participant.vars['subgroup']
        }


page_sequence = [
    Consent,
    # Welcome,
    # Instructions1,
    # Instructions2,
]
