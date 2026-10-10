# Feature details for scalability in TiDB 8.0.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.0.0.md`
- Source Title: `TiDB 8.0.0 Release Notes`
- Source Heading Path: `TiDB 8.0.0 Release Notes > Feature details | TiDB 8.0.0 Release Notes > Feature details > Scalability`
- Source Line Ranges: `59-82`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `tikv`, `operator`
- Topic Tags: `feature-details`, `scalability`, `pd-microservices`, `titan`, `configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0574_cae682f468`
- Source ID: `tidb-docs-8.1:releases/release-8.0.0.md#feature-details`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cf38c9df88357d1adfb7a12de6c7f9502b995e040fcbad001a0c38b6dc59ef20`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.0.0#feature-details
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving detailed TiDB 8.0.0 scalability changes for PD microservice mode or Titan engine configuration behavior.
- Retrieval Keywords: Feature details, Scalability, PD supports the microservice mode, tso microservice, scheduling microservice, TiDB Operator, PD performance bottleneck, Enhance the usability of the Titan engine, shared-blob-cache, blob-cache-size, min-blob-size, blob-file-compression, discardable-ratio
- Follow-up Guidance: The source states that PD microservices can currently only be deployed using TiDB Operator and links to PD microservices and Titan configuration documentation.
- Classification Note: This chunk is classified as feature details for scalability because it expands specific 8.0.0 changes in PD architecture and Titan engine configuration with named microservices and settings.

## Official Source Content

## Feature details
### Scalability

- PD supports the microservice mode (experimental) [#5766](https://github.com/tikv/pd/issues/5766) @[binshi-bing](https://github.com/binshi-bing)

    Starting from v8.0.0, PD supports the microservice mode. This mode splits the timestamp allocation and cluster scheduling functions of PD into separate microservices that can be deployed independently, thereby enhancing performance scalability for PD and addressing performance bottlenecks of PD in large-scale clusters.

    - `tso` microservice: provides monotonically increasing timestamp allocation for the entire cluster.
    - `scheduling` microservice: provides scheduling functions for the entire cluster, including but not limited to load balancing, hot spot handling, replica repair, and replica placement.

  Each microservice is deployed as an independent process. If you configure more than one replica for a microservice, the microservice automatically implements a primary-secondary fault-tolerant mode to ensure high availability and reliability of the service.

    Currently, PD microservices can only be deployed using TiDB Operator. It is recommended to consider this mode when PD becomes a significant performance bottleneck that cannot be resolved by scaling up.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/pd-microservices).

* Enhance the usability of the Titan engine [#16245](https://github.com/tikv/tikv/issues/16245) @[Connor1996](https://github.com/Connor1996)

    - Enable the shared cache for Titan blob files and RocksDB block files by default ([`shared-blob-cache`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#shared-blob-cache-new-in-v800) defaults to `true`), eliminating the need to configure [`blob-cache-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#blob-cache-size) separately.
    - Support dynamically modifying [`min-blob-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#min-blob-size), [`blob-file-compression`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#blob-file-compression), and [`discardable-ratio`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#min-blob-size) to improve performance and flexibility when using the Titan engine.

  For more information, see [documentation](https://docs.pingcap.com/tidb/stable/storage-engine/titan-configuration).
