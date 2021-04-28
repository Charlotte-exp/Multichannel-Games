from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

import random

author = 'Charlotte'

doc = """
        Two simultaneous Prisoner's dilemma/donation game between four players, with two different payoffs.
        For the pairings with two opponents to work, the app uses a four player structure, 
        but one players plays each game against two different other players. 
        Random last round past 20 rounds (50% chance of next round).
        Waitpage assigning the round numbers and pairing by arrival time, with a waiting time limited to 5min thanks to 
        a javascript.
        """


class Constants(BaseConstants):
    """
    Here we set our variables that are constants throughout the game.
    We set the number of players in a group, the number of rounds (see subsession), the payoffs for each game.
    """
    name_in_url = 'crosstalk'
    players_per_group = 4
    num_rounds = 50

    """variables for random-ish last round, mechanics in subsession below"""
    min_rounds = 20
    proba_next_round = 0.5

    conversion = '15pts = £0.20'

    """
    Donation game payoffs
    b = benefit, c = cost, dd = both defect
    """
    b_high = c(4)
    c_high = c(2)
    dd_high = c(0)
    endowment_high = c_high

    b_low = c(3)
    c_low = c(2)
    dd_low = c(0)
    endowment_low = c_low

    """Without endowment!! (for the round results)"""
    sucker_high = -c_high
    temptation_high = b_high
    reward_high = b_high - c_high

    sucker_low = -c_low
    temptation_low = b_low
    reward_low = b_low - c_low


class Subsession(BaseSubsession):
    """
    Instead of creating_session() we need to use group_by_arrival_time_method().
    The function makes sure that only high players play with high players.
    I could only implement that retroactively though and assign treatment in the intro app.
    The inconveninent is that if 3 people read the instructions, 2 become high and 1 becomes low,
    if one of the high one gives and quits the other two cannot play together.
    """

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
        """
        Using the number generated above, it is assigned to each participants in newly formed group when they are
        in the waitroom. This function is from oTree but had to be tweaked with a little to allow to assign a variable
        after the group is formed rather than group the players based on a pre-assigned variable.
        We form the group of four here rather than let group_by_arrival_time do it automatically (with the Constants)
        """
        if len(waiting_players) >= Constants.players_per_group:
            players = [p for _, p in zip(range(4), waiting_players)]
            last_round = subsession.get_random_number_of_rounds()
            for p in players:
                p.participant.vars['last_round'] = last_round
                p.last_round = p.participant.vars['last_round']  # p.vars do not appear in the data put player vars do.
            return players


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    """
    These are all variables that depend on a real person's action.
    The options for the demographics survey & the decisions in the game.
    The last_round variable field is here too.
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

    decision_high = models.IntegerField(
        choices=[
            [1, f'You lose {Constants.c_high} pts for Participant 2 to receive {Constants.b_high} pts.'],
            [0, 'You pay 0 pts for Participant 2 to receive 0 pts.'],
        ],
        doc="""This player's decision""",
        widget=widgets.RadioSelect
    )

    decision_low = models.IntegerField(
        choices=[
            [1, f'You lose {Constants.c_low} pts for Participant 3 to receive {Constants.b_low} pts.'],
            [0, 'You pay 0 pts for Participant 3 to receive 0 pts.'],
        ],
        doc="""This player's decision""",
        widget=widgets.RadioSelect
    )

    payoff_high = models.CurrencyField()
    payoff_low = models.CurrencyField()
    total_payoff = models.CurrencyField()

    def get_opponent(self):
        """
        We need our own custom function to assign the correct opponent to the correct player. Hence we cannot just use
        get_others_in_group() as there are 3 possible opponents and we want 2.
        We create a dictionary (matches) that matches the correct two opponents IN THE RIGHT ORDER with each player.
        We create a list of all the possible opponents in the group (so 3 players without oneself).
        Then for each player, we pick the matching opponents from the dic and the 3 other players,
        and the two id that match in both lists make the new opponents list.
        """
        matches = {1: [2, 4], 2: [1, 3], 3: [4, 2], 4: [3, 1]}
        list_opponents = self.get_others_in_group()
        #print(self.get_others_in_group())
        #print(self.id_in_group)
        opponents = []
        # print(self.get_opponent)
        for opponent_id in matches[self.id_in_group]:
            for opponent in list_opponents:
                # print(opponent.participant.vars['last_round'])
                if opponent.id_in_group == opponent_id:
                    opponents.append(opponent)
        return opponents

    def set_payoffs(self):
        """
        The payoff function layout is from the prisoner template. There is one matrix per game using two separate
        decision variables. Bottom lines calculate the payoff based on actual choices, again, one for each game.
        They are added for the round total (self.total_payoff). The opponent variables need to match our new
        set_opponent function. Because order matters, for the high payoff it is always the first element [0]
        in the opponents vector, and for the low payoff it is always teh second element [1] in the opponents vector.
        (elements here is the player id in the list).
        """
        opponents = self.get_opponent()
        # print([opponent.id_in_group for opponent in opponents])
        payoff_matrix_high = {
            1:
                {
                    1: Constants.endowment_high + (Constants.b_high - Constants.c_high),
                    0: Constants.endowment_high + (-Constants.c_high)
                },
            0:
                {
                    1: Constants.endowment_high + Constants.b_high,
                    0: Constants.endowment_high + Constants.dd_high
                }
        }
        self.payoff_high = payoff_matrix_high[self.decision_high][opponents[0].decision_high]
        # print(self.decision_high)

        payoff_matrix_low = {
            1:
                {
                    1: Constants.endowment_low + (Constants.b_low - Constants.c_low),
                    0: Constants.endowment_low + (-Constants.c_low)
                },
            0:
                {
                    1: Constants.endowment_low + Constants.b_low,
                    0: Constants.endowment_low + Constants.dd_low
                }
        }
        self.payoff_low = payoff_matrix_low[self.decision_low][opponents[1].decision_low]
        # print(self.decision_low)
        self.total_payoff = self.payoff_high + self.payoff_low
        self.payoff = self.payoff_high + self.payoff_low
        # print('self.payment', self.payment)
        # print('Player ID', self.id_in_group)