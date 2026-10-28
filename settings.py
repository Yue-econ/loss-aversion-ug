from os import environ

SESSION_CONFIGS = [
    dict(
        name='ug_loss_aversion',
        display_name='Part 1: Ultimatum game  ->  Part 2: Loss aversion',
        app_sequence=['ultimatum', 'loss_aversion'],
        num_demo_participants=2,  # must be EVEN in the lab (pairs)
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    # Show-up fee. Keep >= $3.50 so the worst Part 2 outcome (-$3.50)
    # combined with $0 in Part 1 never makes total pay negative.
    participation_fee=0.00,
    doc="",
)

PARTICIPANT_FIELDS = ['student_name', 'ug_role', 'ug_offer', 'ug_accepted', 'ug_payoff']
SESSION_FIELDS = []

ROOMS = [dict(name='econlab', display_name='Econ Lab')]

LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = False
REAL_WORLD_CURRENCY_DECIMAL_PLACES = 2

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = ""
SECRET_KEY = '7718046294361'
INSTALLED_APPS = ['otree']
