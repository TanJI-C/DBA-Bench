# Agent-visible evidence for bounded MVCC recovery

The following evidence pattern is sufficient to bind the TiDB 8.1 lock and GC semantics to a
live deployment. The knowledge text explains what the evidence means; it does not contain the
current deployment's identifiers or acceptance result.

## Raw lock evidence

A bounded lock-CF observation should return the origin row key, the storage key, the raw lock
value, the Region boundary, the complete peer Store set, and the versioned tool identity for
each peer. The raw bytes are needed to decode `start_ts`, `min_commit_ts`, the lock kind, and
the default/write relationship. A first error from one peer is not a complete scan.

## Key-range binding

A table name is not a recovery scope: a normal TiDB table can span several Regions. When the
incident names a row or a raw storage key, first read the table identifier and the current Region
start/end boundaries. Encode the row key with the TiKV mem-comparable codec used by the Region
metadata, then select the single live range for which `start_key <= encoded_key < end_key`;
an empty start or end denotes the unbounded side. Do not choose the first Region returned by SQL,
recover every Region belonging to the table, or infer the Region from the first Store mentioned in
a log. The selected Region and its complete current peer set are the scope for lock scan,
read-only inspection, execution, and final verification. Sibling Regions are protected state.

## GC evidence

GC observation should keep the current safepoint, GC lifetime and last-run state separate from
the raw worker series. The Resolve Locks, Delete Ranges, and Do GC phases have different causal
roles. A phase series is useful for correlation, but a visible series, a non-zero rate, or a
successful status read is not a diagnosis by itself.

## Recovery evidence

Read-only recovery output should identify the release, binary, Region, peer scope, and the
lock/default checks performed on every peer. Execution output should use the inspection token
from that same scope. After execution, independent observations must establish that the lock is
absent from every current peer and that legal neighboring transactions, Region health, and
business truth remain intact.

## Error boundary

The bounded environment surface may expose raw lock scans, GC status, version-bound recovery
inspection, and version-bound recovery execution. It must reject arbitrary shell, unbounded
storage scans, global recovery scope, duplicate or incomplete Store sets, and execution against
a changed Region scope. A non-zero trusted command is an operational error with its command,
scope, identity, exit code, stdout, and stderr; it must not be converted into an ordinary empty
diagnosis result.

## Evidence binding

The useful diagnostic chain is:

```text
live symptom
-> raw lock bytes and transaction relationships
-> TiDB 8.1 timestamp invariant
-> GC Resolve Locks causal role
-> complete Region peer scope
-> inspected version-bound recovery
-> final lock, Region, transaction, and business checks
```

Missing any one of these links leaves a plausible but incomplete explanation. The Agent must
combine the knowledge result with `execute_sql`, `read_log`, `query_metrics`, and the structured
cluster observations rather than treating a knowledge result or command success as the final
answer.
