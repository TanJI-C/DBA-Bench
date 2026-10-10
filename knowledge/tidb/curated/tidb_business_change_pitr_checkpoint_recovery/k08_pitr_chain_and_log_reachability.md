# PITR chain, global checkpoint, and log reachability

TiDB PITR is a chain rather than a single restore object. A full snapshot must
precede the requested recovery point, and log backup data must cover the interval
from the usable snapshot boundary through that point. The restore has a snapshot
phase followed by log metadata and log KV replay; a successful snapshot phase does
not prove that the later log phase is reachable or complete.

During log backup, each TiKV reports a local checkpoint. The global checkpoint is
the point before which all participating TiKV log data has been backed up to the
configured storage. The global value is therefore the useful cluster-wide
continuity boundary; one healthy local writer or a recent object is not proof that
the whole chain is available.

Before retrying or restarting a PITR restore, compare the original snapshot
BackupTS, log start boundary, global/log checkpoint, requested recovery point,
retention window, and the actual object inventory. A chain can look healthy while
still having a missing, corrupt, or out-of-retention segment. A requested point
outside the retained interval is not repaired by changing the retry timestamp.

The storage path and phase also matter. BR versions may keep checkpoint records in
the downstream checkpoint database or in an external checkpoint-storage prefix.
For external storage, the downstream cluster ID is part of the restore path and
snapshot, log, and SST checkpoint data have distinct areas. The observed path must
be tied to the current restore request and phase; a nearby prefix with the same
upstream cluster or a similar time range is not interchangeable.

The log backup service may pause GC during log restore because replay order can be
different from write order. A failed restore can therefore leave an operational
state that requires an explicit, version-appropriate recovery decision. Do not
silently change GC, retention, or log-backup ownership merely to make a retry
appear reachable.

