from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

import sentry_sdk
sentry_sdk.init(
    "https://819cca3e1a814e2ea459091cb3787cb8@o493514.ingest.sentry.io/5562864",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
)

import random
import itertools

author = 'Charlotte'

doc = """
        The instructions and consent for the Crosstalk treatment.
        I decided to have them in a separate app so that there can be a waiting page at the beginning of the game app
        where participants wait for an opponent to play (online).
        So the pairing cannot happen before then. Hence a separate app.
"""


class Constants(BaseConstants):
    name_in_url = 'introduction_cross'
    players_per_group = 4
    num_rounds = 1

    """variables for randomish next round"""
    min_rounds = 20
    proba_next_round = 0.5

    currency_per_point = 0.6  # 60pts is £1
    pounds_per_points = currency_per_point * 100

    """
    Donation game payoff
    """
    b_high = c(5)
    c_high = c(1)
    dd_high = c(0)
    endowment_high = c_high

    b_low = c(2)
    c_low = c(1)
    dd_low = c(0)
    endowment_low = c_low

    reward_low = endowment_low + b_low - c_low
    temptation_high = endowment_high + b_high
    sucker_high = endowment_high - c_high


class Subsession(BaseSubsession):
    """
        This is for the 50% chance of another round. We create a function for clarity below in the creating_session().
        We create a list of different number of rounds that is as long as there are groups.
    """
    def get_random_number_of_rounds(self):
        num_groups = int(self.session.num_participants / 2)
        list_num_rounds = []
        for _ in range(num_groups):
            number = Constants.min_rounds
            while Constants.proba_next_round < random.random():
                number += 1
            list_num_rounds.append(number)
        return list_num_rounds

    def creating_session(self):
        """ random last round code. With the function from above,
                we attribute the different elements in the list to each group."""
        list_num_rounds = self.get_random_number_of_rounds()
        group_number_of_rounds = itertools.cycle(list_num_rounds)
        for g in self.get_groups():
            g.last_round = next(group_number_of_rounds)
            print('New number of rounds', g.last_round)
        for p in self.get_players():
            p.participant.vars['last_round'] = p.group.last_round
            print('vars last_round is', p.participant.vars['last_round'])


class Group(BaseGroup):
    """Field of the number of rounds. Each group gets attributed a number of rounds"""
    last_round = models.IntegerField()


class Player(BasePlayer):
    """ These are all variables that depend on a real person's action.
        The options for the demographics survey & the decisions in the game.
        Any variable defined in Player class becomes a new field attached to the player.
        Variables for the f-string are from vars for template in pages.py (since they need to match)
    """

    q1 = models.IntegerField(
        choices=[
            [1, '0 other participants'],
            [2, '1 other participant'],
            [3, '2 other participants']
        ],
        verbose_name='With how many other participant(s) will you be interacting in this study?',
        widget=widgets.RadioSelect
    )

    q2 = models.IntegerField(
        choices=[
            [1, 'There is no bonus possible in this study.'],
            [2, 'My bonus payment depends only on my decisions.'],
            [3, 'My bonus payment depends on my decision and the decision of the other participants.']
        ],
        verbose_name='What will your bonus payment depend on?',
        widget=widgets.RadioSelect
    )

    q3 = models.IntegerField(
        choices=[
            [1, 'You will earn 0 pts.'],
            [2, f'You will earn {Constants.b_high} pts.'],
            [3, 'You will earn 10 pts.']
        ],
        verbose_name=f'In Task A, what amount will you receive from Participant 2 '
                     f'if they choose to pay {Constants.c_high} pts',
        widget=widgets.RadioSelect
    )

    q4 = models.IntegerField(
        choices=[
            [1, '10%'],
            [2, '50%'],
            [3, '100%']
        ],
        verbose_name='What are the chances that there will be another round after the 20th round?',
        widget=widgets.RadioSelect
    )
    # put these as one??
    q5 = models.IntegerField(
        choices=[
            [1, '10%'],
            [2, '50%'],
            [3, '100%']
        ],
        verbose_name='What are the chances that there will be another round after the 21st round?',
        widget=widgets.RadioSelect
    )

    q6 = models.IntegerField(
        choices=[
            [1, '0 points'],
            [2, f'{Constants.sucker_high+Constants.reward_low} points'],
            [3, '10 points']
        ],
        verbose_name='Across both tasks, how many points did Participant 1 earn in total?',
        widget=widgets.RadioSelect
    )

    q7 = models.IntegerField(
        choices=[
            [1, '0 points'],
            [2, '3 points'],
            [3, f'{Constants.temptation_high} points']
        ],
        verbose_name='In Task A, how many points did Participant 2 earn?',
        widget=widgets.RadioSelect
    )

    q8 = models.IntegerField(
        choices=[
            [1, '0 points'],
            [2, '1 points'],
            [3, f'{Constants.reward_low} points']
        ],
        verbose_name='In Task B, how many points did Participant 3 earn?',
        widget=widgets.RadioSelect
    )
