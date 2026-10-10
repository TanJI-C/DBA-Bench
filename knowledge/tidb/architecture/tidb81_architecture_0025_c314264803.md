# DM online DDL migration overview and working details

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/feature-online-ddl.md`
- Source Title: `Migrate from Databases that Use GH-ost/PT-osc`
- Source Heading Path: `Migrate from Databases that Use GH-ost/PT-osc | Migrate from Databases that Use GH-ost/PT-osc > Working details for DM with online DDL tools`
- Source Line Ranges: `5-15`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `shared`
- Topic Tags: `online-ddl`, `online-schema-change`, `gh-ost`, `pt-osc`, `migration`, `workflow`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0025_c314264803`
- Source ID: `tidb-docs-8.1:dm/feature-online-ddl.md#migrate-from-databases-that-use-gh-ost-pt-osc`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d519c7bec351e3cb28218462548f26117662fc69dd71bd24b07092f3f6fe1d2c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/feature-online-ddl#migrate-from-databases-that-use-gh-ost-pt-osc
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/feature-online-ddl.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks for an overview of how DM collaborates with gh-ost or pt-osc for online DDL during MySQL to TiDB migration.
- Retrieval Keywords: DM online DDL migration overview, Working details for DM with online DDL tools, gh-ost, pt-osc, online-schema-change, online-ddl, Migrate from Databases that Use GH-ost/PT-osc, Continuous Replication with gh-ost or pt-osc
- Follow-up Guidance: For how to enable online-ddl and the workflow after enabling it, see Continuous Replication with gh-ost or pt-osc.
- Classification Note: This chunk is classified as architecture because it introduces the overall collaboration scope and working-details context for DM with online DDL tools.

## Official Source Content

# Migrate from Databases that Use GH-ost/PT-osc

In production scenarios, table locking during DDL execution can block the reads from or writes to the database to a certain extent. Therefore, online DDL tools are often used to execute DDLs to minimize the impact on reads and writes. Common DDL tools are [gh-ost](https://github.com/github/gh-ost) and [pt-osc](https://www.percona.com/doc/percona-toolkit/3.0/pt-online-schema-change.html).

When using DM to migrate data from MySQL to TiDB, you can enable online-ddl to allow collaboration of DM and gh-ost or pt-osc. For details about how to enable online-ddl and the workflow after enabling this option, see [Continuous Replication with gh-ost or pt-osc](https://docs.pingcap.com/tidb/stable/migrate-with-pt-ghost). This document focuses on the collaboration details of DM and online DDL tools.
## Working details for DM with online DDL tools

This section describes the working details for DM with the online DDL tools [gh-ost](https://github.com/github/gh-ost) and [pt-osc](https://www.percona.com/doc/percona-toolkit/3.0/pt-online-schema-change.html) when implementing online-schema-change.
