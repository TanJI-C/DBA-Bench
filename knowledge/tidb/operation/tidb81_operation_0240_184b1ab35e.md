# Run output, progress, results, and generated fix SQL

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sync-diff-inspector/sync-diff-inspector-overview.md`
- Source Title: `sync-diff-inspector User Guide`
- Source Heading Path: `sync-diff-inspector User Guide > Run sync-diff-inspector > Progress information | sync-diff-inspector User Guide > Run sync-diff-inspector > Output file | sync-diff-inspector User Guide > Run sync-diff-inspector > Log | sync-diff-inspector User Guide > Run sync-diff-inspector > Progress | sync-diff-inspector User Guide > Run sync-diff-inspector > Result | sync-diff-inspector User Guide > Run sync-diff-inspector > SQL statements to fix inconsistent data`
- Source Line Ranges: `179-291`
- Source Scope: `shared`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `sql`, `shared`
- Topic Tags: `progress`, `stdout`, `output-files`, `checkpoint`, `log`, `summary`, `report`, `data-comparison`, `repair-sql`, `inconsistency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0240_184b1ab35e`
- Source ID: `tidb-docs-8.1:sync-diff-inspector/sync-diff-inspector-overview.md#progress-information`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a6e05664bb2ea92c9402b9cf252adb448987a9e4bb17eaaab37fc1842047182c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sync-diff-inspector/sync-diff-inspector-overview#progress-information
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sync-diff-inspector/sync-diff-inspector-overview.md

## Retrieval Guidance

- Use When: Use this chunk when you need the exact sync-diff-inspector runtime outputs, output directory layout, checkpoint and log file locations, summary report fields, or generated SQL file behavior for inconsistent data.
- Retrieval Keywords: sync-diff-inspector stdout progress information, Comparing the table structure, Comparing the table data, Progress [, output/sync_diff.log, ${output}/sync_diff.log, ${output}/checkpoint/sync_diff_checkpoints.pb, sync_diff_checkpoints.pb, ${output}/summary.txt, summary.txt, output-dir, fix-on-target, ${output}/fix-on-${instance}, task.target-instance, checkpoint, summary report, STRUCTURE EQUALITY, DATA DIFF ROWS, UPCOUNT, DOWNCOUNT, The data of, The patch file has been generated in, REPLACE INTO, DELETE statements, chunk.Index
- Follow-up Guidance: The source also states that the generated SQL file includes the table name and chunk range information, and uses REPLACE or DELETE statements depending on whether rows are missing, redundant, or inconsistent.
- Classification Note: This is classified as operation content because it describes what sync-diff-inspector prints while running, where it stores checkpoint, log, summary, and fix SQL files, and how to interpret comparison results.

## Official Source Content

### Progress information

sync-diff-inspector sends progress information to `stdout` when running. Progress information includes the comparison results of table structures, comparison results of table data and the progress bar.

> **Note:**
>
> To ensure the display effect, keep the display window width above 80 characters.

```
A total of 2 tables need to be compared

Comparing the table structure of ``sbtest`.`sbtest96`` ... equivalent
Comparing the table structure of ``sbtest`.`sbtest99`` ... equivalent
Comparing the table data of ``sbtest`.`sbtest96`` ... failure
Comparing the table data of ``sbtest`.`sbtest99`` ...
_____________________________________________________________________________
Progress [==========================================================>--] 98% 193/200
```

```
A total of 2 tables need to be compared

Comparing the table structure of ``sbtest`.`sbtest96`` ... equivalent
Comparing the table structure of ``sbtest`.`sbtest99`` ... equivalent
Comparing the table data of ``sbtest`.`sbtest96`` ... failure
Comparing the table data of ``sbtest`.`sbtest99`` ... failure
_____________________________________________________________________________
Progress [============================================================>] 100% 0/0
The data of `sbtest`.`sbtest99` is not equal
The data of `sbtest`.`sbtest96` is not equal

The rest of tables are all equal.

A total of 2 tables have been compared, 0 tables finished, 2 tables failed, 0 tables skipped.
The patch file has been generated in
        'output/fix-on-tidb2/'
You can view the comparison details through 'output/sync_diff.log'
```
### Output file

The directory structure of the output file is as follows:

```
output/
|-- checkpoint # Saves the breakpoint information
| |-- bbfec8cc8d1f58a5800e63aa73e5 # Config hash. The placeholder file which identifies the configuration file corresponding to the output directory (output/)
│ |-- DO_NOT_EDIT_THIS_DIR
│ └-- sync_diff_checkpoints.pb # The breakpoint information
|
|-- fix-on-target # Saves SQL files to fix data inconsistency
| |-- xxx.sql
| |-- xxx.sql
| └-- xxx.sql
|
|-- summary.txt # Saves the summary of the check results
└-- sync_diff.log # Saves the output log information when sync-diff-inspector is running
```
### Log

The log of sync-diff-inspector is saved in `${output}/sync_diff.log`, among which `${output}` is the value of `output-dir` in the `config.toml` file.
### Progress

The running sync-diff-inspector periodically (every 10 seconds) prints the progress in checkpoint, which is located at `${output}/checkpoint/sync_diff_checkpoints.pb`, among which `${output}` is the value of `output-dir` in the `config.toml` file.
### Result

After the check is finished, sync-diff-inspector outputs a report. It is located at `${output}/summary.txt`, and `${output}` is the value of `output-dir` in the `config.toml` file.

```
+---------------------+--------------------+----------------+---------+-----------+
|        TABLE        | STRUCTURE EQUALITY | DATA DIFF ROWS | UPCOUNT | DOWNCOUNT |
+---------------------+--------------------+----------------+---------+-----------+
| `sbtest`.`sbtest99` | true               | +97/-97        |  999999 |    999999 |
| `sbtest`.`sbtest96` | true               | +0/-101        |  999999 |   1000100 |
+---------------------+--------------------+----------------+---------+-----------+
Time Cost: 16.75370462s
Average Speed: 113.277149MB/s
```

- `TABLE`: The corresponding database and table names
- `RESULT`: Whether the check is completed. If you have configured `skip-non-existing-table = true`, the value of this column is `skipped` for tables that do not exist in the upstream or downstream
- `STRUCTURE EQUALITY`: Checks whether the table structure is the same
- `DATA DIFF ROWS`: `rowAdd`/`rowDelete`. Indicates the number of rows that need to be added/deleted to fix the table
- `UPCOUNT`: The number of rows in this table in the upstream data source
- `DOWNCOUNT`: The number of rows in this table in the downstream data source
### SQL statements to fix inconsistent data

If different rows exist during the data checking process, the SQL statements will be generated to fix them. If the data inconsistency exists in a chunk, a SQL file named by `chunk.Index` will be generated. The SQL file is located at `${output}/fix-on-${instance}`, and `${instance}` is the value of `task.target-instance` in the `config.toml` file.

A SQL file contains the tale to which the chunk belong and the range information. For the SQL files, you should consider the following three situations:

- If the rows in the downstream database are missing, REPLACE statements will be applied
- If the rows in the downstream database are redundant, DELETE statements will be applied
- If some data of the rows in the downstream database is inconsistent, REPLACE statements will be applied and inconsistent columns will be marked with annotation in the SQL file

```sql
-- table: sbtest.sbtest99
-- range in sequence: (3690708) < (id) <= (3720581)
/*
  DIFF COLUMNS ╏   `K`   ╏                `C`                 ╏               `PAD`
╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╋╍╍╍╍╍╍╍╍╍╋╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╋╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍
  source data  ╏ 2501808 ╏ 'hello'                            ╏ 'world'
╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╋╍╍╍╍╍╍╍╍╍╋╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╋╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍
  target data  ╏ 5003616 ╏ '0709824117-9809973320-4456050422' ╏ '1714066100-7057807621-1425865505'
╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╋╍╍╍╍╍╍╍╍╍╋╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╋╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍
*/
REPLACE INTO `sbtest`.`sbtest99`(`id`,`k`,`c`,`pad`) VALUES (3700000,2501808,'hello','world');
```
