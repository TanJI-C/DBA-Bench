# Start parallel TiDB Lightning import and verify progress

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-distributed-import.md`
- Source Title: `Use TiDB Lightning to Import Data in Parallel`
- Source Heading Path: `Use TiDB Lightning to Import Data in Parallel > Example 1: Use Dumpling + TiDB Lightning to Import Sharded Databases and Tables into TiDB in Parallel > Step 3: Start TiDB Lightning to import data | Use TiDB Lightning to Import Data in Parallel > Example 1: Use Dumpling + TiDB Lightning to Import Sharded Databases and Tables into TiDB in Parallel > Step 4: Check the import progress`
- Source Line Ranges: `116-143`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tikv`, `tiup`
- Topic Tags: `parallel-import`, `startup`, `precheck`, `disk-space`, `resource-requirements`, `region-distribution`, `batch-size`, `monitoring`, `progress`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0455_a6ddbf98e8`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-distributed-import.md#step-3-start-tidb-lightning-to-import-data`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `516bbc0711d2d8eb0e583b5b3ee05ff54cc3bade3f5edbd427b2d3fd674e399e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-distributed-import#step-3-start-tidb-lightning-to-import-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-distributed-import.md

## Retrieval Guidance

- Use When: Use this chunk when you need how to start parallel TiDB Lightning instances and what built-in prechecks and progress verification methods apply during import.
- Retrieval Keywords: tiup tidb-lightning, nohup tiup tidb-lightning -config tidb-lightning.toml > nohup.out &, SIGHUP, sort-kv-dir, lightning.check-requirements, mydumper.batch-size, empty regions exceeds max(1000, number of tables * 3), grep progress, TiDB Lightning Monitoring, parallel import prechecks
- Follow-up Guidance: After starting the import, progress can be checked by grepping the log keyword `progress` or through the monitoring console, and the import is complete after all TiDB Lightning instances finish.
- Classification Note: This is classified as an operation chunk because the content covers starting TiDB Lightning instances, automatic requirement checks during startup, and checking import progress.

## Official Source Content

### Step 3: Start TiDB Lightning to import data

During parallel import, the server configuration requirements for each TiDB Lightning node are the same as the non-parallel import mode. Each TiDB Lightning node needs to consume the same resources. It is recommended to deploy them on different servers. For detailed deployment steps, see [Deploy TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/deploy-tidb-lightning).

Start TiDB Lightning on each server in turn. If you use `nohup` to directly start it from the command line, it might exit due to the SIGHUP signal. So it is recommended to put `nohup` in the script, for example:

```shell
# !/bin/bash
nohup tiup tidb-lightning -config tidb-lightning.toml > nohup.out &
```

During parallel import, TiDB Lightning automatically performs the following checks after starting the task.

- Check whether there is enough space on the local disk (controlled by the `sort-kv-dir` configuration) and on the TiKV cluster for importing data. To learn the required disk space, see [Downstream storage space requirements](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-requirements#storage-space-of-the-target-database) and [Resource requirements](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode#environment-requirements). TiDB Lightning samples the data sources and estimates the percentage of the index size from the sample result. Because indexes are included in the estimation, there might be cases where the size of the source data is less than the available space on the local disk, but still the check fails.
- Check whether the regions in the TiKV cluster are distributed evenly and whether there are too many empty regions. If the number of empty regions exceeds max(1000, number of tables * 3), i.e. greater than the bigger one of "1000" or "3 times the number of tables ", then the import cannot be executed.
- Check whether the data is imported in order from the data sources. The size of `mydumper.batch-size` is automatically adjusted based on the result of the check. Therefore, the `mydumper.batch-size` configuration is no longer available.

You can also turn off the check and perform a forced import with the `lightning.check-requirements` configuration. For more detailed checks, see [TiDB Lightning prechecks](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-prechecks)
### Step 4: Check the import progress

After starting the import, you can check the progress in either of the following ways:

- Check the progress through the `grep` log keyword `progress`. It is updated every 5 minutes by default.
- Check the progress through the monitoring console. For details, see [TiDB Lightning Monitoring](https://docs.pingcap.com/tidb/stable/tidb-lightning/monitor-tidb-lightning).

Wait for all TiDB Lightning instances to finish, then the entire import is completed.
