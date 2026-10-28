from otree.api import *
import random

doc = """
Part 2 - Loss aversion (Gächter, Johnson & Herrmann-style mixed lotteries).
Six 50/50 coin-flip lotteries: heads = lose L, tails = win $3; L = 1, 1.5, ..., 3.5.
Choices are forced to be monotone (single switch from Accept to Reject):
  - client side: choosing Reject on row k auto-sets all later rows to Reject;
                 choosing Accept on row k auto-sets all earlier rows to Accept;
  - server side: error_message() rejects any Reject-then-Accept pattern.
One lottery is drawn at random for payment.
"""


class C(BaseConstants):
    NAME_IN_URL = 'loss_aversion'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    WIN = cu(3)
    LOSSES = [cu(1), cu(1.5), cu(2), cu(2.5), cu(3), cu(3.5)]
    N = 6


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


def lottery_field(i):
    return models.IntegerField(
        choices=[[1, 'Accept'], [0, 'Reject']],
        widget=widgets.RadioSelectHorizontal,
        label=f"Lottery {i}",
    )


class Player(BasePlayer):
    lottery_1 = lottery_field(1)
    lottery_2 = lottery_field(2)
    lottery_3 = lottery_field(3)
    lottery_4 = lottery_field(4)
    lottery_5 = lottery_field(5)
    lottery_6 = lottery_field(6)
    # first lottery rejected (1..6); 7 = accepted all. Main loss-aversion measure.
    switch_point = models.IntegerField()
    num_accepted = models.IntegerField()
    paid_lottery = models.IntegerField()
    coin = models.StringField()          # 'Heads' or 'Tails'
    paid_accepted = models.BooleanField()


FIELDS = [f'lottery_{i}' for i in range(1, C.N + 1)]


# ---------------- PAGES ----------------
class Decide(Page):
    form_model = 'player'
    form_fields = FIELDS

    @staticmethod
    def vars_for_template(player: Player):
        return dict(rows=[dict(idx=i + 1, loss=C.LOSSES[i]) for i in range(C.N)])

    @staticmethod
    def error_message(player: Player, values):
        choices = [values[f] for f in FIELDS]
        for k in range(C.N - 1):
            if choices[k] == 0 and choices[k + 1] == 1:
                return ("Once you choose \"Reject\" for a lottery, you must choose "
                        "\"Reject\" for all later lotteries.")

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        choices = [getattr(player, f) for f in FIELDS]
        player.num_accepted = sum(choices)
        player.switch_point = choices.index(0) + 1 if 0 in choices else C.N + 1

        k = random.randint(1, C.N)
        player.paid_lottery = k
        player.coin = random.choice(['Heads', 'Tails'])
        player.paid_accepted = bool(choices[k - 1])
        if not player.paid_accepted:
            player.payoff = cu(0)
        elif player.coin == 'Heads':
            player.payoff = -C.LOSSES[k - 1]
        else:
            player.payoff = C.WIN


class Payment(Page):
    @staticmethod
    def vars_for_template(player: Player):
        pp = player.participant
        return dict(
            student_name=pp.student_name,
            ug_role=pp.ug_role,
            ug_offer=pp.ug_offer,
            ug_a_keeps=10 - pp.ug_offer,
            ug_accepted=pp.ug_accepted,
            ug_payoff=pp.ug_payoff,
            paid_loss=C.LOSSES[player.paid_lottery - 1],
            fee=player.session.config['participation_fee'],
            total=pp.payoff_plus_participation_fee(),
        )


page_sequence = [Decide, Payment]
