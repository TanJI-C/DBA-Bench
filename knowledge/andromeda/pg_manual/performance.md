## PostgreSQL Performance Configuration

### shared_buffers
Controls how much memory PostgreSQL uses for shared memory buffers. Default is typically 128MB which is too low for production.
- Recommended: 25% of total system RAM
- Too low: frequent disk I/O, poor cache hit ratio
- Too high: leaves insufficient memory for OS cache

### work_mem
Memory used for internal sort operations and hash tables before writing to temporary disk files.
- Default: 4MB
- Too low: excessive temp file creation, slow sorts and joins
- Too high: risk of OOM when many connections run complex queries simultaneously
- Symptom: "temporary file" entries in pg_log, slow ORDER BY / GROUP BY

### effective_cache_size
Planner's assumption about total memory available for disk caching (OS cache + shared_buffers).
- Recommended: 50-75% of total RAM
- Too low: planner avoids index scans, prefers sequential scans
- Too high: planner overestimates cache availability

### maintenance_work_mem
Memory for maintenance operations (VACUUM, CREATE INDEX, ALTER TABLE ADD FOREIGN KEY).
- Default: 64MB
- Too low: VACUUM runs slowly, autovacuum takes too long
- Recommended: 256MB-1GB depending on table sizes

### random_page_cost
Planner's estimate of cost of non-sequential disk page fetch.
- Default: 4.0
- For SSD: set to 1.1-1.5
- Too high on SSD: planner avoids index scans unnecessarily

### effective_io_concurrency
Number of concurrent disk I/O operations the system can handle.
- Default: 1
- For SSD: set to 200
- Too low: underutilizes SSD parallelism
