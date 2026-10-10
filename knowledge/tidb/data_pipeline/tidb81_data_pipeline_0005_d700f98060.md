# Insert design considerations, AUTO_RANDOM inserts, HTAP, and support

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-insert-data.md`
- Source Title: `Insert Data`
- Source Heading Path: `Insert Data > Avoid hotspots | Insert Data > Insert data to a table with the `AUTO_RANDOM` primary key | Insert Data > Use HTAP | Insert Data > Need help?`
- Source Line Ranges: `255-318`
- Source Scope: `developer`
- Primary Component: `tidb`
- Related Components: `sql`, `tiflash`, `shared`
- Topic Tags: `insert`, `hotspots`, `primary-key`, `auto-random`, `explicit-insert`, `htap`, `replica-synchronization`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0005_d700f98060`
- Source ID: `tidb-docs-8.1:develop/dev-guide-insert-data.md#avoid-hotspots`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f93c3f48c6a95fde023b2d469523ac35699215a40f506db5c5e22847035d3466`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data#avoid-hotspots
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-insert-data.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about insert design considerations in TiDB, including avoiding hotspots, inserting into an AUTO_RANDOM primary key table, or whether HTAP requires extra insertion logic.
- Retrieval Keywords: Avoid hotspots, Select primary key, Rules when selecting primary key, Troubleshoot Hotspot Issues, AUTO_RANDOM, Explicit insertion on auto_random column is disabled, ERROR 8216 (HY000), @@allow_auto_random_explicit_insert, SET @@allow_auto_random_explicit_insert = true, INSERT INTO `bookshop`.`users`, Use HTAP, column-oriented replica synchronization, TiDB automatically guarantees data consistency, Need help, Discord, Slack, support ticket
- Follow-up Guidance: The content points to Select primary key, Rules when selecting primary key, Troubleshoot Hotspot Issues, use HTAP capabilities after creating the table, and community or support channels for help.
- Classification Note: This is classified as data_pipeline for the developer scope because it covers insert-path design, explicit INSERT behavior for AUTO_RANDOM primary keys, and HTAP-related insert considerations in TiDB.

## Official Source Content

## Avoid hotspots

When designing a table, you need to consider if there is a large number of insert operations. If so, you need to avoid hotspots during table design. See the [Select primary key](https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-table#select-primary-key) section and follow the [Rules when selecting primary key](https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-table#guidelines-to-follow-when-selecting-primary-key).

For more information on how to handle hotspot issues, see [Troubleshoot Hotspot Issues](https://docs.pingcap.com/tidb/stable/troubleshoot-hot-spot-issues).
## Insert data to a table with the `AUTO_RANDOM` primary key

If the primary key of the table you insert has the `AUTO_RANDOM` attribute, then by default the primary key cannot be specified. For example, in the [`bookshop`](https://docs.pingcap.com/tidb/stable/develop/dev-guide-bookshop-schema-design) database, you can see that the `id` field of the [`users` table](https://docs.pingcap.com/tidb/stable/develop/dev-guide-bookshop-schema-design#users-table) contains the `AUTO_RANDOM` attribute.

In this case, you **cannot** use SQL like the following to insert:

```sql
INSERT INTO `bookshop`.`users` (`id`, `balance`, `nickname`) VALUES (1, 0.00, 'nicky');
```

An error will occur:

```
ERROR 8216 (HY000): Invalid auto random: Explicit insertion on auto_random column is disabled. Try to set @@allow_auto_random_explicit_insert = true.
```

It is not recommended to manually specify the `AUTO_RANDOM` column during insertion time.

There are two solutions to handle this error:

- (Recommended) Remove this column from the insert statement and use the `AUTO_RANDOM` value that TiDB initialized for you. This fits the semantics of `AUTO_RANDOM`.

    ```sql
    INSERT INTO `bookshop`.`users` (`balance`, `nickname`) VALUES (0.00, 'nicky');
    ```

- If you are sure that you **_must_** specify this column, then you can use the [`SET` statement](https://docs.pingcap.com/tidb/stable/sql-statement-set-variable) to allow the column of `AUTO_RANDOM` to be specified during insertion time by changing the user variable.

    ```sql
    SET @@allow_auto_random_explicit_insert = true;
    INSERT INTO `bookshop`.`users` (`id`, `balance`, `nickname`) VALUES (1, 0.00, 'nicky');
    ```
## Use HTAP

In TiDB, HTAP capabilities save you from performing additional operations when inserting data. There is no additional insertion logic. TiDB automatically guarantees data consistency. All you need to do is [turn on column-oriented replica synchronization](https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-table#use-htap-capabilities) after creating the table, and use the column-oriented replica to speed up your queries directly.
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
