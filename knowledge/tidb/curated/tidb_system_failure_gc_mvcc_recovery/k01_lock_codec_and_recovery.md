# TiKV 8.1 lock codec and bounded recover-mvcc

This is a version-pinned engineering note for TiKV 8.1 self-managed recovery. It explains
the product invariant and the recovery boundary; it is not an arbitrary shell procedure and
does not contain any live data or fixture identity.

## Version identity

- TiDB, TiKV, and PD release: v8.1.0.
- TiKV lock codec source: `components/txn_types/src/lock.rs` at the pinned TiKV source commit.
- The recovery implementation is the `recover-mvcc` path in `src/server/debug.rs` at the same
  commit.
- The trusted recovery binary must report the same release and source identity as the running
  TiKV image before its output is used.

## Lock value facts

For a TiKV v8.1 Put lock, the lock CF value contains a compact primary key, a varint
`start_ts`, a varint TTL, an async-commit marker with a big-endian `min_commit_ts`, and an
async-commit secondary-key list. These fields are transaction metadata, not application
columns.

The async-commit timestamp invariant is `min_commit_ts > start_ts`. A lock with
`min_commit_ts <= start_ts` is malformed for this codec. The lock/default/write relationship
must also be checked: a Put lock without the corresponding default record cannot be treated as
a normal pending write. The timestamp violation identifies the mechanism, while the missing
transaction record determines whether the bounded cleanup path is eligible. An arbitrary
RocksDB corruption is not implied to be repairable by this note.

## Recovery boundary

The supported recovery sequence is:

1. Run a fixed-version read-only `recover-mvcc` inspection against the exact Region and its
   complete current peer Store set.
2. Confirm that the inspection identity, Region, peer set, image, and binary are the ones
   intended for the execution.
3. Execute the same fixed-version recovery against that unchanged scope.
4. Re-scan all peers and verify lock absence, Region health, legal transaction liveness, and
   application truth independently.

The execution is not a global `--all` operation. A Store subset, an unbound Region, an
arbitrary data directory, a different binary, or execution without the preceding same-scope
inspection is outside this recovery boundary. A successful process exit is only an operation
result; it is not proof that every peer and the protected business state are correct.

## What this knowledge changes

The codec facts distinguish an invalid async-commit lock from a generic GC delay. The recovery
facts distinguish a version-bound, Region-scoped cleanup from a restart, global policy change,
or broad storage command. The live Region, peer, timestamp, and business values still have to
be discovered and validated through the environment tools.
