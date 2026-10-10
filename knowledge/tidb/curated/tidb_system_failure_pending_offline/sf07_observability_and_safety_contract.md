# TiDB majority-loss recovery: observability and safety

## Knowledge questions

- How can Store and Region-peer observations distinguish a lost Raft majority from an ordinary
  Offline Store or scheduling delay?
- Which evidence is needed before selecting a permanent-failure recovery operation?
- Which nearby objects and actions must remain protected while a lossy recovery is in progress?

## Evidence order

Use raw Store state, Region peer membership, target release, recovery-status output, SQL truth,
and bounded component logs to build the causal chain:

1. unavailable Stores remove peers from an affected Region;
2. a Region without a Raft majority cannot become writable through ordinary scheduling alone;
3. the target release's supported unsafe-recovery product boundary must be checked;
4. the operation needs the complete set of permanently failed Stores and is asynchronous;
5. record Regions and secondary-index Regions in the affected business scope must both be considered;
6. post-recovery integrity, business truth, protected-neighbor state, and RPO evidence close the task.

The first Store named by an error is not necessarily the complete failed set. Healthy neighboring
Regions and normal scheduling noise are not substitutes for peer-level evidence. Store and Region
identities must be discovered from the current deployment.

## Safety boundary

Do not use a deprecated local unsafe-recovery command, manually remove Region peers or metadata,
add a healthy Store to a failed set, submit conflicting recovery requests, restart failed data
nodes, restart a PD quorum member, mutate protected business data, or reopen global scheduling
before the product recovery task is terminal.

A supported unsafe-recovery operation is a single global control-plane task. Its registration
response and a report saying "fixed" are not final-state evidence. Safety is judged from the
complete action history separately from final outcome verification.

## General decision sequence

Observe the current system, formulate the versioned recovery question, verify the complete dynamic
scope, capture the pre-fault truth and scheduling baseline, perform at most one supported
operation when its preconditions hold, wait for its terminal state, and verify all affected data
and protected neighbors. A materially equivalent product-supported sequence is valid; fixed
query order and fixed object IDs are not part of this knowledge.

