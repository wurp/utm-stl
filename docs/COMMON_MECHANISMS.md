# Common Mechanisms

The mechanical abstractions the machine reuses across parts. "Common" here
means *abstraction*, not necessarily multiple instances today — a clearly
generalizable pattern earns an entry even with one current user, so per-
part docs reference it by link rather than redescribing it.

Each entry: what the mechanism is, when to reach for it, the geometry and
tolerance shape, and what fails if you deviate. Per-part docs cite these
by name; dimensions belong in the build123d code, not here.

## Sweeping arm with peg-stop output

A spring-loaded arm pivots or translates from a cocked position; on
release, it travels until it hits a fixed peg; the arm's final position
encodes the mechanism's output. Output values are discretized by the set
of available peg positions.

Reach for it when a discrete mechanical output must be selected from a
small set, and the selection itself is encoded as the position of a stop.
The arm doesn't need to know which output it is producing — the peg's
position determines the answer, and the peg layout encodes the lookup
table.

Geometry: arm pivot or rail with enough travel to reach any peg position;
spring or compliant flexure providing release force; cocking interface for
the crank to re-tension; release latch tripped at the right phase of the
cycle. Critical tolerance is the *relative* position of the peg with
respect to the arm's home — absolute position of either matters less.

Failure modes: insufficient spring force leaves the arm short of the peg;
excessive force overshoots and damages the peg or the arm; sloppy pivot
introduces output error proportional to the slop divided by arm length.

Used by: writer arm (drives the slider to the symbol-position selected by
the transition plate), and the three transition arms (new symbol, head
direction, new state).

## Flexure-returned latch

A latch held in its engaged state by a printed compliant flexure. A
mechanical input deflects the flexure to disengage the latch; on release,
the flexure restores the latch to engaged.

Reach for it when "engaged" is the safe default state — i.e. when stopping
mid-cycle should leave the mechanism latched, not free. Flexures avoid the
metal-spring scope exception (see `VISION.md`) and have no separate
return-spring part to lose.

Geometry: a thin printed beam or hinge that is straight when at rest and
bends elastically to disengage. The beam's length, thickness, and the
material's elastic limit set the deflection range and the engagement
force. Print orientation matters — flexures must be printed so layer lines
are not parallel to the bending axis.

Failure modes: too thin and it cracks; too thick and the deflection force
exceeds what the disengagement input can provide; printed across layer
lines and it delaminates after a few cycles.

Used by: the cell-resident lock that holds each slider in its current
detent.

## FDM detent

A dimple on the moving body engages a sprung bump on the housing (or vice
versa), giving a tactile "click" at each discrete position the moving
body should hold.

Reach for it when a translating or rotating part needs to register at
discrete positions without a separate locking mechanism, and the holding
force only needs to resist incidental disturbance — not deliberate load.
For deliberate locking, pair the detent with a flexure-returned latch.

Geometry: hemispherical or shallow-conical dimple sized to the bump's
radius; bump itself is a printed compliant feature (a small cantilever or
domed flexure) that deflects elastically as it crosses between dimples.
Holding force is set by the bump's spring rate and the dimple depth.
Pitch between dimples bounds the smallest distinguishable position.

Failure modes: bump too stiff and the moving body won't translate without
excessive force; too compliant and the detent doesn't hold; pitch too
fine for the printer's resolution and adjacent dimples merge.

Used by: slider detents inside the cell housing; per-cell registration
between the gantry carriage and the rail.

## Print-in-place with clearance gap

Two solids modeled inside one another, separated by an air gap thick
enough that the slicer treats them as independent bodies. After printing,
the parts come off the bed pre-assembled, mechanically interlocked but
free to move within the gap's constraints.

Reach for it when an enclosure-and-mover pair never needs to come apart,
and assembling the moving part through any opening would weaken the
enclosure.

Geometry: ~0.4 mm slip-fit clearance and ~0.2 mm press-fit clearance are
reasonable FDM starting values; tune to the target printer. The moving
part's overhangs must self-support or use easily-broken bridging — there
is no removable support inside a sealed enclosure.

Failure modes: clearance too tight and the parts fuse during printing;
too loose and the assembly rattles; bridging not breakable and the
moving part remains frozen.

Used by: the cell housing + slider pair (slider is captive inside the
housing once printed).

## Dovetail + alignment pin + magnet join

A self-aligning segment connection that combines three primitives:
geometric registration (dovetail tongues mating with grooves), positive
alignment (an alignment pin pressing into a hole), and pull-in force
(a magnet pair drawing the segments together).

Reach for it when two segments must mate repeatably with sub-millimeter
alignment across a join that the operator may break and remake (e.g.
when extending the tape). The dovetail handles gross alignment; the pin
removes the dovetail's remaining lateral slop; the magnet provides the
force that seats both.

Geometry: a dovetail profile sized so it engages with light push
pressure, an alignment pin running parallel to the seating direction,
and a small printed pocket for a press-fit neodymium magnet on each
side. Magnets are the only non-printed parts in this primitive.

Failure modes: dovetail too tight and the segments don't seat fully;
too loose and the pin takes load it shouldn't; magnet polarity reversed
and the join repels rather than attracts; insufficient face area means
inadequate magnetic pull-in force.

Used by: rail segment-to-segment joins. Likely applicable to end-cap
joins later.
