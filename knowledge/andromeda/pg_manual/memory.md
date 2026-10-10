## PostgreSQL Memory Configuration

### shared_buffers
Amount of memory for shared memory buffers. Default 128MB, recommend 25% of RAM.
Symptom of misconfiguration: low cache_hit_ratio (< 0.90), excessive disk reads.

### work_mem
Memory for sort/hash operations. Default 4MB.
Too low: excessive temp file creation. Too high: OOM risk with many connections.

### max_connections
Each connection uses ~10MB. Too high combined with work_mem causes OOM.

### wal_buffers
WAL data buffer. Too low causes frequent WAL flushes and write latency spikes.
