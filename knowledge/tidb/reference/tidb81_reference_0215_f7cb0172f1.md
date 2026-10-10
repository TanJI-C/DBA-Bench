# DM skipped and rewritten DDL statement handling

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-ddl-compatible.md`
- Source Title: `Special Handling of DM DDLs`
- Source Heading Path: `Special Handling of DM DDLs | Special Handling of DM DDLs > Skip DDL statements | Special Handling of DM DDLs > Rewrite DDL statements`
- Source Line Ranges: `5-136`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `sql`
- Topic Tags: `ddl`, `statement-handling`, `skip-rules`, `rewrite-rules`, `replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0215_f7cb0172f1`
- Source ID: `tidb-docs-8.1:dm/dm-ddl-compatible.md#special-handling-of-dm-ddls`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2ca631c602e3957dbcfd6c4da4c7feed2be173551160f6c70c09e27653e21e64`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-ddl-compatible#special-handling-of-dm-ddls
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-ddl-compatible.md

## Retrieval Guidance

- Use When: Use this chunk when identifying which DDL statements DM skips directly after parsing and which DDL statements DM rewrites before replicating them downstream.
- Retrieval Keywords: Special Handling of DM DDLs, Skip DDL statements, Rewrite DDL statements, DM skipped DDL, DM rewritten DDL, ^SAVEPOINT, ^FLUSH, ^OPTIMIZE\s+TABLE, ^ANALYZE\s+TABLE, ^REPAIR\s+TABLE, ^DROP\s+(\/\*\!40005\s+)?TEMPORARY\s+(\*\/\s+)?TABLE, ^CREATE\s+(DEFINER\s?=.+?)?TRIGGER, ^DROP\s+TRIGGER, ^DROP\s+PROCEDURE, ^CREATE\s+(DEFINER\s?=.+?)?PROCEDURE, ^ALTER\s+PROCEDURE, ^CREATE\s*(OR REPLACE)?\s+(ALGORITHM\s?=.+?)?(DEFINER\s?=.+?)?\s+(SQL SECURITY DEFINER)?VIEW, ^DROP\s+VIEW, ^ALTER\s+(ALGORITHM\s?=.+?)?(DEFINER\s?=.+?)?(SQL SECURITY DEFINER)?VIEW, ^CREATE\s+(AGGREGATE)?\s*?FUNCTION, ^CREATE\s+(DEFINER\s?=.+?)?FUNCTION, ^ALTER\s+FUNCTION, ^DROP\s+FUNCTION, ^CREATE\s+TABLESPACE, ^ALTER\s+TABLESPACE, ^DROP\s+TABLESPACE, ^CREATE\s+(DEFINER\s?=.+?)?EVENT, ^ALTER\s+(DEFINER\s?=.+?)?EVENT, ^DROP\s+EVENT, ^GRANT, ^REVOKE, ^CREATE\s+USER, ^ALTER\s+USER, ^RENAME\s+USER, ^DROP\s+USER, ^CREATE DATABASE...IF NOT EXISTS, ^CREATE TABLE...IF NOT EXISTS, ^DROP DATABASE...IF EXISTS, ^DROP TABLE...IF EXISTS, ^DROP INDEX...IF EXISTS
- Follow-up Guidance: The source also lists shard merge migration tasks and Online DDL as cases where DDL events are handled specially, with separate detail pages referenced.
- Classification Note: This is reference content because it enumerates exact SQL patterns that DM skips and exact DDL forms that DM rewrites during replication.

## Official Source Content

# Special Handling of DM DDLs

When TiDB Data Migration (DM) migrates data, it parses the DDL statements and handles them according to the statement type and the current migration stage.
## Skip DDL statements

The following statements are not supported by DM, so DM skips them directly after parsing.

<table>
    <tr>
        <th>Description</th>
        <th>SQL</th>
    </tr>
    <tr>
        <td>transaction</td>
        <td><code>^SAVEPOINT</code></td>
    </tr>
    <tr>
        <td>skip all flush sqls</td>
        <td><code>^FLUSH</code></td>
    </tr>
    <tr>
        <td rowspan="3">table maintenance</td>
        <td><code>^OPTIMIZE\\s+TABLE</code></td>
    </tr>
    <tr>
        <td><code>^ANALYZE\\s+TABLE</code></td>
    </tr>
    <tr>
        <td><code>^REPAIR\\s+TABLE</code></td>
    </tr>
    <tr>
        <td>temporary table</td>
        <td><code>^DROP\\s+(\\/\\*\\!40005\\s+)?TEMPORARY\\s+(\\*\\/\\s+)?TABLE</code></td>
    </tr>
    <tr>
        <td rowspan="2">trigger</td>
        <td><code>^CREATE\\s+(DEFINER\\s?=.+?)?TRIGGER</code></td>
    </tr>
    <tr>
        <td><code>^DROP\\s+TRIGGER</code></td>
    </tr>
    <tr>
        <td rowspan="3">procedure</td>
        <td><code>^DROP\\s+PROCEDURE</code></td>
    </tr>
    <tr>
        <td><code>^CREATE\\s+(DEFINER\\s?=.+?)?PROCEDURE</code></td>
    </tr>
    <tr>
        <td><code>^ALTER\\s+PROCEDURE</code></td>
    </tr>
    <tr>
        <td rowspan="3">view</td>
        <td><code>^CREATE\\s*(OR REPLACE)?\\s+(ALGORITHM\\s?=.+?)?(DEFINER\\s?=.+?)?\\s+(SQL SECURITY DEFINER)?VIEW</code></td>
    </tr>
    <tr>
        <td><code>^DROP\\s+VIEW</code></td>
    </tr>
    <tr>
        <td><code>^ALTER\\s+(ALGORITHM\\s?=.+?)?(DEFINER\\s?=.+?)?(SQL SECURITY DEFINER)?VIEW</code></td>
    </tr>
    <tr>
        <td rowspan="4">function</td>
        <td><code>^CREATE\\s+(AGGREGATE)?\\s*?FUNCTION</code></td>
    </tr>
    <tr>
        <td><code>^CREATE\\s+(DEFINER\\s?=.+?)?FUNCTION</code></td>
    </tr>
    <tr>
        <td><code>^ALTER\\s+FUNCTION</code></td>
    </tr>
    <tr>
        <td><code>^DROP\\s+FUNCTION</code></td>
    </tr>
    <tr>
        <td rowspan="3">tableSpace</td>
        <td><code>^CREATE\\s+TABLESPACE</code></td>
    </tr>
    <tr>
        <td><code>^ALTER\\s+TABLESPACE</code></td>
    </tr>
    <tr>
        <td><code>^DROP\\s+TABLESPACE</code></td>
    </tr>
    <tr>
        <td rowspan="3">event</td>
        <td><code>^CREATE\\s+(DEFINER\\s?=.+?)?EVENT</code></td>
    </tr>
    <tr>
        <td><code>^ALTER\\s+(DEFINER\\s?=.+?)?EVENT</code></td>
    </tr>
    <tr>
        <td><code>^DROP\\s+EVENT</code></td>
    </tr>
    <tr>
        <td rowspan="7">account management</td>
        <td><code>^GRANT</code></td>
    </tr>
    <tr>
        <td><code>^REVOKE</code></td>
    </tr>
    <tr>
        <td><code>^CREATE\\s+USER</code></td>
    </tr>
    <tr>
        <td><code>^ALTER\\s+USER</code></td>
    </tr>
    <tr>
        <td><code>^RENAME\\s+USER</code></td>
    </tr>
    <tr>
        <td><code>^DROP\\s+USER</code></td>
    </tr>
    <tr>
        <td><code>^DROP\\s+USER</code></td>
    </tr>
</table>
## Rewrite DDL statements

The following statements are rewritten before being replicated to the downstream.

|Original statement|Rewritten statement|
|-|-|
|`^CREATE DATABASE...`|`^CREATE DATABASE...IF NOT EXISTS`|
|`^CREATE TABLE...`|`^CREATE TABLE..IF NOT EXISTS`|
|`^DROP DATABASE...`|`^DROP DATABASE...IF EXISTS`|
|`^DROP TABLE...`|`^DROP TABLE...IF EXISTS`|
|`^DROP INDEX...`|`^DROP INDEX...IF EXISTS`|
