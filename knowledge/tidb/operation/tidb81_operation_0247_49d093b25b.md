# BDR DDL types roles and replication procedures

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-bidirectional-replication.md`
- Source Title: `Bidirectional Replication`
- Source Heading Path: `Bidirectional Replication > DDL types | Bidirectional Replication > DDL types > Replicable DDLs | Bidirectional Replication > DDL types > Non-replicable DDLs | Bidirectional Replication > DDL replication | Bidirectional Replication > DDL replication > Replication scenarios of replicable DDLs | Bidirectional Replication > DDL replication > Replication scenarios of non-replicable DDLs`
- Source Line Ranges: `37-139`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tidb`
- Topic Tags: `ddl replication`, `bdr roles`, `primary`, `secondary`, `replicable ddls`, `non-replicable ddls`, `experimental feature`, `manual ddl execution`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0247_49d093b25b`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-bidirectional-replication.md#ddl-types`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `917e956ef35e692bcdc8c6c67f6414742a1d61a45dd7cdf78adc1f90c4d3ea4d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-bidirectional-replication#ddl-types
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-bidirectional-replication.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks which DDLs are replicable or non-replicable in TiCDC bidirectional replication, how `PRIMARY` and `SECONDARY` BDR roles work, or when `Error 8263` appears during DDL execution.
- Retrieval Keywords: DDL types, Replicable DDLs, Non-replicable DDLs, DDL replication, PRIMARY, SECONDARY, ADMIN SET BDR ROLE PRIMARY, ADMIN SET BDR ROLE SECONDARY, ADMIN SHOW BDR ROLE, ADMIN UNSET BDR ROLE, Error 8263, bdr_mode=true, experimental
- Follow-up Guidance: The source describes two procedures: execute replicable DDLs on the `PRIMARY` cluster for TiCDC replication, or unset BDR roles on all clusters and manually execute non-replicable DDLs on each cluster after writes are fully replicated.
- Classification Note: This is classified as operation because the content defines runtime DDL behavior in BDR mode, the `PRIMARY` and `SECONDARY` roles, the allowed and blocked DDL categories, and the procedures for replicable and non-replicable DDL execution.

## Official Source Content

## DDL types

Starting from v7.6.0, to support DDL replication as much as possible in bi-directional replication, TiDB divides the [DDLs that TiCDC originally supports](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-ddl) into two types: replicable DDLs and non-replicable DDLs, according to the impact of DDLs on the business.
### Replicable DDLs

Replicable DDLs are the DDLs that can be directly executed and replicated to other TiDB clusters in bi-directional replication.

Replicable DDLs include:

- `CREATE DATABASE`
- `CREATE TABLE`
- `ADD COLUMN`: the column can be `null`, or has `not null` and `default value` at the same time
- `ADD NON-UNIQUE INDEX`
- `DROP INDEX`
- `MODIFY COLUMN`: you can only modify the `default value` and `comment` of the column
- `ALTER COLUMN DEFAULT VALUE`
- `MODIFY TABLE COMMENT`
- `RENAME INDEX`
- `ADD TABLE PARTITION`
- `DROP PRIMARY KEY`
- `ALTER TABLE INDEX VISIBILITY`
- `ALTER TABLE TTL`
- `ALTER TABLE REMOVE TTL`
- `CREATE VIEW`
- `DROP VIEW`
### Non-replicable DDLs

Non-replicable DDLs are the DDLs that have a great impact on the business, and might cause data inconsistency between clusters. Non-replicable DDLs cannot be directly replicated to other TiDB clusters in bi-directional replication through TiCDC. Non-replicable DDLs must be executed through specific operations.

Non-replicable DDLs include:

- `DROP DATABASE`
- `DROP TABLE`
- `ADD COLUMN`: the column is `not null` and does not have a `default value`
- `DROP COLUMN`
- `ADD UNIQUE INDEX`
- `TRUNCATE TABLE`
- `MODIFY COLUMN`: you can modify the attributes of the column except `default value` and `comment`
- `RENAME TABLE`
- `DROP PARTITION`
- `TRUNCATE PARTITION`
- `ALTER TABLE CHARACTER SET`
- `ALTER DATABASE CHARACTER SET`
- `RECOVER TABLE`
- `ADD PRIMARY KEY`
- `REBASE AUTO ID`
- `EXCHANGE PARTITION`
- `REORGANIZE PARTITION`
## DDL replication

To solve the problem of replicable DDLs and non-replicable DDLs, TiDB introduces the following BDR roles:

- `PRIMARY`: you can execute replicable DDLs, but cannot execute non-replicable DDLs. Replicable DDLs will be replicated to the downstream by TiCDC.
- `SECONDARY`: you cannot execute replicable DDLs or non-replicable DDLs, but can execute the DDLs replicated by TiCDC.

When no BDR role is set, you can execute any DDL. But after you set `bdr_mode=true` on TiCDC, the executed DDL will not be replicated by TiCDC.

> **Warning:**
>
> This feature is experimental. It is not recommended that you use it in the production environment. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.
### Replication scenarios of replicable DDLs

1. Choose a TiDB cluster and execute `ADMIN SET BDR ROLE PRIMARY` to set it as the primary cluster.

    ```sql
    ADMIN SET BDR ROLE PRIMARY;
    Query OK, 0 rows affected
    Time: 0.003s

    ADMIN SHOW BDR ROLE;
    +----------+
    | BDR_ROLE |
    +----------+
    | primary  |
    +----------+
    ```

2. On other TiDB clusters, execute `ADMIN SET BDR ROLE SECONDARY` to set them as the secondary clusters.
3. Execute **replicable DDLs** on the primary cluster. The successfully executed DDLs will be replicated to the secondary clusters by TiCDC.

> **Note:**
>
> To prevent misuse:
>
> - If you try to execute **non-replicable DDLs** on the primary cluster, you will get the [Error 8263](https://docs.pingcap.com/tidb/stable/error-codes).
> - If you try to execute **replicable DDLs** or **non-replicable DDLs** on the secondary clusters, you will get the [Error 8263](https://docs.pingcap.com/tidb/stable/error-codes).
### Replication scenarios of non-replicable DDLs

1. Execute `ADMIN UNSET BDR ROLE` on all TiDB clusters to unset the BDR role.
2. Stop writing data to the tables that need to execute DDLs in all clusters.
3. Wait until all writes to the corresponding tables in all clusters are replicated to other clusters, and then manually execute all DDLs on each TiDB cluster.
4. Wait until the DDLs are completed, and then resume writing data.
5. Follow the steps in [Replication scenarios of replicable DDLs](#replication-scenarios-of-replicable-ddls) to switch back to the replication scenario of replicable DDLs.

> **Warning:**
>
> After you execute `ADMIN UNSET BDR ROLE` on all TiDB clusters, none of the DDLs are replicated by TiCDC. You need to manually execute the DDLs on each cluster separately.
