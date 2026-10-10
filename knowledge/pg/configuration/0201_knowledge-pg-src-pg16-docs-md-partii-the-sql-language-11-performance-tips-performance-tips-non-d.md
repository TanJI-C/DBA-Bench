# Non-Durable Settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/11_performance_tips.md`
- Source Title: `Performance Tips`
- Source Heading Path: `Performance Tips > Non-Durable Settings`
- Source Line Ranges: `996-1026`
- Chunk ID: `pg16_configuration_0201_80ea8739ad`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a47e817eb70b52240735ab672619e8c9465eb046f4d8703fceb7a2d63eec6372`

## Retrieval Guidance

- Use When: Need to explain performance settings that intentionally weaken durability guarantees.
- Retrieval Keywords: fsync, synchronous_commit, full_page_writes, max_wal_size, checkpoint_timeout, unlogged table, non-durable
- Follow-up Guidance: Require explicit risk acceptance because these settings can lose or corrupt data after crashes or power loss.
- Classification Note: Lists configuration changes that trade durability for speed, including fsync, synchronous_commit, full_page_writes, max_wal_size, checkpoint_timeout, RAM-backed storage, and unlogged tables.

## Official Source Content

## Non-Durable Settings

Durability is a database feature that guarantees the recording of
committed transactions even if the server crashes or loses
power.  However, durability adds significant database overhead,
so if your site does not require such a guarantee,
PostgreSQL can be configured to run
much faster.  The following are configuration changes you can make
to improve performance in such cases.  Except as noted below, durability
is still guaranteed in case of a crash of the database software;
only an abrupt operating system crash creates a risk of data loss
or corruption when these settings are used.

- Place the database cluster's data directory in a memory-backed
file system (i.e., RAM disk).  This eliminates all
database disk I/O, but limits data storage to the amount of
available memory (and perhaps swap).
- Turn off [guc-fsync](#guc-fsync);  there is no need to flush
data to disk.
- Turn off [guc-synchronous-commit](#guc-synchronous-commit);  there might be no
need to force WAL writes to disk on every
commit.  This setting does risk transaction loss (though not data
corruption) in case of a crash of the *database*.
- Turn off [guc-full-page-writes](#guc-full-page-writes);  there is no need
to guard against partial page writes.
- Increase [guc-max-wal-size](#guc-max-wal-size) and [guc-checkpoint-timeout](#guc-checkpoint-timeout); this reduces the frequency
of checkpoints, but increases the storage requirements of
`/pg_wal`.
- Create [unlogged
tables](#sql-createtable-unlogged) to avoid WAL writes, though it
makes the tables non-crash-safe.
