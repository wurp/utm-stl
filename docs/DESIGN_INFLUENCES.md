# Design Influences

Decisions about which mechanism class the machine uses, with the reasoning
behind each. `VISION.md` says what the machine is; this document says why
the design realizing it looks the way it does. Read it after `VISION.md`
and before any layer below.

Each entry is a settled directional decision. Open sub-questions inside an
entry are called out explicitly so they can be tracked; the entry itself is
not relitigated unless the rationale changes.

## Rogozhin (4,6) is the target machine

The machine implements Rogozhin's UTM(4,6): 4 states, 6 symbols, 22
transition rules. Rogozhin (4,6) is the smallest known *standard* universal
Turing machine — finite input, halts on completion, universal in the
conventional Turing-Davis sense. Standard UTM semantics match the
operator's mental model for a physical demo: load a program, turn the
crank, read the result.

Smaller weakly-universal machines (Wolfram (2,3) proven universal by Smith
2007 / Margenstern 2010) require an infinite non-periodic tape pre-filled
before the run and never halt, so they don't fit the "load, run, read"
model.

Consequence: programs simulate 2-tag systems and grow fast, so the tape is
modular by design — segments chain end-to-end to whatever length a program
needs.

## Symbol = slider's position

A cell encodes its symbol as the position of a single linear slider with
six detents. Position *is* the symbol; there is no separate read step that
extracts a code from the slider.

This collapses two operations into one. Downstream of the read, the
machine has to use (state, symbol) to select a row of the transition
table; making position the symbol means the slider's position can directly
drive the row-select coupling, with no intermediate encoding to decode. The
cleanest read mechanism is no read mechanism.

Consequence: the head's interaction with the slider is positional —
mechanically coupling to where the slider sits, not sensing a feature on
its surface. The geometry of that coupler is an open interface (`docs/INTERFACES.md`).

## Lock is cell-resident, flexure-returned

Each cell housing contains its own lock that holds the slider in its
current detent at rest. A printed compliant flexure inside the housing
presses the lock into engagement. When the head arrives over a cell, the
head mechanically disengages that cell's lock for the duration of the
write, then withdraws to let the flexure re-engage the lock before the
head leaves.

Locating the lock in the cell rather than on the head means cell state is a
property of the cell — it stays locked when the head leaves, it stays
locked when the machine is powered down (which for this machine means the
crank stops), and the head doesn't have to remember which cell it just
left. The flexure-return makes engaged the default state: a stuck or
mid-cycle stop leaves cells locked, not free.

## Transition mechanism is peg-stops on a printed plate

The 22 transition rules are embodied as physical pegs on a printed plate.
Each rule contributes one peg to each of three output tracks (new symbol,
head direction, new state) at the position that encodes the output value.
To execute a rule, spring-loaded arms above each output track are released
and travel until they hit their respective pegs; the arm's stop position
drives the corresponding output (writer slider, head L/R latch, state
register).

Peg-stops are robust against print tolerance (a peg's position is its
identity, so small dimensional error shifts the output linearly rather
than discretely), tunable by reprinting one plate, and have no fragile
parts.

Open sub-question: how (current state, current symbol) selects which row
of pegs the arms see. Candidates: translate the plate in two axes (state
along one, symbol along the other); translate the arms instead of the
plate; mask all rows except the selected one with a 6×4 pin matrix above
the plate. The choice constrains gantry footprint, drive sequencing, and
recock geometry — it is the highest-leverage open question in the design,
and it lands before the gantry or drive per-part docs.

## Crank also recocks

A single crank is the sole runtime control. Each transition cycle the
crank both trips the spring-loaded arms in sequence (lock release, write,
direction, state) and re-tensions every spring before the next cycle.

This is a familiar mechanism class — mousetrap clockwork, escapement —
not a new invention. The crank-turns-per-transition ratio is a mechanism-
design choice, not a fixed contract; different transitions may take
different amounts of cranking, and the cycle may sequence read → row-
select → write → move → state-update across many revolutions. The crank
accepts a hand grip or an external motor coupling at the same interface;
any motor is external to the machine.

Consequence: the operator's torque budget covers all springs together, not
one at a time. Recock force is a global constraint tracked in
`docs/CYCLE.md`.
