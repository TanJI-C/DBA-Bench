# Source migration user privileges for Data Migration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/migrate-from-mysql-using-data-migration.md`
- Source Title: `Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration`
- Source Heading Path: `Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Prerequisites > Grant required privileges for migration | Migrate MySQL-Compatible Databases to TiDB Cloud Using Data Migration > Prerequisites > Grant required privileges for migration > Grant required privileges to the migration user in the source MySQL database`
- Source Line Ranges: `291-313`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dm`, `sql`
- Topic Tags: `privileges`, `grant`, `source-user`, `replication`, `full-dump`, `binlog`, `mysql`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0245_4a64049928`
- Source ID: `tidb-docs-8.1:tidb-cloud/migrate-from-mysql-using-data-migration.md#grant-required-privileges-for-migration`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `35ab2f1a8212e0860c69a866b90f869452dfbac43f0e0bfe59d32492df3dfa04`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-mysql-using-data-migration#grant-required-privileges-for-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/migrate-from-mysql-using-data-migration.md

## Retrieval Guidance

- Use When: Use this chunk when you need the required source MySQL user privileges for TiDB Cloud Data Migration full dump and binlog replication.
- Retrieval Keywords: Grant required privileges for migration, source MySQL database, migration user, dedicated user for data dump and replication, SELECT, RELOAD, REPLICATION SLAVE, REPLICATION CLIENT, GRANT SELECT, RELOAD, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'dm_source_user'@'%';, binlog streaming, binlog position, server status, full dump, incremental replication
- Follow-up Guidance: The content distinguishes testing with an administrative user such as `root` from production workloads where a dedicated user with only the necessary privileges is recommended.
- Classification Note: This is classified as configuration because the content specifies the exact privilege configuration and example GRANT statement required for the source migration user.

## Official Source Content

### Grant required privileges for migration

Before starting migration, you need to set up appropriate database users with the required privileges on both the source and target databases. These privileges enable TiDB Cloud DM to read data from MySQL, replicate changes, and write to your TiDB Cloud cluster securely. Because the migration involves both full data dumps for existing data and binlog replication for incremental changes, your migration user requires specific permissions beyond basic read access.
#### Grant required privileges to the migration user in the source MySQL database

For testing purposes, you can use an administrative user (such as `root`) in your source MySQL database.

For production workloads, it is recommended to have a dedicated user for data dump and replication in the source MySQL database, and grant only the necessary privileges:

| Privilege | Scope | Purpose |
|:----------|:------|:--------|
| `SELECT` | Tables | Allows reading data from all tables |
| `RELOAD` | Global | Ensures consistent snapshots during full dump |
| `REPLICATION SLAVE` | Global | Enables binlog streaming for incremental replication |
| `REPLICATION CLIENT` | Global | Provides access to binlog position and server status |

For example, you can use the following `GRANT` statement in your source MySQL instance to grant corresponding privileges:

```sql
GRANT SELECT, RELOAD, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'dm_source_user'@'%';
```
