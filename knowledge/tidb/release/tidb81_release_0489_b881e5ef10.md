# Reliability features: runaway query management, plan bindings, optimizer fix controls, lightweight stats init

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.2.0.md`
- Source Title: `TiDB 7.2.0 Release Notes`
- Source Heading Path: `TiDB 7.2.0 Release Notes > Feature details > Reliability`
- Source Line Ranges: `85-125`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `reliability`, `resource-control`, `runaway-queries`, `sql-plan-management`, `optimizer`, `optimizer-fix-controls`, `statistics`, `startup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0489_b881e5ef10`
- Source ID: `tidb-docs-8.1:releases/release-7.2.0.md#reliability`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `10da5f170ade5bcec8ceb5e5d22a38304d048e0d58c39fbd38a7e7a0231de5d7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.2.0#reliability
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.2.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB v7.2.0 reliability features about runaway query management, historical plan bindings, optimizer fix controls, or lightweight statistics initialization during startup.
- Retrieval Keywords: manage queries that consume more resources than expected, runaway queries, resource group, maximum execution time, deprioritized or cancelled, identified queries by text or execution plan, creating a binding according to a historical execution plan, SQL Plan Management, AGG_TO_COP(), LIMIT_TO_COP(), ORDER_INDEX, NO_ORDER_INDEX(), Optimizer Fix Controls, tidb_opt_fix_control, lightweight statistics initialization, lite-init-stats, force-init-stats, load statistics
- Follow-up Guidance: The content points to documentation for runaway query management, SQL Plan Management, Optimizer Fix Controls, and loading statistics.
- Classification Note: This is classified as a TiDB release feature for reliability because the section introduces stability-related capabilities in resource control, plan management, optimizer behavior control, and statistics startup loading.

## Official Source Content

### Reliability

* Automatically manage queries that consume more resources than expected (experimental) [#43691](https://github.com/pingcap/tidb/issues/43691) @[Connor1996](https://github.com/Connor1996) @[CabinfeverB](https://github.com/CabinfeverB) @[glorv](https://github.com/glorv) @[HuSharp](https://github.com/HuSharp) @[nolouch](https://github.com/nolouch)

    The most common challenge to database stability is the degradation of overall database performance caused by abrupt SQL performance problems. There are many causes for SQL performance issues, such as new SQL statements that have not been fully tested, drastic changes in data volume, and abrupt changes in execution plans. These issues are difficult to completely avoid at the root. TiDB v7.2.0 provides the ability to manage queries that consume more resources than expected. This feature can quickly reduce the scope of impact when a performance issue occurs.

    To manage these queries, you can set the maximum execution time of queries for a resource group. When the execution time of a query exceeds this limit, the query is automatically deprioritized or cancelled. You can also set a period of time to immediately match identified queries by text or execution plan. This helps prevent high concurrency of the problematic queries during the identification phase that could consume more resources than expected.

    Automatic management of queries that consume more resources than expected provides you with an effective means to quickly respond to unexpected query performance problems. This feature can reduce the impact of the problem on overall database performance, thereby improving database stability.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tidb-resource-control#manage-queries-that-consume-more-resources-than-expected-runaway-queries).

* Enhance the capability of creating a binding according to a historical execution plan [#39199](https://github.com/pingcap/tidb/issues/39199) @[qw4990](https://github.com/qw4990)

    TiDB v7.2.0 enhances the capability of [creating a binding according to a historical execution plan](https://docs.pingcap.com/tidb/stable/sql-plan-management#create-a-binding-according-to-a-historical-execution-plan). This feature improves the parsing and binding process for complex statements, making the bindings more stable, and supports the following new hints:

    - [`AGG_TO_COP()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#agg_to_cop)
    - [`LIMIT_TO_COP()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#limit_to_cop)
    - [`ORDER_INDEX`](https://docs.pingcap.com/tidb/stable/optimizer-hints#order_indext1_name-idx1_name--idx2_name-)
    - [`NO_ORDER_INDEX()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#no_order_indext1_name-idx1_name--idx2_name-)

  For more information, see [documentation](https://docs.pingcap.com/tidb/stable/sql-plan-management).

* Introduce the Optimizer Fix Controls mechanism to provide fine-grained control over optimizer behaviors [#43169](https://github.com/pingcap/tidb/issues/43169) @[time-and-fate](https://github.com/time-and-fate)

    To generate more reasonable execution plans, the behavior of the TiDB optimizer evolves over product iterations. However, in some particular scenarios, the changes might lead to performance regression. TiDB v7.2.0 introduces Optimizer Fix Controls to let you control some of the fine-grained behaviors of the optimizer. This enables you to roll back or control some new changes.

    Each controllable behavior is described by a GitHub issue corresponding to the fix number. All controllable behaviors are listed in [Optimizer Fix Controls](https://docs.pingcap.com/tidb/stable/optimizer-fix-controls). You can set a target value for one or more behaviors by setting the [`tidb_opt_fix_control`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_fix_control-new-in-v653-and-v710) system variable to achieve behavior control.

    The Optimizer Fix Controls mechanism helps you control the TiDB optimizer at a granular level. It provides a new means of fixing performance issues caused by the upgrade process and improves the stability of TiDB.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/optimizer-fix-controls).

* Lightweight statistics initialization becomes generally available (GA) [#42160](https://github.com/pingcap/tidb/issues/42160) @[xuyifangreeneyes](https://github.com/xuyifangreeneyes)

    Starting from v7.2.0, the lightweight statistics initialization feature becomes GA. Lightweight statistics initialization can significantly reduce the number of statistics that must be loaded during startup, thus improving the speed of loading statistics. This feature increases the stability of TiDB in complex runtime environments and reduces the impact on the overall service when TiDB nodes restart.

    For newly created clusters of v7.2.0 or later versions, TiDB loads lightweight statistics by default during TiDB startup and will wait for the loading to finish before providing services. For clusters upgraded from earlier versions, you can set the TiDB configuration items [`lite-init-stats`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#lite-init-stats-new-in-v710) and [`force-init-stats`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#force-init-stats-new-in-v657-and-v710) to `true` to enable this feature.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/statistics#load-statistics).
