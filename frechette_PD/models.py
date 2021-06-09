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
    min_rounds = 1
    proba_next_round = 0.5

    conversion = '20pts = £0.05'

    """
    Matrix format payoffs
    temptation = betray, sucker = betrayed, reward = both cooperate, punishment = both defect 
    """
    temptation = c(50)
    sucker = c(12)
    reward = c(32)
    punishment = c(25)


class Subsession(BaseSubsession):

    def get_random_number_of_rounds(self):
        """
        Creating the random-ish number of rounds a group plays for. PP plays for at least 20 rounds (set on constants),
        then they have a 50% chance of another round, and then again 50% chance of another round.
        This function creates a last round number following this method.
        """
        number_of_rounds = Constants.min_rounds
        while Constants.proba_next_round < random.random():
            number_of_rounds += 1
        return number_of_rounds

    def group_by_arrival_time_method(subsession, waiting_players):
        players = [p for p in waiting_players]
        if len(waiting_players) >= 2:
            players = [players[0], players[1]]
            last_round = subsession.get_random_number_of_rounds()
            for p in players:
                p.participant.vars['last_round'] = last_round
                p.last_round = p.participant.vars['last_round']
            return players


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    """
    These are all variables that depend on a real person's action.
    The options for the demographics survey & the decisions in the game.
    Any variable defined in Player class becomes a new field attached to the player.
    """

    last_round = models.IntegerField()
    left_hanging = models.CurrencyField()

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
            [1, '1'],
            [0, '2'],
        ],
        doc="""This player's decision""",
        widget=widgets.RadioSelect
    )

    def get_opponent(self):
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
        self.payoff = payoff_matrix[self.decision][self.get_opponent().decision]

