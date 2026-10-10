# Online Unsafe Recovery: affected scope and RPO

## Dynamic scope

Store IDs, Region IDs, table IDs, and index IDs are runtime evidence. Discover them from the
current PD Store/Region state and the TiDB information schema for the current deployment. Never
reuse an identity from an earlier run.

For a two-of-three peer loss, map every affected record Region and every secondary-index Region
to the same business table. A record-only check is incomplete. An unrelated healthy table or
Region set is a counterfactual and must remain readable with unchanged business truth.

## Boundary and loss

Capture the last confirmed business truth and a committed TSO before data Stores are stopped.
Writes after that boundary and before recovery reaches a terminal state are not confirmed by the
pre-fault truth. An unchanged count, sum, or checksum in one run is not proof of general zero
data loss.

The final report must state:

- the last confirmed commit boundary;
- the write interval that was not confirmed;
- the observed RPO, without claiming losslessness.

## Acceptance

After the product task and peer cleanup settle, verify affected Region leaders and three normal
healthy peers, no residual peer on a failed Store, the affected record/index scope, the public
integrity check, pre-fault business truth, and any separately authorized post-recovery canary.
Verify that unrelated protected truth is unchanged. Restore captured PD scheduling values only
after the recovery task is terminal, then verify them from current PD configuration.

A readable Region, a successful request, a stable metric, or a checksum alone is weaker than this
combined final-state and business verification.

