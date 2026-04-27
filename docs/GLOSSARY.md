# Glossary

Flat alphabetical list of project terms. Each entry is a one-line
definition with a pointer to the authoritative doc when there is one.
Conventions and rationales live in the docs they're cited from.

- **Cell.** One position on the tape, holding one symbol. See
  `parts/slider_cell.md`.
- **Column-select.** Selection of one of 6 columns of the transition
  table; driven by the current cell's symbol. See `INTERFACES.md` and
  `DESIGN_INFLUENCES.md` (states-as-rows convention).
- **Direction arm.** Spring-loaded peg-stop arm above the transition
  cylinder; stop position drives the gantry's move direction. See
  `COMMON_MECHANISMS.md` (sweeping arm with peg-stop output).
- **Gantry.** The carriage that rides the rail and carries the head
  over the currently-selected cell. See `PART_INVENTORY.md`.
- **Halt latch.** Mechanism that stops the crank when the state
  register lands on a halt-labelled position. See
  `PART_INVENTORY.md`.
- **Head.** The portion of the gantry that interacts with the current
  cell — wedge for lock-disengage, writer arm, read arm.
- **Pawl bar.** Compliant flexure running alongside the slider's rack;
  engagement is the default state, deflected by the wedge to release.
  See `COMMON_MECHANISMS.md` (rack and sprung pawl bar).
- **Peg-stop.** A radial peg projecting from a transition cylinder
  facet; sets the stop position of one of the spring-loaded output
  arms. See `DESIGN_INFLUENCES.md`.
- **Print-in-place.** Multi-body geometry printed as one job with
  clearance gaps that the slicer treats as separations. See
  `COMMON_MECHANISMS.md`.
- **Rack-and-pawl.** The cell-resident lock primitive: slider edge
  teeth engaged by a sprung pawl bar. See `COMMON_MECHANISMS.md`.
- **Read arm.** Spring-loaded sweeping arm on the gantry; stopped by
  the symbol slider's protruding cylinder; stop position drives
  cylinder rotation = column-select. See `parts/slider_cell.md`.
- **Recock.** Final phase of each cycle; re-tensions every spring-
  loaded arm tripped during the cycle. See `CYCLE.md`.
- **Rogozhin (4,6).** The target UTM: 4 states, 6 symbols, 22
  transition rules. Notation lists states first, symbols second. See
  `DESIGN_INFLUENCES.md`.
- **Row-select.** Selection of one of 4 rows of the transition
  table; driven by the current state register. See `INTERFACES.md`
  and `DESIGN_INFLUENCES.md`.
- **Rule cell.** A (state, symbol) intersection on the transition
  cylinder; carries three output pegs (new symbol, direction, new
  state).
- **Slider.** Linear translating body inside a cell housing; rest
  position encodes the cell's value. Used for both tape cells (6
  positions = 6 symbols) and the state register (4 labelled
  positions = 4 states + halt landings). See `parts/slider_cell.md`.
- **State arm.** Spring-loaded peg-stop arm above the transition
  cylinder; stop position drives the state register's slider to the
  new state. See `parts/state_register.md`.
- **State register.** The machine's current-state holder; a slider
  cell with state-labelled positions. See `parts/state_register.md`.
- **Symbol arm.** Spring-loaded peg-stop arm above the transition
  cylinder; stop position drives the writer arm to write the new
  symbol.
- **Symbol slider.** The slider inside a tape cell; one of 6 rest
  positions = one of 6 symbols.
- **Tape segment.** A modular section of the rail carrying a row of
  cells; segments chain end-to-end. See `PART_INVENTORY.md`.
- **Transition arms.** Collective name for the three spring-loaded
  peg-stop arms above the transition cylinder: symbol arm, direction
  arm, state arm.
- **Transition cylinder.** Six-faceted hexagonal cylinder carrying
  the 22 Rogozhin rules as peg-stops; rotates for column-select,
  read axially for row-select. See `PART_INVENTORY.md` and
  `DESIGN_INFLUENCES.md`.
- **UTM(m, n).** Universal Turing machine with m states and n
  symbols. This project implements UTM(4, 6).
- **Wedge.** Mechanism that deflects a pawl bar to release a slider's
  lock during the unlatched phase of a cycle. See `CYCLE.md`.
- **Writer arm.** Spring-loaded sweeping arm on the gantry; released
  during the write phase to drag the symbol slider to the new
  position dictated by the symbol arm's peg-stop.
