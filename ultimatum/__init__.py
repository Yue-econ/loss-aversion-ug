from otree.api import *

doc = """
Part 1 - Ultimatum game.
Participants in the room are randomly paired. Person A proposes how to split $10;
Person B accepts or rejects. If B rejects, both earn $0.
Outcome feedback is withheld until the final payment page (after Part 2),
so Part 1 results cannot affect Part 2 choices.
"""


class C(BaseConstants):
    NAME_IN_URL = 'ultimatum'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1
    PIE = 10
    A_ROLE = 'Person A'   # id_in_group 1 = proposer
    B_ROLE = 'Person B'   # id_in_group 2 = responder


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    # Random pairing AND random role (role follows random id_in_group)
    subsession.group_randomly()


class Group(BaseGroup):
    offer = models.IntegerField(
        min=0, max=C.PIE,
        label="How many dollars (out of $10) do you offer to Person B?",
    )
    accepted = models.BooleanField(
        choices=[[True, 'Accept'], [False, 'Reject']],
        widget=widgets.RadioSelectHorizontal,
        label="Do you accept or reject Person A's offer?",
    )


class Player(BasePlayer):
    student_name = models.StringField(label="Please enter your full name (as on the class roster):")
    # filled in after the game, so each row of the export is self-explanatory
    my_role = models.StringField()
    partner_name = models.StringField()
    offer_to_B = models.IntegerField()
    B_decision = models.StringField()


def set_payoffs(group: Group):
    a = group.get_player_by_role(C.A_ROLE)
    b = group.get_player_by_role(C.B_ROLE)
    if group.accepted:
        a.payoff = cu(C.PIE - group.offer)
        b.payoff = cu(group.offer)
    else:
        a.payoff = cu(0)
        b.payoff = cu(0)
    for p, partner in ((a, b), (b, a)):
        p.my_role = p.role
        p.partner_name = partner.field_maybe_none('student_name')
        p.offer_to_B = group.offer
        p.B_decision = 'Accept' if group.accepted else 'Reject'
        pp = p.participant
        pp.ug_role = p.role
        pp.ug_offer = group.offer
        pp.ug_accepted = group.accepted
        pp.ug_payoff = p.payoff


def custom_export(players):
    """One row per pair. Data -> 'ultimatum' custom export."""
    yield ['session', 'pair_id', 'A_name', 'B_name', 'offer_to_B', 'A_keeps',
           'B_decision', 'A_payoff', 'B_payoff']
    for p in players:
        if p.role != C.A_ROLE:
            continue
        g = p.group
        b = g.get_player_by_role(C.B_ROLE)
        offer = g.field_maybe_none('offer')
        acc = g.field_maybe_none('accepted')
        yield [
            p.session.code, g.id_in_subsession,
            p.field_maybe_none('student_name'), b.field_maybe_none('student_name'),
            offer, None if offer is None else C.PIE - offer,
            None if acc is None else ('Accept' if acc else 'Reject'),
            p.payoff, b.payoff,
        ]


# ---------------- PAGES ----------------
class Name(Page):
    form_model = 'player'
    form_fields = ['student_name']

    @staticmethod
    def error_message(player: Player, values):
        if len(values['student_name'].strip()) < 2:
            return "Please enter your full name."

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        name = player.student_name.strip()
        player.participant.student_name = name
        player.participant.label = name   # shows in admin Monitor & Payments tabs


class Intro(Page):
    pass


class Offer(Page):
    form_model = 'group'
    form_fields = ['offer']

    @staticmethod
    def is_displayed(player: Player):
        return player.role == C.A_ROLE


class WaitForOffer(WaitPage):
    body_text = "Please wait while the other participant makes a decision."


class Respond(Page):
    form_model = 'group'
    form_fields = ['accepted']

    @staticmethod
    def is_displayed(player: Player):
        return player.role == C.B_ROLE

    @staticmethod
    def vars_for_template(player: Player):
        return dict(a_keeps=C.PIE - player.group.offer)


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs
    body_text = "Please wait while the other participant makes a decision."


page_sequence = [Name, Intro, Offer, WaitForOffer, Respond, ResultsWaitPage]
