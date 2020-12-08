from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

import random
import itertools

author = 'Charlotte'

doc = """
        Two simultaneous Prisoner's dilemma/donation game between two players with two different payoffs.
        Random pairing and player id attribution
        Random last round past 20 rounds (50% chance of next round).

        You can also use cmd+/ to comment out an entire section!!
        """


class Constants(BaseConstants):
    name_in_url = 'multi_prisoner'
    players_per_group = 2
    num_rounds = 50

    # """variables for randomish end round, used in the intro app at the mo"""
    # min_rounds = 20
    # proba_next_round = 0.5

    currency_per_point = 0.1 # 10pts is £1

    """
    Donation game payoffs
    b = benefit, c = cost, dd = both defect
    """
    b_high = c(5)
    c_high = c(1)
    dd_high = c(0)
    endowment_high = c_high

    b_low = c(2)
    c_low = c(1)
    dd_low = c(0)
    endowment_low = c_low


class Subsession(BaseSubsession):

    """
       Instead of creating_session() we need to use group_by_arrival_time_method().
       The function makes sure that only players with the same last_round will be paired up.
       I could only implement that retroactively though and assign last_round in the intro app.
       The inconveninent is that if 3 people read the instructions, 2 get 5 and 1 gets 6,
       if one of the 5 one gives up and quits the other two cannot play together. So not ideal
    """
    def group_by_arrival_time_method(self, waiting_players):
        print("starting group_by_arrival_time_method")
        from collections import defaultdict
        d = defaultdict(list)
        for p in waiting_players:
            category = p.participant.vars['last_round']
            players_with_this_category = d[category]
            players_with_this_category.append(p)
            if len(players_with_this_category) == 2:
                print("forming group", players_with_this_category)
                print('last_round is', p.participant.vars['last_round'])
                return players_with_this_category


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    """
    These are all variables that depend on a real person's action.
    The options for the demographics survey & the decisions in the game.
    Any variable defined in Player class becomes a new field attached to the player.
    """
    age = models.IntegerField(
        verbose_name='What is your age?',
        min=18, max=100)

    gender = models.StringField(
        choices=['Female', 'Male', 'Other'],
        verbose_name='What gender do you identify as?',
        widget=widgets.RadioSelect)

    income = models.StringField(
        choices=['£9.999 or below', '£10.000 - £29.999', '£30.000 - £49.999',
                 '£50.000 - £69.999', '£70.000 - £89.999', '£90.000 or over', 'Prefer not to say'],
        verbose_name='What is the total combined income of your household?',
        widget=widgets.RadioSelect)

    education = models.StringField(
        choices=['No formal education', 'GCSE or equivalent', 'A-Levels or equivalent', 'Vocational training',
                 'Undergraduate degree', 'Postgraduate degree', 'Prefer not to say'],
        verbose_name='What is the highest level of education you have completed?',
        widget=widgets.RadioSelect)

    ethnicity = models.StringField(
        choices=['Asian/Asian British', 'Black/African/Caribbean/Black British', 'Mixed/Multiple Ethnic groups',
                 'White', 'Other'],
        verbose_name='What is your ethnicity?',
        widget=widgets.RadioSelect)

    decision_high = models.IntegerField(
        choices=[
            [1, f'You pay {Constants.c_high} points in order for Participant 2 to receive {Constants.b_high} points.'],
            [2, 'You pay 0 points in order for Participant 2 to receive 0 points.'],
        ],
        doc="""This player's decision""",
        widget=widgets.RadioSelect
    )

    decision_low = models.IntegerField(
        choices=[
            [3, f'You pay {Constants.c_low} points in order for Participant 2 to receive {Constants.b_low} points.'],
            [4, 'You pay 0 points in order for Participant 2 to receive 0 points.'],
        ],
        doc="""This player's decision""",
        widget=widgets.RadioSelect
    )

    payoff_high = models.CurrencyField()
    payoff_low = models.CurrencyField()
    payment = models.CurrencyField()

    def other_player(self):
        """
        This function is form the prisoner template. It defines who the payoffs are calculated from.
        It uses the otree function get_others_in_group()
        """
        return self.get_others_in_group()[0]

    def set_payoff(self):
        """
        The payoff function layout is from the prisoner template.
        There is one matrix per game using two separate decision variables.
        Bottom lines calculate the payoff based on actual choices, again, one for each game.
        They are added for the round total (self.payment).
        """
        payoff_matrix_high = {
            1:
                {
                    1: Constants.endowment_high + (Constants.b_high - Constants.c_high),
                    2: Constants.endowment_high + (-Constants.c_high)
                },
            2:
                {
                    1: Constants.endowment_high + Constants.b_high,
                    2: Constants.endowment_high + Constants.dd_high
                }
        }
        self.payoff_high = payoff_matrix_high[self.decision_high][self.other_player().decision_high]

        payoff_matrix_low = {
            3:
                {
                    3: Constants.endowment_low + (Constants.b_low - Constants.c_low),
                    4: Constants.endowment_low + (-Constants.c_low)
                },
            4:
                {
                    3: Constants.endowment_low + Constants.b_low,
                    4: Constants.endowment_low + Constants.dd_low
                }
        }

        """
        The payoff variable alone can be used as such if the whole game is in the same app.
        If using multiple apps or setting the payment on another app, then one must use the participant.vars
        I could have written participant.vars = payoff matrix directly,
        but then it means I need to use the participant.vars code everywhere I call the payoff!
        Here only the combined payoffs of the two games together is stored
        """
        self.payoff_low = payoff_matrix_low[self.decision_low][self.other_player().decision_low]
        self.payment = self.payoff_high + self.payoff_low
        self.participant.vars['payment'] = self.payment
        # print('self.payment', self.payment)
        # print('Player ID', self.id_in_group)
