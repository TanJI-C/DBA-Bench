# TiDB v8.1 placement policy semantics

## Read the complete policy definition

`FOLLOWERS=n` means `n` follower replicas in addition to the leader. `PRIMARY_REGION` identifies
the leader locality when the cluster has the matching topology label, while `REGIONS` identifies
the regions available for followers. `SCHEDULE="EVEN"` balances followers across the listed
regions; `MAJORITY_IN_PRIMARY` is a different latency/availability tradeoff and does not mean
"one follower in every listed region".

`LEADER_CONSTRAINTS` and `FOLLOWER_CONSTRAINTS` constrain roles directly. Dictionary constraints
assign replica counts to individual label expressions. List constraints express eligibility but do
not by themselves prove a per-domain replica count. `PRIMARY_REGION`, `REGIONS`, and `SCHEDULE`
must not be mixed with the `CONSTRAINTS` option.

Policy names are identifiers, not semantics. Inspect the complete
`INFORMATION_SCHEMA.PLACEMENT_POLICIES` row or `SHOW CREATE PLACEMENT POLICY`, then compare the
definition with the approved request and the labels that are actually present on TiKV stores.

## Bindings are separate from definitions

A placement policy is reusable metadata. A table or partition attachment is a separate object
binding. `INFORMATION_SCHEMA.TABLES.TIDB_PLACEMENT_POLICY_NAME` identifies the table binding, while
`SHOW PLACEMENT` reports the effective object rule and scheduling state. Do not infer a table's
physical result from a policy name alone.

