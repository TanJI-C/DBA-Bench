# Global hints for views with QB_NAME and target hints

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/optimizer-hints.md`
- Source Title: `Optimizer Hints`
- Source Heading Path: `Optimizer Hints > Hints that take effect globally > Step 1: Define the query block name of the view using the `QB_NAME` hint | Optimizer Hints > Hints that take effect globally > Step 2: Add the target hints`
- Source Line Ranges: `627-721`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `optimizer-hints`, `global-hints`, `qb_name`, `views`, `query-blocks`, `join-hints`, `aggregation-hints`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0458_cd57ff1c39`
- Source ID: `tidb-docs-8.1:optimizer-hints.md#step-1-define-the-query-block-name-of-the-view-using-the-qb-name-hint`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2af588eaee785b0283c6fb9ba2606722f127ca037b7c4ca41517ef442fe336ec`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/optimizer-hints#step-1-define-the-query-block-name-of-the-view-using-the-qb-name-hint
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/optimizer-hints.md

## Retrieval Guidance

- Use When: Use this chunk when you need the syntax and examples for making optimizer hints take effect inside views by defining `QB_NAME` for view query blocks and then applying target hints with `ViewName@QueryBlockName`.
- Retrieval Keywords: QB_NAME, QB_NAME(QB, ViewName@QueryBlockName [.ViewName@QueryBlockName .ViewName@QueryBlockName ...]), global hints for views, ViewName@QueryBlockName, merge_join(t@v2_1), stream_agg(@v2_2), hash_join(t@v1_1), hash_agg(@v1_2), USE_INDEX(t@v_1, idx), v2@SEL_1 .@SEL_1, v2.v1@SEL_2 .@SEL_2
- Follow-up Guidance: The source also notes parsing and omission rules for `@SEL_` in `QB_NAME`, and states that global hints for views do not take effect unless the corresponding `QB_NAME` hints are defined in the view.
- Classification Note: This is reference content because it defines exact `QB_NAME` syntax, naming rules for view query blocks, and concrete target hint forms such as `MERGE_JOIN()`, `STREAM_AGG()`, `HASH_JOIN()`, and `HASH_AGG()`.

## Official Source Content

### Step 1: Define the query block name of the view using the `QB_NAME` hint

Use the [`QB_NAME` hint](#qb_name) to define a new name for each query block of the view. The definition of the `QB_NAME` hint for views is the same as that for [query blocks](#qb_name), but the syntax is extended from `QB_NAME(QB)` to `QB_NAME(QB, ViewName@QueryBlockName [.ViewName@QueryBlockName .ViewName@QueryBlockName ...])`.

> **Note:**
>
> There is a white space between `@QueryBlockName` and the immediately following `.ViewName@QueryBlockName`. Otherwise, the `.ViewName@QueryBlockName` will be treated as a part of the `QueryBlockName`. For example, `QB_NAME(v2_1, v2@SEL_1 .@SEL_1)` is valid, while `QB_NAME(v2_1, v2@SEL_1.@SEL_1)` cannot be parsed correctly.

- For a simple statement with a single view and no subqueries, the following example specifies the first query block name of view `v`:

    ```sql
    SELECT /* Comment: The name of the current query block is the default @SEL_1 */ * FROM v;
    ```

    For view `v`, the first view name in the list (`ViewName@QueryBlockName [.ViewName@QueryBlockName .ViewName@QueryBlockName ...]`) starting from the query statement is `v@SEL_1`. The first query block of the view `v` can be declared as `QB_NAME(v_1, v@SEL_1 .@SEL_1)`, or simply written as `QB_NAME(v_1, v)`, omitting `@SEL_1`:

    ```sql
    CREATE VIEW v AS SELECT /* Comment: The name of the current query block is the default @SEL_1 */ * FROM t;

    -- Specifies the global hint
    SELECT /*+ QB_NAME(v_1, v) USE_INDEX(t@v_1, idx) */ * FROM v;
    ```

- For a complex statement with nested views and subqueries, the following example specifies the names for each of two query blocks of the view `v1` and `v2`:

    ```sql
    SELECT /* Comment: The name of the current query block is the default @SEL_1 */ * FROM v2 JOIN (
        SELECT /* Comment: The name of the current query block is the default @SEL_2 */ * FROM v2) vv;
    ```

    For the first view `v2`, the first view name in the list starting from the first query statement is `v2@SEL_1`. For the second view `v2`, the first view name is `v2@SEL_2`. The following example only considers the first view `v2`.

    The first query block of view `v2` can be declared as `QB_NAME(v2_1, v2@SEL_1 .@SEL_1)`, and the second query block of the view `v2` can be declared as `QB_NAME(v2_2, v2@SEL_1 .@SEL_2)`:

    ```sql
    CREATE VIEW v2 AS
        SELECT * FROM t JOIN /* Comment: For view v2, the name of the current query block is the default @SEL_1. So, the current query block view list is v2@SEL_1 .@SEL_1 */
        (
            SELECT COUNT(*) FROM t1 JOIN v1 /* Comment: For view v2, the name of the current query block is the default @SEL_2. So, the current query block view list is v2@SEL_1 .@SEL_2 */
        ) tt;
    ```

    For view `v1`, the first view name in the list starting from the preceding statement is `v2@SEL_1 .v1@SEL_2`. The first query block in view `v1` can be declared as `QB_NAME(v1_1, v2@SEL_1 .v1@SEL_2 .@SEL_1)`, and the second query block in view `v1` can be declared as `QB_NAME(v1_2, v2@SEL_1 .v1@SEL_2 .@SEL_2)`:

    ```sql
    CREATE VIEW v1 AS SELECT * FROM t JOIN /* Comment: For view `v1`, the name of the current query block is the default @SEL_1. So, the current query block view list is v2@SEL_1 .@SEL_2 .v1@SEL_1 */
        (
            SELECT COUNT(*) FROM t1 JOIN t2 /* Comment: For view `v1`, the name of the current query block is the default @SEL_2. So, the current query block view list is v2@SEL_1 .@SEL_2 .v1@SEL_2 */
        ) tt;
    ```

> **Note:**
>
> - To use global hints with views, you must define the corresponding `QB_NAME` hints in the view. Otherwise, the global hints will not take effect.
>
> - When using a hint to specify multiple table names in a view, you need to ensure that the table names appearing in the same hint are in the same query block of the same view.
>
> - When you define the `QB_NAME` hint in a view for the outermost query block:
>
>     - For the first item of the view list in the `QB_NAME`, if the `@SEL_` is not explicitly declared, the default is consistent with the query block position where the `QB_NAME` is defined. That is, the query `SELECT /*+ QB_NAME(qb1, v2) */ * FROM v2 JOIN (SELECT /*+ QB_NAME(qb2, v2) */ * FROM v2) vv;` is equivalent to `SELECT /*+ QB_NAME(qb1, v2@SEL_1) */ * FROM v2 JOIN (SELECT /*+ QB_NAME(qb2, v2@SEL_2) */ * FROM v2) vv;`.
>     - For items other than the first item of the view list in the `QB_NAME`, only `@SEL_1` can be omitted. That is, if `@SEL_1` is declared in the first query block of the current view, `@SEL_1` can be omitted. Otherwise, `@SEL_` cannot be omitted. For the preceding example:
>
>         - The first query block of the view `v2` can be declared as `QB_NAME(v2_1, v2)`.
>         - The second query block of the view `v2` can be declared as `QB_NAME(v2_2, v2.@SEL_2)`.
>         - The first query block of the view `v1` can be declared as `QB_NAME(v1_1, v2.v1@SEL_2)`.
>         - The second query block of the view `v1` can be declared as `QB_NAME(v1_2, v2.v1@SEL_2 .@SEL_2)`.
### Step 2: Add the target hints

After defining the `QB_NAME` hint for query blocks of the view, you can add required [hints that take effect in query blocks](#hints-that-take-effect-in-query-blocks) in the form of `ViewName@QueryBlockName` to make them effective inside the view. For example:

- Specify the `MERGE_JOIN()` hint for the first query block of the view `v2`:

    ```sql
    SELECT /*+ QB_NAME(v2_1, v2) merge_join(t@v2_1) */ * FROM v2;
    ```

- Specify the `MERGE_JOIN()` and `STREAM_AGG()` hints for the second query block of the view `v2`:

    ```sql
    SELECT /*+ QB_NAME(v2_2, v2.@SEL_2) merge_join(t1@v2_2) stream_agg(@v2_2) */ * FROM v2;
    ```

- Specify the `HASH_JOIN()` hint for the first query block of the view `v1`:

    ```sql
    SELECT /*+ QB_NAME(v1_1, v2.v1@SEL_2) hash_join(t@v1_1) */ * FROM v2;
    ```

- Specify the `HASH_JOIN()` and `HASH_AGG()` hints for the second query block of the view `v1`:

    ```sql
    SELECT /*+ QB_NAME(v1_2, v2.v1@SEL_2 .@SEL_2) hash_join(t1@v1_2) hash_agg(@v1_2) */ * FROM v2;
    ```
