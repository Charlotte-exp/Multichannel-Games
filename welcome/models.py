from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
)


author = 'Charlotte 2020'

doc = """
Start of the multi channel games
"""


class Constants(BaseConstants):
    name_in_url = 'welcome'
    players_per_group = 2
    num_rounds = 1

#    instructions_template = 'introduction/OldInstructions.html'

#    ECU = .01

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    age = models.IntegerField(
        verbose_name='What is your age?',
        min=18, max=100)

    gender = models.StringField(
        choices=['Male', 'Female', 'Other'],
        verbose_name='What is your gender?',
        widget=widgets.RadioSelect)