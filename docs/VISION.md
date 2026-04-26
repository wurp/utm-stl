# Project Vision

This is the source of truth on what this project is. If anything in `CLAUDE.md`,
`HANDOFF.md`, or the code conflicts with this document, this document wins.

## The machine

A fully 3D-printable universal Turing machine implementing Rogozhin's UTM(4,6):
4 states, 6 symbols, 22 transition rules. The operator programs the tape by hand
before the run by setting each cell to a symbol. During the run, the operator's
single repeated action is turning a crank. Each crank turn advances the machine
through exactly one transition — read the symbol under the head, look up the
(state, symbol) entry, write the new symbol, move the head one cell left or
right, and change to the new state — until the machine halts. The transition
table is embodied in printed geometry that drives the writer, the head's
direction of travel, and the state register; the operator supplies motion, not
decisions.

## Constraints that define it

- **Fully 3D-printable.** Every functional part comes off an FDM printer. Allowed
  non-printed parts: standard nuts & bolts, and small magnets where they
  meaningfully help (e.g. segment alignment).
- **Hand-cranked.** The crank is the sole power input and the sole runtime
  control.
- **Modular tape.** Tape segments chain end-to-end so the tape can be extended
  to whatever length a given program needs.
- **Rogozhin (4,6).** The smallest known *standard* universal Turing machine;
  finite input, halts on completion, universal in the conventional sense.

## Done looks like

A printed machine that, loaded with any valid Rogozhin (4,6) program and input,
computes the correct result and halts — driven only by a human turning the
crank.
