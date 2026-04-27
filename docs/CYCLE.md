# Cycle

What happens during one transition. The cycle document is *temporal*:
which mechanical events occur, in what order, with what force budget, and
where the operator is allowed to stop. The gantry, drive, and transition
cylinder must all agree on this cycle or they will fight at integration.

The phase list and the ordering constraints are settled. Crank-angle
assignments and force numbers are placeholders, filled in by the drive
doc and a force-budget test print; per-part docs attach phase-relative
constraints to the structure as they are drafted.

## Phases of one transition

A transition advances the machine from one configuration to the next:
read the symbol under the head, look up the (state, symbol) entry, write
the new symbol, move the head one cell, change to the new state. The
phases below break that into discrete mechanical events; each phase is
either active (something is moving) or static (the system is at rest in
a configuration the next phase will act on).

Phase ordering and timing are encoded in the cam stack on the crank
shaft (`docs/DESIGN_INFLUENCES.md`, cam-driven phase sequencing).
Each phase has a cam whose lobe placement around the shaft determines
when in the rotation that phase fires. The crank-turns-per-transition
ratio is a mechanism-design choice: one revolution if every phase fits
in its angular budget, more if recock or another phase needs more
travel. Phase ordering does not assume a fixed number of revolutions.

1. **Cell-select.** Two independent mechanical selections position the
   transition cylinder's readout. For column-select, the gantry's read
   arm is released and sweeps until stopped by the current cell's
   slider; the read arm's stop drives the cylinder's rotation through
   gearing, landing the selected facet (one of 6) under the readout.
   For row-select, the state register's slider position translates the
   readout assembly along the cylinder axis to the selected row (one
   of 4). Both are direct couplings — no encoding step — so each
   selection is one mechanical operation. The two may happen in either
   order or in parallel; sequencing is a drive-design choice.

2. **Lock-disengage.** The head's wedge deflects the cell's pawl bar
   away from the slider's rack to free the slider for writing. From
   this point until lock-reengage, the slider is unlatched; the cycle
   must not stop here.

3. **Write-release.** The writer arm's release latch is tripped; the
   spring-loaded arm begins traveling toward the slider, dragging the
   slider toward the symbol position selected by the transition cylinder.

4. **Write-travel.** The writer arm travels until it hits the peg at the
   target position. The slider is now at the new symbol's rest position.

5. **Lock-reengage.** The head withdraws the wedge; the cell's pawl bar
   springs back into the slider's rack and locks it. The slider is now
   latched at the new symbol.

6. **Move.** The gantry advances one cell in the direction the transition
   cylinder's direction-arm encodes.

7. **State-update.** A wedge cam on the drive shaft deflects the state
   register's pawl bar to disengage its lock; the state-arm then drives
   the register's slider to the new state encoded by the transition
   cylinder's state-arm; the wedge cam withdraws and the pawl bar
   re-engages the rack at the new tooth. The wedge cam's lobe leads
   the state-arm's lobe so the lock is open before the arm pulls and
   stays open until the arm has settled.

8. **Recock.** Every spring-loaded arm tripped this cycle is re-tensioned
   for the next cycle: writer arm, the three transition arms (symbol,
   direction, state), and the lock-disengagement input on the head.

The ordering constraint is that lock-disengage precedes write-release
(otherwise the writer drags against a locked slider) and lock-reengage
precedes move (otherwise the gantry leaves the cell with the slider
free). Recock may overlap with move and state-update if the drive layout
permits — these phases use independent mechanisms.

## Force / energy budget

The crank delivers, per cycle, the work required to advance the machine
through every phase above. The dominant terms are the spring potential
energy that recock restores. A running tally lives here so the budget is
visible as mechanisms are added — if total torque exceeds what one hand
can comfortably crank, the design is reconsidered before printing.

| Phase                                            | Energy / torque  |
|--------------------------------------------------|------------------|
| Lock-disengage flexure deflection (× cells touched) | TBD           |
| Writer arm spring potential energy               | TBD              |
| Symbol arm spring potential energy               | TBD              |
| Direction arm spring potential energy            | TBD              |
| State arm spring potential energy                | TBD              |
| Friction losses (slider, gantry, cylinder)       | TBD              |
| State-register lock-disengage flexure deflection | TBD              |
| **Total per cycle**                              | **TBD**          |
| **Operator comfort budget (one hand)**           | **TBD**          |

Springs are the limiting term in most printed clockwork, so they are
listed individually. Friction is currently a single line and is split as
the contact geometries are finalized.

## Safe-stop states

A safe-stop state is a crank position the operator may stop at and walk
away without leaving any cell unlatched, any arm in flight, or any output
mid-update.

Currently identified safe-stop states:

- **Cycle complete, before next read.** All locks engaged, all arms
  recocked, state register at its new state, gantry at its new cell.
  This is the canonical safe-stop — the machine is in a complete
  configuration.

States that are *not* safe to stop at:

- Between lock-disengage and lock-reengage (slider unlatched).
- During write-travel (arm in flight; partial state).
- During move (gantry between cells; per-cell detent not yet engaged).
- Between state-register lock-disengage and lock-reengage (state output is intermediate).

Because phase ordering is cam-driven, every safe-stop state corresponds
to a specific crank-angle range — the angles at which all cams are
either at rest dwell or have completed their lobes. If one crank
revolution maps to one transition, the canonical safe-stop is the
crank's home angle. If N revolutions map to one transition, the
safe-stop window is the angle range during the final revolution after
all cams have completed.

The safe-stop set may grow as the cycle is refined — for example, if
recock is sequenced into a separate sub-cycle, a safe-stop between
"transition complete" and "recock complete" may be useful for an
operator who wants to inspect the tape mid-program.
