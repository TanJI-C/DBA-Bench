# Switch statistics versions and prepare ANALYZE

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/statistics.md`
- Source Title: `Introduction to Statistics`
- Source Heading Path: `Introduction to Statistics > Versions of statistics > Switch between statistics versions`
- Source Line Ranges: `389-421`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `statistics`, `analyze`, `version-switching`, `drop-stats`, `count-min-sketch`, `optimizer`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0230_241ed31385`
- Source ID: `tidb-docs-8.1:statistics.md#switch-between-statistics-versions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `290bbe65b6fcb3fb0e97ce00d911b9a37df4f8ef19441e4a575e3189fef67c01`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/statistics#switch-between-statistics-versions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/statistics.md

## Retrieval Guidance

- Use When: Use this chunk when you need information about switching between statistics versions and preparing ANALYZE or DROP STATS statements for affected tables.
- Retrieval Keywords: Switch between statistics versions, tidb_analyze_version, ANALYZE TABLE, DROP STATS, mysql.stats_histograms, information_schema.tables, stats_ver = 2, Count-Min sketch, equal/IN predicate estimation, SELECT DISTINCT(CONCAT('ANALYZE TABLE ', SELECT DISTINCT(CONCAT('DROP STATS ', INTO OUTFILE '/tmp/sql.txt'
- Follow-up Guidance: The source includes SQL that lists ANALYZE TABLE statements for manually analyzed tables, SQL that generates DROP STATS statements when auto-analysis is enabled, and an example of exporting long results to a temporary file for execution.
- Classification Note: This is classified as an operation chunk because the official content describes version switching considerations and concrete SQL used to prepare ANALYZE or DROP STATS during the switch.

## Official Source Content

### Switch between statistics versions

It is recommended to ensure that all tables/indexes (and partitions) utilize statistics collection from the same version. Version 2 is recommended, however, it is not recommended to switch from one version to another without a justifiable reason such as an issue experienced with the version in use. A switch between versions might take a period of time when no statistics are available until all tables have been analyzed with the new version, which might negatively affect the optimizer plan choices if statistics are not available.

Examples of justifications to switch might include - with Version 1, there could be inaccuracies in equal/IN predicate estimation due to hash collisions when collecting Count-Min sketch statistics. Solutions are listed in the [Count-Min Sketch](#count-min-sketch) section. Alternatively, setting `tidb_analyze_version = 2` and rerunning `ANALYZE` on all objects is also a solution. In the early release of Version 2, there was a risk of memory overflow after `ANALYZE`. This issue is resolved, but initially, one solution was to set `tidb_analyze_version = 1` and rerun `ANALYZE` on all objects.

To prepare `ANALYZE` for switching between versions:

- If the `ANALYZE` statement is executed manually, manually analyze every table to be analyzed.

    ```sql
    SELECT DISTINCT(CONCAT('ANALYZE TABLE ', table_schema, '.', table_name, ';'))
    FROM information_schema.tables JOIN mysql.stats_histograms
    ON table_id = tidb_table_id
    WHERE stats_ver = 2;
    ```

- If TiDB automatically executes the `ANALYZE` statement because the auto-analysis has been enabled, execute the following statement that generates the [`DROP STATS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-stats) statement:

    ```sql
    SELECT DISTINCT(CONCAT('DROP STATS ', table_schema, '.', table_name, ';'))
    FROM information_schema.tables ON mysql.stats_histograms
    ON table_id = tidb_table_id
    WHERE stats_ver = 2;
    ```

- If the result of the preceding statement is too long to copy and paste, you can export the result to a temporary text file and then perform execution from the file like this:

    ```sql
    SELECT DISTINCT ... INTO OUTFILE '/tmp/sql.txt';
    mysql -h ${TiDB_IP} -u user -P ${TIDB_PORT} ... < '/tmp/sql.txt'
    ```
