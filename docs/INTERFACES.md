# Interfaces

The geometric contracts between parts, plus the datum chain that keeps
those contracts coherent across the assembled machine. Interfaces are
*spatial*: where parts meet, what tolerances govern the meeting, and what
fails if those tolerances are violated. Cycle ordering — when things meet
in time — is in `docs/CYCLE.md`.

Each contract entry names the two sides, the contract, and the failure
mode. Tolerance numbers are TBD where they have not yet been validated by
a test print; the entries exist so per-part docs and the build123d code
can attach values to them.

## Cell housing ↔ slider

The slider translates inside the cell housing along the cell's slider-
travel axis (perpendicular to the tape axis). Six detents along the
travel give the slider six discrete hold positions = six symbols.

Contract:
- Slip-fit clearance between slider and housing slot, sized to the FDM
  slip-fit primitive (`docs/COMMON_MECHANISMS.md`). The slider must
  translate freely under the writer arm's spring force minus detent
  retention, with no jamming over the full travel.
- Detent geometry pairs a dimple on the slider with a sprung bump on the
  housing (FDM detent primitive). Holding force resists incidental
  disturbance but yields to the writer arm's drive force with margin.
- The cell-resident flexure-returned lock (`docs/COMMON_MECHANISMS.md`)
  engages the slider in any of the six detent positions. The head's
  lock-disengagement input deflects the flexure cleanly without damaging
  it; release restores engagement within one cycle phase.

Failure modes: slider jams (clearance too tight, or layer-line
artifacts in the slot wall); slider rattles and detents don't hold
(clearance too loose, or bump too compliant); lock fails to engage at
some detent positions (flexure travel insufficient, or lock geometry
asymmetric across the detent range); writer arm stalls against detent
(detent retention exceeds drive margin).

This contract is owned by `docs/parts/slider_cell.md` on the cell side
and by the gantry head's lock-disengagement geometry on the other.

## Segment ↔ segment

Adjacent rail segments mate end-to-end so the tape extends to whatever
length the program needs. The join carries both the cell row (cell
pitch must remain exact across the join) and the gantry's running
surface (the T-channel must remain continuous).

Contract:
- The segment join uses the dovetail + alignment pin + magnet primitive
  (`docs/COMMON_MECHANISMS.md`). The dovetail handles gross alignment;
  the pin removes lateral slop; the magnet provides seating force.
- The T-channel surface is continuous across the join within a tolerance
  small enough that the gantry's wheels or sliders do not catch on the
  step. Order of magnitude: ~0.2 mm; tighter if the gantry uses
  sliding pads rather than wheels.
- Cell pitch across the join equals the in-segment cell pitch within a
  tolerance small enough that the gantry's per-cell detent stays
  aligned with each cell's slider over many segments.

Failure modes: gantry catches at the join (T-channel discontinuity);
per-cell detent drifts out of alignment as the gantry moves down a
multi-segment tape (cell-pitch error accumulates); join works loose
during operation (magnet pull-in insufficient relative to operating
forces).

## Gantry ↔ rail

The gantry rides on the rail's T-channel. Both parts are FDM-printed
plastic, so contact between them wears.

Contract:
- The gantry carriage engages the T-channel with low-friction geometry
  and generous contact area. Per-cell detent (FDM detent primitive,
  `docs/COMMON_MECHANISMS.md`) registers the gantry over each cell.
- Wear surfaces are designed to be replaceable — the gantry's running
  pads are separable from the rest of the gantry so they can be
  reprinted as they wear without rebuilding the whole gantry.
- The gantry travels in both directions along the rail, driven by the
  direction-arm's output via whatever transmission the drive provides.
  The carriage must not back-drive — the head's position must hold
  between transitions when the move-mechanism is idle.

Failure modes: friction too high (operator can't crank); contact area
too small (rapid wear, eventual rattle); wear pads fused to the
carriage (replaceability lost); back-drive (gantry drifts off-cell
during recock or operator pause).

## Slider position ↔ row-select

The transition plate's row-select input must be driven by the current
cell's slider position (combined with the state register's output).
Symbol = slider position (`docs/DESIGN_INFLUENCES.md`) means the
coupling is mechanical, not informational — the slider's position
physically translates into the row offset of the transition plate.

Contract: open. The mechanism class for row-selection is not yet
chosen (translate plate, translate arms, or pin-matrix mask — see
`docs/DESIGN_INFLUENCES.md`). Once chosen, the contract names the two
sides (slider-position takeoff vs. plate / arm / mask input), the
positional tolerance required to land on the correct row, and the
failure mode when the row-select drifts off by half a row pitch.

This is the highest-leverage open interface in the design. Resolving
it precedes the gantry and drive per-part docs.

## Datum chain

A datum is the physical surface or feature a part's geometry is
measured from. Mechanical engineers track *which surface* is the
datum because every measurement carries error and errors accumulate
along the chain of "this is measured from that, which is measured
from that other thing." If two parts that need to align are measured
from different datums separated by several intermediate parts, the
intermediate tolerances stack up and the alignment fails.

FDM dimensional accuracy is on the order of ±0.2 mm per feature. A
five-part chain stacks to ±1 mm worst-case, which is enough to make
a millimeter-scale detent pitch unreliable. The cure is shared
datums: parts that need to align should reference the same physical
feature, so any error common to both cancels out.

**Common datum: the rail's T-channel surface.** The gantry rides on
it, the cell housings seat from it, the end caps register against
it, and the segment-to-segment join must keep it continuous. Every
part that needs to align with the gantry's path datums off the
T-channel.

**Critical chain: head coupler to slider detent.** The five links
that determine whether the head's row-select coupler engages the
correct slider detent:

1. Slider detent → slider body. Set by the slider's printed
   geometry; one print, one part — small error.
2. Slider body → cell housing slot. Set by the slider/housing
   slip-fit clearance.
3. Cell housing → rail seating. Set by the housing-to-rail mounting
   geometry. Houses can be integral to the rail or socketed; integral
   eliminates this link entirely.
4. Rail seating → T-channel. Set by the rail's printed geometry.
   Datum-side; small error if cell seats and T-channel are printed
   in one part.
5. T-channel → gantry carriage → coupler. Set by the gantry-to-rail
   contact and the gantry's own geometry.

Worst-case error budget: TBD. Smallest clearance to land within: the
gap between adjacent slider detents, which sets the maximum off-by
position the coupler can tolerate before engaging the wrong row of
pegs. Tracked here as the integration-level constraint that no single
part owns.

**Mitigations available, mapped to chain links:**

- *Cell housings integral to the rail* (decision deferred to
  `docs/parts/rail.md` when written) eliminates link 3 — slider slot
  and T-channel are printed as one part, no inter-part tolerance.
- *Per-cell detent on the gantry* (FDM detent primitive) actively
  re-aligns the gantry against the cell row, partially absorbing
  errors from links 4–5.
- *Dovetail + alignment pin + magnet* on segment joins (`docs/INTERFACES.md` segment↔segment contract) cancels error at the
  join itself, preventing cross-segment accumulation.

A full numeric stack-up analysis lands once the gantry and rail per-
part docs are drafted and tolerance targets are picked. The chain
listed above is the roadmap for that analysis.
