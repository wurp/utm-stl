# Tasks

Active and queued work for the project. Completed work moves to a section
at the bottom or is deleted once it's reflected in the docs.

## Active

(None.)

## Queued

In rough priority order — earlier items unblock later ones.

### Choose the row-selection mechanism for the transition plate

The peg-stop output approach is settled (`docs/DESIGN_INFLUENCES.md`).
Open: how (current state, current symbol) selects which row of pegs the
output arms see. Candidates: translate the plate in two axes (state along
one, symbol along the other); translate the arms instead of the plate;
mask all rows except the selected one with a 6×4 pin matrix above the
plate. The choice constrains gantry footprint, drive sequencing, and
recock geometry. This is the project's keystone open question; resolving
it unblocks the gantry, drive, and transition plate per-part docs.

### Draft per-part doc for the rail / tape segment

`docs/parts/rail.md`. High-level prose: cell housings integral vs.
socketed (the decision lives here, with its tolerance-stack consequences
called out against `docs/INTERFACES.md`'s datum chain), T-channel layout,
segment join geometry. No dimensions.

### Test-print the slider cell

Once the build123d module for the cell is written (after the row-select
mechanism choice), print one housing+slider as-is and verify: slider
releases cleanly from the print-in-place support, slides freely with the
modeled clearances, detents engage perceptibly, the cell-resident lock
engages and disengages cleanly under the lock-disengagement input. Gates
everything downstream — if the cell doesn't print as intended, the cell
geometry needs revision before the rail.

### Two-segment chain validation

Print two short rails and confirm the dovetail + alignment pin + magnet
join holds the T-channel and cell pitch continuous within the tolerance
budget that lands in `docs/INTERFACES.md`.

### Draft per-part docs for gantry, drive, transition plate, end caps

`docs/parts/gantry.md`, `docs/parts/drive.md`,
`docs/parts/transition_plate.md`, `docs/parts/end_caps.md`. The first
three depend on the row-selection mechanism choice; end caps are
cosmetic and can land last.

### Build the spec / upper layer

`spec/utm_spec.py` and `spec/rogozhin_46.py`. Once parts code and the
row-selection mechanism are stable, build the upper layer that takes a
transition table + physical config and emits a full parts manifest
including the peg coordinates encoding the 22 rules. Encode Rogozhin's
actual (4,6) table from his 1996 paper (*Theoretical Computer Science*
168(2):215–240). Parameterize so swapping a different (m,n) machine is a
data change.

### Pick a license

CC-BY-SA 4.0 for STL/docs and MIT for code is a common combo for
hardware projects. Decide before pushing to a public remote.

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
have explicit homes; the slider cell awaits a rewrite once the
row-select mechanism is chosen.
