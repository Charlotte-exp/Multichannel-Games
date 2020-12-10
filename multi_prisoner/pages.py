from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
from decimal import *
import time

getcontext().rounding = ROUND_CEILING  # is this for rounding up the payment?


class PairingWaitPage(WaitPage):
    """
       The code below keeps the groups the same across all rounds automatically.
    """
    group_by_arrival_time = True

    def is_displayed(self):
        return self.round_number == 1

    template_name = 'multi_prisoner/Waitroom.html'


class Decision(Page):
    form_model = 'player'
    form_fields = ['decision_high', 'decision_low']

    def is_displayed(self):
        """ Probabilistic display! """
        if self.player.left_hanging == 1:
            return False
        elif self.player.left_hanging == 2:
            return False
        elif self.subsession.round_number <= self.participant.vars['last_round']:
            return True

    timer_text = 'If you stay inactive for too long you will be considered a dropout:'

    timeout_seconds = 2 * 60

    def before_next_page(self):
        """
            Dropout code! basically if the timer set above runs out, the opponent becomes left_hanging and
            is jumped to the leftHanging page with a link to Prolific. The dropout also goes to that page but gets
            a different text.
            I need to set decisions to avoid an error message that's all
        """
        me = self.player
        opponent = me.other_player()
        if self.timeout_happened:
            opponent.left_hanging = 1
            me.left_hanging = 2
            print('is the other player left hanging?', opponent.left_hanging)
            print('Am I a dropout?', me.left_hanging)
            me.decision_high = 1
            me.decision_low = 3

    def vars_for_template(self):
        """
        This function is for displaying variables in the HTML file (with Django I believe)
        The variables are inserted into calculation or specifications if needed and given a display name
        """
        me = self.player
        opponent = me.other_player()  # the other player attributed to me by the function other_player()
        if self.round_number > 1:
            return {
                'round_number': self.round_number,
                'opponent_previous_decision_high': opponent.in_round(self.round_number - 1).decision_high,
                'opponent_previous_decision_low': opponent.in_round(self.round_number - 1).decision_low,
                'previous_decision_high': me.in_round(self.round_number - 1).decision_high,
                'previous_decision_low': me.in_round(self.round_number - 1).decision_low,

                'cost_high': Constants.c_high,
                'cost_low': Constants.c_low,
                'benefit_high': Constants.b_high,
                'benefit_low': Constants.b_low,
            }
        else:
            return {
                'round_number': self.round_number,

                'cost_high': Constants.c_high,
                'cost_low': Constants.c_low,
                'benefit_high': Constants.b_high,
                'benefit_low': Constants.b_low,
            }


class ResultsWaitPage(WaitPage):
    def after_all_players_arrive(self):
        for p in self.group.get_players():
            p.set_payoff()

    def is_displayed(self):
        """ Probabilistic display! """
        if self.subsession.round_number <= self.participant.vars['last_round']:
            return True

    # body_text = "Please wait while the other participant makes their decision."
    template_name = 'multi_prisoner/ResultsWaitPage.html'


class Results(Page):
    """ This page is for round results """

    def is_displayed(self):
        """ Probabilistic display! """
        if self.player.left_hanging == 1:
            return False
        elif self.player.left_hanging == 2:
            return False
        elif self.subsession.round_number <= self.participant.vars['last_round']:
            return True

    timeout_seconds = 2 * 60
    # my_page_timeout_seconds = 90
    #
    # def get_timeout_seconds(self):
    #     round_number = self.subsession.round_number
    #     timeout = self.my_page_timeout_seconds
    #     if round_number <= 2:
    #         return timeout
    #     else:
    #         timeout -= (round_number - 2) * 5
    #         print(timeout)
    #         return timeout

    def vars_for_template(self):
        me = self.player
        opponent = me.other_player()
        return {
            'my_high_decision': me.decision_high,
            'my_low_decision': me.decision_low,
            'opponent_high_decision': opponent.decision_high,
            'opponent_low_decision': opponent.decision_low,

            'my_high_payoff': me.payoff_high,
            'my_low_payoff': me.payoff_low,
            'opponent_high_payoff': opponent.payoff_high,
            'opponent_low_payoff': opponent.payoff_low,

            'cost_high': Constants.c_high,
            'cost_low': Constants.c_low,
            'benefit_high': Constants.b_high,
            'benefit_low': Constants.b_low,
        }


class End(Page):
    """ This page is for final combined round results """

    def is_displayed(self):
        """ This function makes the page appear only on the last random-ish round """
        if self.player.left_hanging == 1:
            return False
        elif self.player.left_hanging == 2:
            return False
        elif self.subsession.round_number == self.participant.vars['last_round']:
            return True

    def vars_for_template(self):
        me = self.player
        # opponent = me.other_player()  # of we want to display the opponent's payoff
        return {
            'total_payoff_high': sum([p.payoff_high for p in self.player.in_all_rounds()]),
            'total_payoff_low': sum([p.payoff_low for p in self.player.in_all_rounds()]),
            'player_in_all_rounds': self.player.in_all_rounds(),
        }


class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'income', 'education', 'ethnicity']

    def is_displayed(self):
        """ This function makes the page appear only on the last random-ish round """
        if self.player.left_hanging == 1:
            return False
        elif self.player.left_hanging == 2:
            return False
        elif self.subsession.round_number == self.participant.vars['last_round']:
            return True


class Payment(Page):
    """ This page is for final payment in GBP """

    def is_displayed(self):
        """ This function makes the page appear only on the last random-ish round """
        if self.player.left_hanging == 1:
            return False
        elif self.player.left_hanging == 2:
            return False
        elif self.subsession.round_number == self.participant.vars['last_round']:
            return True

    def vars_for_template(self):
        return {
            # 'vars_payment': sum([p.participant.vars['payment'] for p in self.player.in_all_rounds()]),
            # participant.vars is not summing... so if I were to use it below it would not work...

            'total_payoff_high': sum([p.payoff_high for p in self.player.in_all_rounds()]),
            'total_payoff_low': sum([p.payoff_low for p in self.player.in_all_rounds()]),
            'total_payoff': sum([p.payment for p in self.player.in_all_rounds()]),  # same as End page
            'participation_fee': self.session.config['participation_fee'],  # set it in the settings like the currency
            'payment': (sum([p.payment.to_real_world_currency(self.session) for p in self.player.in_all_rounds()])
                        * Constants.currency_per_point),
            'final_payment': ((sum([p.payment.to_real_world_currency(self.session) for p in self.player.in_all_rounds()])
                               * Constants.currency_per_point) + self.session.config['participation_fee'])
        }


class LeftHanging(Page):

    def is_displayed(self):
        """ This function makes the page appear only on the last random-ish round """
        if self.player.left_hanging == 1:
            return True
        elif self.player.left_hanging == 2:
            return True

    # def vars_for_template(self):
    #     me = self.player
    #     opponent = me.other_player()
    #     return {
    #         'left_hanging': opponent.left_hanging,
    #         'dropout': me.left_hanging
    #     }


class ProlificLink(Page):
    def is_displayed(self):
        return self.round_number == self.participant.vars['last_round']


page_sequence = [
    PairingWaitPage,
    Decision,
    ResultsWaitPage,
    Results,
    End,
    # Demographics,
    Payment,
    LeftHanging,
    ProlificLink,
]
