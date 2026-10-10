# Handle downstream DDL execution errors in Drainer

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/tidb-binlog-faq.md`
- Source Title: `TiDB Binlog FAQs`
- Source Heading Path: `TiDB Binlog FAQs > What can I do when some DDL statements supported by the upstream database cause error when executed in the downstream database?`
- Source Line Ranges: `238-251`
- Source Scope: `shared`
- Primary Component: `tidb`
- Related Components: none
- Topic Tags: `drainer`, `ddl`, `downstream`, `drainer-log`, `commit-ts`, `ignore-txn-commit-ts`, `restart`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0081_f21381d4cc`
- Source ID: `tidb-docs-8.1:tidb-binlog/tidb-binlog-faq.md#what-can-i-do-when-some-ddl-statements-supported-by-the-upstream-database-cause-error-when-executed-in-the-downstream-database`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1e969b660c58da6577598dad7fe11bc5aa28f4a891fb3d419d8f2c306fd962cb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-faq#what-can-i-do-when-some-ddl-statements-supported-by-the-upstream-database-cause-error-when-executed-in-the-downstream-database
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/tidb-binlog-faq.md

## Retrieval Guidance

- Use When: Use this chunk when Drainer exits because a DDL supported upstream fails in the downstream database and you need the documented log-based recovery steps.
- Retrieval Keywords: drainer.log, exec failed, failed DDL operation, downstream database, commit-ts, ignore-txn-commit-ts, drainer.toml, restart the Drainer node, add ddl item to syncer
- Follow-up Guidance: The source says to find the failed DDL and its `commit-ts` in `drainer.log`, manually make the DDL compatible in the downstream database, add that `commit-ts` to `ignore-txn-commit-ts` in `drainer.toml`, and restart Drainer.
- Classification Note: This is classified as diagnosis because the content focuses on identifying a failed downstream DDL in `drainer.log` and using the logged `commit-ts` to handle the error.

## Official Source Content

## What can I do when some DDL statements supported by the upstream database cause error when executed in the downstream database?

To solve the problem, follow these steps:

1. Check `drainer.log`. Search `exec failed` for the last failed DDL operation before the Drainer process is exited.
2. Change the DDL version to the one compatible to the downstream. Perform this step manually in the downstream database.
3. Check `drainer.log`. Search for the failed DDL operation and find the `commit-ts` of this operation. For example:

    ```
    [2020/05/21 09:51:58.019 +08:00] [INFO] [syncer.go:398] ["add ddl item to syncer, you can add this commit ts to `ignore-txn-commit-ts` to skip this ddl if needed"] [sql="ALTER TABLE `test` ADD INDEX (`index1`)"] ["commit ts"=416815754209656834].
    ```

4. Modify the `drainer.toml` configuration file. Add the `commit-ts` in the `ignore-txn-commit-ts` item and restart the Drainer node.
