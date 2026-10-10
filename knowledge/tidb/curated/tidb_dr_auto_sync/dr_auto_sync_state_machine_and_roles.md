# DR Auto-Sync state machine and placement roles

TiDB 8.1 DR Auto-Sync is a PD-controlled replication mode for a self-managed
two-domain deployment. Read the product state and the Region-level state as
different observations.

The public replication-mode status distinguishes the normal `sync` state, a
temporary `async` state after the remote domain cannot satisfy the synchronous
contract, and `sync-recover` while Regions are being moved back to the
label-constrained contract. A PD Leader change does not prove any of these
states, and equal TSO text does not prove that the Region replica contract has
converged.

Placement Rules bind a label key and domain values to replica roles and counts.
Read the rule bundle and current Store labels together. A voter and a learner
are different Raft roles; a learner must not be counted as a synchronous voter.
The role, count, label constraint, and location-label fields in the rule bundle
are the source of truth for the requested placement.

A role exchange needs an explicit business write boundary, a fence for the old
writer, the documented synchronization state, and terminal placement/Region
convergence. Changing only a route, changing only the PD Leader, or submitting
a control-plane request without waiting for convergence does not establish a
completed exchange.

Bind these rules to the current release, deployment mode, Store states,
Placement Rules, Region peers, and endpoint routing before selecting an action.

