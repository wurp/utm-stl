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
perpendicular to the tape axis. The slider is a square base with a
cylinder protruding through a slot in the cover; one edge of the base
carries a row of symmetric gear teeth. Six discrete rest positions
along the travel correspond to six symbols (`docs/DESIGN_INFLUENCES.md`);
the slider's position *is* the symbol. A long compliant pawl bar runs
parallel to the slider's tooth edge, pre-curved into engagement with
the rack — engagement is the default state. The head's wedge input
deflects the pawl bar to release the slider for the write phase and
withdraws to let the bar re-engage. The cell uses the rack-and-sprung-
pawl-bar and print-in-place mechanisms (`docs/COMMON_MECHANISMS.md`).
The cylinder serves as operator grip, head read-feature, and read-arm
stop simultaneously. Interfaces: cell housing ↔ slider
(`docs/INTERFACES.md`) on the inside; slider position ↔ column-select
coupling on the head side; cell-to-rail seating on the underside.

Design doc: `docs/parts/slider_cell.md`. Status: design doc drafted;
build123d module not yet written.

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

## State register

A slider cell reused as the holder of the machine's current state. The
register has 4 labelled rest positions, one per Rogozhin (4,6) state;
the slider's position *is* the state, the same way the tape cell's
slider position is the symbol. The register sits in the fixed housing
alongside the transition cylinder, feeds row-select with its position,
and is driven to the new state at end of cycle by the state-arm — one
of the three peg-stop arms above the transition cylinder. The cell
geometry is the slider cell unmodified; the rack is continuous and the
4 labelled positions are teeth on that rack carrying engraved state
labels on the cover. Halt is a cylinder-side mechanism (see Halt latch)
and does not require a register-side landing.

Design doc: `docs/parts/state_register.md`. Status: design doc drafted;
build123d module follows the slider cell module.

## Halt latch

A printed latch that hooks onto the drive gear when the machine reaches
a halt configuration, blocking further cranking until the operator
manually disengages it. The trigger is a halt peg on the transition
cylinder. Three rule cells carry halt pegs: the one normal halt rule
(end of program) and the two unused (state, symbol) cells (24 grid
cells, 22 rules — landing on either of the unused 2 halts the machine
rather than producing undefined behavior). All three trigger the same
latch mechanism; the latch does not distinguish them.

Because the cam stack is on the same drive shaft (`docs/PART_INVENTORY.md`,
Drive entry), the halt latch necessarily freezes every cam event when
it engages. To leave the machine in a safe-stop configuration
(`docs/CYCLE.md`, safe-stop states) rather than mid-cycle, the latch
must engage only at a safe-stop crank angle. Two approaches:
geometrically gate the latch so it physically can't engage outside the
safe-stop window, or accept that the operator must crank to the
end-of-cycle before the trigger is allowed to fire. The first is
preferred — the operator should not have to know about cycle phases.

The latch must distinguish "halted" from "stuck mid-cycle" — typically
by being visible and labeled, and by being the only state in which the
operator-disengage handle is exposed.

Design doc: not yet drafted. Status: not started; depends on the drive
gear geometry and the cam-stack layout.

## Gantry / head

A bridge straddling the tape, riding on the rail's T-channel. The gantry
carries the writer arm, the lock-disengagement input, the read arm
(which takes off slider position into column-select), and the per-cell
registration detent that locates the gantry exactly over one cell at a
time. The state register and the transition cylinder live in a fixed
housing alongside the gantry, not on the gantry itself; the gantry
communicates with the transition cylinder via the column-select
coupling on one side and the writer / direction / state arms on the
other. The gantry is the
part that interacts with each cell during a transition.

Design doc: not yet drafted. Status: not started; depends on the row-
selection mechanism choice (`docs/DESIGN_INFLUENCES.md`, peg-stop
transition entry).

## Drive

The crank and the main shaft, plus the cam stack on that shaft that
sequences every phase of the transition cycle. Each phase — cell-select
rotation, cell-select axial translation, lock-disengage, write-release,
write-travel, lock-reengage, move, state-update, recock — has its own
cam keyed to the shaft, with a follower driving that phase's
mechanism. The cycle's phase ordering is encoded in the cams' lobe
placement around the shaft (`docs/COMMON_MECHANISMS.md`, cam stack on
a shaft). The crank is the sole runtime control and the sole interface
to the outside world; it accepts a hand grip or a motor coupling at
the same interface. Any motor is external to the machine.

Design doc: not yet drafted. Status: not started; depends on the
gantry geometry and on the per-phase force budgets that determine how
many crank revolutions each transition takes.

## Transition cylinder

A six-faceted hexagonal cylinder carrying the 22 rules of Rogozhin
(4,6) as peg-stops on its outer surface (`docs/DESIGN_INFLUENCES.md`,
peg-stop transition entry). Each facet carries one column of the
table (one current-symbol value); four rows along the cylinder's axis
carry the four current-state values. Each grid cell holds three output
pegs (new symbol, head direction, new state) projecting radially. To
execute a rule, three spring-loaded output arms positioned over the
selected cell are released and travel until they hit their pegs; each
arm's stop position drives one output. Selection: the current cell's
slider position is read by the gantry's read arm (the slider's
protruding cylinder stops the read arm at one of six positions) and
the read arm's stop drives the cylinder's rotation through gearing,
landing the correct facet under the readout (column-select); the
state register's slider position translates the readout assembly along
the cylinder's axis to the correct row (row-select). The two unused grid cells (24
cells, 22 rules) carry pegs that trip the halt latch, so a malformed
input halts rather than producing undefined behavior.

The cylinder is printed flat as a six-facet strip with shallow V-groove
fold lines, then folded into a closed hexagonal prism. The V-grooves
register the facets at exact 60° angles without relying on curved
print geometry.

Design doc: not yet drafted. Status: not started. The hexagonal
cylinder is the working architecture; the flat 6×4 plate is the
pre-committed fallback if the test print fails the angular-accuracy
gate (see `docs/TASKS.md`).

## End caps

Left and right terminators with the rail dovetail on one side, solid on
the other. Cap the T-channel cleanly so the gantry cannot run off the
end. End caps may register the rail run against an external surface for
operator ergonomics.

Design doc: not yet drafted. Status: not started; cosmetic, deferred
until the load-bearing parts are stable.
