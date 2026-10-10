# TiCDC progress and TiKV MVCC recovery scope

Replication progress can be blocked by a TiKV transaction or MVCC lock even
when the downstream sink is healthy. A lock observation is only meaningful when
it is correlated with the target Region, lock metadata, transaction timestamps,
the changefeed progress window, and a healthy-feed counterfactual. A log line or
the first Store that returns a record is not the complete recovery scope.

Read the live Region metadata and map every current peer to its stable TiKV
service identity before a lock inspection or recovery. Use the same Region and
complete peer Store set for read-only inspection, execution, and the final
absence check. Recovery must use the version-compatible, bounded product path
and the inspection identity for that unchanged scope. A subset can leave a
replica lock behind; an arbitrary Store, Region-wide global command, or broad
storage scan is outside the safety boundary.

After the operation, independently verify lock absence on every current peer,
Region health, legal neighboring transactions, changefeed progress, and business
truth. A successful process exit or a temporary checkpoint improvement is only
an action result, not proof of a complete recovery.
