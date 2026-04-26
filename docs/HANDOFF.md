# Physical Universal Turing Machine — Project Handoff

`docs/VISION.md` is the source of truth on what this project is. If anything below conflicts with it, VISION.md wins.

## Purpose

Design a hand-operable, 3D-printable physical universal Turing machine based on Rogozhin's UTM(4,6) — 4 states, 6 symbols, 22 transition rules. Operator hand-programs a tape, then runs the machine by turning a hand crank. The tape is modular: any number of segments chained together, indefinitely extensible.

Output is a set of STL files plus build documentation. The whole machine is fully 3D-printable and hand-operated — no firmware, no electronics, no motor, ever. Allowed non-printed parts: standard nuts & bolts, and small magnets where they meaningfully help. The operator does symbol lookup against a printed transition card; that *is* the design, not a placeholder for an electronic version.

## Why Rogozhin (4,6) and not smaller

Rogozhin (4,6) is the smallest known *standard* UTM — finite input, halts on completion, universal in the conventional Turing-Davis sense. Wolfram's (2,3) was rejected: only weakly universal (Smith 2007 / Margenstern 2010), requires an infinite non-periodic tape pre-filled before run, and never halts. Bad fit for a physical demo where "load program, run, read result" is the operator's mental model.

(4,6) does mean a long tape — the machine simulates 2-tag systems, programs grow fast, plan for dozens of cells minimum. So tape modularity is a primary design driver.

## Tooling

- **build123d** (Python, OpenCASCADE B-rep) for all parametric parts. Picked over OpenSCAD because we want real Python (types, modules, tests) and over CadQuery because build123d is the cleaner-API successor.
- Output: STL for printing, optionally STEP for CAD interop.
- Validation: trimesh in the same Python env for sanity checks (volume, bounds, cross-sections, watertight check, center of mass).
- Viewing: viewstl.com or 3dviewer.net (drag-and-drop, no install) for the human; Claude Code has no GUI.

## Code architecture

Two layers, with the seam being the only place SOLID-style abstraction earns its keep (SOLID was overapplied earlier — it's a software idea, partially relevant to code that *generates* parts, not to the parts themselves).

**Lower layer**: build123d code that produces parts. One module per part: `tape_cell.py`, `rail.py`, `gantry.py`, etc. Each exposes a `Config` dataclass and a `make_X(cfg)` function returning a `build123d.Part`. Parametric, no globals, no implicit state.

**Upper layer** (not yet written): a `utm_spec.py` module that takes a UTM specification (states, symbols, transition table) plus a physical config (cell pitch, prism diameter, rail length) and produces a parts manifest — how many cells, how many rail segments, transition card SVG, BOM. Written so that swapping (4,6) for any other (m,n) Turing machine is data-only. The spec layer should depend on abstract part interfaces (`make_cell(symbol_count)`, `make_rail(cell_count, post_pitch)`), not hex-prism specifics, so triangular cells for (2,3) or pentagonal for (5,5) can drop in later.

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
   - *Reader arm*: hangs alongside the cell; 3 spring-loaded probes drop into pin-holes on the upward face. Probe up/down state = symbol (3-bit binary).
   - *Writer*: operator lifts head, edits cell by hand, drops head back. (A 3-plunger manual-lever writer is a possible refinement, still hand-driven.)
   - *State indicator*: 4-position rotary dial on top, color-coded.

4. **Drive** — rack on the rail's edge, pinion on the carriage, hand crank. Geared for 1 crank revolution = 1 cell of travel. Hand-cranked, full stop — no motor interface.

5. **End caps** — left and right terminators with the rail dovetail on one side, solid on the other. Cap the T-channel cleanly so the gantry can't run off the end.

6. **Transition table card holder** — frame for a laminated 4×6 (really 22-entry) lookup card. Clips to the gantry or sits beside the machine.

## Symbol encoding (decided)

3-bit binary pin pattern per face. Each face has 3 hole positions along the prism's long axis; bit set = hole drilled, bit clear = solid. 2³ = 8 patterns, use 6.

The tape cell as currently coded has **fixed** symbols at print time — face N is permanently symbol X. To "write," operator rotates the cell. This is correct for a UTM where the tape's *content* changes by writing, but here writing means: rotate the cell so the new symbol's face is up. All cells are identical at print time, programmed by orientation. (Design alternative considered and rejected: settable pegs that are pushed in/out per face. Too fiddly for v1.)

The reader has 3 spring-loaded probes; their up/down state on the upward face = the 3-bit symbol code. Operator looks at probe-flag positions, cross-references transition card, performs the action.

Suggested mapping: assign the most common symbol (Rogozhin's "blank" equivalent) to pattern `000` (no holes — easiest to read at a glance). Other 5 symbols to any 5 of the remaining 7 patterns. Mapping is a `face_patterns` list in `TapeCellConfig`.

Engraved labels on each face next to the pin column give a human-readable sanity check.

## Critical geometric interfaces

These three contracts are 80% of the engineering work. Tolerance them carefully and validate with test prints before committing to the full machine.

1. **Cell ↔ post fit** — bore diameter, detent dimple geometry, rotation friction. 0.4mm clearance on the bore is a reasonable FDM start; iterate. Detent dimples (currently hemispherical, 2mm diameter) must match a sprung bump on the post — bump not yet designed.

2. **Segment ↔ segment join** — dovetail + alignment pin + magnet. Guide rail (T-channel) must be continuous across the join to within ~0.2mm or the gantry's wheels will catch. Get this right once and the tape is genuinely modular.

3. **Gantry ↔ rail fit** — how the carriage rides the T-channel. Printed-plastic-on-printed-plastic wears, so this needs careful design: low-friction geometry, generous contact area, possibly a sacrificial wear surface that can be reprinted. Metal ball bearings would be easier but violate the print-only scope; only revisit that tradeoff if a printed solution proves genuinely unworkable after honest iteration.

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

1. **Draft `parts/rail.py`** — the tape segment. This is the next critical piece because it locks in cell pitch, post diameter, the sprung detent bump on the post (which must match the cell's dimples), and the segment-to-segment dovetail. Likely the second-hardest part after the gantry.

2. **Test print validation** — once the rail exists, the operator should print *one* cell + *one* rail and verify the cell-on-post fit, detent feel, and rotation friction before committing to anything else. This is a 2-3 hour exercise that prevents wasted prints later.

3. **Two-segment chain validation** — print 2 short rails and confirm the dovetail join holds the T-channel continuous within tolerance.

4. **Gantry / carriage** — the T-channel rider. Most complex part. Must work with printed contact surfaces (no metal bearings); design for low friction and replaceable wear surfaces. Reader probes are a sub-design here.

5. **Drive (rack + pinion + crank)** — straightforward gear math. Specify the gearing for 1-crank-rev = 1-cell.

6. **End caps + state dial + card holder** — cosmetic, save for last.

7. **Upper layer (`spec/utm_spec.py` + `spec/rogozhin_46.py`)** — once the parts code is stable, build the spec layer that takes a transition table + physical config and emits a full parts manifest and a printable transition card SVG. Encode Rogozhin's actual 22-rule (4,6) table from his 1996 paper (*Theoretical Computer Science* 168(2):215-240).

## Open questions / things to validate

- Pin diameter (2 mm) and pitch (4 mm) are conservative starting values; tune to what the target printer can resolve cleanly. A test print with descending hole sizes is the right first experiment.

- The detent scheme on the bottom of the cell (dimples engaging a sprung bump on the post) is unverified — alternatives include detents on the *side* of the bore engaging a sprung pin in the post, or a sprung washer at the post base. Pick one after the rail draft makes the geometry concrete.

- Label engraving uses single characters. Rogozhin's symbols in the original paper use multi-character notation (e.g. `b₁`, `c₁`). Either rewrite as single Unicode glyphs, or design face labels as small icon SVGs and emboss those. Defer until cosmetic pass.

- Operator ergonomics not yet considered — table height, head-rotation force, crank torque. Deal with after first end-to-end mechanical mockup.

- License: pick one before pushing to GitHub. CC-BY-SA 4.0 for the STL/docs and MIT for the code is a common combo for hardware projects.

## Constraints / preferences

- Keep code SOLID-ish only where it pays off — the part/spec seam, the abstract `make_X(cfg)` interface, dataclass configs. Don't over-engineer the geometry code itself.
- Brief explanations preferred. The user is a senior software engineer (~30 yrs) but not a mechanical engineer; flag any mechanical-engineering reasoning explicitly rather than treating it as obvious.
- Existing tools first: before designing a new geometric helper, check whether build123d already has it. Snap-fits, threads, gears, bearings have library support.
