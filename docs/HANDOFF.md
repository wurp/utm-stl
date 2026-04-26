# Physical Universal Turing Machine — Project Handoff

`docs/VISION.md` is the source of truth on what this project is. If anything below conflicts with it, VISION.md wins.

## Purpose

Design a crank-driven, 3D-printable physical universal Turing machine based on Rogozhin's UTM(4,6) — 4 states, 6 symbols, 22 transition rules. Operator hand-programs the tape (sets each cell's symbol by sliding its slider to the desired detent), then runs the machine by turning a single crank. Cranking advances the machine through transitions — read the symbol under the head, look up the (state, symbol) entry in the embodied transition table, write the new symbol, move the head one cell L/R, change to the new state — until it halts. The operator supplies motion, not decisions. The tape is modular: any number of segments chained together, indefinitely extensible.

Output is a set of STL files plus build documentation. The whole machine is fully 3D-printable and crank-operated. No active electronics are part of the machine. Allowed non-printed parts: standard nuts & bolts, and small magnets where they meaningfully help. The crank may be turned by hand or by an external motor coupled to it; the motor is external to the machine. The 22-rule transition table is embodied in printed geometry — cams, followers, plates; exact mechanism TBD.

The ratio of crank turns to transitions is a mechanism-design choice, not a fixed contract. Different transitions may take different amounts of cranking. The mechanism may sequence read → lookup → write → move → state-update across many revolutions, and across a variable number of revolutions per transition.

## Why Rogozhin (4,6)

Rogozhin (4,6) is the smallest known *standard* UTM — finite input, halts on completion, universal in the conventional Turing-Davis sense. That matches the operator's mental model for a physical demo: load program, run, read result.

Smaller weakly-universal machines (e.g. Wolfram (2,3), proven universal by Smith 2007 / Margenstern 2010) require an infinite non-periodic tape pre-filled before the run and never halt, so they don't fit that model.

(4,6) does mean a long tape — the machine simulates 2-tag systems, programs grow fast, plan for dozens of cells minimum. The tape is modular for this reason: chain segments to the length the program needs.

## Tooling

- **build123d** (Python, OpenCASCADE B-rep) for all parametric parts.
- Output: STL for printing, optionally STEP for CAD interop.
- Validation: trimesh in the same Python env for sanity checks (volume, bounds, cross-sections, watertight check, center of mass).
- Viewing: viewstl.com or 3dviewer.net (drag-and-drop, no install) for the human; Claude Code has no GUI.

## Code architecture

Two layers, with the parts/spec seam as the only place SOLID-style abstraction earns its keep. Inside `parts/`, geometry code stays flat and procedural — no class hierarchies, no interfaces.

**Lower layer**: build123d code that produces parts. One module per part: `slider_cell.py`, `rail.py`, `gantry.py`, etc. Each exposes a `Config` dataclass and a `make_X(cfg)` function returning a `build123d.Part`. Parametric, no globals, no implicit state.

**Upper layer** (not yet written): a `utm_spec.py` module that takes a UTM specification (states, symbols, transition table) plus a physical config (cell pitch, slider travel, rail length) and produces a parts manifest — how many cells, how many rail segments, the peg coordinates on the transition plate that encode the rules, and a BOM. Written so that swapping (4,6) for any other (m,n) Turing machine is data-only. The spec layer depends on abstract part interfaces (`make_cell(symbol_count)`, `make_rail(cell_count, cell_pitch)`, `make_transition_plate(rules, state_count, symbol_count)`), so a different (m,n) drops in by changing the symbol count (more detents on the slider, more bump lanes if needed) and the transition plate's row count.

Suggested project layout:
```
3d-parts/         # build123d modules — one per part
  slider_cell.py  # DONE
  rail.py         # NEXT
  gantry.py
  ...
spec/
  utm_spec.py     # upper layer, generates manifests
  rogozhin_46.py  # the actual transition table data
tests/            # geometry sanity checks
build/            # generated STLs (gitignored)
docs/
  HANDOFF.md      # this file
```

## Part inventory

1. **Tape cell** — flat housing containing a single linear slider that translates perpendicular to the tape axis. Six detent positions along the slider's travel = six symbols. The slider carries a 6×3 grid of bumps along its length; in any detent position, one column of 3 bumps sits under three stationary reader probes on the gantry, giving a parallel 3-bit read. A lock bar drops into a notch on the slider top to hold it in position; a triangle pin pushed in from above lifts the lock bar to free the slider for writing. **Status: drafted in `3d-parts/slider_cell.py`, see below.**

2. **Rail / tape segment** — flat base that holds ~10 cell housings in a row, cells tiling along the tape axis. Both short ends carry a dovetail + alignment pin + magnet pair for chaining to neighbour segments. Long edges carry a continuous T-channel guide rail for the gantry to ride on. **Status: not started.**

3. **Gantry / head** — bridge straddling the tape, riding on the rail's T-channel via small wheels or printed sliders. Subassemblies:
   - *Carriage*: engages rails, has its own per-cell detent (one click per cell), so head locates exactly over one cell at a time.
   - *Reader*: 3 spring-loaded probes drop onto the slider's upward bump grid in the column currently latched under the head. Probe up/down state is the 3-bit symbol code.
   - *Writer*: a triangle pin descends to lift the cell's lock bar; a zero-arm sweeps the slider to its home end stop; a write-arm under spring tension is released and drags the slider toward +X until it hits a peg printed on the transition plate; the triangle pin withdraws and the lock bar drops into the notch above the new detent column.
   - *State register*: 4-position indexed register driven by the transition plate's state output.

   The state register and the transition plate live in a fixed housing alongside the gantry; the gantry carries the reader, writer, and triangle pin actuators.

4. **Drive** — crank into a main shaft that sequences the transition cycle (read → row-select → release write-arm → move → state-update) and re-cocks the springs between cycles. The crank-turns-per-transition ratio is a mechanism-design choice and may vary per transition. The crank is the sole runtime control and the sole interface to the outside world; it accepts a hand grip or a motor coupling.

5. **End caps** — left and right terminators with the rail dovetail on one side, solid on the other. Cap the T-channel cleanly so the gantry can't run off the end.

6. **Transition table mechanism** — a printed plate with the 22 rules embodied as physical pegs. The plate is laid out as a grid: rows indexed by (current state, current symbol), columns split into three output tracks (new symbol, head direction, new state). Each rule places one peg on each output track in the position that encodes the output value. To execute a rule, the (state, symbol) pair selects a row by translating the plate (or the arms above it) along one axis; spring-loaded arms above each output track are then released and travel until they hit their respective pegs. The arm's stop position drives the corresponding output: writer slider, head L/R latch, state register. **Status: not started — row-selection mechanism is the next open question, see "What's next" step 4.**

## Symbol encoding (decided)

3-bit binary bump pattern per detent column. Each cell's slider carries a 6×3 grid of bumps on its top face: 6 columns along the travel axis, 3 lanes across. In any latched detent position k, column k sits under the gantry's three stationary reader probes; the bumps' presence/absence in that column = the 3-bit symbol code. 2³ = 8 patterns, use 6.

The slider carries all 6 symbol patterns at print time — every cell is identical. The cell is "programmed" by sliding to the detent column that holds the desired pattern. Writing, in this design, means unlocking the slider, sweeping it to home, then releasing a spring-loaded arm that drags it to the new detent column.

Suggested mapping: assign the most common symbol (Rogozhin's "blank" equivalent) to pattern `001` (one bump — distinguishable from "no slider" or "no cell" which read as `000`). Other 5 symbols to any 5 of the remaining patterns. Mapping is `symbol_patterns` in `SliderCellConfig`.

Engraved labels along the slider top edge give the operator a human-readable sanity check when programming the tape.

## Critical geometric interfaces

These four contracts are most of the engineering work. Tolerance them carefully and validate with test prints before committing to the full machine.

1. **Probe state + state register → rule selection** — how the 3 probe positions plus the 4-position state register select one of 22 rules and drive the writer, the head's L/R motion, and the state update. The mechanism class is the peg-stop transition plate (see part 6); the open sub-problem is the row-selection geometry that translates (state, symbol) into "which row of pegs the arms see." This is decided before the gantry is finalized.

2. **Cell housing ↔ slider fit** — slot dimensions, FDM clearance, detent dimple geometry, sliding friction. ~0.4 mm slip-fit clearance is a reasonable FDM start; iterate. Detent dimples on the slider underside (currently 1.6 mm hemispheres at 3 mm pitch) must match a sprung bump in the cell floor — bump geometry is a printed compliant feature, not yet validated. The write-arm spring force must overcome detent retention plus slider friction.

3. **Segment ↔ segment join** — dovetail + alignment pin + magnet. Guide rail (T-channel) must be continuous across the join to within ~0.2 mm or the gantry's wheels will catch. Cell pitch must be exact across the join so the gantry's per-cell detent stays aligned. Get this right once and the tape is genuinely modular.

4. **Gantry ↔ rail fit** — how the carriage rides the T-channel. Printed-plastic-on-printed-plastic wears, so this needs careful design: low-friction geometry, generous contact area, possibly a sacrificial wear surface that can be reprinted.

## Tape cell — current state

`3d-parts/slider_cell.py` is drafted as a print-in-place housing+slider pair. Defaults:

- 40 mm × 25 mm × 12 mm cell housing (cell pitch 25 mm along tape axis)
- Slider 30 × 8 × 6 mm, 15 mm travel along the cell's X axis (perpendicular to tape)
- 6 detent positions at 3 mm pitch with 1.6 mm hemispherical dimples on slider underside
- 6×3 bump grid on slider top: 1.8 mm diameter, 1.2 mm tall, 2 mm lane pitch along Y
- Lock bar pocket along Y above the slider, sized for a 3 × 3 mm bar
- Triangle-pin port (4 mm side) cut through the housing top to lift the lock bar
- `SliderCellConfig` dataclass exposes every dimension; `symbol_patterns` is the 3-bit code list, `symbol_labels` is the human-readable sanity-check labels

Print-in-place strategy: slider is modeled as a separate solid inside the housing slot with ~0.4 mm clearance on all sides. The slicer treats it as a free body. After printing, breaking any bridge supports frees the slider to translate.

## What's next

In rough priority:

1. **Test print the slider cell** — print one `slider_cell.py` housing+slider as-is and verify: slider releases cleanly from print-in-place support, slides freely with the modeled clearances, detent dimples engage perceptibly when a corresponding bump is added, the lock bar (a separate test print, just a 3×3 mm bar) drops cleanly into the notches. This is a 2-3 hour exercise that gates everything downstream — if the slider doesn't print free or the detents don't feel right, the cell geometry needs revision before the rail.

2. **Draft `3d-parts/rail.py`** — the tape segment. Holds ~10 cell housings tiled along the tape axis. Locks in segment-to-segment dovetail, the T-channel for the gantry, and the per-cell registration that keeps the slider's bump grid aligned with the gantry's reader probes. Cell housings may be integral to the rail (one print per segment) or socketed (cells snap into rail slots) — decide during the draft.

3. **Two-segment chain validation** — print 2 short rails and confirm the dovetail join holds the T-channel and cell pitch continuous within tolerance.

4. **Row-selection mechanism for the transition plate** — the open sub-problem in part 6. The peg-stop output trick is settled (spring-loaded arms hit pegs printed on the plate); what's not settled is how (current state, current symbol) selects which row of pegs the arms see. Candidates: translate the plate in two axes (state along one, symbol along the other) so the right row is under the arms; translate the arms instead of the plate; use a 6×4 pin matrix above the plate that masks all rows except the selected one. Pick one direction; the gantry geometry depends on it.

5. **Gantry / carriage** — the T-channel rider. Carries reader probes, triangle-pin actuator, zero-arm, write-arm spring catch. Works with printed contact surfaces; design for low friction and replaceable wear surfaces. Depends on step 4.

6. **Drive (crank + main shaft)** — crank turns a main shaft that sequences the transition cycle and re-cocks the springs (cell-lock triangle pin, zero-arm, write-arm, direction arm, state-register arm) between cycles. Gear/cam profiles depend on the row-selection mechanism chosen in step 4. The crank accepts either a hand grip or a motor coupling at the same interface.

7. **End caps** — cosmetic, save for last.

8. **Upper layer (`spec/utm_spec.py` + `spec/rogozhin_46.py`)** — once the parts code and the row-selection mechanism are stable, build the spec layer that takes a transition table + physical config and emits a full parts manifest, including the peg coordinates on the transition plate that encode the 22 rules. Encode Rogozhin's actual 22-rule (4,6) table from his 1996 paper (*Theoretical Computer Science* 168(2):215-240). With the mechanism parameterized, swapping in a different (m,n) machine becomes a data change — for a different (m,n) the plate gains rows and the arms gain travel range, but the mechanism class stays the same.

## Open questions / things to validate

- Bump diameter (1.8 mm) and lane pitch (2 mm) on the slider are conservative starting values; tune to what the target printer can resolve cleanly and what the reader probes can discriminate. A test print with descending bump sizes is the right first experiment.

- The detent scheme (dimples on the slider underside engaging a sprung bump in the cell floor) needs the bump itself designed as a printed compliant feature. The write-arm spring's torque must overcome detent retention plus sliding friction by a margin large enough to be reliable across temperature and wear.

- Triangle-pin port shape: equilateral triangle is chosen so the pin can only insert in one orientation, and the housing-side port keys to it. Whether the pin lifts the lock bar by a wedge action or by direct contact with a flange on the bar is unresolved.

- Label engraving on the slider top edge uses single characters. Rogozhin's symbols in the original paper use multi-character notation (e.g. `b₁`, `c₁`). Either rewrite as single Unicode glyphs, or emboss small icon SVGs. Defer until cosmetic pass.

- **Row-selection geometry for the transition plate.** Settled is the peg-stop output. Open is how the plate (or the arms above it) is positioned so the correct row of pegs is reachable for a given (state, symbol). The choice constrains gantry footprint, drive sequencing, and re-cocking geometry. See "What's next" step 4.

- Operator ergonomics: table height and crank torque. The crank drives the full transition cycle including re-cocking every spring, so torque budget covers all arms together. Deal with after first end-to-end mechanical mockup.

- License: pick one before pushing to GitHub. CC-BY-SA 4.0 for the STL/docs and MIT for the code is a common combo for hardware projects.

## Constraints / preferences

- The user is a senior software engineer (~30 yrs) but not a mechanical engineer; flag any mechanical-engineering reasoning explicitly rather than treating it as obvious. Brief explanations preferred.
- Existing tools first: before designing a new geometric helper, check whether build123d already has it. Snap-fits, threads, gears, bearings have library support.
