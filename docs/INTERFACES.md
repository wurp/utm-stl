# Interfaces

The geometric contracts between parts, plus the datum chain that keeps
those contracts coherent across the assembled machine. Interfaces are
*spatial*: where parts meet, what tolerances govern the meeting, and what
fails if those tolerances are violated. Cycle ordering — when things meet
in time — is in `docs/CYCLE.md`.

Each contract entry names the two sides, the contract, and the failure
mode. Tolerance numbers are TBD until validated by a test print; per-part
docs and the build123d code attach concrete values to the entries.

## Cell housing ↔ slider

The slider translates inside the cell housing along the cell's slider-
travel axis (perpendicular to the tape axis). Six rest positions along
the travel give the slider six discrete hold values = six symbols.

Contract:
- Slip-fit clearance between slider base and housing channel, sized to
  the print-in-place clearance primitive (`docs/COMMON_MECHANISMS.md`).
  The slider must translate freely under the writer arm's spring force
  with no jamming over the full travel.
- A row of symmetric gear teeth on one edge of the slider engages a
  long compliant pawl bar in the channel (rack and sprung pawl bar
  primitive, `docs/COMMON_MECHANISMS.md`). The pawl bar holds the
  slider in shear at every tooth; rest positions are quantized to the
  tooth pitch.
- The head's wedge input deflects the pawl bar far enough to clear
  the rack at all six rest positions. Withdrawal restores engagement
  within one cycle phase.
- The cylinder protruding from the slider through the cover slot is
  the read feature. Its diameter and height set the read arm's
  stopping geometry; the cylinder must withstand the read arm's
  spring force without deflecting laterally past the engaged lock.

Failure modes: slider jams (clearance too tight, or layer-line
artifacts in the channel wall); pawl bar fails to re-engage at some
positions (bar travel insufficient, or rack tooth profile asymmetric);
writer arm stalls against the slider (slider friction exceeds drive
margin during lock-disengaged phase); cylinder deflects under read-arm
load (cylinder too tall, or root not fileted, allowing the slider to
creep past the lock under sustained read-arm pressure).

This contract is owned by `docs/parts/slider_cell.md` on the cell side
and by the gantry head's wedge geometry and read-arm geometry on the
other.

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

## Slider position ↔ grid-cell select

The hexagonal transition cylinder is selected one cell at a time, by
two independent mechanical motions (`docs/DESIGN_INFLUENCES.md`).
Symbol = slider position means each motion's coupling is mechanical,
not informational.

**Column-select — symbol slider ↔ read arm ↔ cylinder rotation.**
The read arm on the gantry sweeps when released; the slider's
protruding cylinder stops the arm at one of six positions; the arm's
stop drives the transition cylinder's rotation through gearing,
landing one of six 60° facet positions under the readout. Contract:
angular tolerance must land within half a facet pitch (i.e., within
±30°) — easy in absolute terms, but the relevant tolerance is much
tighter at the peg-arm contact. With facet radius `R`, the angular
error in radians times `R` is the lateral displacement of the peg
under the readout arm; this must be small relative to the peg's own
diameter so the arm strikes the peg square-on. Failure mode: the
readout arm grazes the peg edge-on instead of striking it square,
producing under-travel.

**Row-select — state register ↔ readout-assembly axial translation.**
The state register's slider position drives the readout assembly along
the cylinder's axis to one of four row-positions. Contract: positional
tolerance within half a row pitch; the readout arms must hold position
against the spring force that releases them onto the pegs. Failure
mode: readout assembly lands one row off and reads the neighbouring
rule's pegs.

**Combined.** Both contracts compose into the peg-stop tolerance
budget tracked in `docs/TASKS.md`. The two axes are sized
independently; each has its own tolerance margin. The cylinder's
faceted-print accuracy contributes to the column-select error budget
and is gated by the test print called out in TASKS.

If the test print triggers the flat-plate fallback (see
`docs/DESIGN_INFLUENCES.md`), column-select becomes symbol-slider ↔
plate translation and row-select becomes state-register ↔ readout-arm
translation. Failure modes and tolerance shape are analogous; the
fallback doesn't affect any other interface in this document.

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
a millimeter-scale rest-position pitch unreliable. The cure is shared
datums: parts that need to align should reference the same physical
feature, so any error common to both cancels out.

**Common datum: the rail's T-channel surface.** The gantry rides on
it, the cell housings seat from it, the end caps register against
it, and the segment-to-segment join must keep it continuous. Every
part that needs to align with the gantry's path datums off the
T-channel.

**Critical chain: head coupler to slider rest position.** The five
links that determine whether the head's column-select coupler engages
the correct slider rest position:

1. Slider rest position → slider body. Set by the slider's printed
   rack geometry; one print, one part — small error.
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
gap between adjacent slider rest positions, which sets the maximum
off-by the coupler can tolerate before engaging the wrong row of pegs.
Tracked here as the integration-level constraint that no single part
owns.

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
