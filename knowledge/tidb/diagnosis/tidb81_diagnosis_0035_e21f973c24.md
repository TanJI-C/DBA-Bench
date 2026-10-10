# Error codes for IMPORT INTO, DDL, resource control, and storage component failures

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/error-codes.md`
- Source Title: `Error Codes and Troubleshooting`
- Source Heading Path: `Error Codes and Troubleshooting > Error codes`
- Source Line Ranges: `366-621`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`, `tiflash`, `sql`, `ticdc`
- Topic Tags: `error-codes`, `troubleshooting`, `import-into`, `ddl`, `resource-control`, `runaway-queries`, `pd-timeout`, `tikv-timeout`, `tiflash-timeout`, `write-conflict`, `gc-life-time`, `transaction-size`, `region-unavailable`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0035_e21f973c24`
- Source ID: `tidb-docs-8.1:error-codes.md#error-codes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `da464a8c0510e7455ba544a6c617c201f44c0027345a874a211ef59f0c361138`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/error-codes#error-codes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/error-codes.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing TiDB error numbers for IMPORT INTO, DDL, resource control, runaway queries, or PD/TiKV/TiFlash timeout and availability failures.
- Retrieval Keywords: Error Number 8157, Error Number 8158, Error Number 8159, Error Number 8160, Error Number 8162, Error Number 8163, Error Number 8164, Error Number 8165, Error Number 8166, Error Number 8170, Error Number 8171, Error Number 8173, Error Number 8200, Error Number 8214, Error Number 8215, Error Number 8216, Error Number 8223, Error Number 8224, Error Number 8225, Error Number 8226, Error Number 8227, Error Number 8228, Error Number 8229, Error Number 8230, Error Number 8248, Error Number 8249, ERROR 8250 (HY000) : Resource control feature is disabled, tidb_enable_resource_control, Error Number 8251, ERROR 8252 (HY000) : Exceeded resource group quota limitation, Error Number 8253, Error Number 8254, Error Number 8260, Error Number 8261, Error Number 8262, Error Number 8263, ERROR 9001 (HY000): PD server timeout, ERROR 9002 (HY000): TiKV server timeout, ERROR 9003 (HY000): TiKV Server is Busy, ERROR 9004 (HY000): Resolve Lock Timeout, ERROR 9005 (HY000): Region is unavailable, ERROR 9006 (HY000): GC life time is shorter than transaction duration, SET GLOBAL tidb_gc_life_time = '30m', Error Number 9500, ERROR 9007 (HY000): Write conflict, reason=LazyUniquenessCheck, tidb_constraint_check_in_place_pessimistic, Error Number 9008, tidb_store_limit, Error Number 9010, Error Number 9012, Error Number 9013, IMPORT INTO, ADMIN PAUSE, ADMIN RESUME, admin cancel, ADMIN REPAIR TABLE, AUTO_RANDOM, SETVAL, Sequence, resource group quota limitation, Runaway Queries
- Follow-up Guidance: The content points to related references such as IMPORT INTO, Sequence, AUTO_RANDOM, Runaway Queries, bidirectional replication, and support, and for some errors it includes exact checks or SQL like checking PD/TiKV/TiFlash status, monitoring data and logs, or running SET GLOBAL tidb_gc_life_time = '30m'.
- Classification Note: This chunk is classified as diagnosis because it maps specific error numbers and exact error texts to their meanings and the documented troubleshooting context across shared components.

## Official Source Content

The provided path cannot be empty. You need to set a correct path before the import.

* Error Number: 8157

    The provided file format is unsupported. For the supported formats, see [`IMPORT INTO`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into#format).

* Error Number: 8158

    The provided path is invalid. Refer to the specific error message for actions. For Amazon S3 or GCS path settings, see [URI Formats of External Storage Services](https://docs.pingcap.com/tidb/stable/external-storage-uri).

* Error Number: 8159

    TiDB cannot access the provided Amazon S3 or GCS path. Make sure that the specified S3 or GCS bucket exists and that you have provided the correct Access Key and Secret Access Key for TiDB to access the corresponding bucket.

* Error Number: 8160

    Failed to read the data files. Refer to the specific error message for actions.

* Error Number: 8162

    There is an error in the statement. Refer to the specific error message for actions.

* Error Number: 8163

    The provided option is unknown. For supported options, see [`IMPORT INTO`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into#parameter-description).

* Error Number: 8164

    The provided option value is invalid. For valid values, see [`IMPORT INTO`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into#parameter-description).

* Error Number: 8165

    Duplicate options are specified. Each option can only be specified once.

* Error Number: 8166

    Certain options can only be used in specific conditions. Refer to the specific error message for actions. For supported options, see [`IMPORT INTO`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into#parameter-description).

* Error Number: 8170

    The specified job does not exist.

* Error Number: 8171

    The current operation cannot be performed for the current job status. Refer to the specific error message for actions.

* Error Number: 8173

    When executing `IMPORT INTO`, TiDB checks the current environment, such as checking if the downstream table is empty. Refer to the specific error message for actions.

* Error Number: 8200

    The DDL syntax is not yet supported.

    See [compatibility of MySQL DDL](https://docs.pingcap.com/tidb/stable/mysql-compatibility#ddl-operations) for reference.

* Error Number: 8214

    The DDL operation is terminated by the `admin cancel` operation.

* Error Number: 8215

    [`ADMIN REPAIR TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin#admin-repair-statement) fails.

    If you encounter this error, [get support](https://docs.pingcap.com/tidb/stable/support) from PingCAP or the community.

* Error Number: 8216

    The usage of the `AUTO_RANDOM` columns is incorrect.

    See [`AUTO_RANDOM`](https://docs.pingcap.com/tidb/stable/auto-random) to modify.

* Error Number: 8223

    This error occurs when detecting that the data is not consistent with the index.

    If you encounter this error, [get support](https://docs.pingcap.com/tidb/stable/support) from PingCAP or the community.

* Error Number: 8224

    The DDL job cannot be found.

    Check whether the job id specified by the `restore` operation exists.

* Error Number: 8225

    The DDL operation is completed and cannot be canceled.

* Error Number: 8226

    The DDL operation is almost completed and cannot be canceled.

* Error Number: 8227

    Unsupported options are used when creating Sequence.

    See [Sequence documentation](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-sequence#parameters) to find the list of the supported options.

* Error Number: 8228

    Unsupported types are specified when using `SETVAL` on Sequence.

    See [Sequence documentation](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-sequence#examples) to find the example of the function.

* Error Number: 8229

    The transaction exceeds the survival time.

    Commit or roll back the current transaction, and start a new transaction.

* Error Number: 8230

    TiDB currently does not support using Sequence as the default value on newly added columns, and reports this error if you use it.

* Error Number: 8248

    The resource group already exists. This error is returned when a resource group is repeatedly created.

* Error Number: 8249

    The resource group does not exist. This error is returned when you modify or bind a resource group that does not exist. See [Create a resource group](https://docs.pingcap.com/tidb/stable/tidb-resource-control#create-a-resource-group).

* Error Number: 8250

    The complete error message is as follows:

    `ERROR 8250 (HY000) : Resource control feature is disabled. Run "SET GLOBAL tidb_enable_resource_control='on'" to enable the feature`

    This error is returned when you try to use the resource control feature but it is not enabled. You can turn on the global variable [`tidb_enable_resource_control`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_resource_control-new-in-v660) to enable resource control.

* Error Number: 8251

    The `Resource Control` component is initialized upon TiDB startup. The associated configuration is fetched from the `Resource Manager` on the server side of `Resource Control`. This error is returned if there is an error during this process.

* Error Number: 8252

    The complete error message is as follows:

    `ERROR 8252 (HY000) : Exceeded resource group quota limitation`

    This error is returned when the attempted consumption exceeds the resource group limit. This error is usually caused by a single transaction that is too large or too many concurrent transactions. You need to adjust the transaction size or reduce the number of concurrent clients.

* Error Number: 8253

    The query stops because it meets the condition of a runaway query. See [Runaway Queries](https://docs.pingcap.com/tidb/stable/tidb-resource-control#manage-queries-that-consume-more-resources-than-expected-runaway-queries).

* Error Number: 8254

    The query stops because it meets the quarantined watch condition of a runaway query. See [Runaway Queries](https://docs.pingcap.com/tidb/stable/tidb-resource-control#manage-queries-that-consume-more-resources-than-expected-runaway-queries).

* Error Number: 8260

    DDL operations cannot be paused by `ADMIN PAUSE`.

* Error Number: 8261

    DDL operations cannot be resumed by `ADMIN RESUME`.

* Error Number: 8262

    DDL is paused by `ADMIN PAUSE` and cannot be paused again.

* Error Number: 8263

    This DDL cannot be executed under a specific BDR role. Make sure that the cluster is in [bidirectional replication](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-bidirectional-replication). If the cluster is not in bidirectional replication, you can use `ADMIN UNSET BDR ROLE;` to make DDL normal.

* Error Number: 9001

    The complete error message: `ERROR 9001 (HY000): PD server timeout`

    The PD request timed out.

    Check the status, monitoring data and log of the PD server, and the network between the TiDB server and the PD server.

* Error Number: 9002

    The complete error message: `ERROR 9002 (HY000): TiKV server timeout`

    The TiKV request timed out.

    Check the status, monitoring data and log of the TiKV server, and the network between the TiDB server and the TiKV server.

* Error Number: 9003

    The complete error message: `ERROR 9003 (HY000): TiKV Server is Busy`

    The TiKV server is busy and this usually occurs when the workload is too high.

    Check the status, monitoring data, and log of the TiKV server.

* Error Number: 9004

    The complete error message: `ERROR 9004 (HY000): Resolve Lock Timeout`

    A lock resolving timeout. This error occurs when a large number of transactional conflicts exist in the database.

    Check the application code to see whether lock contention exists in the database.

* Error Number: 9005
    The complete error message: `ERROR 9005 (HY000): Region is unavailable`

    The accessed Region or a certain Raft Group is not available, with possible reasons such as insufficient replicas. This error usually occurs when the TiKV server is busy or the TiKV node is down.

    Check the status, monitoring data and log of the TiKV server.

* Error Number: 9006

    The complete error message: `ERROR 9006 (HY000): GC life time is shorter than transaction duration`

    The interval of `GC Life Time` is too short. The data that should have been read by long transactions might be deleted. You can adjust [`tidb_gc_life_time`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_life_time-new-in-v50) using the following command:

    ```sql
    SET GLOBAL tidb_gc_life_time = '30m';
    ```

    > **Note:**
    >
    > "30m" means only cleaning up the data generated 30 minutes ago, which might consume some extra storage space.

* Error Number: 9500

    A single transaction is too large.

    See [the error message `transaction too large`](https://docs.pingcap.com/tidb/stable/faq/migration-tidb-faq#the-error-message-transaction-too-large-is-displayed) for the solution.

* Error Number: 9007

    The error message starts with `ERROR 9007 (HY000): Write conflict`.

    If the error message contains `reason=LazyUniquenessCheck`, it means that the transaction is pessimistic, `@@tidb_constraint_check_in_place_pessimistic=OFF` is set, and a write conflict occurs on a unique index for the application. In this case, successful execution of the pessimistic transaction is not guaranteed. You can retry the transaction from the application, or set the variable to `ON` to avoid the error.

* Error Number: 9008

    Too many requests are sent to TiKV at the same time. The number exceeds limit.

    Increase `tidb_store_limit` or set it to `0` to remove the limit on the traffic of requests.

* Error Number: 9010

    TiKV cannot process this raft log.

    Check the state/monitor/log of the TiKV server.

* Error Number: 9012

    The TiFlash request timed out.

    Check the state/monitor/log of the TiFlash server and the network between the TiDB server and TiFlash server.

* Error Number: 9013

    The TiFlash server is busy and this usually occurs when the workload is too high.

    Check the state/monitor/log of the TiFlash server.
