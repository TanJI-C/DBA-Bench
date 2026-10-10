# pg_buffercache view; summary; usage counts; sample output

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVIII_appendixes/06_additional_supplied_modules_and_extensions.md`
- Source Title: `postgresql.conf`
- Source Heading Path: `Additional Supplied Modules and Extensions > pg_buffercache - inspect PostgreSQL > pg_buffercache view; summary; usage counts; sample output`
- Source Line Ranges: `5261-5294, 5295-5317, 5341-5385, 6134-6168, 6315-6327, 6641-6741, 6742-6746`
- Chunk ID: `pg16_guide_0060_4f58c6e531`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bd148e9e5eff2de3abc87a39a461f3cedb2fb61f06806e3935d737dbc87b2d6f`

## Retrieval Guidance

- Use When: Diagnose buffer-cache contents, cache pressure, or relation residency in shared buffers.
- Retrieval Keywords: pg_buffercache, shared buffers, buffer cache, usagecount, pg_buffercache_summary, cache residency
- Follow-up Guidance: Correlate with workload, cache hit ratio, and IO metrics before changing memory settings.
- Classification Note: The module exposes shared-buffer contents and usage-count summaries that confirm cache residency and buffer-cache pressure.

## Official Source Content

### The `pg_buffercache` View

The definitions of the columns exposed by the view are shown in [pgbuffercache-columns](#pgbuffercache-columns).

| Column Type                      Description |
| --- |
| `bufferid` `integer`                      ID, in the range 1..`shared_buffers` |
| `relfilenode` `oid`        (references [`pg_class`](#catalog-pg-class).`relfilenode`)                      Filenode number of the relation |
| `reltablespace` `oid`        (references [`pg_tablespace`](#catalog-pg-tablespace).`oid`)                      Tablespace OID of the relation |
| `reldatabase` `oid`        (references [`pg_database`](#catalog-pg-database).`oid`)                      Database OID of the relation |
| `relforknumber` `smallint`                      Fork number within the relation;  see        `common/relpath.h` |
| `relblocknumber` `bigint`                      Page number within the relation |
| `isdirty` `boolean`                      Is the page dirty? |
| `usagecount` `smallint`                      Clock-sweep access count |
| `pinning_backends` `integer`                      Number of backends pinning this buffer |

There is one row for each buffer in the shared cache. Unused buffers are
shown with all fields null except `bufferid`.  Shared system
catalogs are shown as belonging to database zero.

Because the cache is shared by all the databases, there will normally be
pages from relations not belonging to the current database.  This means
that there may not be matching join rows in `pg_class` for
some rows, or that there could even be incorrect joins.  If you are
trying to join against `pg_class`, it's a good idea to
restrict the join to rows having `reldatabase` equal to
the current database's OID or zero.

Since buffer manager locks are not taken to copy the buffer state data that
the view will display, accessing `pg_buffercache` view
has less impact on normal buffer activity but it doesn't provide a consistent
set of results across all buffers.  However, we ensure that the information of
each buffer is self-consistent.

### The `pg_buffercache_summary()` Function

The definitions of the columns exposed by the function are shown in [pgbuffercache-summary-columns](#pgbuffercache-summary-columns).

| Column Type                      Description |
| --- |
| `buffers_used` `int4`                      Number of used shared buffers |
| `buffers_unused` `int4`                      Number of unused shared buffers |
| `buffers_dirty` `int4`                      Number of dirty shared buffers |
| `buffers_pinned` `int4`                      Number of pinned shared buffers |
| `usagecount_avg` `float8`                      Average usage count of used shared buffers |

The `pg_buffercache_summary()` function returns a
single row summarizing the state of all shared buffers. Similar and more
detailed information is provided by the
`pg_buffercache` view, but
`pg_buffercache_summary()` is significantly cheaper.

Like the `pg_buffercache` view,
`pg_buffercache_summary()` does not acquire buffer
manager locks. Therefore concurrent activity can lead to minor inaccuracies
in the result.

### Sample Output

```
regression=# SELECT n.nspname, c.relname, count(*) AS buffers
FROM pg_buffercache b JOIN pg_class c
ON b.relfilenode = pg_relation_filenode(c.oid) AND
b.reldatabase IN (0, (SELECT oid FROM pg_database
WHERE datname = current_database()))
JOIN pg_namespace n ON n.oid = c.relnamespace
GROUP BY n.nspname, c.relname
ORDER BY 3 DESC
LIMIT 10;

nspname   |        relname         | buffers
------------+------------------------+---------
public     | delete_test_table      |     593
public     | delete_test_table_pkey |     494
pg_catalog | pg_attribute           |     472
public     | quad_poly_tbl          |     353
public     | tenk2                  |     349
public     | tenk1                  |     349
public     | gin_test_idx           |     306
pg_catalog | pg_largeobject         |     206
public     | gin_test_tbl           |     188
public     | spgist_text_tbl        |     182
(10 rows)

regression=# SELECT * FROM pg_buffercache_summary();
buffers_used | buffers_unused | buffers_dirty | buffers_pinned | usagecount_avg
--------------+----------------+---------------+----------------+----------------
248 |        2096904 |            39 |              0 |       3.141129
(1 row)

regression=# SELECT * FROM pg_buffercache_usage_counts();
usage_count | buffers | dirty | pinned
-------------+---------+-------+--------
0 |   14650 |     0 |      0
1 |    1436 |   671 |      0
2 |     102 |    88 |      0
3 |      23 |    21 |      0
4 |       9 |     7 |      0
5 |     164 |   106 |      0
(6 rows)
```

### Sample Output

```
postgres=# SELECT * FROM pg_freespace('foo');
blkno | avail
-------+-------
0 |     0
1 |     0
2 |     0
3 |    32
4 |   704
5 |   704
6 |   704
7 |  1216
8 |   704
9 |   704
10 |   704
11 |   704
12 |   704
13 |   704
14 |   704
15 |   704
16 |   704
17 |   704
18 |   704
19 |  3648
(20 rows)

postgres=# SELECT * FROM pg_freespace('foo', 7);
pg_freespace
--------------
1216
(1 row)
```

### Sample Output

```
=# SELECT * FROM pgrowlocks('t1');
locked_row | locker | multi | xids  |     modes      |  pids
------------+--------+-------+-------+----------------+--------
(0,1)      |    609 | f     | {609} | {"For Share"}  | {3161}
(0,2)      |    609 | f     | {609} | {"For Share"}  | {3161}
(0,3)      |    607 | f     | {607} | {"For Update"} | {3107}
(0,4)      |    607 | f     | {607} | {"For Update"} | {3107}
(4 rows)
```

### Sample Output

```
bench=# SELECT pg_stat_statements_reset();

$ pgbench -i bench
$ pgbench -c10 -t300 bench

bench=# \x
bench=# SELECT query, calls, total_exec_time, rows, 100.0 * shared_blks_hit /
nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 5;
-[ RECORD 1 ]---+--------------------------------------------------------------------
query           | UPDATE pgbench_branches SET bbalance = bbalance + $1 WHERE bid = $2
calls           | 3000
total_exec_time | 25565.855387
rows            | 3000
hit_percent     | 100.0000000000000000
-[ RECORD 2 ]---+--------------------------------------------------------------------
query           | UPDATE pgbench_tellers SET tbalance = tbalance + $1 WHERE tid = $2
calls           | 3000
total_exec_time | 20756.669379
rows            | 3000
hit_percent     | 100.0000000000000000
-[ RECORD 3 ]---+--------------------------------------------------------------------
query           | copy pgbench_accounts from stdin
calls           | 1
total_exec_time | 291.865911
rows            | 100000
hit_percent     | 100.0000000000000000
-[ RECORD 4 ]---+--------------------------------------------------------------------
query           | UPDATE pgbench_accounts SET abalance = abalance + $1 WHERE aid = $2
calls           | 3000
total_exec_time | 271.232977
rows            | 3000
hit_percent     | 98.8454011741682975
-[ RECORD 5 ]---+--------------------------------------------------------------------
query           | alter table pgbench_accounts add primary key (aid)
calls           | 1
total_exec_time | 160.588563
rows            | 0
hit_percent     | 100.0000000000000000

bench=# SELECT pg_stat_statements_reset(0,0,s.queryid) FROM pg_stat_statements AS s
WHERE s.query = 'UPDATE pgbench_branches SET bbalance = bbalance + $1 WHERE bid = $2';

bench=# SELECT query, calls, total_exec_time, rows, 100.0 * shared_blks_hit /
nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 5;
-[ RECORD 1 ]---+--------------------------------------------------------------------
query           | UPDATE pgbench_tellers SET tbalance = tbalance + $1 WHERE tid = $2
calls           | 3000
total_exec_time | 20756.669379
rows            | 3000
hit_percent     | 100.0000000000000000
-[ RECORD 2 ]---+--------------------------------------------------------------------
query           | copy pgbench_accounts from stdin
calls           | 1
total_exec_time | 291.865911
rows            | 100000
hit_percent     | 100.0000000000000000
-[ RECORD 3 ]---+--------------------------------------------------------------------
query           | UPDATE pgbench_accounts SET abalance = abalance + $1 WHERE aid = $2
calls           | 3000
total_exec_time | 271.232977
rows            | 3000
hit_percent     | 98.8454011741682975
-[ RECORD 4 ]---+--------------------------------------------------------------------
query           | alter table pgbench_accounts add primary key (aid)
calls           | 1
total_exec_time | 160.588563
rows            | 0
hit_percent     | 100.0000000000000000
-[ RECORD 5 ]---+--------------------------------------------------------------------
query           | vacuum analyze pgbench_accounts
calls           | 1
total_exec_time | 136.448116
rows            | 0
hit_percent     | 99.9201915403032721

bench=# SELECT pg_stat_statements_reset(0,0,0);

bench=# SELECT query, calls, total_exec_time, rows, 100.0 * shared_blks_hit /
nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 5;
-[ RECORD 1 ]---+-----------------------------------------------------------------------------
query           | SELECT pg_stat_statements_reset(0,0,0)
calls           | 1
total_exec_time | 0.189497
rows            | 1
hit_percent     |
-[ RECORD 2 ]---+-----------------------------------------------------------------------------
query           | SELECT query, calls, total_exec_time, rows, $1 * shared_blks_hit /          +
|                nullif(shared_blks_hit + shared_blks_read, $2) AS hit_percent+
|           FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT $3
calls           | 0
total_exec_time | 0
rows            | 0
hit_percent     |
```

### Authors

Takahiro Itagaki itagaki.takahiro@oss.ntt.co.jp.
Query normalization added by Peter Geoghegan peter@2ndquadrant.com.
