# Slider Cell

The tape cell. One cell per tape position; many cells tile along the tape
axis on a rail segment.

## What it is

A flat housing containing a single linear slider. The slider translates
inside the housing along the cell's slider-travel axis, perpendicular to
the tape axis. Six detent positions along the travel correspond to the
six symbols of Rogozhin (4,6); the slider's position *is* the symbol
(`../DESIGN_INFLUENCES.md`).

The cell has three interactions:

- **Operator.** The operator slides the slider to the desired detent to
  set the cell's symbol when programming the tape, before any cranking
  begins. Each detent is labeled with its symbol on a visible face of
  the slider so the operator has a human-readable check.
- **Head, during read.** The head couples to the slider's position
  (mechanism class TBD; see `../INTERFACES.md`, slider position ↔
  row-select). The slider does not move during read — the coupling
  transmits its current position to the transition plate's row-select
  input.
- **Head, during write.** The head deflects the cell-resident flexure
  to disengage the lock, the writer arm drags the slider to the new
  detent, the head withdraws, and the flexure re-engages the lock.

## Mechanisms used

The cell instantiates four primitives from `../COMMON_MECHANISMS.md`:

- **Print-in-place with clearance gap.** The slider is printed inside
  the housing with a slip-fit air gap; after printing, breaking any
  bridge support frees the slider to translate.
- **FDM detent.** The slider's underside carries six detent dimples;
  the housing floor carries a sprung bump that engages each dimple in
  turn as the slider crosses, giving a tactile click at each symbol
  position.
- **Flexure-returned latch.** The cell-resident lock is held in its
  engaged state by a printed compliant flexure inside the housing.
  Engaged is the default; the head's lock-disengagement input deflects
  the flexure during the write phase only.
- **Sweeping arm with peg-stop output** is *not* used inside the cell —
  the writer arm lives on the head, not the cell. The cell is a passive
  recipient of the writer arm's output.

## Interfaces owned

The cell owns these contracts from `../INTERFACES.md`:

- **Cell housing ↔ slider** on the inside: slip-fit clearance, detent
  geometry, lock engagement across all six detent positions.
- **Slider position ↔ row-select coupling** on the head side: the
  geometry and tolerance that allow the head's coupler to take off the
  slider's current position. The contract itself is open — the
  row-select mechanism class is the project's keystone open question
  — but when it lands, the cell side of the contract is owned by this
  part.
- **Cell housing ↔ rail seating** on the underside, shared with the
  rail. The cell may be integral to the rail (in which case this
  interface vanishes) or socketed; the decision lives in the rail's
  per-part doc, but the cell's underside geometry follows from it.

## Open questions

- **Compliant flexure geometry for the lock.** Beam length, thickness,
  and print orientation that yield acceptable engagement force across
  the print's elastic limit. The flexure must engage repeatably for at
  least the lifetime of one program (thousands of cycles).

- **Lock-disengagement input shape.** Whether the head lifts the lock
  by a wedge action against a tapered face, or by direct contact with
  a flange on the lock bar. Wedge gives mechanical advantage but adds
  contact area that must wear cleanly; direct-contact is simpler but
  needs higher input force. Decision deferred until the head's
  geometry is drafted.

- **Detent retention margin vs. writer arm spring force.** The detent
  must hold against incidental disturbance but yield to the writer
  arm. The margin between the two forces sets reliability — a test
  print with a range of bump compliances is the right first
  experiment.

- **Symbol labels on the slider.** Single Unicode glyphs vs. small
  embossed icons for symbols whose conventional notation is multi-
  character (e.g. Rogozhin's `b₁`, `c₁`). Defer until the cosmetic
  pass.

## Status

Design doc drafted; build123d module not yet written. The module is
written once the row-select mechanism class is chosen, since the
slider-position takeoff geometry on the cell side depends on it.
