# Project Vision

This is the source of truth on what this project is. If anything in `CLAUDE.md`,
the other layered docs in `docs/`, or the code conflicts with this document,
this document wins.

## The machine

A fully 3D-printable universal Turing machine implementing Rogozhin's UTM(4,6):
4 states, 6 symbols, 22 transition rules. The operator programs the tape by hand
before the run by setting each cell to a symbol. During the run, the operator's
single repeated action is turning a crank. Turning the crank advances the
machine through transitions — read the symbol under the head, look up the
(state, symbol) entry, write the new symbol, move the head one cell left or
right, and change to the new state — until the machine halts. The ratio of
crank turns to transitions is a mechanism-design choice; different transitions
may require different amounts of cranking. The transition table is embodied
in printed geometry that drives the writer, the head's direction of travel,
and the state register; the operator supplies motion, not decisions.

## Constraints that define it

- **Fully 3D-printable.** Every functional part comes off an FDM printer. Allowed
  non-printed parts: standard nuts & bolts, and small magnets where they
  meaningfully help (e.g. segment alignment).
- **Crank-driven, no electronics in the machine itself.** A single crank is
  the sole runtime control. No firmware, sensors, motors, solenoids, or active
  electronics are part of the machine. The crank accepts a hand grip or an
  external motor coupling at the same interface; any such motor is external
  to the machine.
- **Modular tape.** Tape segments chain end-to-end so the tape can be extended
  to whatever length a given program needs.
- **Rogozhin (4,6).** The smallest known *standard* universal Turing machine;
  finite input, halts on completion, universal in the conventional sense.

## Done looks like

A printed machine that, loaded with any valid Rogozhin (4,6) program and input,
computes the correct result and halts — driven only by turning the crank.

## Lifespan scope

This is a toy and a demonstration object. The expected use pattern is
that someone runs a few programs, watches the mechanism work for a
while, and sets it aside. Cranking through a Rogozhin (4,6) program
that grows under 2-tag simulation is slow by definition; nobody is
going to run computations on this that their phone can't do in a
millisecond.

Consequence: wear is acknowledged as a real but accepted design flaw.
Plastic-on-plastic contact at high-cycle interfaces (slider in
channel, writer-arm peg-stops, pawl-bar fatigue, cam followers,
gantry-rail running pads) will eventually loosen, score, or fatigue.
The print-only constraint precludes the standard fixes — bearings,
brass bushings, metal pivots — and introducing a heavier assembly
process or harder-to-source parts isn't warranted for a toy. The
gantry's running pads are designed replaceable because they will
wear fastest and replacement is cheap; everywhere else accepts the
flaw.

Out of scope: continuous-duty operation, predictable cycle-count
lifetime, anything implying the machine is built to last beyond
recreational use.

## Prior art

Two physical Turing machines that informed this design:

- **Richard Ridel's wooden Turing machine (2015).** A 3-state, 3-symbol
  hand-built mechanical Turing machine in wood, with a flat-strip
  transition table read by rocker arms and phase sequencing via cams
  on a single shaft. Source of the cam-driven sequencing decision and
  the asymmetric two-stage selector geometry recorded as the
  linear-stack alternative in `DESIGN_INFLUENCES.md`. Documentation:
  https://archive.org/details/mechanical-turing-machine-in-wood-richard-ridel.
- **The Bananaman's LEGO Turing Machine (2024).** A working LEGO
  mechanical Turing machine, hand-cranked, no electronics, built from
  ~2,900 LEGO parts. Confirms a hand-crank-only universal-class
  machine is mechanically feasible. Notable: the builder originally
  attempted a truth-table lookup approach and pivoted to a register-
  based design, a cautionary signal for this project's
  cylinder-as-truth-table architecture.
  Project page: https://ideas.lego.com/projects/10a3239f-4562-4d23-ba8e-f4fc94eef5c7.
