from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class PairingWaitPage(WaitPage):
    """
    The Waitroom. This wait page has two purposes: making sure pps don't wait too long for other players in case there
    is little traffic, and allows one pp to leave before being grouped with others so that a dropout at the instruction
    level does not mean all pp in the group are out.
    The code below keeps the groups the same across all rounds automatically.
    We added a special pairing method in models.py.
    The waitroom has a 5min timer after which the pp is given a code to head back to prolific.
    This is coded on the template below and uses a javascript. (don't forget to paste the correct link!)
    """
    group_by_arrival_time = True

    def is_displayed(self):
        return self.round_number == 1

    template_name = 'control_PD/Waitroom.html'


class Decision(Page):
    """
    This is where the pp are presented with the PD options and give their decision. It's simple form fields from Django.
    There is a timer to check for dropouts. If one of the players' timer runs out the others are linked back to prolific
    """
    form_model = 'player'

    def get_form_fields(self):
        """ Only one decision per subgroup or we have an empty field error"""
        if self.participant.vars['subgroup'] == 'high':
            return ['decision_high']
        else:
            return ['decision_low']

    def is_displayed(self):
        """
        This page is displayed only if the player is neither left hanging (1) or a dropout (2).
        And only for the number of rounds assigned to the group by the random number function.
        """
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
        Dropout check code! If the timer set above runs out, all the other players in the group become left_hanging = 1
        and are jumped to the leftHanging page with a link to Prolific. The dropout also goes to that page but gets
        a different text (left_hanging = 2).
        Decisions for the missed round are automatically filled to avoid an NONE type error.
        """
        me = self.player
        other_players = me.get_others_in_group()
        if self.timeout_happened:
            other_players[0].left_hanging = 1
            other_players[1].left_hanging = 1
            other_players[2].left_hanging = 1
            me.left_hanging = 2
            me.decision_high = 1
            me.decision_low = 1

    def vars_for_template(self):
        """
        This function is for displaying variables in the HTML file using Django.
        The variables are inserted into calculation or specifications and given a display name used in the HTML.
        """
        me = self.player
        opponent = me.get_opponent()
        opponent_high = opponent[0]
        opponent_low = opponent[0]
        if self.round_number > 1:
            return {
                'round_number': self.round_number,
                'my_treatment': me.participant.vars['subgroup'],

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
                'my_treatment': me.participant.vars['subgroup'],

                'cost_high': Constants.c_high,
                'cost_low': Constants.c_low,
                'benefit_high': Constants.b_high,
                'benefit_low': Constants.b_low,
            }


class ResultsWaitPage(WaitPage):
    """
    This wait page is necessary to compile the payoffs as the results can only be displayed on the results page if all
    the players have made a decision. Thus players have to wait for the decision of the others before moving on to the
    results page.
    I use a template for some special text rather than just the body_text variable.
    """

    def after_all_players_arrive(self):
        """ The function that waits for players to arrive to calculate the payoffs like instructed in models.py """
        for p in self.group.get_players():
            p.set_payoff()

    def is_displayed(self):
        """
        This page is displayed only if the number of rounds assigned to the group by the random number function.
        Curiously it does not need to be hidden for left_hanging participants...
        """
        if self.subsession.round_number <= self.participant.vars['last_round']:
            return True

    # body_text = "Please wait while the other participant makes their decision."
    template_name = 'control_PD/ResultsWaitPage.html'


class Results(Page):
    """
    This page is for the round results. It gives feedback on what the opponents decided for this round.
    It has a timer so that a dropout is automatically pushed to the decision page where the dropout function is.
    """

    def is_displayed(self):
        """
        This page is displayed only if the player is neither left hanging (1) or a dropout (2).
        And only for the number of rounds assigned to the group by the random number function.
        """
        if self.player.left_hanging == 1:
            return False
        elif self.player.left_hanging == 2:
            return False
        elif self.subsession.round_number <= self.participant.vars['last_round']:
            return True

    timer_text = 'You are about to be automatically moved to the next round decision page'
    timeout_seconds = 2 * 6000

    def vars_for_template(self):
        """
        This function is for displaying variables in the HTML file using Django.
        The variables are inserted into calculation or specifications and given a display name used in the HTML.
        """
        me = self.player
        opponent = me.get_opponent()
        opponent_high = opponent[0]
        opponent_low = opponent[0]
        return {
            'my_treatment': me.participant.vars['subgroup'],

            'my_decision_high': me.decision_high,
            'my_decision_low': me.decision_low,
            'opponent_decision_high': opponent_high.decision_high,
            'opponent_decision_low': opponent_low.decision_low,

            'my_payoff': me.payoff,
            'my_result_high': me.payoff - Constants.endowment_high,
            'my_result_low': me.payoff - Constants.endowment_low,

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
        }


class End(Page):
    """
    This page is for final combined round results. It displays the payoffs of each round played for all opponents
    and sums the total across round of the player.
    """

    def is_displayed(self):
        """
        This page is displayed only if the player is neither left hanging (1) or a dropout (2).
        And only appears on the last round.
        """
        if self.player.left_hanging == 1:
            return False
        elif self.player.left_hanging == 2:
            return False
        elif self.subsession.round_number == self.participant.vars['last_round']:
            return True

    def vars_for_template(self):
        """
        This function is for displaying variables in the HTML file using Django.
        The variables are inserted into calculation or specifications and given a display name used in the HTML.
        """
        me = self.player
        return {
            'my_treatment': me.participant.vars['subgroup'],
            'player_in_all_rounds': me.in_all_rounds(),

            'total_payoff': sum([p.payoff for p in me.in_all_rounds()]),
            'my_result_high': me.payoff - Constants.endowment_high,
            'my_result_low': me.payoff - Constants.endowment_low,
        }


class Demographics(Page):
    """ This page displays survey box to record pp's demographics. it's just made of simple form fields. """
    form_model = 'player'
    form_fields = ['age', 'gender', 'income', 'education', 'ethnicity']

    def is_displayed(self):
        """
        This page is displayed only if the player is neither left hanging (1) or a dropout (2).
        And only appears on the last round.
        """
        if self.player.left_hanging == 1:
            return False
        elif self.player.left_hanging == 2:
            return False
        elif self.subsession.round_number == self.participant.vars['last_round']:
            return True


class CommentBox(Page):
    form_model = 'player'
    form_fields = ['comment_box']

    def is_displayed(self):
        """ This function makes the page appear only on the last random-ish round """
        if self.player.left_hanging == 1:
            return False
        elif self.player.left_hanging == 2:
            return False
        elif self.subsession.round_number == self.participant.vars['last_round']:
            return True


class Payment(Page):
    """
    This page is for final payment in GBP. A lot of the mechanics relating to payment is set in the settings
    (currency/point exchange rate, currency). It displays the total for each game and the total combined, the show-up fee,
    the conversion rate, the total bonus in GBP and the final payment in GBP of bonus and participation fee combined.
    """

    def is_displayed(self):
        """
        This page is displayed only if the player is neither left hanging (1) or a dropout (2).
        And only appears on the last round.
        """
        if self.player.left_hanging == 1:
            return False
        elif self.player.left_hanging == 2:
            return False
        elif self.subsession.round_number == self.participant.vars['last_round']:
            return True

    def vars_for_template(self):
        """"
        The currency per point and participation fee are set in settings.py. However it can only be set in GBP per point
        which is not human friendly. So I need to reverse it for display.
        The bonus and final payment are not saved in the data sheet automatically.
        I'd have to save the result in a form field under the player class I guess... but it is annoying.
        Since I use the oTree variable "payoff" it all gets displayed in the admin interface and I can download that.
        """
        return {
            'total_payoff': self.participant.payoff,
            'points_per_currency': 1 / self.session.config['real_world_currency_per_point'],
            'participation_fee': self.session.config['participation_fee'],
            'bonus': self.participant.payoff.to_real_world_currency(self.session),
            'final_payment': self.participant.payoff_plus_participation_fee()
        }

    def before_next_page(self):
        for p in self.group.get_players():
            p.report_vars_for_database()


class LeftHanging(Page):
    """
    This page is for dropouts. If a participant quits after the waitroom there is a timer on the results
    and decision page that redirect them to this page. Here depending on who left and who was left hanging,
    they get a different message (based on their left_hanging value).
    The left-hanging pp get a link to go back to Prolific (don't forget to paste the correct link!).
    """

    def is_displayed(self):
        """ This page is displayed only if the player is either left hanging (1) or a dropout (2)."""
        if self.player.left_hanging == 1:
            return True
        elif self.player.left_hanging == 2:
            return True


class ProlificLink(Page):
    """
    This page redirects pp to prolific automatically with a javascript (don't forget to put paste the correct link!).
    There is a short text and the link in case it is not automatic.
    """

    def is_displayed(self):
        """ This page only appears on the last round. It's after LeftHanging so no need to hide it from dropouts."""
        return self.round_number == self.participant.vars['last_round']


page_sequence = [
    PairingWaitPage,
    Decision,
    ResultsWaitPage,
    Results,
    End,
    Demographics,
    CommentBox,
    Payment,
    LeftHanging,
    ProlificLink,
]
