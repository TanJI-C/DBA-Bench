# Zapier FAQ: trigger deduplication and find-or-create behavior

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/integrate-tidbcloud-with-zapier.md`
- Source Title: `Integrate TiDB Cloud with Zapier`
- Source Heading Path: `Integrate TiDB Cloud with Zapier > FAQ > How do TiDB Cloud triggers perform de-duplication? | Integrate TiDB Cloud with Zapier > FAQ > How do I use the `find or create` action?`
- Source Line Ranges: `194-236`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `zapier`, `faq`, `triggers`, `deduplication`, `polling`, `new-row`, `custom-query`, `order-by`, `limit`, `timeout`, `find-or-create`, `table-creation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0808_f8aa4cbf4c`
- Source ID: `tidb-docs-8.1:tidb-cloud/integrate-tidbcloud-with-zapier.md#how-do-tidb-cloud-triggers-perform-de-duplication`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b8d0b82abfb71de9a5961df26e0391a4669e68eb93a1daf4ee11d59fac037a92`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/integrate-tidbcloud-with-zapier#how-do-tidb-cloud-triggers-perform-de-duplication
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/integrate-tidbcloud-with-zapier.md

## Retrieval Guidance

- Use When: Use this chunk when answering how TiDB Cloud Zapier triggers deduplicate polled results, what limits and requirements apply to `New Row` or `New Row (Custom Query)`, or how the `find or create` behavior works for `Find Table`.
- Retrieval Keywords: TiDB Cloud Zapier trigger deduplication, polling API call duplication, id field deduplication, New Cluster trigger cluster_id, New Table trigger table_id, New Row trigger 10000 results, Order By configuration, Dedupe Key, primary key, unique key, first column of the table, New Row (Custom Query) trigger 1000000 results, ORDER BY, LIMIT, You must return the results with id field, timeout error, less than 30 seconds, find or create action, Find Table action, Create TiDB Cloud Table if it doesn’t exist yet?
- Follow-up Guidance: The source also states that testing the `Find Table` action with `Create TiDB Cloud Table if it doesn’t exist yet?` enabled creates the table directly if it does not exist yet.
- Classification Note: This is reference content because it documents Zapier FAQ behavior, limits, identifier selection order, exact error text, and the `find or create` option for TiDB Cloud.

## Official Source Content

### How do TiDB Cloud triggers perform de-duplication?

Zapier triggers can work with a polling API call to check for new data periodically (the interval depends on your Zapier plan).

TiDB Cloud triggers provide a polling API call that returns a lot of results. However, most of the results have been seen by Zapier before, that is, most of the results are duplication.

Since we don’t want to trigger an action multiple times when an item in your API exists in multiple distinct polls, TiDB Cloud triggers deduplicate the data with the `id` field.

`New Cluster` and `New Table` triggers simply use the `cluster_id` or `table_id` as the `id` field to do the deduplication. You do not need to do anything for the two triggers.

**New Row Trigger**

The `New Row` trigger limits 10,000 results in every fetch. Therefore, if some new rows are not included in the 10,000 results, they cannot trigger Zapier.

One way to avoid this is to specify the `Order By` configuration in the trigger. For example, once you sort the rows by their creation time, the new rows will always be included in the 10,000 results.

The `New Row` trigger also uses a flexible strategy to generate the `id` field to do the deduplication. The trigger generates the `id` field in the following order:

1. If the result contains an `id` column, use the `id` column.
2. If you specify a `Dedupe Key` in the trigger configuration, use the `Dedupe Key`.
3. If the table has a primary key, use the primary key. If there are multiple primary keys, use the first column.
4. If the table has a unique key, use the unique key.
5. Use the first column of the table.

**New Row (Custom Query) Trigger**

The `New Row (Custom Query)` trigger limits 1,000,000 results in every fetch. 1,000,000 is a large number, and it is only set so as to protect the whole system. It is recommended that your query includes `ORDER BY` and `LIMIT`.

To perform deduplication, your query results must have a unique id field. Otherwise, you will get the `You must return the results with id field` error.

Make sure that your custom query executes in less than 30 seconds. Otherwise, you will get the timeout error.
### How do I use the `find or create` action?

`Find or create` action enables you to create a resource if it does not exist. Here is an example:

1. Choose `Find Table` action

2. In the`set up action` step, tick the `Create TiDB Cloud Table if it doesn’t exist yet?` box to enable `find and create`.

   ![Find and create](/media/tidb-cloud/zapier/zapier-tidbcloud-find-and-create.png)

This workflow creates a table if it does not exist yet. Note that the table will be created directly if you test your action.
