# State Register

The machine's current-state holder. Rogozhin (4,6) has four states; the
register holds whichever one the machine is currently in, feeds that value
into the transition cylinder's row-select, and accepts a new value from the
state-arm at the end of each cycle.

## What it is

A slider cell, reused as-is from the tape. The slider's position is the
current state, exactly as the slider's position is the symbol on a tape
cell (`../DESIGN_INFLUENCES.md`).

The register's housing, slider, channel, rack, and pawl bar are the
slider cell geometry. The rack is a continuous series of teeth and any
tooth is an admissible rest position; "labelled position" means a tooth
that carries an engraved state label on the cover and a corresponding
peg-stop on the state-arm. The register-specific parameters are the
labelled positions and the state-arm's peg layout that targets them.

The state-arm drives the register the way the writer arm drives a tape
slider: deflect the pawl bar, drag
the slider to the new position, withdraw the wedge to re-engage.

The register sits in the fixed housing alongside the transition cylinder,
not on the gantry. It does not move with the head.

## Interactions

- **Operator, before the run.** The operator slides the register to the
  program's start state when loading a program, the same way they set
  each tape cell to its starting symbol.
- **Row-select, every cycle.** The register's slider position drives
  the readout assembly's axial position along the transition cylinder,
  selecting one of four rows (`../INTERFACES.md`, row-select). The
  readout assembly carries the three peg-stop arms; combined with
  column-select (driven by the current cell's slider via the read
  arm), this lands the readout over a single rule cell.
- **State-arm, end of cycle.** The state-arm — one of the three peg-stop
  arms above the transition cylinder — drives the register to the new state
  encoded by the rule's state peg. The arm acts as the register's
  "writer," analogous to the writer arm on the tape side.

## Reused mechanisms

Same primitives as the tape slider cell (`../COMMON_MECHANISMS.md`):
print-in-place with clearance gap, rack and sprung pawl bar, and (on
the driving side) sweeping arm with peg-stop output. The pawl bar is a
flexure, so the flexure-returned latch primitive is implicit in the
rack-and-pawl-bar.

## Interfaces owned

- **State register ↔ row-select coupling.** The register's slider
  position drives the readout assembly's axial translation along the
  transition cylinder. Tolerance, stroke, and takeoff geometry land
  with the readout-assembly per-part doc.
- **State register ↔ state-arm.** The state-arm reaches the register
  across the fixed housing. Stroke length, lock-disengagement timing,
  and recock geometry are the contract; phasing is in `../CYCLE.md`.

## Open questions

- **Spacing of labelled positions.** The register has 4 labelled
  positions, one per Rogozhin state. The labels are teeth on a
  continuous rack, so the spacing is independent of the cell geometry;
  it is set by the state-arm's peg layout and by the row-select
  coupling's discrimination tolerance — adjacent labels must be far
  enough apart that the coupling reliably distinguishes them. Lands
  with the readout-assembly per-part doc.
- **Lock-disengagement is cam-driven.** A small wedge driven by its
  own cam on the drive shaft (`../COMMON_MECHANISMS.md`, cam stack on
  a shaft) deflects the pawl bar to release the lock. The wedge cam's
  lobe leads the state-arm's cam by enough angle that the lock is
  fully disengaged before the state-arm starts pulling the slider,
  and stays open until the state-arm has settled at the new position.
  Open: the exact lead angle, which lands with the drive doc's
  per-phase dimensioning.

## Status

Per-part doc drafted; build123d module not yet written. The module
follows the slider cell module — same primitives. The register-specific
parameters are the labelled positions (which teeth carry state /
halt labels and where they sit on the cover) and the state-arm peg
layout that targets them; both depend on the readout-assembly's
discrimination tolerance, which lands with that per-part doc.
