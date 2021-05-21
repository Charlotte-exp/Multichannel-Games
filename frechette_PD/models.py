from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

import random

author = 'Charlotte'

doc = """
        Prisoner's dilemma from Dal bo & Fréchette 2011.
        Random pairing and player id attribution
        Random last round past 20 rounds (50% chance of next round)
        """


class Constants(BaseConstants):
    """
    Here we set our variables that are constants throughout the game.
    We set the number of players in a group, the number of rounds (see subsession), the payoffs for each game.
    """
    name_in_url = 'frechette_PD'
    players_per_group = 2
    num_rounds = 50

    """ variables for randomish end round, used in the intro app at the mo"""
    min_rounds = 20
    proba_next_round = 0.5

    conversion = '20pts = £0.05'

    """
    Matrix format payoffs
    temptation = betray, sucker = betrayed, reward = both cooperate, punishment = both defect 
    """
    temptation = c(30)
    sucker = c(0)
    reward = c(20)
    punishment = c(10)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    """
    These are all variables that depend on a real person's action.
    The options for the demographics survey & the decisions in the game.
    Any variable defined in Player class becomes a new field attached to the player.
    """

    last_round = models.IntegerField()
    left_hanging = models.CurrencyField()[0]

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

    comment_box = models.LongStringField(
        verbose_name=''
    )

    decision = models.IntegerField(
        choices=[
            [1, 'A'],
            [0, 'B'],
        ],
        doc="""This player's decision""",
        widget=widgets.RadioSelect
    )

    def other_player(self):
        return self.get_others_in_group()[0]

    def set_payoff(self):
        payoff_matrix = {
            1:
                {
                    1: Constants.reward,
                    0: Constants.sucker
                },
            0:
                {
                    1: Constants.temptation,
                    0: Constants.punishment
                }
        }
        self.payoff = payoff_matrix[self.decision][self.other_player().decision]

