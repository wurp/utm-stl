# Part Inventory

The parts the machine is built from, what each one does, and which other
parts it interfaces with. One paragraph per part, no dimensions, no
mechanism-internal detail. This document is the table of contents for
`docs/parts/`; per-part design lives there, dimensioned implementation
lives in `3d-parts/`.

A status field on each entry says where the part is in the design →
draft → code → printed pipeline.

## Tape cell

A flat housing containing a single linear slider that translates
perpendicular to the tape axis. The slider has six discrete detent
positions = six symbols (`docs/DESIGN_INFLUENCES.md`); the slider's
position *is* the symbol. A cell-resident lock holds the slider at its
current detent at rest, with a printed compliant flexure pressing the
lock into engagement; the head disengages the lock for write and
withdraws to let the flexure re-engage it. The cell uses the FDM detent,
flexure-returned latch, and print-in-place mechanisms
(`docs/COMMON_MECHANISMS.md`). Interfaces: cell housing ↔ slider
(`docs/INTERFACES.md`) on the inside; slider position ↔ row-select
coupling on the head side; cell-to-rail seating on the underside.

Design doc: `docs/parts/slider_cell.md`. Status: design doc drafted; code
deleted, awaiting rewrite.

## Rail / tape segment

A flat base that holds a row of cell housings tiled along the tape axis,
with both short ends carrying a dovetail + alignment pin + magnet pair
for chaining to neighbour segments and long edges carrying a continuous
T-channel guide rail for the gantry. The rail is the part that owns the
common datum for the machine: every other part datums off its T-channel
surface (`docs/INTERFACES.md`, datum chain). Cell housings may be
integral to the rail (one print per segment) or socketed (cells snap
into rail slots) — that decision lives in the per-part doc and trades
off ease of replacement against tolerance-stack length.

Design doc: not yet drafted. Status: not started.

## Gantry / head

A bridge straddling the tape, riding on the rail's T-channel. The gantry
carries the writer arm, the lock-disengagement input, the row-select
coupling that takes off slider position, and the per-cell registration
detent that locates the gantry exactly over one cell at a time. The
state register and the transition plate live in a fixed housing
alongside the gantry, not on the gantry itself; the gantry communicates
with the transition plate via the row-select coupling on one side and
the writer / direction / state arms on the other. The gantry is the
part that interacts with each cell during a transition.

Design doc: not yet drafted. Status: not started; depends on the row-
selection mechanism choice (`docs/DESIGN_INFLUENCES.md`, peg-stop
transition entry).

## Drive

The crank and the main shaft that sequence one transition cycle and
recock every spring-loaded arm between cycles (`docs/CYCLE.md`). The
crank-turns-per-transition ratio is a mechanism-design choice; the
drive's gear and cam profile is shaped by the cycle's phase ordering
and the recock force budget. The crank is the sole runtime control and
the sole interface to the outside world; it accepts a hand grip or a
motor coupling at the same interface. Any motor is external to the
machine.

Design doc: not yet drafted. Status: not started; depends on the row-
selection mechanism choice and the gantry geometry.

## Transition plate

A printed plate carrying the 22 rules of Rogozhin (4,6) as physical
pegs (`docs/DESIGN_INFLUENCES.md`, peg-stop transition entry). Each
rule contributes one peg to each of three output tracks (new symbol,
head direction, new state) at the position encoding the rule's output
value. The plate is selected, row by row, by the combination of the
current cell's slider position and the state register's output;
spring-loaded arms above each output track are released and travel
until they hit their pegs, driving the writer, the head's L/R latch,
and the state register to the new state. The row-selection mechanism
itself — translate plate, translate arms, or pin-matrix mask — is the
open question on this part.

Design doc: not yet drafted. Status: not started; the row-selection
mechanism choice is the highest-leverage open question in the project.

## End caps

Left and right terminators with the rail dovetail on one side, solid on
the other. Cap the T-channel cleanly so the gantry cannot run off the
end. End caps may register the rail run against an external surface for
operator ergonomics.

Design doc: not yet drafted. Status: not started; cosmetic, deferred
until the load-bearing parts are stable.
