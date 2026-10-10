# TiCDC progress state after a capture restart

TiCDC exposes more than one progress timestamp for a changefeed. `ResolvedTS`
describes the source timestamp through which the capture has observed the required
input, while `CheckpointTS` describes the timestamp durably committed at the sink.
The exact relation and the error state must be read from the live changefeed; a
running process or a control-plane `NORMAL` state is not proof that the sink is
caught up.

When a capture has restarted after an out-of-memory event, compare its progress
over a bounded window with a healthy feed and with the source and downstream
business truth. A feed that remains normal and advances can be experiencing
ordinary sink lag. A feed whose progress is flat or whose checkpoint remains
behind while the sink has capacity needs correlation with source-region and TiKV
evidence. A restart can clear a transient process failure, but it does not prove
that an underlying transaction lock or region condition has been cleared.

Do not infer a repair from one successful status request. Recheck the timestamp
relation, the error field, continued progress, and an independent data invariant.
The live feed ID, capture identity, timestamps, error text, and comparison window
are environment facts and must be bound from current observations.
