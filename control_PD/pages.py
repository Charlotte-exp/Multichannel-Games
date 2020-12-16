from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class PairingWaitPage(WaitPage):
    """
    The code below keeps the groups the same across all rounds automatically.
    """
    group_by_arrival_time = True

    def is_displayed(self):
        return self.round_number == 1

    template_name = 'control_PD/Waitroom.html'


class SetGroupThings(Page):

    def is_displayed(self):
        return self.round_number == 1

    timeout_seconds = 0.5

    def before_next_page(self):
        if self.player.id_in_group <= 2:
            self.player.subgroup = 'high'
        elif self.player.id_in_group >= 3:
            self.player.subgroup = 'low'


class Decision(Page):
    form_model = 'player'

    def get_form_fields(self):
        if self.player.subgroup == 'high':
            return ['decision_high']
        else:
            return ['decision_low']

    def is_displayed(self):
        """ Probabilistic display! """
        if self.player.left_hanging == 1:
            return False
        elif self.player.left_hanging == 2:
            return False
        elif self.subsession.round_number <= self.participant.vars['last_round']:
            return True

    timer_text = 'If you stay inactive for too long you will be considered a dropout:'
    # timeout_seconds = 2 * 60

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

    def vars_for_template(self):
        """
        This function is for displaying variables in the HTML file (with Django I believe)
        The variables are inserted into calculation or specifications if needed and given a display name
        """
        me = self.player
        opponent = me.get_opponent()
        opponent_high = opponent[0]
        opponent_low = opponent[0]
        if self.round_number > 1:
            return {
                'round_number': self.round_number,
                'my_treatment': me.subgroup,

                'opponent_previous_decision_high': opponent_high.in_round(self.round_number - 1).decision_high,
                'opponent_previous_decision_low': opponent_low.in_round(self.round_number - 1).decision_low,
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
                'my_treatment': me.subgroup,

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
    template_name = 'control_PD/ResultsWaitPage.html'


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
    # timeout_seconds = 2 * 60
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
        opponent = me.get_opponent()
        opponent_high = opponent[0]
        opponent_low = opponent[0]
        return {
            'my_treatment': me.subgroup,

            'my_decision_high': me.decision_high,
            'my_decision_low': me.decision_low,
            'opponent_decision_high': opponent_high.decision_high,
            'opponent_decision_low': opponent_low.decision_low,

            'my_payoff': me.payoff,
            'opponent_payoff_high': opponent_high.payoff,
            'opponent_payoff_low': opponent_low.payoff,

            'cost_high': Constants.c_high,
            'cost_low': Constants.c_low,
            'benefit_high': Constants.b_high,
            'benefit_low': Constants.b_low,
        }


class End(Page):
    """ This page is for final combined results """

    def is_displayed(self):
        """ This function makes the page appear only on the last round """
        if self.player.left_hanging == 1:
            return False
        elif self.player.left_hanging == 2:
            return False
        elif self.subsession.round_number == self.participant.vars['last_round']:
            return True

    def vars_for_template(self):
        me = self.player
        opponent = me.other_player()
        return {
            'my_treatment': me.subgroup,
            'total_payoff': sum([p.payoff for p in self.player.in_all_rounds()]),  # both work!
            # 'total_payment': sum([p.participant.vars['payment'] for p in self.player.in_all_rounds()]),
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
        participant = self.participant
        # self.player.payoff = self.participant.vars[self.participant.vars['payment_app']]  # this won't work and I don't why
        return {
            # 'vars_payment': sum([p.participant.vars['payment'] for p in self.player.in_all_rounds()]),
            # this is not summing... so if I were to use it below it would not work...
            'total_payoff': sum([p.payoff for p in self.player.in_all_rounds()]),  # same as End page
            'participation_fee': self.session.config['participation_fee'],  # set it in the settings like currency
            'payment': (sum([p.payoff.to_real_world_currency(self.session) for p in
                             self.player.in_all_rounds()]) * Constants.currency_per_point),
            'final_payment': ((sum([p.payoff.to_real_world_currency(self.session) for p in
                                    self.player.in_all_rounds()]) * Constants.currency_per_point) + self.session.config[
                                  'participation_fee'])
        }


class LeftHanging(Page):

    def is_displayed(self):
        """ This function makes the page appear only on the last random-ish round """
        if self.player.left_hanging == 1:
            return True
        elif self.player.left_hanging == 2:
            return True


class ProlificLink(Page):
    def is_displayed(self):
        return self.round_number == self.participant.vars['last_round']


page_sequence = [
    PairingWaitPage,
    SetGroupThings,
    Decision,
    ResultsWaitPage,
    Results,
    End,
    # Demographics,
    Payment,
    LeftHanging,
    ProlificLink,
]
