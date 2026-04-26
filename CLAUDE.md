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

## Hard scope: print-only, crank-driven

The machine is fully 3D-printable and crank-driven. No active electronics are part of
the machine.  The crank is the sole runtime control and the sole interface to the
outside world; it accepts a hand grip or an external motor coupling at the same
interface, and any such motor is external to the machine.

The transition table is embodied in printed geometry that drives the writer, head
direction, and state register. The operator supplies motion via the crank; the
machine performs read, lookup, write, move, and state update.

Allowed non-printed parts: standard nuts & bolts, and small magnets where they
meaningfully help (e.g. segment alignment). Springs should be printed (compliant
flexures) where feasible; if a metal spring is the only practical option for a given
mechanism, flag it explicitly and propose a printed alternative first.

If a design problem seems to need active electronics, the answer is to redesign the
mechanism.

## Documentation style

Project docs (`VISION.md`, `HANDOFF.md`, `CLAUDE.md`, anything in `docs/`) are
greenfield reference documents. Each section is a standalone description of
the current state of the project, readable cold by someone who has never seen
a prior version.

- State each rule directly. Describe what the design *is*, not what it isn't,
  and not what it once was.
- Scope boundaries and forward-looking exceptions are part of the rule itself
  and belong in the doc ("the crank accepts a hand grip or a motor coupling at
  the same interface"). Catalogues of alternatives that were considered and
  set aside do not.
- Justify priority with concrete consequences ("this constrains gantry
  geometry, so resolve it before drafting the gantry"), not with meta-ranking
  ("highest-priority", "biggest unsolved").
- When a request is phrased as "change X to Y", produce prose that reads as if
  Y were the original design. The diff captures the change; the doc captures
  the result.

## Workflow notes

- For non-trivial changes (new part, geometric interface change, spec layer work), enter
  plan mode before coding.
- After a logical change to a part, run the module's `__main__` and have the user eyeball
  the STL before moving on. There is no automated visual regression test.
- When uncertain about a build123d API or tolerance, write a small standalone script in
  `/tmp/` and verify before editing the real part.
