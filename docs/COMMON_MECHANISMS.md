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
the transition cylinder), and the three transition arms (new symbol, head
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

Used by: the pawl bar in the rack-and-sprung-pawl-bar primitive is
itself a flexure-returned latch — the bar's compliant pre-curve is the
flexure, and the wedge input is the disengagement input.

## FDM detent

A dimple on the moving body engages a sprung bump on the housing (or
vice versa), giving a tactile "click" at each discrete position the
moving body should hold.

Reach for it when a translating or rotating part needs to register at
discrete positions and the holding force only needs to resist
incidental disturbance. For deliberate locking against load, use the
rack-and-sprung-pawl-bar primitive.

Geometry: hemispherical or shallow-conical dimple sized to the bump's
radius; bump itself is a printed compliant feature (a small cantilever
or domed flexure) that deflects elastically as it crosses between
dimples. Holding force is set by the bump's spring rate and the dimple
depth. Pitch between dimples bounds the smallest distinguishable
position.

Failure modes: bump too stiff and the moving body won't translate
without excessive force; too compliant and the detent doesn't hold;
pitch too fine for the printer's resolution and adjacent dimples
merge.

Used by: per-cell registration between the gantry carriage and the
rail (light registration between deliberate gantry moves; not load-
bearing).

## Rack and sprung pawl bar

A rack of symmetric gear teeth on one edge of a translating slider
engages a long pawl bar — itself a printed compliant flexure — that runs
parallel to the slider's travel and is pre-curved so its rest shape
presses into the rack. A wedge input deflects the pawl bar away from
the rack to release the slider; on withdrawal, the bar springs back
into engagement and locks the slider at whichever tooth it landed on.

Reach for it when a translating part must hold at discrete positions
against deliberate load, not just incidental disturbance. Tooth-on-tooth
contact carries load in shear, which is much stronger than friction-
based detent retention; the pawl bar being a flexure means engagement
is the default state and there is no separate spring or loose part.

Geometry: symmetric (isosceles-triangle) tooth profile so the lock
holds equally against load from either direction along the slider's
travel — asymmetric saw teeth allow the slider to creep one way under
repeated load. Tooth pitch sets the position resolution: the slider's
discrete rest positions are quantized to the pitch, so the spacing
between intended positions must be an integer multiple of one tooth.
At least three teeth should be engaged in any rest position so the
load is distributed. Place the rack on the slider edge perpendicular
to any expected lateral force (e.g. from a sweeping read arm), so the
load is carried by the pawl teeth in shear rather than by the channel
walls in friction. The pawl bar's flexure thickness, length, and print
orientation set the engagement force and the wedge travel needed to
release.

Failure modes: asymmetric teeth — slider creeps one direction under
repeated read-arm impact; flexure too thin — bar cracks or fails to
re-engage; flexure too thick — wedge can't deflect it without
excessive input force; pitch finer than the printer can resolve —
adjacent teeth merge; fewer than ~3 teeth engaged — single-tooth
shear failure under load.

Used by: the slider in every slider cell (tape cells and the state
register).

## Print-flat-and-fold prism

A polygonal prism (or any faceted-surface part) printed as a single
flat strip of facets joined edge-to-edge, with shallow triangular
V-grooves along each fold line. After printing, the strip folds along
the V-grooves into the closed prism shape; the V-groove's two
triangular faces meet flush at each edge, registering adjacent facets
at the V-groove's complementary angle.

Reach for it when a part needs flat polygonal facets at exact angles
to one another, and the printer's accuracy across a curved or angled
geometry is worse than its accuracy on a flat surface. The V-groove
itself is the angular reference; the print's job is to deliver flat
facets and accurately-cut grooves, both of which are FDM's strengths.

Geometry: the strip prints flat with each facet as a flat panel and
each fold line as a triangular V-cut whose total included angle
equals 180° minus the desired exterior fold angle. For a regular
hexagonal prism (60° exterior fold), V-grooves are 120° included.
Cut depth must reach almost through the strip's thickness — a thin
remaining web acts as the hinge while still printing as one solid
part. Glue, snap features, or end-cap clips hold the closed prism
shut once folded; the V-groove faces in compression hold the angle.

Failure modes: web too thin and it tears during folding; web too
thick and the fold won't close cleanly; V-groove angle wrong and
adjacent facets meet with a gap or interfere; closed prism not
held shut and it springs open under load.

Used by: the transition cylinder (six facets, 60° folds, hexagonal
prism).

## Cam stack on a shaft

A set of cams of differing lobe profiles, all keyed to one rotating
shaft, each driving one mechanical event via a follower riding on its
profile. Continuous shaft rotation produces a sequenced set of timed
mechanical events whose ordering is set entirely by lobe placement
around each cam.

Reach for it when many events must be sequenced through one rotational
input, the ordering is fixed at design time, and runtime state-machine
logic (latches, interlocks) is unwanted. The shaft's angular position
is the system's state; reading it tells you exactly which events have
fired and which are pending.

Geometry: each cam is a printed disc with one or more lobes whose
radial profile defines the follower's displacement vs. crank angle.
Lobe rise should be gradual enough that the follower tracks the
profile without bouncing, and the dwell (constant-radius arc) at the
top of the lobe sets how long the driven phase holds at peak. The
cam disc bore press-fits or keys onto the shaft. Followers can be
sliding (a flat foot riding the profile) or rolling (a small printed
wheel on a pin); sliding is simpler to print but wears faster on
plastic-on-plastic.

Failure modes: lobe rise too steep — follower bounces off the cam
under load; dwell too short — driven event under-completes;
follower spring too weak — follower lifts off the cam during the
return stroke; cams not phased correctly to one another — events
fire in the wrong order; sliding follower wears a groove into the
cam after thousands of cycles.

Used by: the drive shaft, sequencing every phase of the transition
cycle (cell-select rotation and translation, lock-disengage,
write-release, write-travel, lock-reengage, move, state-update,
recock).

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
