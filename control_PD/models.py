from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

import random

author = 'Charlotte'

doc = """
        Prisoner's dilemma/donation game between two players with two possible payoffs, low and high cooperation.
        Random pairing and player id attribution
        Random last round past 20 rounds (50% chance of next round)
        Two payoff matrices for one game display, depending on treatment group assignement.
        
        You can also use cmd+/ to comment out an entire section!!
        """


class Constants(BaseConstants):
    name_in_url = 'control_PD'
    players_per_group = 4
    num_rounds = 50

    """ variables for randomish end round, used in the intro app at the mo"""
    min_rounds = 2
    proba_next_round = 0.5

    conversion = '20pts = £0.05'

    """
    Donation game payoffs
    b = benefit, c = cost, dd = both defect
    """
    b_high = c(20)
    c_high = c(10)
    dd_high = c(0)
    endowment_high = c_high

    b_low = c(15)
    c_low = c(10)
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
        high_players = [p for p in waiting_players if p.participant.vars['subgroup'] == 'high']
        low_players = [p for p in waiting_players if p.participant.vars['subgroup'] == 'low']
        if len(high_players) >= 2 and len(low_players) >= 2:
            players = [high_players[0], high_players[1], low_players[0], low_players[1]]
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

    decision_high = models.IntegerField(
        choices=[
            [1, f'You lose {Constants.c_high} pts for Participant 2 to receive {Constants.b_high} pts.'],
            [0, 'You lose 0 pts for Participant 2 to receive 0 pts.'],
        ],
        doc="""This player's decision""",
        widget=widgets.RadioSelect
    )

    decision_low = models.IntegerField(
        choices=[
            [1, f'You lose {Constants.c_low} pts for Participant 2 to receive {Constants.b_low} pts.'],
            [0, 'You lose 0 pts for Participant 2 to receive 0 pts.'],
        ],
        doc="""This player's decision""",
        widget=widgets.RadioSelect
    )

    def get_opponent(self):
        """
        Since we have 4 players in a group but only want pairs to play each other, we need our own custom function
        to assign the correct opponent to the correct player. Hence we cannot just use get_others_in_group()
        as there are 3 possible opponents and we want just one.
        We create a dictionary (matches) that matches the correct opponent with each player.
        We create a list of all the possible opponents in the group (so 3 players without oneself).
        Then for each player, we pick the matching opponents from the dic and the 3 other players,
        and the id that match in both lists make the new opponents list.
        """
        matches = {1: [2], 2: [1], 3: [4], 4: [3]}
        list_opponents = self.get_others_in_group()
        # print(self.get_others_in_group())
        # print(self.id_in_group)
        opponent = []
        for opponent_id in matches[self.id_in_group]:  # picks the two opponents from the matches dict
            for other_player in list_opponents:  #
                if other_player.id_in_group == opponent_id:
                    opponent.append(other_player)
        return opponent

    def set_payoff(self):
        """
        The payoff function layout is from the prisoner template. There is one matrix per game using two separate
        decision variables. Participant get one or the other matrix based on subgroup.
        Bottom lines calculate the payoff based on actual choices depending on subgroup.
        There is only one payoff for control. The opponent variables need to match our new set_opponent function.
        """
        opponent = self.get_opponent()
        # print([opponent.id_in_group for opponent in opponents])
        if self.participant.vars['subgroup'] == 'high':
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
            self.payoff = payoff_matrix_high[self.decision_high][opponent[0].decision_high]
            # print('payoff is', self.payoff)

        if self.participant.vars['subgroup'] == 'low':
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
            self.payoff = payoff_matrix_low[self.decision_low][opponent[0].decision_low]
            # print('payoff is', self.payoff)
