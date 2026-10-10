# Lightning checkpoint admission and terminal acceptance

Capacity admission for a resumable import is a versioned state transition. Correlate the
current request with its plan epoch and checkpoint generation, then compare the reservation,
checkpoint manifest, lease journal, and resume gate. The selected Store must satisfy the
request's zone, device, free-space, topology, and checkpoint-compatibility constraints. A
stale lease, an older generation, a duplicate committed reservation, a mismatched reservation
token, or a fence that was not renewed after manifest inspection is not a valid admission.

Plausible candidates are expected in a live control plane. Choose by current evidence and
scope the mutation to the request, reservation, lease, and resume gate for the same task. Do
not stop healthy Stores, start an unapproved candidate, rewrite evidence, change protection
settings, or broaden a control-plane update merely because one candidate is convenient.

Acceptance is a closed loop. First observe the import's terminal state and checkpoint state;
then independently verify source and schema identity, checkpoint task and table metadata,
active Store health, and the physical-import protection preconditions. Finally verify the
business row count, deterministic aggregates, checksum, statistics, and any required table
health checks. A checkpoint being present, a request being accepted, or a process being
running is not terminal success; all core invariants must agree before the change is closed.
