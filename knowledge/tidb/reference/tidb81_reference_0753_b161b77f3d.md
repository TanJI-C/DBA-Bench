# Telemetry overview and shared usage information

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/telemetry.md`
- Source Title: `Telemetry`
- Source Heading Path: `Telemetry | Telemetry > What is shared when telemetry is enabled? | Telemetry > What is shared when telemetry is enabled? > TiUP | Telemetry > What is shared when telemetry is enabled? > TiSpark`
- Source Line Ranges: `6-56`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tiup`, `ecosystem`
- Topic Tags: `telemetry`, `usage-information`, `privacy`, `default-disabled`, `tiup`, `tispark`, `shared-data`, `logs`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0753_b161b77f3d`
- Source ID: `tidb-docs-8.1:telemetry.md#telemetry`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `79242701b152a64251a92296fc1091465d5bc305707d551bacd8ee1a20d63eea`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/telemetry#telemetry
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/telemetry.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks what telemetry shares for TiUP or TiSpark, whether telemetry is disabled by default, how to inspect the shared usage information, or whether user data is included.
- Retrieval Keywords: telemetry, What is shared when telemetry is enabled?, TiUP telemetry, TiSpark telemetry, TiUP v1.11.3 disabled by default, TiSpark v3.0.3 disabled by default, v8.1.0 telemetry feature removed, randomly generated telemetry ID, execution status of TiUP commands, deployment configuration names that have been modified, TIUP_CLUSTER_DEBUG=enable, tiup cluster list, Spark logs, Telemetry report, cat {spark.log} | grep Telemetry report | tail -n 1, user data stored in the TiDB cluster will NOT be shared, PingCAP Privacy Policy
- Follow-up Guidance: This chunk also states that TiUP shared content can be viewed with `TIUP_CLUSTER_DEBUG=enable` and TiSpark collected usage information can be viewed in Spark logs with `grep Telemetry report`.
- Classification Note: This is reference content because it describes telemetry behavior, default status notes, and the specific usage information shared by TiUP and TiSpark.

## Official Source Content

# Telemetry

When the telemetry feature is enabled, TiUP and TiSpark collect usage information and share the information with PingCAP to help understand how to improve the product.

> **Note:**
>
> - Starting from TiUP v1.11.3, the telemetry feature in TiUP is disabled by default, which means TiUP usage information is not collected by default. If you upgrade from a TiUP version earlier than v1.11.3 to v1.11.3 or a later version, the telemetry feature keeps the same status as before the upgrade.
> - Starting from TiSpark v3.0.3, the telemetry feature in TiSpark is disabled by default, which means TiSpark usage information is not collected by default.
> - Starting from v8.1.0, the telemetry feature in TiDB and TiDB Dashboard is removed.
## What is shared when telemetry is enabled?

The following sections describe the shared usage information in detail for TiUP and TiSpark. The usage details that get shared might change over time. These changes (if any) will be announced in [release notes](https://docs.pingcap.com/releases/tidb-self-managed/).

> **Note:**
>
> In **ALL** cases, user data stored in the TiDB cluster will **NOT** be shared. You can also refer to [PingCAP Privacy Policy](https://pingcap.com/privacy-policy).
### TiUP

When the telemetry collection feature is enabled in TiUP, usage details of TiUP will be shared, including (but not limited to):

- A randomly generated telemetry ID.
- Execution status of TiUP commands, such as whether the execution is successful and the execution duration.
- Deployment characteristics, such as the size of hardware, TiDB components versions, and deployment configuration names that have been modified.

To view the full content of the usage information shared to PingCAP, set the `TIUP_CLUSTER_DEBUG=enable` environment variable when executing the TiUP command. For example:

```shell
TIUP_CLUSTER_DEBUG=enable tiup cluster list
```
### TiSpark

> **Note:**
>
> Starting from v3.0.3, the telemetry collection is disabled by default in TiSpark, and usage information is not collected and shared with PingCAP.

When the telemetry collection feature is enabled for TiSpark, the Spark module will share the usage details of TiSpark, including (but not limited to):

- A randomly generated telemetry ID.
- Some configuration information of TiSpark, such as the read engine and whether streaming read is enabled.
- Cluster deployment information, such as the machine hardware information, OS information, and component version number of the node where TiSpark is located.

You can view TiSpark usage information that is collected in Spark logs. You can set the Spark log level to INFO or lower, for example:

```shell
cat {spark.log} | grep Telemetry report | tail -n 1
```
