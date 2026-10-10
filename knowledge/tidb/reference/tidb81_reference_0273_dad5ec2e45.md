# EXPLAIN behavior and index usage for views

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explain-views.md`
- Source Title: `EXPLAIN Statements Using Views`
- Source Heading Path: `EXPLAIN Statements Using Views`
- Source Line Ranges: `5-119`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `explain`, `views`, `query-plan`, `index-lookup`, `predicate-pushdown`, `composite-index`, `base-table`, `optimizer`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0273_dad5ec2e45`
- Source ID: `tidb-docs-8.1:explain-views.md#explain-statements-using-views`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a3ade754e3daac6e6235cfdbb101b7e318b7e00ff12c0a13fbcecc9afbfee9c4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explain-views#explain-statements-using-views
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explain-views.md

## Retrieval Guidance

- Use When: Use this chunk when explaining how EXPLAIN shows plans for queries that reference a view, including why the plan lists base tables and indexes instead of the view name and how predicates and indexes are applied.
- Retrieval Keywords: EXPLAIN Statements Using Views, EXPLAIN view references base tables not view name, views are virtual tables, view definition merged during SQL optimization, IndexLookUp, IndexRangeScan, TableRowIDScan, Selection, TableFullScan, predicate pushdown from view to base table, ALTER TABLE trips ADD INDEX (duration), CREATE OR REPLACE VIEW long_trips AS SELECT * FROM trips WHERE duration > 3600, EXPLAIN SELECT * FROM long_trips, EXPLAIN SELECT * FROM trips WHERE duration > 3600, EXPLAIN SELECT * FROM long_trips WHERE bike_number = 'W00950', composite index (bike_number, duration), range:(3600,+inf], range:("W00950" 3600,"W00950" +inf]
- Follow-up Guidance: The examples further compare a duration index and a composite index `(bike_number, duration)` to show when TiDB uses the view predicate only, when it applies `bike_number = 'W00950'` after row lookup, and when both parts of the composite index are used.
- Classification Note: This is reference content because it documents the observed EXPLAIN output and index usage behavior for views, base tables, predicate pushdown, and composite indexes in specific SQL examples.

## Official Source Content

# EXPLAIN Statements Using Views

`EXPLAIN` displays the tables and indexes that a [view](https://docs.pingcap.com/tidb/stable/views) references, not the name of the view itself. This is because views are only virtual tables and do not store any data themselves. The definition of the view and the rest of the statement are merged together during SQL optimization.

From the [bikeshare example database](https://docs.pingcap.com/tidb/stable/import-example-data), you can see that the following two queries are executed in a similar manner:

From the [bikeshare example database](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-sample-data), you can see that the following two queries are executed in a similar manner:

```sql
ALTER TABLE trips ADD INDEX (duration);
CREATE OR REPLACE VIEW long_trips AS SELECT * FROM trips WHERE duration > 3600;
EXPLAIN SELECT * FROM long_trips;
EXPLAIN SELECT * FROM trips WHERE duration > 3600;
```

```sql
Query OK, 0 rows affected (2 min 10.11 sec)

Query OK, 0 rows affected (0.13 sec)

+--------------------------------+------------+-----------+---------------------------------------+-------------------------------------+
| id                             | estRows    | task      | access object                         | operator info                       |
+--------------------------------+------------+-----------+---------------------------------------+-------------------------------------+
| IndexLookUp_12                 | 6372547.67 | root      |                                       |                                     |
| ├─IndexRangeScan_10(Build)     | 6372547.67 | cop[tikv] | table:trips, index:duration(duration) | range:(3600,+inf], keep order:false |
| └─TableRowIDScan_11(Probe)     | 6372547.67 | cop[tikv] | table:trips                           | keep order:false                    |
+--------------------------------+------------+-----------+---------------------------------------+-------------------------------------+
3 rows in set (0.00 sec)

+-------------------------------+-----------+-----------+---------------------------------------+-------------------------------------+
| id                            | estRows   | task      | access object                         | operator info                       |
+-------------------------------+-----------+-----------+---------------------------------------+-------------------------------------+
| IndexLookUp_10                | 833219.37 | root      |                                       |                                     |
| ├─IndexRangeScan_8(Build)     | 833219.37 | cop[tikv] | table:trips, index:duration(duration) | range:(3600,+inf], keep order:false |
| └─TableRowIDScan_9(Probe)     | 833219.37 | cop[tikv] | table:trips                           | keep order:false                    |
+-------------------------------+-----------+-----------+---------------------------------------+-------------------------------------+
3 rows in set (0.00 sec)
```

Similarly, predicates from the view are pushed down to the base table:

```sql
EXPLAIN SELECT * FROM long_trips WHERE bike_number = 'W00950';
EXPLAIN SELECT * FROM trips WHERE bike_number = 'W00950';
```

```sql
+--------------------------------+---------+-----------+---------------------------------------+---------------------------------------------------+
| id                             | estRows | task      | access object                         | operator info                                     |
+--------------------------------+---------+-----------+---------------------------------------+---------------------------------------------------+
| IndexLookUp_14                 | 3.33    | root      |                                       |                                                   |
| ├─IndexRangeScan_11(Build)     | 3333.33 | cop[tikv] | table:trips, index:duration(duration) | range:(3600,+inf], keep order:false, stats:pseudo |
| └─Selection_13(Probe)          | 3.33    | cop[tikv] |                                       | eq(bikeshare.trips.bike_number, "W00950")         |
|   └─TableRowIDScan_12          | 3333.33 | cop[tikv] | table:trips                           | keep order:false, stats:pseudo                    |
+--------------------------------+---------+-----------+---------------------------------------+---------------------------------------------------+
4 rows in set (0.00 sec)

+-------------------------+-------------+-----------+---------------+-------------------------------------------+
| id                      | estRows     | task      | access object | operator info                             |
+-------------------------+-------------+-----------+---------------+-------------------------------------------+
| TableReader_7           | 43.00       | root      |               | data:Selection_6                          |
| └─Selection_6           | 43.00       | cop[tikv] |               | eq(bikeshare.trips.bike_number, "W00950") |
|   └─TableFullScan_5     | 19117643.00 | cop[tikv] | table:trips   | keep order:false                          |
+-------------------------+-------------+-----------+---------------+-------------------------------------------+
3 rows in set (0.00 sec)
```

In the first statement above, you can see that the index is used to satisfy the view definition, and then the `bike_number = 'W00950'` is applied when TiDB reads the table row. In the second statement, there are no indexes to satisfy the statement, and a `TableFullScan` is used.

TiDB makes use of indexes that satisfy both the view definition and the statement itself. Consider the following composite index:

```sql
ALTER TABLE trips ADD INDEX (bike_number, duration);
EXPLAIN SELECT * FROM long_trips WHERE bike_number = 'W00950';
EXPLAIN SELECT * FROM trips WHERE bike_number = 'W00950';
```
```sql
Query OK, 0 rows affected (2 min 31.20 sec)

+--------------------------------+----------+-----------+-------------------------------------------------------+-------------------------------------------------------+
| id                             | estRows  | task      | access object                                         | operator info                                         |
+--------------------------------+----------+-----------+-------------------------------------------------------+-------------------------------------------------------+
| IndexLookUp_13                 | 63725.48 | root      |                                                       |                                                       |
| ├─IndexRangeScan_11(Build)     | 63725.48 | cop[tikv] | table:trips, index:bike_number(bike_number, duration) | range:("W00950" 3600,"W00950" +inf], keep order:false |
| └─TableRowIDScan_12(Probe)     | 63725.48 | cop[tikv] | table:trips                                           | keep order:false                                      |
+--------------------------------+----------+-----------+-------------------------------------------------------+-------------------------------------------------------+
3 rows in set (0.00 sec)

+-------------------------------+----------+-----------+-------------------------------------------------------+---------------------------------------------+
| id                            | estRows  | task      | access object                                         | operator info                               |
+-------------------------------+----------+-----------+-------------------------------------------------------+---------------------------------------------+
| IndexLookUp_10                | 19117.64 | root      |                                                       |                                             |
| ├─IndexRangeScan_8(Build)     | 19117.64 | cop[tikv] | table:trips, index:bike_number(bike_number, duration) | range:["W00950","W00950"], keep order:false |
| └─TableRowIDScan_9(Probe)     | 19117.64 | cop[tikv] | table:trips                                           | keep order:false                            |
+-------------------------------+----------+-----------+-------------------------------------------------------+---------------------------------------------+
3 rows in set (0.00 sec)
```

In the first statement, TiDB is able to use both parts of the composite index `(bike_number, duration)`. In the second statement, only the first part which is `bike_number` of the index `(bike_number, duration)` is used.
