from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

import itertools

author = 'Charlotte'

doc = """
        The instructions and consent for the control treatment.
        I decided to have them in a separate app so that there can be a waiting page at the beginning of the game app
        where participants wait for an opponent to play (online).
        So the pairing cannot happen before then. Hence a separate app.
"""


class Constants(BaseConstants):
    name_in_url = 'introduction_frechette'
    players_per_group = None
    num_rounds = 1
    min_rounds = 20

    session_time = 20
    conversion = '20pts = £0.05'

    """
    Matrix format payoffs
    temptation = betray, sucker = betrayed, reward = both cooperate, punishment = both defect 
    """
    temptation = c(300)
    sucker = c(0)
    reward = c(200)
    punishment = c(100)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass
