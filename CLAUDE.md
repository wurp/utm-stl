Physical Universal Turing Machine — 3D-printable parts generated from build123d Python.

`docs/VISION.md` is the source of truth on what this project is. Read it first; if anything
here conflicts with it, VISION.md wins.

Read `docs/HANDOFF.md` for the full project context (why Rogozhin (4,6), part inventory,
what's next). This file covers conventions for working in the repo.

## Project layout

parts/        # build123d modules — one per physical part
spec/         # (not yet created) upper layer: UTM spec → parts manifest
tests/        # (not yet created) trimesh-based geometry sanity checks
build/        # generated STLs, gitignored
docs/HANDOFF.md

The parts/spec seam is the only place SOLID-style abstraction is wanted. Don't introduce
class hierarchies or interfaces inside `parts/` — geometry code stays flat and procedural.

## Per-part conventions

Every module in `parts/` follows the same shape (see `parts/tape_cell.py` as the reference):

- A frozen-ish `XConfig` dataclass exposing every dimension as a field with a default.
- A `make_x(cfg: XConfig = XConfig()) -> build123d.Part` function. No globals, no
  module-level state, no I/O at import time.
- A `__main__` block that constructs with defaults, exports an STL to `/tmp/`, and prints
  a short summary. Keep this — it's the one-liner smoke test.
- Coordinate convention: +Z is the part's primary axis. Document the convention at the
  top of the file when it matters (see tape_cell.py docstring).

When adding a new part, mirror this structure exactly. Don't invent a new pattern.

## Tooling

- **build123d** for all geometry. Check the build123d API before writing a geometric
  helper from scratch — snap-fits, threads, gears, bearings, fillets, chamfers all have
  library support. Don't reinvent.
- **trimesh** for validation (volume, bounds, watertight, center of mass, cross-sections).
- STL is the primary output; STEP is optional.
- No GUI here — the user views STLs at viewstl.com or 3dviewer.net.

Run a part module directly to regenerate its STL: `python parts/tape_cell.py`.

## Mechanical engineering hygiene

- The user is a senior software engineer but not a mechanical engineer. Flag any
  non-obvious mechanical reasoning explicitly (tolerances, FDM artifacts, fits, friction,
  stress, gear ratios) rather than assuming it's shared knowledge.
- FDM clearance rule of thumb: ~0.4 mm on slip fits, ~0.2 mm on press fits. State the
  assumption in the config comment when you pick one.
- The three load-bearing geometric interfaces are: cell↔post, segment↔segment, gantry↔rail.
  Changes that touch tolerances on these must be called out — they're the contracts that
  break the machine if violated.

## STL artifacts

Engraved `Text` features can produce microscopic self-intersections (broken faces) at
glyph edges. Slicers handle this silently; trimesh will flag it. If you need a perfectly
clean STL, set `label_depth_mm=0` to skip engraving. Don't chase these defects otherwise.

## Hard scope: print-only, hand-operated

This machine is fully 3D-printable and hand-operated. No firmware, no electronics, no
motor — ever. Operator hand-cranks (or hand-advances) the gantry and does symbol lookup
against a printed transition card.

Allowed non-printed parts: standard nuts & bolts, and small magnets where they
meaningfully help (e.g. segment alignment). Springs should be printed (compliant
flexures) where feasible; if a metal spring is the only practical option for a given
mechanism, flag it explicitly and propose a printed alternative first.

Do not propose MCUs, sensors, motors, solenoids, encoders, or any active electronics.
If a design problem seems to need one, the answer is to redesign the mechanism, not to
add electronics. There is no "v2 with electronics" — that direction is closed.

## Workflow notes

- For non-trivial changes (new part, geometric interface change, spec layer work), enter
  plan mode before coding.
- After a logical change to a part, run the module's `__main__` and have the user eyeball
  the STL before moving on. There is no automated visual regression test.
- When uncertain about a build123d API or tolerance, write a small standalone script in
  `/tmp/` and verify before editing the real part.
