# ALTER TABLE COMPACT compatibility and related statements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-alter-table-compact.md`
- Source Title: `ALTER TABLE ... COMPACT`
- Source Heading Path: `ALTER TABLE ... COMPACT > Compatibility | ALTER TABLE ... COMPACT > Compatibility > MySQL compatibility | ALTER TABLE ... COMPACT > Compatibility > TiDB Binlog and TiCDC compatibility | ALTER TABLE ... COMPACT > See also`
- Source Line Ranges: `200-213`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `ticdc`, `shared`, `tidb`
- Topic Tags: `compatibility`, `mysql-protocol`, `tidb-binlog`, `ticdc`, `logical-changes`, `see-also`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0531_5a291f17d8`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-alter-table-compact.md#compatibility`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `08b96abb9b21888ab0ba98295ad36494d773a14b0579c7e3179fb3293ab9ad10`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-table-compact#compatibility
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-alter-table-compact.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about MySQL compatibility, MySQL client support, or whether `ALTER TABLE ... COMPACT` is replicated by TiDB Binlog or TiCDC.
- Retrieval Keywords: MySQL compatibility, TiDB specific, extension to the standard SQL syntax, MySQL protocol, database drivers that comply with the MySQL protocol, TiDB Binlog, TiCDC, does not result in logical data changes, not replicated to downstream, ALTER TABLE, KILL TIDB
- Follow-up Guidance: The related statements listed are `ALTER TABLE` and `KILL TIDB`.
- Classification Note: This is reference content because it states compatibility facts for MySQL protocol usage and for TiDB Binlog and TiCDC replication behavior.

## Official Source Content

## Compatibility
### MySQL compatibility

The `ALTER TABLE ... COMPACT` syntax is TiDB specific, which is an extension to the standard SQL syntax. Although there is no equivalent MySQL syntax, you can still execute this statement by using MySQL clients or various database drivers that comply with the MySQL protocol.
### TiDB Binlog and TiCDC compatibility

The `ALTER TABLE ... COMPACT` statement does not result in logical data changes and are therefore not replicated to downstream by TiDB Binlog or TiCDC.
## See also

- [ALTER TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-table)
- [KILL TIDB](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-kill)
