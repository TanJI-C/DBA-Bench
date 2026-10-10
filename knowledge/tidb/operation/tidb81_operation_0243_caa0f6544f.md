# Enable, disable, check, and compliance for telemetry

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/telemetry.md`
- Source Title: `Telemetry`
- Source Heading Path: `Telemetry > Enable telemetry | Telemetry > Enable telemetry > Enable TiUP telemetry | Telemetry > Enable telemetry > Enable TiSpark telemetry | Telemetry > Disable telemetry | Telemetry > Disable telemetry > Disable TiUP telemetry | Telemetry > Disable telemetry > Disable TiSpark telemetry | Telemetry > Check telemetry status | Telemetry > Compliance`
- Source Line Ranges: `57-100`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tiup`, `ecosystem`
- Topic Tags: `telemetry`, `enable`, `disable`, `status`, `compliance`, `tiup`, `tispark`, `configuration`, `command`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0243_caa0f6544f`
- Source ID: `tidb-docs-8.1:telemetry.md#enable-telemetry`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `41b8786f8b9a976bb1c924b911bdc055a94ef85573010f2e5fa58e70cc7d13b9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/telemetry#enable-telemetry
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/telemetry.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks how to enable, disable, or check telemetry status for TiUP or TiSpark, or asks about telemetry compliance and data location by sender IP address.
- Retrieval Keywords: Enable telemetry, Disable telemetry, Check telemetry status, Compliance, tiup telemetry enable, tiup telemetry disable, tiup telemetry status, spark.tispark.telemetry.enable = true, spark.tispark.telemetry.enable = false, TiSpark configuration file, Chinese mainland IP addresses, outside of the Chinese mainland, cloud servers in the US, PingCAP Privacy Policy
- Follow-up Guidance: This chunk also states that usage information is sent to servers in the Chinese mainland for sender IP addresses from the Chinese mainland and to servers in the US for sender IP addresses from outside of the Chinese mainland.
- Classification Note: This is operation content because it gives the commands and configuration settings for enabling, disabling, and checking telemetry, plus the compliance routing description.

## Official Source Content

## Enable telemetry
### Enable TiUP telemetry

To enable the TiUP telemetry collection, execute the following command:

```shell
tiup telemetry enable
```
### Enable TiSpark telemetry

To enable the TiSpark telemetry collection, configure `spark.tispark.telemetry.enable = true` in the TiSpark configuration file.
## Disable telemetry
### Disable TiUP telemetry

To disable the TiUP telemetry collection, execute the following command:

```shell
tiup telemetry disable
```
### Disable TiSpark telemetry

To disable the TiSpark telemetry collection, configure `spark.tispark.telemetry.enable = false` in the TiSpark configuration file.
## Check telemetry status

For TiUP telemetry, execute the following command to check the telemetry status:

```shell
tiup telemetry status
```
## Compliance

To meet compliance requirements in different countries or regions, the usage information is sent to servers located in different countries according to the IP address of the sender machine:

- For IP addresses from the Chinese mainland, usage information is sent to and stored on cloud servers in the Chinese mainland.
- For IP addresses from outside of the Chinese mainland, usage information is sent to and stored on cloud servers in the US.

See [PingCAP Privacy Policy](https://www.pingcap.com/privacy-policy/) for details.
