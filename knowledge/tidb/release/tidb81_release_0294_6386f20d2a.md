# Bug fixes across TiKV, PD, TiFlash, BR, TiCDC, DM, Lightning, Dumpling, and TiDB Binlog

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.0.0-dmr.md`
- Source Title: `TiDB 6.0.0 Release Notes`
- Source Heading Path: `TiDB 6.0.0 Release Notes > Bug fixes`
- Source Line Ranges: `713-797`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tikv`, `pd`, `tiflash`, `br`, `ticdc`, `dm`, `lightning`, `dumpling`, `tidb`
- Topic Tags: `bug fixes`, `stability`, `panic`, `replication`, `restore`, `import`, `export`, `metrics`, `mpp`, `memory leak`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0294_6386f20d2a`
- Source ID: `tidb-docs-8.1:releases/release-6.0.0-dmr.md#bug-fixes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6bf48f9a6218ab24d16d27ebc2a4540266e398d2a7fe9c40c83eedcdd7355bc4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.0.0-dmr#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.0.0-dmr.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.0.0 DMR bug fixes across TiKV, PD, TiFlash, BR, TiCDC, DM, Lightning, Dumpling, or TiDB Binlog for issues such as panic, high latency, stuck restore or replication, incorrect results, memory leak, MPP hang, or metrics problems.
- Retrieval Keywords: TiDB 6.0.0 Release Notes bug fixes, TiKV panic Applying snapshot files, level0_slowdown_trigger flow control QPS drop, unsafe_destroy_range GC worker busy, StoreMeta panic, tikv-ctl incorrect result wrong string match, memory metrics overflow intermittent packet loss OOM, PD Joint Consensus meaningless steps, dr-autosync Duration dynamically configured, TiFlash memory limit panic, TiFlash canceled MPP queries hang forever local tunnel, MPP tasks leak threads forever, BR gets stuck unrecoverable errors restore, encryption information lost during backup retry, TiCDC duplicated replace SQL batch-replace-enable, Unknown system variable transaction_isolation, Canal-JSON panic string nil, Avro NOT NULL nullable field, DM syncer metrics updated only when querying the status, checkpoint has no change skip sync flush checkpoint, DML loss merging shards pessimistic mode, TiDB Lightning GC life time is shorter than transaction duration, Dumpling --sql progress not accurate, Amazon S3 compressed data size, TiDB Binlog skipped large upstream write transactions Kafka
- Follow-up Guidance: The chunk groups the fixes by component: TiKV, PD, TiFlash, BR, TiCDC, DM, TiDB Lightning, Dumpling, and TiDB Binlog.
- Classification Note: This is a release-note bug-fix summary for shared components in self-managed deployments, covering stability, replication, restore, import and export, metrics, MPP, panic, and memory-leak related fixes.

## Official Source Content

- Fix the panic issue caused by deleting snapshot files when the peer status is `Applying` [#11746](https://github.com/tikv/tikv/issues/11746)
    - Fix the issue of QPS drop when flow control is enabled and `level0_slowdown_trigger` is set explicitly [#11424](https://github.com/tikv/tikv/issues/11424)
    - Fix the issue that destroying a peer might cause high latency [#10210](https://github.com/tikv/tikv/issues/10210)
    - Fix a bug that TiKV cannot delete a range of data (which means the internal command `unsafe_destroy_range` is executed) when the GC worker is busy [#11903](https://github.com/tikv/tikv/issues/11903)
    - Fix a bug that TiKV panics when the data in `StoreMeta` is accidentally deleted in some corner cases [#11852](https://github.com/tikv/tikv/issues/11852)
    - Fix a bug that TiKV panics when performing profiling on an ARM platform [#10658](https://github.com/tikv/tikv/issues/10658)
    - Fix a bug that TiKV might panic if it has been running for 2 years or more [#11940](https://github.com/tikv/tikv/issues/11940)
    - Fix the compilation issue on the ARM64 architecture caused by missing SSE instruction set [#12034](https://github.com/tikv/tikv/issues/12034)
    - Fix the issue that deleting an uninitialized replica might cause an old replica to be recreated [#10533](https://github.com/tikv/tikv/issues/10533)
    - Fix a bug that stale messages cause TiKV to panic [#12023](https://github.com/tikv/tikv/issues/12023)
    - Fix the issue that undefined behavior (UB) might occur in TsSet conversions [#12070](https://github.com/tikv/tikv/issues/12070)
    - Fix a bug that replica reads might violate the linearizability [#12109](https://github.com/tikv/tikv/issues/12109)
    - Fix the potential panic issue that occurs when TiKV performs profiling on Ubuntu 18.04 [#9765](https://github.com/tikv/tikv/issues/9765)
    - Fix the issue that tikv-ctl returns an incorrect result due to its wrong string match [#12329](https://github.com/tikv/tikv/issues/12329)
    - Fix the issue of intermittent packet loss and out of memory (OOM) caused by the overflow of memory metrics [#12160](https://github.com/tikv/tikv/issues/12160)
    - Fix the potential issue of mistakenly reporting TiKV panics when exiting TiKV [#12231](https://github.com/tikv/tikv/issues/12231)

+ PD

    - Fix the issue that PD generates the operator with meaningless steps of Joint Consensus [#4362](https://github.com/tikv/pd/issues/4362)
    - Fix a bug that the TSO revoking process might get stuck when closing the PD client [#4549](https://github.com/tikv/pd/issues/4549)
    - Fix the issue that the Region scatterer scheduling lost some peers [#4565](https://github.com/tikv/pd/issues/4565)
    - Fix the issue that `Duration` fields of `dr-autosync` cannot be dynamically configured [#4651](https://github.com/tikv/pd/issues/4651)

+ TiFlash

    - Fix the TiFlash panic issue that occurs when the memory limit is enabled [#3902](https://github.com/pingcap/tiflash/issues/3902)
    - Fix the issue that expired data is recycled slowly [#4146](https://github.com/pingcap/tiflash/issues/4146)
    - Fix the potential issue of TiFlash panic when `Snapshot` is applied simultaneously with multiple DDL operations [#4072](https://github.com/pingcap/tiflash/issues/4072)
    - Fix the potential query error after adding columns under heavy read workload [#3967](https://github.com/pingcap/tiflash/issues/3967)
    - Fix the issue that the `SQRT` function with a negative argument returns `NaN` instead of `Null` [#3598](https://github.com/pingcap/tiflash/issues/3598)
    - Fix the issue that casting `INT` to `DECIMAL` might cause overflow [#3920](https://github.com/pingcap/tiflash/issues/3920)
    - Fix the issue that the result of `IN` is incorrect in multi-value expressions [#4016](https://github.com/pingcap/tiflash/issues/4016)
    - Fix the issue that the date format identifies `'\n'` as an invalid separator [#4036](https://github.com/pingcap/tiflash/issues/4036)
    - Fix the issue that the learner-read process takes too much time under high concurrency scenarios [#3555](https://github.com/pingcap/tiflash/issues/3555)
    - Fix the wrong result that occurs when casting `DATETIME` to `DECIMAL` [#4151](https://github.com/pingcap/tiflash/issues/4151)
    - Fix the issue of memory leak that occurs when a query is canceled [#4098](https://github.com/pingcap/tiflash/issues/4098)
    - Fix a bug that enabling the elastic thread pool might cause a memory leak [#4098](https://github.com/pingcap/tiflash/issues/4098)
    - Fix a bug that canceled MPP queries might cause tasks to hang forever when the local tunnel is enabled [#4229](https://github.com/pingcap/tiflash/issues/4229)
    - Fix a bug that the failure of the HashJoin build side might cause MPP queries to hang forever [#4195](https://github.com/pingcap/tiflash/issues/4195)
    - Fix a bug that MPP tasks might leak threads forever [#4238](https://github.com/pingcap/tiflash/issues/4238)

+ Tools

    + Backup & Restore (BR)

        - Fix a bug that BR gets stuck when the restore operation meets some unrecoverable errors [#33200](https://github.com/pingcap/tidb/issues/33200)
        - Fix a bug that causes the restore operation to fail when the encryption information is lost during backup retry [#32423](https://github.com/pingcap/tidb/issues/32423)

    + TiCDC

        - Fix a bug that MySQL sink generates duplicated `replace` SQL statements when `batch-replace-enable` is disabled [#4501](https://github.com/pingcap/tiflow/issues/4501)
        - Fix a bug that a TiCDC node exits abnormally when a PD leader is killed [#4248](https://github.com/pingcap/tiflow/issues/4248)
        - Fix the error `Unknown system variable 'transaction_isolation'` for some MySQL versions [#4504](https://github.com/pingcap/tiflow/issues/4504)
        - Fix the TiCDC panic issue that might occur when `Canal-JSON` incorrectly handles `string` [#4635](https://github.com/pingcap/tiflow/issues/4635)
        - Fix a bug that sequence is incorrectly replicated in some cases [#4552](https://github.com/pingcap/tiflow/issues/4552)
        - Fix the TiCDC panic issue that might occur because `Canal-JSON` does not support nil [#4736](https://github.com/pingcap/tiflow/issues/4736)
        - Fix the wrong data mapping for avro codec of type `Enum/Set` and `TinyText/MediumText/Text/LongText` [#4454](https://github.com/pingcap/tiflow/issues/4454)
        - Fix a bug that Avro converts a `NOT NULL` column to a nullable field [#4818](https://github.com/pingcap/tiflow/issues/4818)
        - Fix an issue that TiCDC cannot exit [#4699](https://github.com/pingcap/tiflow/issues/4699)

    + TiDB Data Migration (DM)
        - Fix the issue that syncer metrics are updated only when querying the status [#4281](https://github.com/pingcap/tiflow/issues/4281)
        - Fix the issue that execution errors of the update statement in safemode may cause the DM-worker panic [#4317](https://github.com/pingcap/tiflow/issues/4317)
        - Fix a bug that long varchars report an error `Column length too big` [#4637](https://github.com/pingcap/tiflow/issues/4637)
        - Fix the conflict issue caused by multiple DM-workers writing data from the same upstream [#3737](https://github.com/pingcap/tiflow/issues/3737)
        - Fix the issue that hundreds of "checkpoint has no change, skip sync flush checkpoint" print in the log and the replication is very slow [#4619](https://github.com/pingcap/tiflow/issues/4619)
        - Fix the DML loss issue when merging shards and replicating incremental data from upstream in the pessimistic mode [#5002](https://github.com/pingcap/tiflow/issues/5002)

    + TiDB Lightning

        - Fix a bug that TiDB Lightning may not delete the metadata schema when some import tasks do not contain source files [#28144](https://github.com/pingcap/tidb/issues/28144)
        - Fix the panic that occurs when the table names in the source file and in the target cluster are different [#31771](https://github.com/pingcap/tidb/issues/31771)
        - Fix the checksum error "GC life time is shorter than transaction duration" [#32733](https://github.com/pingcap/tidb/issues/32733)
        - Fix the issue that TiDB Lightning gets stuck when it fails to check empty tables [#31797](https://github.com/pingcap/tidb/issues/31797)

    + Dumpling

        - Fix the issue that the displayed progress is not accurate when running `dumpling --sql $query` [#30532](https://github.com/pingcap/tidb/issues/30532)
        - Fix the issue that Amazon S3 cannot correctly calculate the size of compressed data [#30534](https://github.com/pingcap/tidb/issues/30534)

    + TiDB Binlog

        - Fix the issue that TiDB Binlog might be skipped when large upstream write transactions are replicated to Kafka [#1136](https://github.com/pingcap/tidb-binlog/issues/1136)
