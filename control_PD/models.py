from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

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
    players_per_group = 2
    num_rounds = 50

    min_rounds = 5
    proba_next_round = 0.5

    currency_per_point = 0.01  # I think... if 100pts is £1

    """
    Donation game payoff matrix
    """
    b_high = c(5)
    c_high = c(1)
    dd_high = c(0)
    endowment_high = c_high

    b_low = c(2)
    c_low = c(1)
    dd_low = c(0)
    endowment_low = c_low


class Subsession(BaseSubsession):
    """
       Instead of creating_session() we need to use group_by_arrival_time_method().
       The function makes sure that only high players play with high players.
       I could only implement that retroactively though and assign treatment in the intro app.
       The inconveninent is that if 3 people read the instructions, 2 become high and 1 becomes low,
       if one of the high one gives and quits the other two cannot play together.
    """
    def group_by_arrival_time_method(self, waiting_players):
        print("starting group_by_arrival_time_method")
        from collections import defaultdict
        d = defaultdict(list)
        for p in waiting_players:
            category = p.participant.vars['treatment']
            players_with_this_category = d[category]
            players_with_this_category.append(p)
            if len(players_with_this_category) == 2:
                print("forming group...")
                return players_with_this_category
        for p in waiting_players:
            category = p.participant.vars['last_round']
            players_with_this_category = d[category]
            players_with_this_category.append(p)
            if len(players_with_this_category) == 2:
                print("forming group", players_with_this_category)
                print('last_round is', p.participant.vars['last_round'])
                return players_with_this_category

# Can this be merged?


class Group(BaseGroup):
    pass


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
                 'White', 'Other'],
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

    def other_player(self):
        """ This function is form the prisoner template. It defines who the payoffs are calculated from.
            It uses the otree function get_others_in_group() """
        return self.get_others_in_group()[0]

    def set_payoff(self):
        """ The payoff function layout is from the prisoner template.
            there is one matrix per treatment using two one decision variable.
            Bottom lines calculate the payoff based on actual choices,.
            The if statement contains .group because the treatment variable is defined in group.
            If defined in player it is not needed. """
        if self.participant.vars['treatment'] == 'high':
            payoff_matrix_high = {
                1:
                    {
                        1: Constants.endowment_high + (Constants.b_high - Constants.c_high),
                        2: Constants.endowment_high + (-Constants.c_high)
                    },
                2:
                    {
                        1: Constants.endowment_high + Constants.b_high,
                        2: Constants.endowment_high + Constants.dd_high
                    }
            }
            self.payoff = payoff_matrix_high[self.decision_high][self.other_player().decision_high]
            self.participant.vars['payment'] = self.payoff
            # print('payoff is', self.payoff)
            # print('vars payoff is', self.participant.vars['payment'])

        elif self.participant.vars['treatment'] == 'low':
            payoff_matrix_low = {
                3:
                    {
                        3: Constants.endowment_low + (Constants.b_low - Constants.c_low),
                        4: Constants.endowment_low + (-Constants.c_low)
                    },
                4:
                    {
                        3: Constants.endowment_low + Constants.b_low,
                        4: Constants.endowment_low + Constants.dd_low
                    }
            }
            """
            The payoff variable alone can be used as such if the whole game is in the same app.
            If using multiple apps or setting hte payment on another app, then one must use the participant.vars
            I could have written participant.vars = payoff matrix directly,
            but then it means I need to use the participant.vars code everywhere I call the payoff!
            """
            self.payoff = payoff_matrix_low[self.decision_low][self.other_player().decision_low]
            self.participant.vars['payment'] = self.payoff
            # print('payoff is', self.payoff)
            # print('vars payoff is', self.participant.vars['payment'])

        # print('treatment is', self.group.treatment)
        # print('Player ID', self.id_in_group) # I need participant ID to check the random pairing is working
