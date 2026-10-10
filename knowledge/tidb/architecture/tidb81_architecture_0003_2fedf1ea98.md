# TiDB DDL Owner module and owner inspection

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/ddl-introduction.md`
- Source Title: `Execution Principles and Best Practices of DDL Statements`
- Source Heading Path: `Execution Principles and Best Practices of DDL Statements > DDL execution principles > TiDB DDL module`
- Source Line Ranges: `38-62`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `sql`
- Topic Tags: `ddl-owner`, `owner-election`, `etcd`, `run-ddl`, `admin-show-ddl`, `failover`, `cluster-coordination`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0003_2fedf1ea98`
- Source ID: `tidb-docs-8.1:best-practices/ddl-introduction.md#tidb-ddl-module`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e592d7e5dc62bd364947cc08f44f3358b9551ec785009e65223e0613ce5b0fc5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/ddl-introduction#tidb-ddl-module
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/ddl-introduction.md

## Retrieval Guidance

- Use When: Use this chunk when identifying what the TiDB DDL Owner is, how owner election works across TiDB nodes through etcd, or how to view the current owner with SQL.
- Retrieval Keywords: DDL Owner, Owner, TiDB DDL module, etcd election mechanism, run-ddl, ADMIN SHOW DDL, OWNER_ID, OWNER_ADDRESS, SELF_ID, RUNNING_JOBS, SCHEMA_VER, only one TiDB node, continue executing DDL tasks
- Follow-up Guidance: The source provides the `ADMIN SHOW DDL;` statement and shows output columns including `OWNER_ID`, `OWNER_ADDRESS`, `RUNNING_JOBS`, and `SELF_ID` for inspecting the current DDL owner.
- Classification Note: This is classified as architecture content because it describes the cluster-level DDL Owner role, single-owner execution model, etcd-based election, and owner failover behavior in TiDB.

## Official Source Content

### TiDB DDL module

The TiDB DDL module introduces the role of the DDL Owner (or Owner), which serves as a proxy for executing all DDL statements within the TiDB cluster. In the current implementation, only one TiDB node in the entire cluster can be elected as the Owner at any given time. Once a TiDB node is elected as Owner, the worker started in that TiDB node can handle the DDL tasks in the cluster.

TiDB uses the election mechanism of etcd to elect a node to host the Owner from multiple TiDB nodes. By default, each TiDB node can potentially be elected as the Owner (you can configure `run-ddl` to manage node participation in the election). The elected Owner node has a term, and it actively maintains the term by renewing it. When the Owner node is down, another node can be elected as the new Owner through etcd and continue executing DDL tasks in the cluster.

A simple illustration of the DDL Owner is as follows:

![DDL Owner](/media/ddl-owner.png)

You can use the `ADMIN SHOW DDL` statement to view the current DDL owner:

```sql
ADMIN SHOW DDL;
```

```sql
+------------+--------------------------------------+---------------+--------------+--------------------------------------+-------+
| SCHEMA_VER | OWNER_ID                             | OWNER_ADDRESS | RUNNING_JOBS | SELF_ID                              | QUERY |
+------------+--------------------------------------+---------------+--------------+--------------------------------------+-------+
|         26 | 2d1982af-fa63-43ad-a3d5-73710683cc63 | 0.0.0.0:4000  |              | 2d1982af-fa63-43ad-a3d5-73710683cc63 |       |
+------------+--------------------------------------+---------------+--------------+--------------------------------------+-------+
1 row in set (0.00 sec)
```
