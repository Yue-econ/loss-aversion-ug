from otree.api import Bot, SubmissionMustFail, expect
from . import *


class PlayerBot(Bot):
    def play_round(self):
        # Reject-then-Accept must be blocked by the server
        yield SubmissionMustFail(Decide, dict(
            lottery_1=1, lottery_2=0, lottery_3=1, lottery_4=0, lottery_5=0, lottery_6=0))
        # Consistent: accept 1-3, reject 4-6 -> switch point 4
        yield Decide, dict(
            lottery_1=1, lottery_2=1, lottery_3=1, lottery_4=0, lottery_5=0, lottery_6=0)
        expect(self.player.switch_point, 4)
        expect(self.player.num_accepted, 3)
        yield Payment
