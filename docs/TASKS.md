# Tasks

Active and queued work for the project. Completed work moves to a section at the bottom or is deleted once it's reflected in the docs.

## Active

### Reorganize docs top-down before writing more code

Restructure the project documentation so it works from the highest level down to per-part design, in this order:

1. **Vision** — what the machine is and the constraints that define it. (`docs/VISION.md` already covers this.)
2. **Design influences** — prior art surveyed, the encoding/mechanism archetypes considered, and which were chosen and why. The peg-stop transition mechanism, the binary-coded symbol encoding, the linear-slider cell, etc., all belong here as decisions with their justifications.
3. **Common mechanisms** — the small set of mechanical primitives the machine reuses across parts: spring-loaded arm with peg-stop output, gravity/flexure-returned lock bar, print-in-place with clearance gaps, FDM detent (dimple + sprung bump), dovetail + magnet segment join. Each described once, referenced by the parts that use it.
4. **Part inventory** — the list of parts and how they fit together, at the level of "what does each part do and what does it interface with." No dimensions; no build123d code.
5. **Per-part design docs** — one document per part, describing geometry, interfaces, tolerances, and open questions in enough detail that a build123d module is a mechanical translation of the doc.
6. **Code** — a build123d module per part, written *only after* the corresponding design doc is complete.

The current `docs/HANDOFF.md` mixes layers 2 through 5. Split its content into the new layered docs, then delete it — it was a one-time project-initialization document and has no role once the layered docs exist. Keep `VISION.md` as is. Drafts of layers 2–4 should land before any new per-part design doc; per-part docs land before any new code.

Once the higher-level design information for the slider cell is captured in the design-influences and per-part design docs, delete `3d-parts/slider_cell.py`. It was written ahead of its design doc, contains a known bug (lock bar must be cell-resident, not gantry-resident), and shouldn't be iterated on in place. Git history preserves it if needed.

## Queued

### Decisions to capture in the design-influences doc when the reorg happens

These are settled directionally but not yet written down in a layered doc. Capture them as decisions with their rationale so the per-part design docs can reference them.

- **Symbol is the slider's position.** Six detents = six symbols. The compute head interacts with the slider at one of six positions; the position itself is the input to downstream mechanisms, collapsing read and row-select on the transition plate into one mechanical operation — the slider's position *is* the row select.

- **Lock is cell-resident, flexure-returned.** Each cell housing contains its own lock that holds the slider in its current detent at rest, with a printed compliant flexure pressing the lock into engagement. The compute head, when it arrives over a cell, mechanically disengages that cell's lock for the duration of write, then withdraws to let the flexure re-engage it before leaving.

- **Transition mechanism is peg-stops on a printed plate.** Spring-loaded arms are released and travel until they hit pegs printed at the appropriate (state, symbol) row. One arm per output (new symbol, head direction, new state). The 22 rules are 22 sets of three pegs on one plate. Open: how (state, symbol) selects which row of pegs the arms see — translate the plate, translate the arms, or mask with a pin matrix.

- **Crank's job includes re-cocking.** Each transition cycle re-tensions every spring-loaded arm and trips the releases in sequence. This is a familiar mechanism class (mousetrap clockwork, escapement), not a new invention.

## Completed

(Empty.)
