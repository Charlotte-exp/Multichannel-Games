from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

import random
import itertools

author = 'Charlotte'

doc = """
        The instructions and consent for the multichannel treatment.
        I decided to have them in a separate app so that there can be a waiting page at the beginning of the game app
        where participants wait for an opponent to play (online).
        So the pairing cannot happen before then. Hence a separate app.
"""


class Constants(BaseConstants):
    name_in_url = 'introduction_multi'
    players_per_group = None
    num_rounds = 1

    currency_per_point = 60

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
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    """
        These are all variables that depend on a real person's action.
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
            [3, 'My bonus payment depends on my decision and the decision of the other participant.']
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
        verbose_name='What are the chances that there will be another round after the 21th round?',
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
        verbose_name='In Task B, how many points did Participant 2 earn?',
        widget=widgets.RadioSelect
    )
