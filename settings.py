from os import environ

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = {
    'real_world_currency_per_point': 1/60,
    'participation_fee': 3.00,
    'doc': "",
}

ALLOWED_HOSTS = ['*']

SESSION_CONFIGS = [
    {
        'name': 'crosstalk',
        'display_name': "Crosstalk game",
        'num_demo_participants': 12,
        'app_sequence': ['introduction_cross', 'crosstalk'],
        'use_browser_bots': True
    },
    {
        'name': 'multi_prisoner',
        'display_name': "Multichannel Game",
        'num_demo_participants': 12,
        'app_sequence': ['introduction_multi', 'multi_prisoner'],
        'use_browser_bots': False
    },
    {
        'name': 'control_PD',
        'display_name': "Control group",
        'num_demo_participants': 12,
        'app_sequence': ['introduction_control', 'control_PD'],
        'use_browser_bots': True
    },
    {
        'name': 'control_PD_test',
        'display_name': "PD fro testing",
        'num_demo_participants': 4,
        'app_sequence': ['introduction_control', 'control_PD_test'],
        'use_browser_bots': True
    },
]
# see the end of this file for the inactive session configs


# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'GBP'
USE_POINTS = True
POINTS_CUSTOM_NAME = ''

ROOMS = [
    {
        'name': 'econ101',
        'display_name': 'Econ 101 class',
        'participant_label_file': '_rooms/econ101.txt',
    },
    {
        'name': 'live_demo',
        'display_name': 'Room for live demo (no participant labels)',
    },
]


# AUTH_LEVEL:
# this setting controls which parts of your site are freely accessible,
# and which are password protected:
# - If it's not set (the default), then the whole site is freely accessible.
# - If you are launching a study and want visitors to only be able to
#   play your app if you provided them with a start link, set it to STUDY.
# - If you would like to put your site online in public demo mode where
#   anybody can play a demo version of your game, but not access the rest
#   of the admin interface, set it to DEMO.

# for flexibility, you can set it in the environment variable OTREE_AUTH_LEVEL
AUTH_LEVEL = environ.get('OTREE_AUTH_LEVEL')

ADMIN_USERNAME = 'charlotte'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')


# Consider '', None, and '0' to be empty/false
# DEBUG = (environ.get('OTREE_PRODUCTION') in {None, '', '0'})
# DEBUG = True
# DEMO_PAGE_INTRO_HTML = """
# Here are various games implemented with
# oTree. These games are open
# source, and you can modify them as you wish.
# """

# don't share this with anybody.
SECRET_KEY = 'q=ig%=7m1hg%*%^_7e9!%xrrdpi!g+i=n7vhn4l%uuw@!6_#w*'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']

# inactive session configs

# dict(
#     name="twopd",
#     display_name="Two simultaneous PD",
#     num_demo_participants=4,
#     app_sequence=['twopd'],
#     use_browser_bots=False
# ),
# {
#     'name': 'finitely_repeated_PD',
#     'display_name': "Fendi PD",
#     'num_demo_participants': 2,
#     'app_sequence': ['finitely_repeated_PD'],
# },
# {
#     'name': 'prisoner',
#     'display_name': "Prisoner's Dilemma",
#     'num_demo_participants': 2,
#     'app_sequence': ['prisoner', 'payment_info'],
# },
# {
#     'name': 'survey',
#     'display_name': "Survey",
#     'num_demo_participants': 1,
#     'app_sequence': ['survey', 'payment_info'],
# },
# {
#     'name': 'quiz',
#     'display_name': "Quiz",
#     'num_demo_participants': 1,
#     'app_sequence': ['quiz'],
# },
# {
#     'name': 'centipede',
#     'display_name': "Baseline Centipede",
#     'num_demo_participants': 2,
#     'app_sequence': ['centipede', 'payment_info'],
# },
# {
#     'name': 'linear_centipede',
#     'display_name': "Linear Centipede",
#     'num_demo_participants': 2,
#     'app_sequence': ['linear_centipede', 'payment_info'],
# },
# {
#     'name': 'zero_centipede',
#     'display_name': "Zero finish Centipede",
#     'num_demo_participants': 2,
#     'app_sequence': ['zero_centipede', 'payment_info'],
# },
# {
#     'name': 'introduction',
#     'display_name': "All together - no chat",
#     'num_demo_participants': 2,
#     'app_sequence': ['introduction', 'centipede', 'centipede_2', 'centipede_3', 'centipede_4', 'centipede_5',
#                      'centipede_6', 'ending_credits'],
# },
# {
#     'name': 'introduction_C',
#     'display_name': "All together with Chat",
#     'num_demo_participants': 2,
#     'app_sequence': ['introduction_C', 'centipede_C', 'centipede_2_C', 'centipede_3_C', 'centipede_4_C',
#                      'centipede_5_C', 'centipede_6_C', 'FRPD_C', 'FRPD_D8_C', 'ending_credits'],
# },
# {
#     'name': 'dictator',
#     'display_name': "Dictator Game",
#     'num_demo_participants': 2,
#     'app_sequence': ['dictator', 'payment_info'],
# },
# {
#     'name': 'public_goods',
#     'display_name': "Public Goods",
#     'num_demo_participants': 3,
#     'app_sequence': ['public_goods', 'payment_info'],
# },
# {
#     'name': 'guess_two_thirds',
#     'display_name': "Guess 2/3 of the Average",
#     'num_demo_participants': 3,
#     'app_sequence': ['guess_two_thirds', 'payment_info'],
# },
