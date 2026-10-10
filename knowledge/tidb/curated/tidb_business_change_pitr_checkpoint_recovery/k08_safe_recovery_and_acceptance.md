# Safe recovery after a failed PITR checkpoint

An exact checkpoint resume is appropriate only after the restore version,
upstream and downstream identities, snapshot and log time boundaries, checkpoint
storage, target state, and log continuity all agree. The target must remain within
the state that BR owns for the failed request. A request being accepted, a
checkpoint file existing, or a process restarting is not a terminal recovery
result.

If the failed target was changed by an external operator after checkpoint
persistence, do not retry the checkpoint against that target. Preserve the source
cluster and backup objects, record the incompatible target-side change, and make
the old target unavailable for further restore writes. The recovery procedure must
explicitly abandon or otherwise retire the incompatible attempt according to the
product's restore control plane, then use a newly isolated downstream target (and
an appropriately scoped checkpoint location when required) for a clean restore of
the same snapshot, log chain, and requested recovery point. The new target is not
the old partial target under a new label.

Do not arbitrarily delete checkpoint metadata, PITR ID mappings, source backup
objects, or log segments to force compatibility. If the snapshot/log chain is
missing, corrupt, outside retention, or bound to another version or upstream, the
safe result is to stop and report that the requested recovery cannot be proven.

Completion requires more than a successful BR command. Verify the restore reached
its terminal completed state, the snapshot and log chain remained continuous, the
target contains data through the requested point and excludes later data, and
business counts/checksums or equivalent invariants match the expected boundary.
Also verify that the source cluster, protected backup objects, and unrelated
targets were not modified. These checks distinguish a real recovery from a
partial retry or a superficially healthy process.

