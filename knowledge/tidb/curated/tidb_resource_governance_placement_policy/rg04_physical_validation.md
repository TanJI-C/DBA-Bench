# TiDB v8.1 physical placement validation and scoped repair

## Prove the physical result

Correlate the policy definition with `SHOW PLACEMENT LABELS`,
`INFORMATION_SCHEMA.TIKV_STORE_STATUS`, `INFORMATION_SCHEMA.TIKV_REGION_STATUS`, and
`INFORMATION_SCHEMA.TIKV_REGION_PEERS`. For every target Region, count healthy voter peers,
check learner state, verify the required fault-domain labels, and identify the current leader.
Also check Store state and available capacity. A business query can remain successful while a
placement migration is still unsafe or incomplete.

## Keep the repair narrow

Use a table-scoped attachment on the relation selected by the current request context and route
fence. Do not choose an object from a service name, a policy name, a historical row, or a larger
future generation alone. Do not modify an existing shared policy definition, a protected neighbor,
database/global placement, scheduler configuration, Store labels, or business rows.

Final acceptance requires the target to be physically converged and the protected relation,
control-plane, data, and topology truth to remain unchanged. `DEFAULT` is an inheritance operation,
not an equivalent custom compliance policy.

