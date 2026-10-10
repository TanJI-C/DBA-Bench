# TiDB v8.1 placement constraints and asynchronous progress

## Policy fields

`FOLLOWERS=n` requests n follower replicas in addition to the leader, so the normal replica
count is n+1. `PRIMARY_REGION` selects the leader region and `REGIONS` supplies the regions for
followers; these options depend on matching TiKV topology labels. `SCHEDULE` controls follower
distribution, with `EVEN` as the normal default and `MAJORITY_IN_PRIMARY` as a different
availability/latency tradeoff. `CONSTRAINTS`, `LEADER_CONSTRAINTS`, `FOLLOWER_CONSTRAINTS`, and
`LEARNER_CONSTRAINTS` express label requirements. Dictionary form assigns replica counts to
individual constraint keys, while list form applies a constraint without a per-key count.

`PRIMARY_REGION`, `REGIONS`, and `SCHEDULE` cannot be combined with the `CONSTRAINTS` option.
Do not infer the meaning of a policy from its name or from one field. Read
`information_schema.placement_policies`, `SHOW CREATE PLACEMENT POLICY`, and the available
labels. A policy definition being accepted by SQL does not prove that its requested layout is
currently realizable.

## Capacity and progress

A placement request requiring more replicas or fault domains than the currently available
TiKV Stores and labels can provide remains unsatisfied even when the SQL DDL succeeds. The
Store list, Store labels, Region peer list, policy definition, and placement output must be
correlated before choosing a repair. `SHOW PLACEMENT` exposes policy-definition rows with a
null scheduling state and object rows with asynchronous states. `PENDING`, `INPROGRESS`, and
`SCHEDULED` describe different scheduling stages; an accepted DDL is only an admission event,
not convergence. Re-read the object placement state after a change and accept success only
when the target object has converged.
