# Unstable result set causes and support

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-unstable-result-set.md`
- Source Title: `Unstable Result Set`
- Source Heading Path: `Unstable Result Set > The result set is unstable because order by is not used in `GROUP_CONCAT()` | Unstable Result Set > Unstable results in `SELECT * FROM T LIMIT N` | Unstable Result Set > Need help?`
- Source Line Ranges: `172-250`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`, `shared`
- Topic Tags: `unstable-result-set`, `group-concat`, `order-by`, `limit`, `parallel-read`, `region-distribution`, `query-results`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0025_671f31f34b`
- Source ID: `tidb-docs-8.1:develop/dev-guide-unstable-result-set.md#the-result-set-is-unstable-because-order-by-is-not-used-in-group-concat`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e2f9772f00ff28fdd675fbf9b366c90923161c0e4b485c9ee21fa90bb2f5d46f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-unstable-result-set#the-result-set-is-unstable-because-order-by-is-not-used-in-group-concat
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-unstable-result-set.md

## Retrieval Guidance

- Use When: Use this chunk when investigating unstable query results involving `GROUP_CONCAT()` without `ORDER BY` or `SELECT * FROM T LIMIT N` returning different rows across repeated queries.
- Retrieval Keywords: unstable result set, GROUP_CONCAT(), GROUP_CONCAT without ORDER BY, GROUP_CONCAT customer_id SEPARATOR ',', order by customer_id, SELECT * FROM T LIMIT N, parallel read, TiDB reads data from the storage layer in parallel, TiKV, Region distribution, different storage units return results at different speeds, query results unstable
- Follow-up Guidance: If more help is needed, the source points to Discord, Slack, and submitting a support ticket.
- Classification Note: This chunk is classified as diagnosis because it explains why result sets can appear unstable in TiDB and identifies the related SQL patterns and storage-layer behavior.

## Official Source Content

## The result set is unstable because order by is not used in `GROUP_CONCAT()`

The result set is unstable because TiDB reads data from the storage layer in parallel, so the result set order returned by `GROUP_CONCAT()` without `ORDER BY` is easily perceived as unstable.

To let `GROUP_CONCAT()` get the result set output in order, you need to add the sorting fields to the `ORDER BY` clause, which conforms to the SQL semantics. In the following example, `GROUP_CONCAT()` that splices `customer_id` without `ORDER BY` causes an unstable result set.

1. Excluded `ORDER BY`

    First query:

    ```sql
    mysql>  select GROUP_CONCAT( customer_id SEPARATOR ',' ) FROM customer where customer_id like '200002%';
    +-------------------------------------------------------------------------+
    | GROUP_CONCAT(customer_id  SEPARATOR ',')                                |
    +-------------------------------------------------------------------------+
    | 20000200992,20000200993,20000200994,20000200995,20000200996,20000200... |
    +-------------------------------------------------------------------------+
    ```

    Second query:

    ```sql
    mysql>  select GROUP_CONCAT( customer_id SEPARATOR ',' ) FROM customer where customer_id like '200002%';
    +-------------------------------------------------------------------------+
    | GROUP_CONCAT(customer_id  SEPARATOR ',')                                |
    +-------------------------------------------------------------------------+
    | 20000203040,20000203041,20000203042,20000203043,20000203044,20000203... |
    +-------------------------------------------------------------------------+
    ```

2. Include `ORDER BY`

    First query:

    ```sql
    mysql>  select GROUP_CONCAT( customer_id order by customer_id SEPARATOR ',' ) FROM customer where customer_id like '200002%';
    +-------------------------------------------------------------------------+
    | GROUP_CONCAT(customer_id  SEPARATOR ',')                                |
    +-------------------------------------------------------------------------+
    | 20000200000,20000200001,20000200002,20000200003,20000200004,20000200... |
    +-------------------------------------------------------------------------+
    ```

    Second query:

    ```sql
    mysql>  select GROUP_CONCAT( customer_id order by customer_id SEPARATOR ',' ) FROM customer where customer_id like '200002%';
    +-------------------------------------------------------------------------+
    | GROUP_CONCAT(customer_id  SEPARATOR ',')                                |
    +-------------------------------------------------------------------------+
    | 20000200000,20000200001,20000200002,20000200003,20000200004,20000200... |
    +-------------------------------------------------------------------------+
    ```
## Unstable results in `SELECT * FROM T LIMIT N`

The returned result is related to the distribution of data on the storage node (TiKV). If multiple queries are performed, different storage units (Regions) of the storage nodes (TiKV) return results at different speeds, which can cause unstable results.
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
