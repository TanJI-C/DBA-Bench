# TiCDC progress, sink retry, and recovery boundary

## Checkpoint and resolved progress

TiCDC exposes more than one progress value. Checkpoint progress describes the
latest change event that the sink has successfully applied. Resolved progress
describes the source timestamp through which no earlier event is expected to
arrive. A healthy-looking control-plane state does not prove that the sink has
applied every event: compare the state, checkpoint, resolved value, source
progress, and sink logs in the same time window.

When a sink cannot apply one event, resolved progress can continue moving while
checkpoint remains at the blocking event. This is a retry and ordering signal,
not evidence that the blocking event can be ignored.

## DDL retry evidence

For a sink DDL error, the raw TiCDC log is the authoritative place to identify
the failed event. Keep the DDL error, table operation, and event commit
timestamp together. Do not manufacture a timestamp from the current TSO or
from a later checkpoint; repeated log lines may describe the same event, so
deduplicate the commit timestamp before choosing a recovery boundary.

## Recovery boundary

After the sink-side schema is made equivalent, a changefeed recovery must
replay the failed event boundary deliberately. The safe replay point is the
first timestamp after the isolated failed DDL event. Starting after a later
current checkpoint can skip source changes that were committed while the sink
was retrying. Validate the recreated feed with checkpoint, resolved progress,
source progress, and business rows rather than with the recreate command's
success response alone.
