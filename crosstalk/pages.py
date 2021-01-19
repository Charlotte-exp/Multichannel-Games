from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
from decimal import *

import itertools

getcontext().rounding = ROUND_CEILING  # is this for rounding up the payment?


class PairingWaitPage(WaitPage):
    """
    The code below keeps the groups the same across all rounds automatically.
    """
    group_by_arrival_time = True

    def is_displayed(self):
        return self.round_number == 1

    template_name = 'crosstalk/Waitroom.html'


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
        other_players = me.get_others_in_group()
        if self.timeout_happened:
            other_players[0].left_hanging = 1
            other_players[1].left_hanging = 1
            other_players[2].left_hanging = 1
            me.left_hanging = 2
            me.decision_high = 1
            me.decision_low = 3

            # attempt at a loop...
            # for p in other_players:
            #     return p.left_hanging == 1

    # player id for for troubleshooting. If I want to display the player in the group of four though I can keep it.

    def vars_for_template(self):
        """
        This function is for displaying variables in the HTML file (with Django I believe)
        The variables are inserted into calculation or specifications if needed and given a display name
        """
        me = self.player
        opponents = me.get_opponent()
        opponent_high = opponents[0]
        opponent_low = opponents[1]
        if self.round_number > 1:
            return {
                'round_number': self.round_number,
                'opponent_previous_decision_high': opponent_high.in_round(self.round_number - 1).decision_high,
                'opponent_previous_decision_low': opponent_low.in_round(self.round_number - 1).decision_low,
                'previous_decision_high': me.in_round(self.round_number - 1).decision_high,
                'previous_decision_low': me.in_round(self.round_number - 1).decision_low,

                'cost_high': Constants.c_high,
                'cost_low': Constants.c_low,
                'benefit_high': Constants.b_high,
                'benefit_low': Constants.b_low,

                'my_player_id': me.id_in_group,
                'opponent_high_id': opponent_high.id_in_group,
                'opponent_low_id': opponent_low.id_in_group,
            }
        else:
            return {
                'round_number': self.round_number,

                'cost_high': Constants.c_high,
                'cost_low': Constants.c_low,
                'benefit_high': Constants.b_high,
                'benefit_low': Constants.b_low,

                'my_player_id': me.id_in_group,
                'opponent_high_id': opponent_high.id_in_group,
                'opponent_low_id': opponent_low.id_in_group,
            }


class ResultsWaitPage(WaitPage):
    def after_all_players_arrive(self):
        for p in self.group.get_players():
            p.set_payoffs()

    def is_displayed(self):
        """ Probabilistic display! """
        if self.subsession.round_number <= self.participant.vars['last_round']:
            return True

    # body_text = "Please wait while the other participant makes their decision."
    template_name = 'crosstalk/ResultsWaitPage.html'


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

    timer_text = 'You are about to be automatically moved to the next round decision page'
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
        opponents = me.get_opponent()
        opponent_high = opponents[0]
        opponent_low = opponents[1]
        return {
            'my_decision_high': me.decision_high,
            'my_decision_low': me.decision_low,
            'opponent_decision_high': opponent_high.decision_high,
            'opponent_decision_low': opponent_low.decision_low,

            'my_payoff_high': me.payoff_high,
            'my_payoff_low': me.payoff_low,
            'opponent_payoff_high': opponent_high.payoff_high,
            'opponent_payoff_low': opponent_low.payoff_low,

            'cost_high': Constants.c_high,
            'cost_low': Constants.c_low,
            'benefit_high': Constants.b_high,
            'benefit_low': Constants.b_low,

            'my_player_id': me.id_in_group,
            'opponent_id_high': opponent_high.id_in_group,
            'opponent_id_low': opponent_low.id_in_group,
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
        opponents = me.get_opponent()
        opponent_high = opponents[0]
        opponent_low = opponents[1]
        return {
            'player_in_all_rounds': me.in_all_rounds(),
            'opponent_high_in_all_rounds': opponent_high.in_all_rounds(),
            'opponent_low_in_all_rounds': opponent_low.in_all_rounds(),
            'player_and_opponent_high': zip(me.in_all_rounds(), opponent_high.in_all_rounds()),
            'player_and_opponent_low': zip(me.in_all_rounds(), opponent_low.in_all_rounds()),

            'total_payoff_high': sum([p.payoff_high for p in self.player.in_all_rounds()]),
            'total_payoff_low': sum([p.payoff_low for p in self.player.in_all_rounds()]),
        }

    # def before_next_page(self):
    #     for p in self.group.get_players():
    #         p.set_payoff()


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
        """
        The currency per point and participation fee are set in settings.py. The the currency like that ut displays in
        the payment section of the admin interface. (the total payoff and payment is not in the data sheet!)
        to display the number of points per GBP I need to reverse the number though as in settings it's the opposite
        (GBP per points).
        """
        return {
            'total_payoff_high': sum([p.payoff_high for p in self.player.in_all_rounds()]),
            'total_payoff_low': sum([p.payoff_low for p in self.player.in_all_rounds()]),
            'total_payoff': sum([p.total_payoff for p in self.player.in_all_rounds()]),
            'points_per_currency': 1 / self.session.config['real_world_currency_per_point'],
            'participation_fee': self.session.config['participation_fee'],
            'payment': sum([p.total_payoff.to_real_world_currency(self.session) for p in self.player.in_all_rounds()]),
            'final_payment': sum(
                [p.total_payoff.to_real_world_currency(self.session) for p in self.player.in_all_rounds()]
                ) + self.session.config['participation_fee']
        }


class LeftHanging(Page):
    """
    This page is for dropouts. If a participant quits after the waitroom there is a timer on the results
    and decision page that redirect them to this page. Here depending on who left and who was left hanging,
    There get a different message (based on their left_hanging value)
    """

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
    Demographics,
    Payment,
    LeftHanging,
    ProlificLink,
]
