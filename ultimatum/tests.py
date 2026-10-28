from otree.api import Bot, SubmissionMustFail
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Intro
        if self.player.role == C.A_ROLE:
            yield SubmissionMustFail(Offer, dict(offer=11))
            yield Offer, dict(offer=4)
        else:
            yield Respond, dict(accepted=True)
