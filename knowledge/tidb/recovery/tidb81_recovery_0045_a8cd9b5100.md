# Eventually consistent replication for disaster scenarios

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-sink-to-mysql.md`
- Source Title: `Replicate Data to MySQL-compatible Databases`
- Source Heading Path: `Replicate Data to MySQL-compatible Databases > Eventually consistent replication in disaster scenarios`
- Source Line Ranges: `117-134`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `disaster-recovery`, `eventual-consistency`, `rto`, `rpo`, `replication-lag`, `object-storage`, `nfs`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0045_a8cd9b5100`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-sink-to-mysql.md#eventually-consistent-replication-in-disaster-scenarios`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `84c1989794586e190382d6b5e06922c7c6146cc51f89668e48508c26b191bd24`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-mysql#eventually-consistent-replication-in-disaster-scenarios
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-sink-to-mysql.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about TiCDC eventually consistent replication for disaster scenarios, including supported storage targets, RTO/RPO targets, and causes of replication lag.
- Retrieval Keywords: Eventually consistent replication in disaster scenarios, eventually consistent replication, disaster scenarios, object storage, NFS, Amazon S3-compatible object storage, GCS-compatible object storage, Azure-compatible object storage, RTO <= 5 min, P95 RPO <= 10s, replication lag, TPS increases significantly, large or long transactions, TiKV or TiCDC cluster is reloaded or upgraded, add index, frequent transfer of Region leaders, Region merge, Region split
- Follow-up Guidance: The source lists scenarios that increase TiCDC replication lag, including short-term TPS spikes, large or long transactions, upstream TiKV or TiCDC reload or upgrade, time-consuming DDL such as add index, and aggressive PD scheduling with frequent Region leader transfer, merge, or split.
- Classification Note: This is classified as a recovery chunk because it describes disaster recovery behavior, eventual consistency objectives, and lag conditions for failover scenarios.

## Official Source Content

## Eventually consistent replication in disaster scenarios

Starting from v6.1.1, this feature becomes GA. Starting from v5.3.0, TiCDC supports backing up incremental data from an upstream TiDB cluster to an object storage or an NFS of the downstream cluster. When the upstream cluster encounters a disaster and becomes unavailable, TiCDC can restore the downstream data to the recent eventually consistent state. This is the eventually consistent replication capability provided by TiCDC. With this capability, you can switch applications to the downstream cluster quickly, avoiding long-time downtime and improving service continuity.

Currently, TiCDC can replicate incremental data from a TiDB cluster to another TiDB cluster or a MySQL-compatible database system (including Aurora, MySQL, and MariaDB). In case the upstream cluster crashes, TiCDC can restore data in the downstream cluster within 5 minutes, given the conditions that TiCDC replicates data normally before the crash, and the replication lag is small. It allows data loss of 10s at most, that is, RTO <= 5 min, and P95 RPO <= 10s.

TiCDC replication lag increases in the following scenarios:

- The TPS increases significantly in a short time.
- Large or long transactions occur in the upstream.
- The TiKV or TiCDC cluster in the upstream is reloaded or upgraded.
- Time-consuming DDL statements, such as `add index`, are executed in the upstream.
- The PD is configured with aggressive scheduling strategies, resulting in frequent transfer of Region leaders, or frequent Region merge or Region split.

> **Note:**
>
> Starting from v6.1.1, the eventually consistent replication feature of TiCDC supports Amazon S3-compatible object storage. Starting from v6.1.4, this feature supports GCS- and Azure-compatible object storage.
