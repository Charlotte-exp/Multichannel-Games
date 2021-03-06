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
    name_in_url = 'introduction_control'
    players_per_group = None
    num_rounds = 1
    min_rounds = 20

    session_time = 20
    conversion = '20pts = £0.05'

    """
    Donation game payoff
    """
    b_high = c(20)
    c_high = c(10)
    dd_high = c(0)
    endowment_high = c_high

    b_low = c(15)
    c_low = c(10)
    dd_low = c(0)
    endowment_low = c_low

    sucker_high = -c_high
    temptation_high = b_high
    reward_high = b_high - c_high

    sucker_low = -c_low
    temptation_low = b_low
    reward_low = b_low - c_low


class Subsession(BaseSubsession):
    """
    Here we create the session with high and low treatments assigned to players as a subgroup. It must be done before
    proper pairing at the waitpage so that pp see the correct payoff in the instructions.
    """

    def creating_session(self):
        """
        AWe use itertools to assign treatment regularly to make sure there is a somewhat equal amount of each in the
        session but also that is it equally distributed in the sample. (So pp don't have to wait to long get matched
        in a pair. It simply cycles through the list of treatments (high & low) and that's saved in the participant vars.
        """

        self.session.vars['conversion'] = Constants.conversion

        self.session.vars['b_high'] = Constants.b_high
        self.session.vars['c_high'] = Constants.c_high
        self.session.vars['endowment_high'] = Constants.endowment_high

        self.session.vars['b_low'] = Constants.b_low
        self.session.vars['c_low'] = Constants.c_low
        self.session.vars['endowment_low'] = Constants.endowment_low

        treatments = itertools.cycle(['high', 'low'])
        for p in self.get_players():
            p.subgroup = next(treatments)
            p.participant.vars['subgroup'] = p.subgroup
            # print('subgroup is', p.subgroup)
            # print('vars subgroup is', p.participant.vars['subgroup'])


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    """
    These are all variables that depend on a real person's action.
    The options for the demographics survey & the decisions in the game.
    Any variable defined in Player class becomes a new field attached to the player, including the subgroup.
    Variables for the f-string are from vars for template in pages.py (since they need to match)
    """

    subgroup = models.StringField()

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

    q3a = models.IntegerField(
        choices=[
            [1, 'You will earn 0 pts.'],
            [2, f'You will earn {Constants.c_high} pts.'],
            [3, f'You will earn {Constants.b_high} pts.']
        ],
        verbose_name=f'What amount will you receive from Participant 2 '
                     f'if they choose to pay {Constants.c_high} pts',
        widget=widgets.RadioSelect
    )

    q3b = models.IntegerField(
        choices=[
            [1, 'You will earn 0 pts.'],
            [2, f'You will earn {Constants.c_low} pts.'],
            [3, f'You will earn {Constants.b_low} pts.']
        ],
        verbose_name=f'What amount will you receive from Participant 2 '
                     f'if they choose to pay {Constants.c_low} pts',
        widget=widgets.RadioSelect
    )

    q4 = models.IntegerField(
        choices=[
            [1, '10%'],
            [2, '50%'],
            [3, '100%']
        ],
        verbose_name=f'What are the chances that there will be another round after the {Constants.min_rounds}th round?',
        widget=widgets.RadioSelect
    )
    # put these as one??
    q5 = models.IntegerField(
        choices=[
            [1, '10%'],
            [2, '50%'],
            [3, '100%']
        ],
        verbose_name=f'What are the chances that there will be another round after the {Constants.min_rounds + 1}th round?',
        widget=widgets.RadioSelect
    )

    q6h = models.IntegerField(
        choices=[
            [1, f'{Constants.sucker_high} points'],
            [2, '0 points'],
            [3, f'{Constants.b_high} points']
        ],
        verbose_name='In Example 1, how many points did Participant 1 earn?',
        widget=widgets.RadioSelect
    )

    q7h = models.IntegerField(
        choices=[
            [1, '0 points'],
            [2, f'{Constants.c_high} points'],
            [3, f'{Constants.temptation_high} points']
        ],
        verbose_name='In Example 1, how many points did Participant 2 earn?',
        widget=widgets.RadioSelect
    )

    q8h = models.IntegerField(
        choices=[
            [1, f'{Constants.sucker_high} points'],
            [2, f'{Constants.reward_high} points'],
            [3, f'{Constants.b_high} points']
        ],
        verbose_name='In Example 2, how many points did Participant 2 earn?',
        widget=widgets.RadioSelect
    )

    q6l = models.IntegerField(
        choices=[
            [1, f'{Constants.sucker_low} points'],
            [2, '0 points'],
            [3, f'{Constants.b_low} points']
        ],
        verbose_name='In Example 1, how many points did Participant 1 earn?',
        widget=widgets.RadioSelect
    )

    q7l = models.IntegerField(
        choices=[
            [1, '0 points'],
            [2, f'{Constants.c_low} points'],
            [3, f'{Constants.temptation_low} points']
        ],
        verbose_name='In Example 1, how many points did Participant 2 earn?',
        widget=widgets.RadioSelect
    )

    q8l = models.IntegerField(
        choices=[
            [1, f'{Constants.sucker_low} points'],
            [2, f'{Constants.reward_low} points'],
            [3, f'{Constants.b_low} points']
        ],
        verbose_name='In Example 2, how many points did Participant 2 earn?',
        widget=widgets.RadioSelect
    )
