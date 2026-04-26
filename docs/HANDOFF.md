# Physical Universal Turing Machine — Project Handoff

`docs/VISION.md` is the source of truth on what this project is. If anything below conflicts with it, VISION.md wins.

## Purpose

Design a crank-driven, 3D-printable physical universal Turing machine based on Rogozhin's UTM(4,6) — 4 states, 6 symbols, 22 transition rules. Operator hand-programs the tape (sets each cell's symbol by rotation), then runs the machine by turning a single crank. Cranking advances the machine through transitions — read the symbol under the head, look up the (state, symbol) entry in the embodied transition table, write the new symbol, move the head one cell L/R, change to the new state — until it halts. The operator supplies motion, not decisions. The tape is modular: any number of segments chained together, indefinitely extensible.

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

**Lower layer**: build123d code that produces parts. One module per part: `tape_cell.py`, `rail.py`, `gantry.py`, etc. Each exposes a `Config` dataclass and a `make_X(cfg)` function returning a `build123d.Part`. Parametric, no globals, no implicit state.

**Upper layer** (not yet written): a `utm_spec.py` module that takes a UTM specification (states, symbols, transition table) plus a physical config (cell pitch, prism diameter, rail length) and produces a parts manifest — how many cells, how many rail segments, the rule-encoding geometry (cam profiles / plate cutouts / pin-matrix data) for the transition mechanism, and a BOM. Written so that swapping (4,6) for any other (m,n) Turing machine is data-only. The spec layer should depend on abstract part interfaces (`make_cell(symbol_count)`, `make_rail(cell_count, post_pitch)`, `make_transition_mechanism(rules, state_count, symbol_count)`), not hex-prism specifics, so triangular cells for (2,3) or pentagonal for (5,5) can drop in later.

Suggested project layout:
```
parts/           # build123d modules — one per part
  tape_cell.py   # DONE
  rail.py        # NEXT
  gantry.py
  ...
spec/
  utm_spec.py    # upper layer, generates manifests
  rogozhin_46.py # the actual transition table data
tests/           # geometry sanity checks
build/           # generated STLs (gitignored)
docs/
  HANDOFF.md     # this file
```

## Part inventory

1. **Tape cell** — hex prism, 6 vertical faces = 6 symbols. Threads onto a vertical post on the rail. Hand-rotated to set symbol; detents click into 6 orientations. **Status: drafted in `tape_cell.py`, see below.**

2. **Rail / tape segment** — flat base with ~10 evenly spaced posts. Each post holds one tape cell with a sprung detent engaging the cell's bottom dimples. Both short ends carry a dovetail + alignment pin + magnet pair for chaining to neighbour segments. Long edges carry a continuous T-channel guide rail for the gantry to ride on. **Status: not started.**

3. **Gantry / head** — bridge straddling the tape, riding on the rail's T-channel via small wheels or printed sliders. Subassemblies:
   - *Carriage*: engages rails, has its own per-cell detent (one click per cell), so head locates exactly over one cell at a time.
   - *Reader arm*: hangs alongside the cell; 3 spring-loaded probes drop into pin-holes on the upward face. Probe up/down state (3-bit binary) is the input to the lookup mechanism.
   - *Writer linkage*: driven by the transition mechanism, rotates the cell under the head to the new symbol's orientation.

   The state register and the lookup mechanism may live on the gantry or in a fixed housing — decide alongside the mechanism class (see part 6).

4. **Drive** — crank into a main shaft that sequences the transition cycle (read → lookup → write → move → state-update). The crank-turns-per-transition ratio is a mechanism-design choice and may vary per transition. The crank is the sole runtime control and the sole interface to the outside world; it accepts a hand grip or a motor coupling.

5. **End caps** — left and right terminators with the rail dovetail on one side, solid on the other. Cap the T-channel cleanly so the gantry can't run off the end.

6. **Transition table mechanism** — the embodied 22-rule lookup. Takes (current state, current symbol) as inputs and produces (new symbol, head-move direction, new state) as outputs that drive the writer, the carriage advance, and the state register. The mechanism's footprint constrains the gantry, so its class is chosen before gantry geometry is finalized. **Status: not started — see "What's next" step 4 for candidates.**

## Symbol encoding (decided)

3-bit binary pin pattern per face. Each face has 3 hole positions along the prism's long axis; bit set = hole drilled, bit clear = solid. 2³ = 8 patterns, use 6.

Each face is fixed at print time — face N is permanently symbol X. All cells are identical; a cell is "programmed" by its orientation on the post. Writing, in this design, means rotating the cell so the target symbol's face is up.

The reader has 3 spring-loaded probes; their up/down state on the upward face = the 3-bit symbol code. The probe positions feed the transition mechanism, which together with the current-state register selects the matching transition rule and drives the writer / move / state update.

Suggested mapping: assign the most common symbol (Rogozhin's "blank" equivalent) to pattern `000` (no holes — easiest to read at a glance). Other 5 symbols to any 5 of the remaining 7 patterns. Mapping is a `face_patterns` list in `TapeCellConfig`.

Engraved labels on each face next to the pin column give the operator a human-readable sanity check when programming the tape.

## Critical geometric interfaces

These four contracts are most of the engineering work. Tolerance them carefully and validate with test prints before committing to the full machine.

1. **Probe state + state register → rule selection** — how the 3 probe positions plus the 4-position state register select one of 22 rules and drive the writer, the head's L/R motion, and the state update. The mechanism class chosen here sets the geometry budget for the gantry and the drive, so it is decided before either is finalized.

2. **Cell ↔ post fit** — bore diameter, detent dimple geometry, rotation friction. 0.4mm clearance on the bore is a reasonable FDM start; iterate. Detent dimples (currently hemispherical, 2mm diameter) must match a sprung bump on the post — bump not yet designed. The writer drives cell rotation against this detent, so detent force is part of the transition mechanism's torque budget.

3. **Segment ↔ segment join** — dovetail + alignment pin + magnet. Guide rail (T-channel) must be continuous across the join to within ~0.2mm or the gantry's wheels will catch. Get this right once and the tape is genuinely modular.

4. **Gantry ↔ rail fit** — how the carriage rides the T-channel. Printed-plastic-on-printed-plastic wears, so this needs careful design: low-friction geometry, generous contact area, possibly a sacrificial wear surface that can be reprinted.

## Tape cell — current state

`parts/tape_cell.py` is drafted and validated (volume ~11 cm³, dimensions correct, symmetric inertia tensor, cross-sections show expected features). Defaults:

- 25 mm across flats × 22 mm tall hex prism
- 5.4 mm bore (5 mm post + FDM clearance)
- 3 pin holes per face, 2 mm diameter, 4 mm pitch, 2.5 mm deep
- 6 hemispherical detent dimples on bottom face, 2 mm diameter, at 75% of apothem
- Engraved single-character label per face, 5 mm tall, 0.6 mm deep
- `TapeCellConfig` dataclass exposes every dimension; `face_patterns` is the symbol-code list, `face_labels` is the engraved characters

Known artifact: 12 broken faces in the STL at engraved-text edges (microscopic Text self-intersections). Slicers fix this silently. If a clean STL is needed, set `label_depth_mm=0` to skip engraving.

## What's next

In rough priority:

1. **Draft `parts/rail.py`** — the tape segment. This locks in cell pitch, post diameter, the sprung detent bump on the post (which must match the cell's dimples), and the segment-to-segment dovetail. Independent of the transition mechanism, so safe to do now.

2. **Test print validation** — once the rail exists, the operator should print *one* cell + *one* rail and verify the cell-on-post fit, detent feel, and rotation friction before committing to anything else. This is a 2-3 hour exercise that prevents wasted prints later.

3. **Two-segment chain validation** — print 2 short rails and confirm the dovetail join holds the T-channel continuous within tolerance.

4. **Transition mechanism feasibility sketch** — precedes gantry finalization. Sketch how 22 rules get embodied mechanically. Inputs: 3 probe states + 4-state register. Outputs: rotate the cell under the head to the new symbol's orientation, drive L/R head motion, update the state register. A transition may take many crank revolutions, and the count may differ between transitions. Candidates: rotating drum with 22 cam tracks indexed by (state, symbol); stack of 22 plates selected by a 6×4 pin matrix; Geneva-driven lookup wheel. Pick one direction; the gantry must accommodate it.

5. **Gantry / carriage** — the T-channel rider. Most complex passive part. Works with printed contact surfaces; design for low friction and replaceable wear surfaces. Reader probes and the writer's mechanical link to the transition mechanism are sub-designs here. Depends on step 4.

6. **Drive (crank + main shaft)** — crank turns a main shaft that sequences the transition cycle. Gear/cam profiles depend on the transition mechanism chosen in step 4. The crank accepts either a hand grip or a motor coupling at the same interface.

7. **End caps** — cosmetic, save for last.

8. **Upper layer (`spec/utm_spec.py` + `spec/rogozhin_46.py`)** — once the parts code and the transition mechanism class are stable, build the spec layer that takes a transition table + physical config and emits a full parts manifest, including the cam profiles / plate cutouts / pin-matrix that encode the 22 rules. Encode Rogozhin's actual 22-rule (4,6) table from his 1996 paper (*Theoretical Computer Science* 168(2):215-240). With the mechanism parameterized, swapping in a different (m,n) machine becomes a data change.

## Open questions / things to validate

- Pin diameter (2 mm) and pitch (4 mm) are conservative starting values; tune to what the target printer can resolve cleanly. A test print with descending hole sizes is the right first experiment.

- The detent scheme on the bottom of the cell (dimples engaging a sprung bump on the post) is unverified — alternatives include detents on the *side* of the bore engaging a sprung pin in the post, or a sprung washer at the post base. Pick one after the rail draft makes the geometry concrete.

- Label engraving uses single characters. Rogozhin's symbols in the original paper use multi-character notation (e.g. `b₁`, `c₁`). Either rewrite as single Unicode glyphs, or design face labels as small icon SVGs and emboss those. Defer until cosmetic pass.

- **Transition mechanism class.** 22 rules × (3-bit symbol output + L/R + 2-bit new state) is small enough to encode in printed geometry, but the mechanism class is open. The choice constrains gantry, drive, and writer geometry, so it is decided before any of those. See "What's next" step 4.

- Operator ergonomics: table height and crank torque. The crank drives the full transition cycle, so torque budget covers the writer, the carriage advance, and the lookup mechanism together. Deal with after first end-to-end mechanical mockup.

- License: pick one before pushing to GitHub. CC-BY-SA 4.0 for the STL/docs and MIT for the code is a common combo for hardware projects.

## Constraints / preferences

- The user is a senior software engineer (~30 yrs) but not a mechanical engineer; flag any mechanical-engineering reasoning explicitly rather than treating it as obvious. Brief explanations preferred.
- Existing tools first: before designing a new geometric helper, check whether build123d already has it. Snap-fits, threads, gears, bearings have library support.
