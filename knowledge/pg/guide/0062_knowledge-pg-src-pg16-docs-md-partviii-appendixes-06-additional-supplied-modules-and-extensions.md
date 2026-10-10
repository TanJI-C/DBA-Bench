# Overview; Sample Output

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVIII_appendixes/06_additional_supplied_modules_and_extensions.md`
- Source Title: `postgresql.conf`
- Source Heading Path: `Additional Supplied Modules and Extensions > pgrowlocks - show a table row locking information > Overview; Sample Output`
- Source Line Ranges: `5341-5385, 6134-6168, 6315-6327, 6641-6741, 6742-6746`
- Chunk ID: `pg16_guide_0062_f8324e3ea3`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4e35ed4f721c352325566064c6c2685f6e04a6dac1f577c03fbb36a0d001254c`

## Retrieval Guidance

- Use When: Diagnose row-level locking conflicts that are not sufficiently explained by relation-level lock views.
- Retrieval Keywords: pgrowlocks, row locks, tuple locks, locked row, transaction ID, lock mode
- Follow-up Guidance: Correlate with pg_locks, pg_stat_activity, and transaction age before taking action.
- Classification Note: The module exposes tuple-level lock information that confirms row-lock blockers and lock modes.

## Official Source Content

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
