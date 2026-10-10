## Problem: INSERT statements are very slow
The database INSERT performance degrades significantly under load.

## Solution
Check `wal_buffers` and `checkpoint_completion_target`. Increase `wal_buffers` to 64MB.
Set `checkpoint_completion_target = 0.9` to spread checkpoint I/O.
Also verify `synchronous_commit` setting — set to `off` for non-critical writes.

---

## Problem: High CPU usage during query execution
CPU spikes to 100% when running analytical queries.

## Solution
Check `work_mem` — if too low, queries do excessive disk-based sorting.
Increase `work_mem` to 256MB for analytical workloads.
Also check `max_parallel_workers_per_gather` to utilize parallel query.

---

## Problem: Database runs out of memory (OOM killed)
PostgreSQL process killed by OOM killer under concurrent load.

## Solution
Reduce `max_connections` or use connection pooling (PgBouncer).
Lower `work_mem` if many concurrent complex queries run simultaneously.
Total memory ≈ shared_buffers + (max_connections × work_mem).
