# Tasks

Active and queued work for the project. Completed work moves to a section
at the bottom or is deleted once it's reflected in the docs.

## Active

### Rogozhin (4,6) reference implementation

A Python implementation of Rogozhin's UTM(4,6) with a small set of test
cases that match outputs published in the literature. This pins down the
22 transition rules as data the rest of the project depends on — peg
coordinates on the transition cylinder, halt-cell identity, halt
behaviour. A wrong rule here propagates to every printed peg.

Output: a module under `spec/` (or `tests/`) that can be imported and
exercised, plus enough tests that we'd notice if a rule was transcribed
incorrectly. Until this is done, every doc reference to a specific rule
or to "the 22 rules" is unanchored.

Lands before the chain-and-head architecture rewrite, so any rule-shape
assumptions in the rewritten docs can be checked against the reference.

## Queued

In rough priority order — earlier items unblock later ones.

### Chain-and-head architecture rewrite

A previous conversation introduced "the gantry rides the rail's
T-channel" as the cell↔head transport mechanism. The actual design is
the inverse: the head is stationary, and the tape is a chain of cells
joined by ball-and-socket joints that the crank pulls through the head.
The fabricated gantry/rail framing has propagated through the doc set
and needs a systematic rewrite.

The chain-and-head architecture is anchored in
`docs/DESIGN_INFLUENCES.md` ("Tape is a chain of cells; the head is
stationary"). The rewrite brings every dependent doc into line with
that anchor.

Affected docs:

- **`CLAUDE.md`** — load-bearing interfaces are currently
  "cell housing↔slider, segment↔segment, gantry↔rail." Becomes
  "cell housing↔slider, cell↔cell joint, head↔chain feed."
- **`PART_INVENTORY.md`** — replace "Rail / tape segment" with a tape-
  chain entry (cell↔cell joint geometry). Replace "Gantry / head" with
  a head entry (the stationary tabletop assembly that contains the
  wedge, read arm, writer arm, transition cylinder, state register,
  drive, and crank). Update the datum-chain anchoring to land on the
  head's internal frame.
- **`INTERFACES.md`** — drop "Gantry ↔ rail." Add "Cell ↔ cell joint"
  (ball-and-socket geometry, pull-force in both directions, yaw/roll
  pinned, pitch admitted). Add "Head ↔ chain feed" (sprocket or pawl
  engagement that advances exactly one cell-width per cycle). Re-
  anchor the datum chain on the head's frame.
- **`CYCLE.md`** — phase 6 "the gantry advances one cell" → "the chain
  advances one cell-width through the head."
- **`VISION.md`** — "move the head one cell left or right" is the
  abstract Turing-machine action; the physical realization is "advance
  the chain one cell-width." Worth a clarifying note.
- **`parts/slider_cell.md`** — drop "Cell housing ↔ rail seating on the
  underside"; replace with the cell↔cell joint contract. The cell's
  underside no longer references a rail.
- **TASKS.md** — every reference to gantry/rail per-part docs becomes
  head/chain per-part docs. Several queued items below this one are
  written against the old architecture and need to be closed or
  reshaped during the rewrite: "Decide cell housings: integral to the
  rail vs. socketed" (no rail), "Draft per-part doc for the rail /
  tape segment" (no rail), "Two-segment chain validation" (reframe as
  cell-joint validation), "Gantry single-cell indexing mechanism"
  (becomes head-feed indexing), and the multi-doc "Draft per-part docs
  for gantry, drive, transition cylinder, end caps" entry.

New per-part docs implied: `docs/parts/head.md`, `docs/parts/cell_joint.md`
(or fold into `slider_cell.md`), `docs/parts/feed.md` (sprocket/pawl).
Existing `docs/parts/state_register.md` is fine — the register lives
inside the head, but its design is unaffected.

Sub-questions to resolve during the rewrite:

- **Inter-cell joint geometry.** Two balls and two sockets is the
  current sketch; clearance, retention force, and pitch range need
  numbers.
- **Feed mechanism.** Sprocket teeth on cell undersides vs. linear
  pawl/ratchet driven by a cam. Sprocket is the obvious lead.
- **Where the chain hangs/coils.** Loose drape, gravity into a bin, or
  a guide on either side of the head. Depends on the head's footprint
  and the operator's table layout.

### Resume the docs review

After the chain-and-head rewrite lands, return to the review-decisions
working list at `.claude/review-decisions.md`. Items still open:

- **E1** — Read arm pinned against cylinder during write phase: real
  mechanical concern (force fights writer or loads channel friction).
  Likely fix: lift read arm during write.
- **E2** — Pre-curved pawl bar printed in mesh with the rack: zero CAD
  distance between contacting surfaces will fuse during printing.
  Print-in-place claim at risk; needs explicit clearance or different
  rest-shape strategy.
- **E3** — Cylinder under sustained read-arm spring load: FDM creep.
  Doc treats only elastic deflection. Acknowledge as toy-grade
  lifespan, redesign, or accept silently.
- **E4** — Print-flat-and-fold prism residual fold error from hinge-web
  thickness: not bounded. Primitive is sold as the FDM angular-error
  fix; the bound matters.
- **E5** — Halt-latch geometric gate must engage *after recock*, not
  just "completed cycle," or springs don't re-tension before freeze.
  Tighten doc wording or design the gate to enforce.
- **F1** — TASKS "Active" item should track the build123d module write,
  not "draft the state register design" (already drafted).
- **F2** — `slider_cell.md` state-register variant section overlaps
  with `state_register.md`. Consolidate or drop.
- **F4** — Are there 4 arms (writer + symbol + direction + state) or 3
  (writer-as-symbol + direction + state)? Docs disagree.
- **F5** — Add "Halt latch ↔ drive gear" entry to INTERFACES.md.
- **F6** — "Cylinder turns on bearings" — printed journal or ball
  bearings? Ball bearings extend VISION's allowed non-printed list.
- **F8** — `3d-parts/` directory truly doesn't exist; CLAUDE.md treats
  it as existing. Multiple downstream tasks (test prints, force
  budget) depend on having build123d modules.
- **F9** — VISION Bananaman entry calls truth-table-lookup a cautionary
  signal, but the current architecture *is* a peg-stop lookup table.
  Reflect as known risk in TASKS or revise the framing.
- **F10** — COMMON_MECHANISMS print-flat-and-fold prism mentions glue;
  VISION's print-only scope allows only nuts/bolts/magnets. Remove or
  extend the allowed list.
- **F11** — CYCLE phase 8 recock lists "lock-disengagement input on the
  head" but the lock is cam-driven (no spring to recock). Stale.

Items closed by the chain-and-head rewrite (no further action):

- A5 (head wedge driving from a fixed cam shaft): moot — the head is
  stationary, the wedge cam lives inside the head.
- A6 (cell→cylinder readout routing across a moving gantry): moot —
  the cell is stationary in the head's working volume during readout,
  no routing problem.

### Faceted-cylinder accuracy test print

The hexagonal transition cylinder is the working architecture. Gate:
print a six-facet strip with V-groove fold lines, fold it into a
closed hexagonal prism, and measure the angular accuracy at each fold
(deviation from exact 60°). Also print a few test pegs on the facets
and measure the lateral position of each peg's tip relative to the
cylinder's rotational axis. The cylinder passes if angular error per
fold is small enough that, multiplied by facet radius at the peg
height, the resulting peg-tip lateral displacement is much less than
the readout arm's contact width — i.e., the arm always strikes the
peg square-on, never edge-on. Fail-over: the flat 6×4 plate (see
alternative in `docs/DESIGN_INFLUENCES.md`).

### Dimension the cylinder + readout selection mechanisms

Open: facet width and cylinder radius, axial row pitch, the gearing
that translates the read arm's stop position into cylinder rotation,
the linear mechanism that translates the state register's position
into readout-assembly axial position, and the cycle phase ordering
that interleaves "rotate to facet" and "translate to row" with read /
write / state-update. Lands before the transition cylinder per-part
doc, after the accuracy test print passes.

### Decide cell housings: integral to the rail vs. socketed

Lives in `docs/parts/rail.md` when written. Integral eliminates link 3
of the datum chain (`docs/INTERFACES.md`), shortening the tolerance
stack between slider lock and gantry coupler; socketed allows
individual cell replacement without reprinting a whole rail segment. Three downstream
docs (`INTERFACES.md`, `PART_INVENTORY.md`, `parts/slider_cell.md`) are
all waiting on this decision. Promote it ahead of the rail per-part doc
so the slider cell module isn't blocked.

### Draft per-part doc for the rail / tape segment

`docs/parts/rail.md`. High-level prose: T-channel layout, segment join
geometry, cell-housing mounting (per the integral-vs-socketed decision
above). No dimensions.

### Halt mechanism design

`docs/parts/halt.md`. Decision settled: a printed latch hooks onto the
drive gear when the machine halts, blocking further cranking until the
operator manually disengages it. The trigger is the state register
landing on a designated halt position, driven by a halt peg on the
transition cylinder's state track. Malformed-input rows (the two of 24
that have no defined Rogozhin rule) route to the same halt position so
the machine halts rather than producing undefined behavior. Open:
latch geometry (overcenter? compliant snap?); operator-disengage
interface; how the operator distinguishes "halted" from "stuck
mid-cycle"; and the safe-stop gating that prevents the latch from
engaging mid-cycle and freezing the cam stack in an unsafe
configuration (preferred: a geometric gate so the latch physically
can't engage outside the end-of-cycle crank-angle window). Depends
on the drive gear geometry and the cam-stack layout.

### Tape extent and program-loading conventions

`docs/TAPE_LAYOUT.md` (or a section in `docs/parts/rail.md`). Cells per
segment, head's initial position, where program / input / working area
live on the tape, and the convention for extending segments mid-run.
Rogozhin (4,6) tapes grow fast under 2-tag simulation, so even a small
program can need many segments — the doc should give an order-of-
magnitude estimate for a sample program. Operator-facing: how a fresh
segment's cells get initialized to the blank symbol (printed jig vs.
deeper "blank" rest position vs. manual). Lands once the slider cell prints
cleanly.

### Mechanical step counter (deferred / non-goal candidate)

A mechanical counter that increments once per transition. Useful for
debugging long programs ("cell N had wrong symbol after step M"). Not
required by the VISION constraints. Decide explicitly: queue it as a
nice-to-have or close it as a non-goal.

### Test-print the slider cell

Once the build123d module for the cell is written, print one
housing+slider as-is and verify: slider releases cleanly from the
print-in-place support, slides freely with the modeled clearances,
the pawl bar engages the rack reliably at every position, the wedge
input deflects the bar with reasonable force without cracking it, and
the cylinder withstands lateral load from a simulated read arm. First
test print should sweep a range of pawl-bar thicknesses and rack tooth
pitches. Gates everything downstream — if the cell doesn't print as
intended, the cell geometry needs revision before the rail.

### Two-segment chain validation

Print two short rails and confirm the dovetail + alignment pin + magnet
join holds the T-channel and cell pitch continuous within the tolerance
budget that lands in `docs/INTERFACES.md`.

### Tolerance budget for peg-stop → rest-position landing

The peg-stop approach assumes the writer arm lands close enough to a
target rest position that the slider's pawl bar engages the correct
tooth rather than the neighbour. Verify experimentally: print a
writer-arm + plate + slider mockup at intentional peg-position errors
of 0, ±0.2, ±0.4, ±0.6 mm and record the smallest error that produces
a wrong-tooth landing. The margin between that error and the realistic
peg-positioning accuracy (a function of plate print quality plus arm
pivot slop) is the design's real tolerance budget. With the rack
primitive, the relevant pitch is the slider tooth pitch, not a detent
spacing. Lands with the readout-assembly per-part doc, since arm
geometry is dimensioned there.

### Cycle force budget — first numbers

`docs/CYCLE.md` has a force/torque table that is currently all TBD.
Plug in rough numbers (printed-flexure spring rates from a small test
print, slider friction from the test-print task, four arm springs at
target travel) and check that the per-cycle total is within one-handed
cranking comfort. If not, redesign before per-part design proceeds.

### Wear-management pass

Wear is an accepted design flaw within the lifespan scope set by
`docs/VISION.md` (toy, recreational use). The remaining decision is
narrow: identify which plastic-on-plastic high-cycle interfaces
(slider in housing, writer-arm peg-stop contact, pawl-bar flexure
fatigue, cam followers, gantry-rail running pads) are worth making
replaceable, and document the rest as accepted-as-is. Replaceable
interfaces should follow the gantry-pad pattern — separable, single-
function, cheap to reprint. Don't introduce non-printed bushings or
bearings.

### Gantry single-cell indexing mechanism

The gantry must advance exactly one cell in either direction on demand.
Treated as "whatever transmission the drive provides" today; in
practice this is an escapement-class problem that probably needs its
own design entry. Lands with the gantry per-part doc, but flag the
sub-mechanism explicitly so it doesn't get glossed.

### Recreate `3d-parts/` directory

CLAUDE.md describes the directory and its conventions but the directory
does not exist. Recreate with at minimum a stub README pointing to the
conventions, so the layout matches the doc.

### Transcribe Rogozhin's 22 transition rules

The (4,6) table from Rogozhin (1996) *Theoretical Computer Science*
168(2):215–240. Land it now in `spec/rogozhin_46.py` (or as a
machine-readable table in `docs/`) so it is version-controlled before
peg coordinates depend on it. If the table is wrong, every peg is wrong.

### Draft per-part docs for gantry, drive, transition cylinder, end caps

`docs/parts/gantry.md`, `docs/parts/drive.md`,
`docs/parts/transition_cylinder.md`, `docs/parts/end_caps.md`. The first
three depend on the faceted-cylinder accuracy test print; end caps are
cosmetic and can land last.

### Build the spec / upper layer

`spec/utm_spec.py`. Once parts code and the Rogozhin table are stable,
build the upper layer that takes a transition table + physical config
and emits a full parts manifest including the peg coordinates encoding
the 22 rules. Parameterize so swapping a different (m,n) machine is a
data change.

### Confirm or change the license

The repo currently ships GPL v3 (`LICENSE`). For a hardware project,
CC-BY-SA 4.0 for STL/docs and MIT for code is the common combo. Decide
whether to keep GPL v3 or switch — and if switching, do it before
public-remote push.

### Operator ergonomics pass

Table height, crank torque, and the operator's interaction with the
machine end-to-end. Land after the first end-to-end mechanical mockup
gives concrete numbers for the `docs/CYCLE.md` force budget.

## Completed

### Reorganize docs top-down before writing more code

Split `docs/HANDOFF.md` into the layered documentation set (`VISION.md`,
`DESIGN_INFLUENCES.md`, `COMMON_MECHANISMS.md`, `CYCLE.md`,
`INTERFACES.md`, `PART_INVENTORY.md`, `parts/slider_cell.md`) and
deleted `HANDOFF.md` and `3d-parts/slider_cell.py`. Each layer is now
editable independently; integration constraints (cycle, datum chain)
have explicit homes; the slider cell module awaits the read arm's
sweep geometry from the gantry per-part doc.
