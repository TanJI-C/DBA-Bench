# MySQL native error messages and troubleshooting links

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/error-codes.md`
- Source Title: `Error Codes and Troubleshooting`
- Source Heading Path: `Error Codes and Troubleshooting > Error codes > MySQL native error messages | Error Codes and Troubleshooting > Troubleshooting`
- Source Line Ranges: `622-660`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `sql`
- Topic Tags: `error-codes`, `mysql-errors`, `connection-loss`, `oom`, `version-mismatch`, `load-data-local`, `pd-timeout`, `safepoint`, `eof`, `troubleshooting`, `faq`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0036_d4b59ff290`
- Source ID: `tidb-docs-8.1:error-codes.md#mysql-native-error-messages`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9859b6d9cee28ff02e94356f3c6ce79860d0ae09bacaa4a9afd3bbbc08af3f85`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/error-codes#mysql-native-error-messages
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/error-codes.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing MySQL native TiDB-related errors such as lost connection, version mismatch, LOAD DATA LOCAL not allowed, PD server timeout with safepoint, or EOF log messages.
- Retrieval Keywords: ERROR 2013 (HY000), Lost connection to MySQL server during query, panic in the log, dmesg -T | grep -i oom, TCP timeout, ERROR 1105 (HY000), other error: unknown error Wire Error(InvalidEnumValue(4004)), version of TiDB does not match with that of TiKV, ERROR 1148 (42000), the used command is not allowed with this TiDB version, LOAD DATA LOCAL, local_infile, mysql --local-infile=1 -u root -h 127.0.0.1 -P 4000, ERROR 9001 (HY000), PD server timeout start timestamp may fall behind safe point, TiDB fails to access PD, safepoint from PD, disk on PD is slow and busy, EOF error, client or proxy disconnects from TiDB, troubleshooting, FAQ
- Follow-up Guidance: The source also points readers to the troubleshooting and FAQ documents for more details.
- Classification Note: This chunk is classified as diagnosis because the official content maps specific error numbers and log messages to their described causes, checks, and related troubleshooting references.

## Official Source Content

### MySQL native error messages

* Error Number: 2013 (HY000)

    The complete error message: `ERROR 2013 (HY000): Lost connection to MySQL server during query`

    You can handle this error as follows:

    - Check whether panic is in the log.
    - Check whether OOM exists in dmesg using `dmesg -T | grep -i oom`.
    - A long time of no access might also lead to this error. It is usually caused by TCP timeout. If TCP is not used for a long time, the operating system kills it.

* Error Number: 1105 (HY000)

    The complete error message: `ERROR 1105 (HY000): other error: unknown error Wire Error(InvalidEnumValue(4004))`

    This error usually occurs when the version of TiDB does not match with that of TiKV. To avoid version mismatch, upgrade all components when you upgrade the version.

* Error Number: 1148 (42000)

    The complete error message: `ERROR 1148 (42000): the used command is not allowed with this TiDB version`

    When you execute the `LOAD DATA LOCAL` statement but the MySQL client does not allow executing this statement (the value of the `local_infile` option is 0), this error occurs.

    The solution is to use the `--local-infile=1` option when you start the MySQL client. For example, run the command `mysql --local-infile=1 -u root -h 127.0.0.1 -P 4000`. The default value of `local-infile` varies in different versions of the MySQL client. Therefore, you need to configure it in specific MySQL clients.

* Error Number: 9001 (HY000)

    The complete error message: `ERROR 9001 (HY000): PD server timeout start timestamp may fall behind safe point`

    This error occurs when TiDB fails to access PD. A worker in the TiDB background continuously queries the safepoint from PD and reports this error if it fails to query within 100s. Generally, it is because the disk on PD is slow and busy or the network failed between TiDB and PD. For the details of common errors, see [Error Number and Fault Diagnosis](https://docs.pingcap.com/tidb/stable/error-codes).

* TiDB log error message: EOF error

    When the client or proxy disconnects from TiDB, TiDB does not immediately notice the disconnection. Instead, TiDB notices the disconnection only when it begins to return data to the connection. At this time, the log prints an EOF error.
## Troubleshooting

See the [troubleshooting](https://docs.pingcap.com/tidb/stable/troubleshoot-tidb-cluster) and [FAQ](https://docs.pingcap.com/tidb/stable/faq/tidb-faq) documents.
