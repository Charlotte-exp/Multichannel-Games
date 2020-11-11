from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
from decimal import *
getcontext().rounding = ROUND_CEILING  # is this for rounding up the payment?


# class PairingWaitPage(WaitPage):
#     group_by_arrival_time = True # this code keeps the groups the same across all rounds automatically
#
#     def is_displayed(self):
#         return self.round_number == 1
#
#     template_name = 'crosstalk/Waitroom.html'


class Decision(Page):
    form_model = 'player'
    form_fields = ['decision_high', 'decision_low']

    def is_displayed(self):
        """ Probabilistic display! """
        if self.subsession.round_number <= self.group.last_round:
            return True

    # player id for for troubleshooting. If I want to display the player in the group of four though I can keep it.
    # Check that I actually call
    def vars_for_template(self):
        """ This function is for displaying variables in the HTML file (with Django I believe)
            The variables are inserted into calculation or specifications if needed and given a display name """
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
            p.set_payoff()

    def is_displayed(self):
        """ Probabilistic display! """
        if self.subsession.round_number <= self.group.last_round:
            return True

    # body_text = "Please wait while the other participant makes their decision."
    template_name = 'crosstalk/Dropout.html'


class Results(Page):
    """ Probabilistic display! """
    def is_displayed(self):
        if self.subsession.round_number <= self.group.last_round:
            return True

    def vars_for_template(self):
        me = self.player
        opponents = me.get_opponent()
        opponent_high = opponents[0]
        opponent_low = opponents[1]
        return {
            'my_high_decision': me.decision_high,
            'my_low_decision': me.decision_low,
            'opponent_high_decision': opponent_high.decision_high,
            'opponent_low_decision': opponent_low.decision_low,

            'my_high_payoff': me.payoff_high,
            'my_low_payoff': me.payoff_low,
            'opponent_high_payoff': opponent_high.payoff_high,
            'opponent_low_payoff': opponent_low.payoff_low,

            'cost_high': Constants.c_high,
            'cost_low': Constants.c_low,
            'benefit_high': Constants.b_high,
            'benefit_low': Constants.b_low,

            'my_player_id': me.id_in_group,
            'opponent_high_id': opponent_high.id_in_group,
            'opponent_low_id': opponent_low.id_in_group,
        }


class End(Page):
    """ This page is for final combined round results """

    def is_displayed(self):
        """ This function makes the page appear only on the last round """
        return self.round_number == self.group.last_round

    def vars_for_template(self):
        me = self.player
        opponents = me.get_opponent()
        opponent_high = opponents[0]
        opponent_low = opponents[1]
        return {
            'opponent_payoff_high': opponent_high.payoff_high,
            'opponent_payoff_low': opponent_low.payoff_low,

            'opponent_decision_high': opponent_high.decision_high,
            'opponent_decision_low': opponent_low.decision_low,

            'total_payoff_high': sum([p.payoff_high for p in self.player.in_all_rounds()]),
            'total_payoff_low': sum([p.payoff_low for p in self.player.in_all_rounds()]),

            'player_in_all_rounds': me.in_all_rounds(),
            'opponent_high_in_all_rounds': opponent_high.in_all_rounds(),  # one of my attempts to solve the loop issue
            'opponent_low_in_all_rounds': opponent_low.in_all_rounds(),    # see notion for sample HTML code
        }


class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'income', 'education', 'ethnicity']

    def is_displayed(self):
        """ This function makes the page appear only on the last random-ish round """
        return self.round_number == self.group.last_round


class Payment(Page):
    """ This page is for final payment in GBP """

    def is_displayed(self):
        """ This function makes the page appear only on the last round """
        return self.round_number == self.group.last_round

    def vars_for_template(self):
        participant = self.participant
        return {
            # 'vars_payment': sum([p.participant.vars['payment'] for p in self.player.in_all_rounds()]),
            # participant.vars is not summing... so if I were to use it below it would not work...

            'total_payoff_high': sum([p.payoff_high for p in self.player.in_all_rounds()]),
            'total_payoff_low': sum([p.payoff_low for p in self.player.in_all_rounds()]),
            'total_payoff': sum([p.payment for p in self.player.in_all_rounds()]),  # same as End page
            'participation_fee': self.session.config['participation_fee'],  # set it in the settings along with the currency
            'payment': (sum([p.payment.to_real_world_currency(self.session) for p in self.player.in_all_rounds()]) * Constants.currency_per_point),
            'final_payment': ((sum([p.payment.to_real_world_currency(self.session) for p in self.player.in_all_rounds()]) * Constants.currency_per_point) + self.session.config['participation_fee'])
        }


class ProlificLink(Page):
    def is_displayed(self):
        return self.round_number == self.group.last_round


page_sequence = [
    Decision,
    ResultsWaitPage,
    Results,
    End,
    # Demographics,
    Payment,
    ProlificLink,
]
