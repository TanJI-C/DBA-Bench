# PITR checkpoint identity and retry semantics

This material applies to self-managed TiDB 8.1 Backup & Restore (BR) checkpoint
restore. A checkpoint is durable progress metadata for one restore request; it is
not an independent backup and it is not safe to select it only because its files
are present in object storage.

For snapshot restore, checkpoint records associate restored key ranges with the
table identities in the downstream cluster. For log restore, checkpoint metadata
records ordered positions in the log-backup metadata and preserves the upstream
to-downstream ID mapping needed to replay metadata consistently. A retry can skip
previously recorded progress only when the current restore still represents the
same request and the same target state.

PITR combines snapshot restore and log restore. The checkpoint identity includes
the upstream cluster identity, the snapshot BackupTS, the log restore `start-ts`,
the requested `restored-ts`, and the downstream target identity. These values are
part of the original restore request. Changing the log time range, upstream
identity, backup identity, or target while reusing the checkpoint is a
compatibility error, not a harmless way to adjust the retry.

The downstream cluster identity is necessary but not sufficient. The retry must
also account for the target-side checkpoint records, table identities, ID mapping,
and changes made after the failed attempt. The BR documentation explicitly warns
against writing, deleting, or creating tables after a restore failure: an external
DDL or data change can make it impossible to distinguish restore-owned state from
operator-owned state. In that situation, a matching cluster ID does not prove that
the checkpoint can be safely reused in place.

Checkpoint restore is version-scoped. TiDB 7.1.0 and later introduced the
checkpoint feature, while cross-major-version checkpoint recovery is not a safe
general assumption. Confirm the running BR and target release before treating a
checkpoint as resumable.

