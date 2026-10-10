# Application retry logic and related references

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-transaction-troubleshoot.md`
- Source Title: `Handle Transaction Errors`
- Source Heading Path: `Handle Transaction Errors > Application retry and error handling | Handle Transaction Errors > See also | Handle Transaction Errors > Need help?`
- Source Line Ranges: `74-170`
- Source Scope: `developer`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `transactions`, `application-retry`, `error-handling`, `error-codes`, `optimistic-transactions`, `write-conflicts`, `rollback`, `commit`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0076_c67fc8979e`
- Source ID: `tidb-docs-8.1:develop/dev-guide-transaction-troubleshoot.md#application-retry-and-error-handling`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f128ab551840d7f585d5b81efc00f70aa2b94e299a696c58382ff2be101653e8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-transaction-troubleshoot#application-retry-and-error-handling
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-transaction-troubleshoot.md

## Retrieval Guidance

- Use When: Use this chunk when implementing or reviewing application-level retry handling for TiDB transaction commit failures and write conflicts in optimistic transactions.
- Retrieval Keywords: Application retry and error handling, Error 8002: can not retry select for update statement, Error 8022: Error: KV error safe to retry, Error 8028: Information schema is changed during the execution of the statement, Error 9007: Write conflict, SELECT FOR UPDATE write conflict error, transaction commit failed error, COMMIT, ROLLBACK, max_retries, try catch, exponentially increase the wait time, Error Codes and Troubleshooting, Troubleshoot Lock Conflicts, Troubleshoot Write Conflicts in Optimistic Transactions
- Follow-up Guidance: The source links to Error Codes and Troubleshooting, Troubleshoot Lock Conflicts, and Troubleshoot Write Conflicts in Optimistic Transactions for related error details and conflict troubleshooting.
- Classification Note: This is classified as operation because the content provides concrete application retry rules, handled error codes, and transaction control flow for runtime error handling.

## Official Source Content

## Application retry and error handling

Although TiDB is as compatible as possible with MySQL, the nature of its distributed system leads to certain differences. One of them is the transaction model.

The Adapters and ORMs that developers use to connect with databases are tailored for traditional databases such as MySQL and Oracle. In these databases, transactions rarely fail to commit at the default isolation level, so retry mechanisms are not required. When a transaction fails to commit, these clients abort due to an error, as it is treated as an exception in these databases.

Different from traditional databases such as MySQL, in TiDB, if you use the optimistic transaction model and want to avoid commit failure, you need to add a mechanism to handle related exceptions in your applications.

The following Python pseudocode shows how to implement application-level retries. It does not require your driver or ORM to implement advanced retry logic. It can be used in any programming language or environment.

Your retry logic must follow the following rules:

- Throws an error if the number of failed retries reaches the `max_retries` limit.
- Use `try ... catch ...` to catch SQL execution exceptions. Retry when encountering the following errors. Roll back when encountering other errors.
    - `Error 8002: can not retry select for update statement`: SELECT FOR UPDATE write conflict error
    - `Error 8022: Error: KV error safe to retry`: transaction commit failed error.
    - `Error 8028: Information schema is changed during the execution of the statement`: Table schema has been changed by DDL operation, resulting in an error in the transaction commit.
    - `Error 9007: Write conflict`: Write conflict error, usually caused by multiple transactions modifying the same row of data when the optimistic transaction mode is used.
- `COMMIT` the transaction at the end of the try block.

For more information about error codes, see [Error Codes and Troubleshooting](https://docs.pingcap.com/tidb/stable/error-codes).

For more information about error codes, see [Error Codes and Troubleshooting](https://docs.pingcap.com/tidb/stable/error-codes).

```python
while True:
    n++
    if n == max_retries:
        raise("did not succeed within #{n} retries")
    try:
        connection.execute("your sql statement here")
        connection.exec('COMMIT')
        break
    catch error:
        if (error.code != "9007" && error.code != "8028" && error.code != "8002" && error.code != "8022"):
            raise error
        else:
            connection.exec('ROLLBACK')

            # Capture the error types that require application-side retry,
            # wait for a short period of time,
            # and exponentially increase the wait time for each transaction failure
            sleep_ms = int(((1.5 ** n) + rand) * 100)
            sleep(sleep_ms) # make sure your sleep() takes milliseconds
```

> **Note:**
>
> If you frequently encounter `Error 9007: Write conflict`, you may need to check your schema design and the data access patterns of your workload to find the root cause of the conflict and try to avoid conflicts by a better design.

For information about how to troubleshoot and resolve transaction conflicts, see [Troubleshoot Lock Conflicts](https://docs.pingcap.com/tidb/stable/troubleshoot-lock-conflicts).

For information about how to troubleshoot and resolve transaction conflicts, see [Troubleshoot Lock Conflicts](https://docs.pingcap.com/tidb/stable/troubleshoot-lock-conflicts).
## See also

- [Troubleshoot Write Conflicts in Optimistic Transactions](https://docs.pingcap.com/tidb/stable/troubleshoot-write-conflicts)

- [Troubleshoot Write Conflicts in Optimistic Transactions](https://docs.pingcap.com/tidb/stable/troubleshoot-write-conflicts)
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
