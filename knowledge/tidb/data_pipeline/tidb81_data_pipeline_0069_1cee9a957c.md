# TiCDC DDL allow list and async index DDL replication

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-ddl.md`
- Source Title: `Changefeed DDL Replication`
- Source Heading Path: `Changefeed DDL Replication | Changefeed DDL Replication > DDL allow list | Changefeed DDL Replication > DDL replication considerations | Changefeed DDL Replication > DDL replication considerations > Asynchronous execution of `ADD INDEX` and `CREATE INDEX` DDLs`
- Source Line Ranges: `5-59`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tidb`, `sql`
- Topic Tags: `ddl replication`, `allow list`, `add index`, `create index`, `asynchronous execution`, `replication latency`, `ddl jobs`, `permissions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0069_1cee9a957c`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-ddl.md#changefeed-ddl-replication`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e9731c21337c49974f5ba54cd544c82b9364ed9ba0384f2daa6e90187661f0a5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-ddl#changefeed-ddl-replication
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-ddl.md

## Retrieval Guidance

- Use When: Use this chunk when determining which DDL statements TiCDC replicates and when understanding asynchronous downstream handling of `ADD INDEX` or `CREATE INDEX` DDLs.
- Retrieval Keywords: DDL allow list, TiCDC replicate DDL statements, create database, drop database, create table, drop table, add column, drop column, create index / add index, drop index, truncate table, modify column, rename table, alter column default value, alter table comment, rename index, add partition, drop partition, truncate partition, create view, drop view, alter table character set, alter database character set, recover table, add primary key, drop primary key, rebase auto id, alter table index visibility, exchange partition, reorganize partition, alter table ttl, alter table remove ttl, Asynchronous execution of `ADD INDEX` and `CREATE INDEX` DDLs, downstream is TiDB, replication latency, queueing state, ADMIN SHOW DDL JOBS, SUPER permission
- Follow-up Guidance: Starting from v8.1.2, if TiCDC has the downstream `SUPER` permission, it periodically runs `ADMIN SHOW DDL JOBS` and waits for index creation to complete before proceeding with replication.
- Classification Note: This is classified under data_pipeline because the content defines TiCDC changefeed DDL replication rules and downstream execution behavior that affect replication progress and latency.

## Official Source Content

# Changefeed DDL Replication

This document describes the rules and special cases of DDL replication in TiCDC.
## DDL allow list

Currently, TiCDC uses an allow list to determine whether to replicate a DDL statement. Only the DDL statements in the allow list are replicated to the downstream. The DDL statements not in the allow list are not replicated.

The allow list of DDL statements supported by TiCDC is as follows:

- create database
- drop database
- create table
- drop table
- add column
- drop column
- create index / add index
- drop index
- truncate table
- modify column
- rename table
- alter column default value
- alter table comment
- rename index
- add partition
- drop partition
- truncate partition
- create view
- drop view
- alter table character set
- alter database character set
- recover table
- add primary key
- drop primary key
- rebase auto id
- alter table index visibility
- exchange partition
- reorganize partition
- alter table ttl
- alter table remove ttl
## DDL replication considerations
### Asynchronous execution of `ADD INDEX` and `CREATE INDEX` DDLs

When the downstream is TiDB, TiCDC executes `ADD INDEX` and `CREATE INDEX` DDL operations asynchronously to minimize the impact on changefeed replication latency. This means that, after replicating `ADD INDEX` and `CREATE INDEX` DDLs to the downstream TiDB for execution, TiCDC returns immediately without waiting for the completion of the DDL execution. This avoids blocking subsequent DML executions.

During the execution of the `ADD INDEX` or `CREATE INDEX` DDL operation in the downstream, when TiCDC executes the next DDL operation of the same table, this DDL operation might be blocked in the `queueing` state for a long time. This can cause TiCDC to repeatedly execute this DDL operation, and if retries take too long, it might lead to replication task failure. Starting from v8.1.2, if TiCDC has the `SUPER` permission of the downstream database, it periodically runs `ADMIN SHOW DDL JOBS` to check the status of asynchronously executed DDL tasks. TiCDC will wait for index creation to complete before proceeding with replication. Although this might increase replication latency, it avoids replication task failure.

> **Note:**
>
> - If the execution of certain downstream DMLs relies on indexes that have not completed replication, these DMLs might be executed slowly, thereby affecting TiCDC replication latency.
> - Before replicating DDLs to the downstream, if a TiCDC node crashes or if the downstream is performing other write operations, the DDL replication has an extremely low probability of failure. You can check the downstream to see whether that occurs.
