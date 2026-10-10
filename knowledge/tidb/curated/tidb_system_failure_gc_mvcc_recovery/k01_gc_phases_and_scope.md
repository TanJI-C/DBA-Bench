# TiDB 8.1 GC phases, MVCC scope, and legal neighbors

This note describes reusable TiDB 8.1 self-managed semantics for diagnosing a lock-related
GC problem. It does not describe a particular run, table, Region, Store, timestamp, or
business result. Those facts must come from the live cluster.

## GC causal chain

TiDB garbage collection is a sequence of distinct phases, not one generic "GC is slow"
condition. The GC leader calculates a safe point and then coordinates:

1. Resolve Locks examines locks older than the safe point and determines whether they should
   be committed or rolled back.
2. Delete Ranges removes ranges recorded by destructive DDL after their timestamps are safe.
3. Do GC removes obsolete MVCC versions while retaining the versions required by snapshots
   after the safe point.

A worker metric or a long GC round proves that the phase is observable. It does not by itself
identify the cause. A lock-related incident requires correlating the raw lock record, its
timestamp fields, the current safe point, and the phase that is handling locks. Disk pressure,
generic compaction activity, or a delayed later phase are competing explanations rather than
proof of a malformed lock.

## MVCC neighbors

An ordinary pessimistic lock can be valid, and a long-running transaction can legitimately
retain MVCC history and constrain the safe point. Their presence is a counterfactual: it shows
that not every visible lock or retained version is corruption. A repair must distinguish the
lock whose codec and transaction relationships are invalid from legal locks and transactions
that must remain usable.

## Replicated scope

The first error or first visible Store is not necessarily the full impact scope. A Region is
replicated across its current peer Stores. Before a lock scan or recovery action, read the live
PD Region metadata and map every current peer Store to its stable TiKV service identity. The
same complete peer set must be used for observation, inspection, execution, and final absence
checks. A subset can leave a stale copy; an unknown or extra Store means the scope is not bound
to the Region being repaired.

## Unsafe masking

Advancing a global GC safepoint, changing GC lifetime or enablement, deleting user data,
dropping the affected database, restarting components, or killing legal transactions can hide
a symptom without repairing the lock relationship. These actions change global policy or
protected state and are not substitutes for a bounded, version-supported MVCC recovery.
