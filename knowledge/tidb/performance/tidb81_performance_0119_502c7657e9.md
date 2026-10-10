# SQL and database optimization FAQs

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/sql-faq.md`
- Source Title: `SQL FAQs`
- Source Heading Path: `SQL FAQs > SQL optimization > Does TiDB support CBO (Cost-Based Optimization)? If yes, to what extent? | SQL FAQs > SQL optimization > How to determine whether I need to execute `analyze` on a table? | SQL FAQs > SQL optimization > What is the ID rule when a query plan is presented as a tree? What is the execution order for this tree? | SQL FAQs > SQL optimization > In the TiDB query plan, `cop` tasks are in the same root. Are they executed concurrently? | SQL FAQs > Database optimization | SQL FAQs > Database optimization > Edit TiDB options | SQL FAQs > Database optimization > How to avoid hotspot issues and achieve load balancing? Is hot partition or range an issue in TiDB? | SQL FAQs > Database optimization > Tune TiKV performance`
- Source Line Ranges: `453-493`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `tikv`, `sql`, `shared`
- Topic Tags: `cbo`, `cost-based-optimizer`, `statistics`, `analyze`, `query-plan`, `execution-order`, `cop-task`, `root-task`, `database-optimization`, `command-options`, `hotspot`, `load-balancing`, `shard-row-id-bits`, `auto-random`, `coprocessor-cache`, `load-base-split`, `cached-tables`, `tikv-tuning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0119_502c7657e9`
- Source ID: `tidb-docs-8.1:faq/sql-faq.md#does-tidb-support-cbo-cost-based-optimization-if-yes-to-what-extent`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `65d888981335d6da4c0a9df22968da05ac8445ec02f2bdacaf3e1a1bb58184ec`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/sql-faq#does-tidb-support-cbo-cost-based-optimization-if-yes-to-what-extent
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/sql-faq.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks about TiDB SQL optimization basics such as CBO support, when to run ANALYZE based on SHOW STATS_HEALTHY, query plan ID meaning and execution order, cop task versus root task concurrency, hotspot mitigation features, TiDB command options, or TiKV performance tuning references.
- Retrieval Keywords: Cost-Based Optimization, CBO, statistics, ANALYZE, SHOW STATS_HEALTHY, Healthy, smaller than 60, query plan, ID rule, execution order, root node, cop task, root task, concurrently, TiDB Command Options, hotspot, load balancing, SHARD_ROW_ID_BITS, AUTO_RANDOM, Coprocessor Cache, Load Base Split, Cached tables, Troubleshoot Hotspot Issues, Tune TiKV Thread Performance, Tune TiKV Memory Performance
- Follow-up Guidance: The source points to Understanding the TiDB Query Execution Plan, The TiDB Command Options, Troubleshoot Hotspot Issues, Tune TiKV Thread Performance, and Tune TiKV Memory Performance for more details.
- Classification Note: This chunk is classified as performance for TiDB because the official content covers optimizer behavior, statistics health, query plan execution, concurrent cop and root tasks, hotspot handling, and TiKV tuning guidance.

## Official Source Content

### Does TiDB support CBO (Cost-Based Optimization)? If yes, to what extent?

Yes. TiDB uses the cost-based optimizer. The cost model and statistics are constantly optimized. TiDB also supports join algorithms like hash join and sort-merge join.
### How to determine whether I need to execute `analyze` on a table?

View the `Healthy` field using `SHOW STATS_HEALTHY` and generally you need to execute `ANALYZE` on a table when the field value is smaller than 60.
### What is the ID rule when a query plan is presented as a tree? What is the execution order for this tree?

No rule exists for these IDs but the IDs are unique. When IDs are generated, a counter works and adds one when one plan is generated. The execution order has nothing to do with the ID. The whole query plan is a tree and the execution process starts from the root node and the data is returned to the upper level continuously. For details about the query plan, see [Understanding the TiDB Query Execution Plan](https://docs.pingcap.com/tidb/stable/explain-overview).
### In the TiDB query plan, `cop` tasks are in the same root. Are they executed concurrently?

Currently the computing tasks of TiDB belong to two different types of tasks: `cop task` and `root task`.

`cop task` is the computing task which is pushed down to the KV end for distributed execution; `root task` is the computing task for single point execution on the TiDB end.

Generally the input data of `root task` comes from `cop task`; when `root task` processes data, `cop task` of TiKV can processes data at the same time and waits for the pull of `root task` of TiDB. Therefore, `cop` tasks can be considered as executed concurrently with `root task`; but their data has an upstream and downstream relationship. During the execution process, they are executed concurrently during some time. For example, the first `cop task` is processing the data in [100, 200] and the second `cop task` is processing the data in [1, 100]. For details, see [Understanding the TiDB Query Plan](https://docs.pingcap.com/tidb/stable/explain-overview).
## Database optimization
### Edit TiDB options

See [The TiDB Command Options](https://docs.pingcap.com/tidb/stable/command-line-flags-for-tidb-configuration).
### How to avoid hotspot issues and achieve load balancing? Is hot partition or range an issue in TiDB?

To learn the scenarios that cause hotspots, refer to [common hotpots](https://docs.pingcap.com/tidb/stable/troubleshoot-hot-spot-issues#common-hotspots). The following TiDB features are designed to help you solve hotspot issues:

- The [`SHARD_ROW_ID_BITS`](https://docs.pingcap.com/tidb/stable/troubleshoot-hot-spot-issues#use-shard_row_id_bits-to-process-hotspots) attribute. After setting this attribute, row IDs are scattered and written into multiple Regions, which can alleviate the write hotspot issue.
- The [`AUTO_RANDOM`](https://docs.pingcap.com/tidb/stable/troubleshoot-hot-spot-issues#handle-auto-increment-primary-key-hotspot-tables-using-auto_random) attribute, which helps resolve hotspots brought by auto-increment primary keys.
- [Coprocessor Cache](https://docs.pingcap.com/tidb/stable/coprocessor-cache), for read hotspots on small tables.
- [Load Base Split](https://docs.pingcap.com/tidb/stable/configure-load-base-split), for hotspots caused by unbalanced access between Regions, such as full table scans for small tables.
- [Cached tables](https://docs.pingcap.com/tidb/stable/cached-tables), for frequently accessed but rarely updated small hotspot tables.

If you have a performance issue caused by hotspot, refer to [Troubleshoot Hotspot Issues](https://docs.pingcap.com/tidb/stable/troubleshoot-hot-spot-issues) to get it resolved.
### Tune TiKV performance

See [Tune TiKV Thread Performance](https://docs.pingcap.com/tidb/stable/tune-tikv-thread-performance) and [Tune TiKV Memory Performance](https://docs.pingcap.com/tidb/stable/tune-tikv-memory-performance).
