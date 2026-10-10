# Joint TiCDC and GC recovery verification

A TiCDC incident with both feed progress trouble and an old service safepoint has
two independent completion conditions. Restoring the target capture does not
release an abandoned PD service owner, and removing an abandoned owner does not
clear a target Region lock. The repair order can vary when each product
precondition is satisfied, but both chains must converge.

Use a final observation window to verify target feed state, error absence,
ResolvedTS and CheckpointTS progress, lock absence on every observed peer,
Region health, exact abandoned-feed removal, and release of its owner to the
`gc_worker` boundary. Also verify effective GC progress, headroom, disk and
compaction limits, source/downstream business equality, and unchanged protected
feed or archive truth. These checks use current environment values and public
task thresholds, not action names or a prescribed command sequence.

Safe recovery is narrowly scoped. Preserve healthy and backup feeds and owners,
avoid global GC policy changes, do not delete business or evidence data, and do
not recreate a feed from an unproven late timestamp. A valid alternative repair
may use a product-supported target-feed recreation or a different order if its
start boundary, peer scope, owner scope, and final invariants are independently
proved.
