# SQL development specifications and query usage guidelines

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sql-development-specification.md`
- Source Title: `SQL Development Specifications`
- Source Heading Path: `SQL Development Specifications | SQL Development Specifications > Create and delete tables | SQL Development Specifications > `SELECT *` usage | SQL Development Specifications > Use functions on fields | SQL Development Specifications > Other specifications | SQL Development Specifications > Need help?`
- Source Line Ranges: `5-68`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`, `tiflash`, `shared`
- Topic Tags: `sql-development`, `table-creation`, `table-deletion`, `select-star`, `indexes`, `where-clause`, `functions`, `expression-index`, `multi-statements`, `pushdown`, `oom`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0183_05564f548a`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sql-development-specification.md#sql-development-specifications`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f5e33f0e1ac0e1716756707a45d555e727de8f3aaffe23b654205b5b357308cf`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sql-development-specification#sql-development-specifications
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sql-development-specification.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB SQL development guidelines about safe table creation or deletion, avoiding `SELECT *`, index-friendly `WHERE` clauses, `OR` replacement, Multi Statements behavior, or push-down related memory and OOM considerations.
- Retrieval Keywords: SQL Development Specifications, create table if not exists, drop table if exists, SELECT * usage, covering index, Use functions on fields, WHERE clause, expression index, DATE_FORMAT, str_to_date, Do not perform mathematical operations or functions on the index column, Replace OR with IN or UNION, IN must be less than 300, % prefix for fuzzy prefix queries, Multi Statements, TiDB only returns the result of the first SQL execution, computing push-down, TiKV, TiFlash, OOM, Predicate push down, TiFlash supported push-down calculations, List of Expressions for Pushdown, support ticket, Discord, Slack
- Follow-up Guidance: The source also points to TiFlash supported push-down calculations, the TiKV list of expressions for pushdown, Predicate push down, and community or support channels including Discord, Slack, and support ticket links.
- Classification Note: This chunk is reference content because it lists general SQL development specifications and query usage guidelines, including exact SQL patterns, limits, and component-specific push-down references.

## Official Source Content

# SQL Development Specifications

This document introduces some general development specifications for using SQL.
## Create and delete tables

- Basic principle: under the premise of following the table naming convention, it is recommended that the application internally packages the table creation and deletion statements and adds judgment logic to prevent abnormal interruption of business processes.
- Details: `create table if not exists table_name` or `drop table if exists table_name` statements are recommended to add `if` judgments to avoid abnormal interruptions caused by SQL commands running abnormally on the application side.
## `SELECT *` usage

- Basic principle: avoid using `SELECT *` for queries.
- Details: select the appropriate columns as required and avoid using `SELECT *` to read all fields because such operations consume network bandwidth. Consider adding the queried fields to the index to make effective use of the covering index.
## Use functions on fields

- Basic principle: You can use related functions on the queried fields. To avoid index failure, do not use any functions on the filtered fields in the `WHERE` clause, including data type conversion functions. You may consider using the expression index.
- Detailed description:

    NOT recommended:

    ```sql
    SELECT gmt_create
    FROM ...
    WHERE DATE_FORMAT(gmt_create, '%Y%m%d %H:%i:%s') = '20090101 00:00:00'
    ```

    Recommended:

    ```sql
    SELECT DATE_FORMAT(gmt_create, '%Y%m%d %H:%i:%s')
    FROM ...
    WHERE gmt_create = str_to_date('20090101 00:00:00', '%Y%m%d %H:%i:%s')
    ```
## Other specifications

- Do not perform mathematical operations or functions on the index column in the `WHERE` condition.
- Replace `OR` with `IN` or `UNION`. The number of `IN` must be less than `300`.
- Avoid using the `%` prefix for fuzzy prefix queries.
- If the application uses **Multi Statements** to execute SQL, that is, multiple SQLs are joined with semicolons and sent to the client for execution at once, TiDB only returns the result of the first SQL execution.
- When you use expressions, check if the expressions support computing push-down to the storage layer (TiKV or TiFlash). If not, you should expect more memory consumption and even OOM at the TiDB layer. Computing that can be pushed down to the storage layer is as follows:
    - [TiFlash supported push-down calculations](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-supported-pushdown-calculations).
    - [TiKV - List of Expressions for Pushdown](https://docs.pingcap.com/tidb/stable/functions-and-operators/expressions-pushed-down).
    - [Predicate push down](https://docs.pingcap.com/tidb/stable/predicate-push-down).
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
