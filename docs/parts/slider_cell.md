# Slider Cell

The tape cell. One cell per tape position; many cells tile along the tape
axis on a rail segment. The same cell geometry, with a different number
of active positions, also serves as the state register.

## What it is

A flat housing containing a single linear slider. The slider translates
inside the housing along the cell's slider-travel axis, perpendicular to
the tape axis. The rack-and-pawl-bar lock holds the slider at any tooth
along the travel; six of those teeth are labelled on the cover as the
six symbols of Rogozhin (4,6), and the slider's position *is* the symbol
(`../DESIGN_INFLUENCES.md`).

The slider is a square flat base with a cylinder protruding upward
through a slot in the housing's cover. The cylinder is the operator's
grip, the head's read feature, and the stop the read arm collides with —
one physical feature serving all three roles, eliminating the inter-
feature tolerance stack that separate features would introduce. Symbol labels are engraved on the cover next
to each rest position; the slider's cylinder sitting next to a label
means that label is the cell's current symbol.

One edge of the slider's square base carries a row of symmetric gear
teeth. A long compliant pawl bar runs the length of the channel
parallel to that edge, pre-curved so its rest shape engages the rack
and locks the slider at whichever tooth it is on. The head's
lock-disengagement input is a wedge that pushes through a hole in the
housing wall and deflects the pawl bar away from the rack, freeing the
slider; on withdrawal, the bar springs back into engagement.

## The cell's interactions

- **Operator.** The operator slides the slider to the desired position
  to set the cell's symbol when programming the tape, before any
  cranking begins. The cylinder's location relative to the engraved
  cover labels gives a human-readable check.
- **Head, during read.** The gantry's read arm sweeps across the cover
  slot and is stopped by the cylinder; the arm's stopped position is
  the column-select output, gear-coupled to the transition cylinder's
  rotation. The slider does not move. The arm remains pinned against
  the cylinder for the rest of the transition cycle, so column-select
  is held statically while writes happen downstream.
- **Head, during write.** The wedge deflects the pawl bar to disengage
  the lock, the writer arm drives the slider to the new position, the
  wedge withdraws, and the pawl bar re-engages the rack at the new
  tooth.

## Mechanisms used

The cell instantiates these primitives from `../COMMON_MECHANISMS.md`:

- **Print-in-place with clearance gap.** The slider is printed inside
  the housing with a slip-fit air gap; after printing, breaking any
  bridge support frees the slider to translate. The cover and the
  pawl bar print in place at the same time.
- **Rack and sprung pawl bar.** The slider's edge teeth and the
  channel's compliant pawl bar form the lock; engagement is the
  default state, the wedge releases it. Symmetric tooth profile so
  the lock holds equally against load from either direction. The
  pawl bar is itself a flexure, so the flexure-returned latch
  primitive is implicit in the rack-and-pawl-bar.

The cell is a passive participant: it presents the cylinder for the
read arm to hit and accepts the writer arm's motion when unlocked.
The read arm and the writer arm live on the gantry / transition
cylinder side.

## Interfaces owned

The cell owns these contracts from `../INTERFACES.md`:

- **Cell housing ↔ slider** on the inside: slip-fit clearance between
  the slider base and the channel, rack tooth pitch and engagement
  count, pawl bar engagement force across all six positions.
- **Slider position ↔ grid-cell select** on the head side
  (`../INTERFACES.md`, column-select half): the cylinder's height,
  diameter, and tolerance set the contract that lets the read arm
  stop on it cleanly without deflecting it laterally past the lock.
- **Cell housing ↔ rail seating** on the underside, shared with the
  rail. The cell may be integral to the rail (in which case this
  interface vanishes) or socketed; the decision lives in the rail's
  per-part doc, but the cell's underside geometry follows from it.

## Force constraints

The read arm's spring force only needs to be large enough to drive
the downstream gearing that rotates the transition cylinder. It is
*not* sized to overcome the lock; the lock is engaged throughout the
read.

The writer arm's force must overcome the slider's slip-fit friction in
the channel during the lock-disengaged phase, with margin. Because the
lock is rack-and-pawl, only the slider's channel friction resists
writer-arm motion while the lock is open.

The wedge input force from the head must deflect the pawl bar far
enough to clear the rack teeth, against the bar's compliant restoring
force. Bar geometry sets this; it is the dominant force budget item
for the lock-disengage phase of the cycle (`../CYCLE.md`).

## Open questions

- **Pawl bar geometry.** Length, thickness, pre-curve, and print
  orientation that yield reliable engagement across the print's
  elastic limit, with a wedge-deflection force the head can supply.
  First test print: a single cell with a range of bar thicknesses.
- **Tooth pitch and rest-position spacing.** Position spacing must be
  an integer multiple of tooth pitch so all six positions land on a
  tooth. Picking pitch trades off position resolution (smaller is
  finer) against tooth shear strength (larger is stronger). FDM
  resolution puts a floor of ~1.5 mm on tooth pitch.
- **Wedge entry point and travel.** Which housing wall the wedge
  enters through, and how far it travels to deflect the bar. Decision
  deferred until the head's geometry is drafted.
- **Symbol label rendering.** Single Unicode glyphs vs. small embossed
  icons for symbols whose conventional notation is multi-character
  (e.g. Rogozhin's `b₁`, `c₁`). Defer until the cosmetic pass.

## State-register variant

The state register is a slider cell with the same geometry. It uses the
same continuous rack; the labelled rest positions on its cover are the
four Rogozhin states. Halt is a cylinder-side mechanism (a halt peg
trips the halt latch) and does not require a register-side landing.
The spacing of the four labelled positions is a register-side
decision, not a cell-geometry change. See `../parts/state_register.md`.

## Status

Design doc drafted; build123d module not yet written. The module
lands once the read arm's sweep geometry is dimensioned, since the
slider cylinder's height and the read-arm contact geometry are joint
design decisions with the gantry.
