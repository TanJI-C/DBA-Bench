# TiCDC service GC safepoint ownership and cleanup

TiCDC changefeed processing registers a service-level GC safepoint with PD. The
owner identity, capture liveness, expiration time, and safe point are separate
facts. A service owner can remain visible after a capture stops, and its safe point
can become the effective oldest service point until the owner is explicitly
cleaned up or its lease expires. This service-level mechanism is independent of
the TiDB GC lifetime setting; changing the global lifetime does not remove a
stale TiCDC owner.

Inspect all service owners, the `gc_worker` boundary, the effective minimum, and
the matching changefeed and capture before changing anything. Separate active,
healthy, backup, and abandoned scopes. Remove only the exact abandoned
changefeed through the product-supported owning capture path after its observed
runtime is stopped. Verify that the exact feed is absent from the capture's feed
list and that the matching owner is absent or has advanced to at least the live
`gc_worker` safe point. A cluster-level owner row may remain while its lease is
valid; row deletion is not the completion condition when the safe point is no
longer an effective pin.

Preserve active and healthy owners. Do not delete all owners, advance a global
safe point, change the GC lifetime, or wait for a long owner TTL as a substitute
for exact feed cleanup. Owner IDs, feed IDs, capture targets, timestamps, and
worker values are dynamic facts that must come from the current PD and TiCDC
observations.
