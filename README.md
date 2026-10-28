# Ultimatum Game + Loss Aversion (oTree)

In-class experiment in two parts, run in one oTree session (`ug_loss_aversion`).

## Design

**Start: Name.** Each student enters their name. It is saved as `student_name` and shown as the participant label in the admin pages. Other participants never see it.

**Part 1: Ultimatum game** (app: `ultimatum`)
- Everyone in the room is randomly paired, and roles within each pair are random.
- Person A splits $10 and offers Person B a whole-dollar amount from $0 to $10.
- Person B accepts or rejects. If B accepts, B gets the offer and A keeps the rest. If B rejects, both get $0.
- Played once. Nobody sees the outcome until the final page, so Part 1 results can't affect Part 2 choices.

**Part 2: Loss aversion** (app: `loss_aversion`)
- Six 50/50 coin-flip lotteries. Tails wins $3. Heads loses $1, $1.50, $2, $2.50, $3 or $3.50 (Lotteries 1–6).
- For each lottery the student chooses Accept or Reject. Reject pays $0 for sure.
- **Choices must be consistent:** once a student rejects a lottery, every later lottery is also a reject.
  - In the browser, choosing Reject on a lottery automatically sets all later lotteries to Reject, and choosing Accept automatically sets all earlier lotteries to Accept.
  - On the server, any Reject followed by an Accept is refused with an error message. This covers students with JavaScript turned off.
- One lottery is drawn at random and a coin is flipped to determine the Part 2 payoff.

**Payment.** Part 1 + Part 2 + show-up fee (`participation_fee`, set in `settings.py`, default 5). Keep the fee at 3.5 or more so that no total can be negative.

## Project structure

```
settings.py               session config, show-up fee, room "econlab"
Procfile, .python-version Heroku
ultimatum/                Name, Intro, Offer (A), Respond (B), payoffs
loss_aversion/            Decide (6 lotteries), Payment (final summary)
*/tests.py                bots; the loss-aversion bot checks that inconsistent choices are rejected
```

## Run locally

```bash
pip install -r requirements.txt
otree test ug_loss_aversion 2     # bot test (use an even number)
otree devserver                   # http://localhost:8000
```

## Deploy to Heroku

```bash
heroku login
heroku create <app-name>
heroku addons:create heroku-postgresql:essential-0
heroku config:set OTREE_PRODUCTION=1 OTREE_AUTH_LEVEL=STUDY OTREE_ADMIN_PASSWORD='<password>'
git push heroku HEAD:main
heroku ps:scale web=1 worker=1
heroku run otree resetdb          # erases all data, so export first if a session has already run
```

Alternatively, run `otree zip` and upload the `.otreezip` through otreehub.com.

## Running a session

1. Log in at `https://<app>.herokuapp.com/admin` (user `admin`).
2. Students go to `https://<app>.herokuapp.com/room/econlab`.
3. In **Rooms → econlab**, wait until the arrival count equals the headcount. The headcount **must be even**. Then create the session with that many participants.
4. Watch progress in **Monitor**. Afterward, **Payments** lists each student's name and total.
5. Use **Data → Export** to download the data.

## Key variables

| Variable | App | Meaning |
|---|---|---|
| `participant.label` / `ultimatum.player.student_name` | ultimatum | Student's name |
| `participant.id_in_session`, `group.id_in_subsession` | ultimatum | IDs for matching the two people in a pair |
| `player.role` | ultimatum | Person A (proposer) / Person B (responder) |
| `group.offer` | ultimatum | Amount offered to B (0–10) |
| `group.accepted` | ultimatum | 1 = B accepted, 0 = B rejected |
| `player.payoff` | ultimatum | Part 1 earnings |
| `lottery_1` … `lottery_6` | loss_aversion | 1 = Accept, 0 = Reject |
| `switch_point` | loss_aversion | First lottery rejected (1–6); 7 = accepted all. Higher = less loss averse |
| `num_accepted` | loss_aversion | Number of lotteries accepted (0–6) |
| `paid_lottery`, `coin`, `paid_accepted` | loss_aversion | Lottery drawn for payment, coin result, whether the student had accepted it |
| `player.payoff` | loss_aversion | Part 2 earnings |

Implied loss-aversion bounds: a student who accepts Lottery *k* but rejects Lottery *k+1* has λ between 3/L<sub>k+1</sub> and 3/L<sub>k</sub>, where L<sub>k</sub> is the loss in Lottery *k*.
