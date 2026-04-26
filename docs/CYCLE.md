# Cycle

What happens during one transition. The cycle document is *temporal*:
which mechanical events occur, in what order, with what force budget, and
where the operator is allowed to stop. The gantry, drive, and transition
plate must all agree on this cycle or they will fight at integration.

The cycle is currently a skeleton — the phase list and the ordering
constraints are settled, but most crank-angle assignments and force
numbers are TBD. The structure exists so per-part docs have a place to
attach phase-relative constraints as they are written.

## Phases of one transition

A transition advances the machine from one configuration to the next:
read the symbol under the head, look up the (state, symbol) entry, write
the new symbol, move the head one cell, change to the new state. The
phases below break that into discrete mechanical events; each phase is
either active (something is moving) or static (the system is at rest in
a configuration the next phase will act on).

The crank-turns-per-transition ratio is a mechanism-design choice. A
single transition may span multiple crank revolutions, and different
transitions may take different amounts of cranking. Phase ordering does
not assume a fixed number of revolutions per cycle.

1. **Read / row-select.** The slider's position under the head, together
   with the state register, selects which row of the transition plate's
   pegs the output arms see. Because symbol = slider position
   (`docs/DESIGN_INFLUENCES.md`), this is one mechanical operation, not
   two.

2. **Lock-disengage.** The head mechanically deflects the cell-resident
   flexure to free the slider for writing. From this point until
   lock-reengage, the slider is unlatched; the cycle must not stop here.

3. **Write-release.** The writer arm's release latch is tripped; the
   spring-loaded arm begins traveling toward the slider, dragging the
   slider toward the symbol position selected by the transition plate.

4. **Write-travel.** The writer arm travels until it hits the peg at the
   target position. The slider is now at the new symbol's detent.

5. **Lock-reengage.** The head withdraws its disengagement input; the
   cell's flexure restores the lock to engaged. The slider is now
   latched at the new symbol.

6. **Move.** The gantry advances one cell in the direction the transition
   plate's direction-arm encodes.

7. **State-update.** The state register advances to the new state encoded
   by the transition plate's state-arm.

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
| Friction losses (slider, gantry, plate)          | TBD              |
| State-register indexing torque                   | TBD              |
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
- During state-register indexing (state output is intermediate).

If the drive's gear ratio is chosen so that one full crank revolution
maps to one transition, the safe-stop state corresponds to the crank's
home angle. If the ratio is N revolutions per transition, only the
revolution that completes the cycle is a safe-stop window.

The safe-stop set may grow as the cycle is refined — for example, if
recock is sequenced into a separate sub-cycle, a safe-stop between
"transition complete" and "recock complete" may be useful for an
operator who wants to inspect the tape mid-program.
