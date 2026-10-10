# Lightning physical import capacity and protection boundaries

Lightning import capacity is not determined by the source file byte total alone. Local
physical import can require space for encoded key-values, indexes, sort or temporary data,
replication, and compaction headroom. Capacity admission must use the documented estimate for
the selected backend and compare it with current Store free space, topology labels, and the
scope of the import. A candidate that looks large enough from a source-size comparison can
still be unsafe.

The import backend and its protection prerequisites are independent facts. Check whether the
backend is local or another supported mode, whether parallel import is enabled, whether the
target-empty precondition applies, and whether empty-Region or topology prechecks are within
the supported boundary. Inspect the current PITR and TiCDC state instead of assuming that a
backup or changefeed protects an in-flight physical import. A protection setting that is
incompatible with the selected import mode is a precheck failure, not a reason to force a
resume or change global protection policy.

Use raw Store, Region, configuration, and import observations to bind these rules to the
current task. Source size, a successful SQL admission, or a single Store status is not proof
that the encoded-KV, index, replica, and temporary-space envelope is safe. Preserve the
protected target and unrelated Store state while resolving the capacity condition.
