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


def pair_randomly(l):
    """
    This code comes from Ty in my centipede game. it partitions list l into random pairs
    It must be used with the section below in Constants class
    """
    if len(l) < 2:
        return
    return_value = []
    shuffled_l = l[:]
    random.shuffle(shuffled_l)
    for i in range(0, len(shuffled_l), 2):
        return_value.append(shuffled_l[i:i + 2])
    return return_value


class Constants(BaseConstants):
    name_in_url = 'multi_prisoner'
    players_per_group = 2
    num_rounds = 100

    min_rounds = 2
    proba_next_round = 0.5

    currency_per_point = 0.01

    instructions_template = 'multi_prisoner/OldInstructions.html'
    results_previous_round_template = 'multi_prisoner/Results.html'

    """
    if I want to do it with just b, c, and 0 
    b = benefit, c = cost, dd = both defect
    """
    b_high = c(500)
    c_high = c(200)
    dd_high = c(0)

    b_low = c(555)
    c_low = c(222)
    dd_low = c(0)


class Subsession(BaseSubsession):
    """
    This is for the 50% chance of another round. We create a function for clarity below in the creating_session().
    We create a list of different number of rounds that is as long as there are groups.
    """
    def get_random_number_of_rounds(self):
        arbitrary_high_number = 100
        list_num_rounds = []
        for _ in range(arbitrary_high_number):
            number = Constants.min_rounds
            while Constants.proba_next_round < random.random():
                number += 1
            list_num_rounds.append(number)
        return list_num_rounds

    def creating_session(self):
        """
        creating_session is an otree function??
        Here we define the pairing/randomising of participants in this session/game
        And how the treatments need to be assigned to each group.
        Here itertools means 1st pair gets high, 2nd pair low, 3rd pair high, 4th pair low, etc.
        Use get_groups() so that the treatment is assigned to pairs, not individual players, otherwise write get_players()
        Don't forget to set group_like_round(1) if you want them to keep the same opponent!
        """
        if self.round_number == 1:
            all_players = []
            for g in self.get_groups():
                all_players.extend(g.get_players())

            group_matrix = []
            group_matrix.extend(pair_randomly(all_players))
            print(all_players)
            print(group_matrix)
            self.group_randomly()  # that's the key bit!

        if self.round_number <= Constants.num_rounds:
            self.group_like_round(1)

            """ random last round code. With the function from above, 
                    we attribute the different elements in the list to each group."""
            if self.round_number == 1:
                list_num_rounds = self.get_random_number_of_rounds()
                group_number_of_rounds = itertools.cycle(list_num_rounds)
                for g in self.get_groups():
                    g.last_round = next(group_number_of_rounds)
                    print('New number of rounds', g.last_round)
            else:
                """ This bit ensures the round number are the same for each rounds rather
                 than generating a new one each time."""
                previous_groups = self.in_previous_rounds()[-1].get_groups()
                for g, previous_g in zip(self.get_groups(), previous_groups):
                    g.last_round = previous_g.last_round
                    print('New number of rounds', g.last_round)


class Group(BaseGroup):
    """Field of the number of rounds. Each group gets attributed a number of rounds"""
    last_round = models.IntegerField()


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
                 'White', 'Prefer not to say'],
        verbose_name='What is your ethnicity?',
        widget=widgets.RadioSelect)

    decision_high = models.IntegerField(
        choices=[
            [1, 'You pay XX points in order for Participant 2 to receive XX points.'],
            [2, 'You pay 0 points in order for Participant 2 to receive 0 points.'],
        ],
        doc="""This player's decision""",
        widget=widgets.RadioSelect
    )
    decision_low = models.IntegerField(
        choices=[
            [3, 'You pay YY points in order for Participant 2 to receive YY points.'],
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
        there is one matrix per game using two separate decision variables.
        Bottom lines calculate the payoff based on actual choices, again, one for each game.
        They are added for the round total.
        """
        payoff_matrix_high = {
            1:
                {
                    1: (Constants.b_high - Constants.c_high),
                    2: -(Constants.c_high)
                },
            2:
                {
                    1: Constants.b_high,
                    2: Constants.dd_high
                }
        }

        payoff_matrix_low = {
            3:
                {
                    3: (Constants.b_low - Constants.c_low),
                    4: -(Constants.c_low)
                },
            4:
                {
                    3: Constants.b_low,
                    4: Constants.dd_low
                }
        }

        """
        The payoff variable alone can be used as such if the whole game is in the same app.
        If using multiple apps or setting hte payment on another app, then one must use the participant.vars
        I could have written participant.vars = payoff matrix directly,
        but then it means I need to use the participant.vars code everywhere I call the payoff!
        Here only the combined payoffs of the two games together is stored
        """
        self.payoff_low = payoff_matrix_low[self.decision_low][self.other_player().decision_low]
        self.payoff_high = payoff_matrix_high[self.decision_high][self.other_player().decision_high]
        self.payment = self.payoff_high + self.payoff_low
        self.participant.vars['payment'] = self.payment
        # print('self.payment', self.payment)
        # print('Player ID', self.id_in_group)