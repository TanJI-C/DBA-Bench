# Session-level stale read variable, related links, and support

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-use-stale-read.md`
- Source Title: `Stale Read`
- Source Heading Path: `Stale Read > Session level | Stale Read > Read more | Stale Read > Need help?`
- Source Line Ranges: `447-513`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`, `tiflash`, `shared`
- Topic Tags: `stale-read`, `historical-data`, `session-variable`, `tidb_read_staleness`, `java`, `read-more`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0206_3b4f2433ac`
- Source ID: `tidb-docs-8.1:develop/dev-guide-use-stale-read.md#session-level`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2fff8a5d598c956b3e8565e290ffb58d3ff01317d81c1660b04865bab2c12d47`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-use-stale-read#session-level
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-use-stale-read.md

## Retrieval Guidance

- Use When: Use this chunk when you need the session-level stale read variable, its scope and type, enable or disable statements, or the related stale read documentation and support links.
- Retrieval Keywords: tidb_read_staleness, SESSION scope, int data type, SET @@tidb_read_staleness="-5", set @@tidb_read_staleness="", session level stale read, TiKV or TiFlash historical data, enableStaleReadOnSession, disableStaleReadOnSession, Read Historical Data Using the tidb_read_staleness System Variable, Read Historical Data Using the AS OF TIMESTAMP Clause, Usage Scenarios of Stale Read, Discord, Slack, support ticket
- Follow-up Guidance: The source links to additional stale read pages for usage scenarios, `AS OF TIMESTAMP`, and `tidb_read_staleness`, and it lists Discord, Slack, and support ticket channels for help.
- Classification Note: This is classified as reference content because it defines the `tidb_read_staleness` session variable with exact SQL and Java examples and includes related documentation and support resources.

## Official Source Content

## Session level

To support reading historical data, TiDB has introduced a new system variable `tidb_read_staleness` since v5.4. you can use it to set the range of historical data that the current session is allowed to read. Its data type is `int` and its scope is `SESSION`.

<div label="SQL" value="sql">

Enable Stale Read in a session:

```sql
SET @@tidb_read_staleness="-5";
```

For example, if the value is set to `-5` and TiKV or TiFlash has the corresponding historical data, TiDB selects a timestamp as new as possible within a 5-second time range.

Disable Stale Read in the session:

```sql
set @@tidb_read_staleness="";
```

</div>
<div label="Java" value="java">

```java
public static class StaleReadHelper{

    public static void enableStaleReadOnSession(Connection conn, Integer seconds) throws SQLException {
        PreparedStatement stmt = conn.prepareStatement(
            "SET @@tidb_read_staleness= ?;"
        );
        stmt.setString(1, String.format("-%d", seconds));
        stmt.execute();
    }

    public static void disableStaleReadOnSession(Connection conn) throws SQLException {
        PreparedStatement stmt = conn.prepareStatement(
            "SET @@tidb_read_staleness=\"\";"
        );
        stmt.execute();
    }

}
```

</div>
## Read more

- [Usage Scenarios of Stale Read](https://docs.pingcap.com/tidb/stable/stale-read)
- [Read Historical Data Using the `AS OF TIMESTAMP` Clause](https://docs.pingcap.com/tidb/stable/as-of-timestamp)
- [Read Historical Data Using the `tidb_read_staleness` System Variable](https://docs.pingcap.com/tidb/stable/tidb-read-staleness)
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
