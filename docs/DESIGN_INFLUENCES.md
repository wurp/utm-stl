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

## Transition table is states-as-rows, symbols-as-columns

The Rogozhin (4,6) transition table is laid out as 4 rows × 6 columns =
24 grid cells, of which 22 carry rules and 2 are unused (reserved for
halt). Rows are indexed by current state; columns by current symbol.
This matches the standard UTM literature (Rogozhin, Wolfram, Minsky) and
the function signature `δ(state, symbol) → (state', symbol', move)`,
where the first argument indexes rows. The Rogozhin notation `(m, n)`
also lists states first, symbols second — consistent with the same
ordering.

Two consequences thread through every layer below:

- **Selection terminology.** State drives **row-select**; symbol drives
  **column-select**. Any "row-select" usage on the symbol side is
  inverted under this convention and should be read as a slip.
- **Cylinder layout.** On the transition cylinder, the 6 columns lay
  out as 6 facets around the circumference (60° apart) and the 4 rows
  lay out as 4 axial positions along the cylinder's axis.

## Tape is a chain of cells; the head is stationary

The tape is a flexible chain. Each cell is one slider-cell housing,
joined to its neighbours by a ball-and-socket joint at each end — two
balls on one end of the cell, two inward-facing sockets on the other,
so cells snap together. The joint geometry pins yaw and roll (the
slider always faces the same way) and admits pitch (the chain bends
along its length).

The head, the transition cylinder, the state register, the drive, and
the crank all live in a single tabletop assembly. The chain feeds in
from one side of the head, passes through the head's working volume,
and feeds out the other side. Cells exiting either side hang loose or
flop into a bin.

The "Move" phase advances the chain by one cell-width through the
head, in the direction the direction-arm encodes. The chain is the
moving body; the head is fixed.

Consequences thread through every layer below:

- **Datums anchor on the head's frame**, not on a tape-length surface.
  The head's working volume is the rigid reference; the chain is
  flexible everywhere outside it (`docs/INTERFACES.md`, datum chain).
- **Tape length is unbounded.** The chain extends by snapping more
  cells onto either end. There is no rail or segment to print at full
  tape length.
- **Cell ↔ cell joint is a load-bearing geometric interface.** It
  transmits the feed force in both directions and constrains cell
  orientation so the head can engage the slider reliably.
- **Loading & reading.** The operator builds up the chain off-machine
  by snapping cells together and setting each cell's slider to the
  starting symbol, then feeds the chain into the head's input side.
  After halt, the chain is pulled out and read by eye.

## Symbol = slider's position

A cell encodes its symbol as the position of a single linear slider with
six rest positions. Position *is* the symbol; there is no separate read
step that extracts a code from the slider.

Downstream of the read, the machine has to use (state, symbol) to
select one rule cell of the transition table. Position-as-symbol means
the slider's position drives the column-select coupling directly,
without an intermediate encoding step. The transmission step — getting
the slider's position from inside the cell up to the transition table's
selection input — remains, and is the column-select mechanism
(`docs/INTERFACES.md`).

Consequence: the head's interaction with the slider is positional —
mechanically coupling to where the slider sits, not sensing a feature on
its surface. The coupler is the read arm: a sweeping spring-loaded arm
on the gantry, stopped by the slider's protruding cylinder; the arm's
stop position is what column-select consumes (`docs/INTERFACES.md`).

## Lock is cell-resident, rack-and-pawl

Each cell housing contains its own lock that holds the slider at its
current rest position. The slider's edge carries a row of symmetric
gear teeth; a long compliant pawl bar runs alongside, pre-curved into
engagement, and locks the slider in shear at every tooth. When the
head arrives over a cell, a wedge on the head deflects the pawl bar
out of engagement for the duration of the write, then withdraws to
let the bar re-engage before the head leaves.

Locating the lock in the cell rather than on the head means cell state
is a property of the cell — it stays locked when the head leaves, it
stays locked when the machine is powered down (which for this machine
means the crank stops), and the head doesn't have to remember which
cell it just left. The pawl bar being a compliant flexure makes
engagement the default: a stuck or mid-cycle stop leaves cells locked,
not free. The rack-and-pawl holds the slider in shear, so it resists
deliberate load — read-arm impact and sustained read-arm spring
pressure throughout the cycle.

## Transition mechanism is a hexagonal peg-stop cylinder

The 22 rules of Rogozhin (4,6) live on a six-faceted cylinder: each of
six facets carries one column of the table (one current-symbol value),
and four rows along the cylinder's axis carry the four current-state
values. Each grid cell on the cylinder holds three output pegs (new
symbol, head direction, new state) projecting radially from the facet,
at heights encoding that rule's outputs. To execute a rule, three
spring-loaded output arms positioned over the selected cell are released
and travel until they hit their respective pegs; each arm's stop
position drives one output — the writer arm's stop sets the new
symbol's slider position, the direction arm's stop sets the head's L/R
latch, and the state arm's stop sets the state register's slider
position.

Selection is two independent mechanical motions. The current cell's
slider position drives **column-select**: the read arm on the gantry
sweeps across the slider's protruding cylinder, the slider stops the
arm at one of 6 positions, and the arm's stop drives the transition
cylinder's rotation through gearing, landing one of 6 facets under
the readout. The state register's slider position drives
**row-select**: the readout assembly translates along the cylinder's
axis to one of 4 axial positions. Rotation and axial translation are
independent and may happen in either order or in parallel; sequencing
is a drive-design choice.

Choosing rotation for the column-select axis exploits the crank's
native motion — the cylinder turns on a shaft parallel to (or coaxial
with) the crank shaft, and 60° facet detents are easier to hit
accurately than equivalent linear positions on a sliding plate. The
axial translation is short (≈4 row pitches, ≈30 mm) compared to a
flat-plate alternative's row stage (≈4 row pitches with the plate
sliding through its full travel), reducing absolute positional
tolerance demand. The cylinder rotates in place rather than
translating, so the machine's footprint is smaller and there are no
plate end-stops to crash into.

Peg-stops are robust against print tolerance: a peg's height is its
identity, so small dimensional error shifts an output's landing point
linearly rather than discretely. The slider's rack-and-pawl primitive
(`docs/COMMON_MECHANISMS.md`) sets the relevant downstream pitch — the
writer arm's stop must land within half a tooth pitch of the target
position. Tolerance budget for that landing, plus the faceted-cylinder
print accuracy that drives angular error at the peg face, are tracked
in `docs/TASKS.md`.

The cylinder is fabricated by printing the six facets as one flat
strip, with shallow triangular V-grooves along each fold line. The
strip folds up into a closed hexagonal prism, the V-groove's
triangular faces meeting flush at each edge to register the facets at
exact 60° angles. This both prints flat (no curved or overhanging
geometry to print) and uses the V-groove geometry as the angular
reference, rather than relying on the printer's accuracy across a
curved surface.

Reprinting the strip changes the program-class — same machine,
different transition table, including different (m,n) UTMs if peg
layout follows a parameterized spec.

The hexagonal cylinder is the working choice; the flat plate and the
linear stack are pre-committed fallbacks if the test print called out
in TASKS shows the cylinder's faceted-print accuracy is insufficient.

**Flat 6×4 plate.** Same 6×4 grid laid out flat, with symbol-driven
plate translation for column-select and state-driven readout-arm
translation for row-select. Falling back to the plate changes the
selection mechanisms but leaves the peg-stop primitive, the slider
geometry, the rack-and-pawl, and the halt latch unchanged. Validated
by Ridel's wooden Turing machine in spirit (Ridel uses a linear-stack
variant of the same idea).

**Linear stack** (Ridel's actual layout). All 24 rule-cells in a single
line; state coarsely positions the strip by `state_index × N_symbols ×
row_pitch`; symbol then fine-positions the readout within the selected
group. Stronger than the plate against cross-axis tolerance
interaction, but a 24-row strip at 8 mm pitch is ~190 mm long, so the
coarse stage's absolute positional accuracy across that span is
harder. The cascade reaches it only if the plate fallback also proves
insufficient.

## Crank also recocks

A single crank is the sole runtime control. Each transition cycle the
crank both trips the spring-loaded arms in sequence (lock release,
write, direction, state) and re-tensions every spring before the next
cycle.

This is a familiar mechanism class — mousetrap clockwork, escapement —
not a new invention. The crank-turns-per-transition ratio is a
mechanism-design choice, not a fixed contract; different transitions
may take different amounts of cranking, and the cycle may sequence its
phases across more than one revolution. The crank accepts a hand grip
or an external motor coupling at the same interface; any motor is
external to the machine.

Consequence: the operator's torque budget covers all springs together,
not one at a time. Recock force is a global constraint tracked in
`docs/CYCLE.md`.

## Phase sequencing is cam-driven from the crank shaft

Each phase of the cycle (cell-select rotation, cell-select axial
translation, lock-disengage, write-release, write-travel, lock-reengage,
move, state-update, recock) is timed by a cam riding on the crank shaft. The cam's lobe profile decides at what crank angle
its phase fires, how long the action takes, and how much mechanical
advantage the crank delivers to that phase. Following Ridel's wooden
Turing machine, which uses the same primitive.

A cam stack on one shaft is the working layout: every event reads off
a known angle of the same rotation, so phase ordering is set by lobe
placement at design time rather than by interlocks at runtime. Sub-
shafts geared off the crank are an option for events that need more
travel than one cam can deliver in their angular budget (e.g., recock
pulling a long spring); none are committed to until a specific event
proves it needs one.

Choosing cams over latches-with-interlocks means the cycle is
deterministic from crank angle alone — there is no state-machine of
"if this latch is set, then that event fires." The crank's angular
position *is* the cycle's state. This makes the cycle inspectable and
makes safe-stop windows (`docs/CYCLE.md`) directly identifiable as
crank-angle ranges.

Cell-select happens via two cam-released motions in parallel — one cam
releases the read arm, which sweeps until the symbol slider stops it
and the arm's stop drives the cylinder's rotation through gearing; the
other cam drives the linear motion of the readout assembly along the
cylinder's axis to the row dictated by the state register's position.
Both cam events share the same angular range at the start of the
cycle.

Open sub-questions: cam-follower geometry (sliding contact is simpler
to print but wears faster than a printed roller follower; sliding is
the default until wear data argues otherwise) and crank-turns per
transition (one revolution if every phase fits in its angular budget;
more if recock or another phase doesn't). Both land in the drive
per-part doc.
