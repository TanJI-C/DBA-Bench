# Scalability feature details

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.4.0.md`
- Source Title: `TiDB 7.4.0 Release Notes`
- Source Heading Path: `TiDB 7.4.0 Release Notes > Feature details > Scalability`
- Source Line Ranges: `69-94`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `dm`, `dumpling`, `lightning`, `ticdc`, `br`
- Topic Tags: `scalability`, `dxf`, `add-index`, `import-into`, `service-scope`, `partitioned-raft-kv`, `disaggregated-storage`, `s3`, `ga`, `experimental`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0504_ad3e815349`
- Source ID: `tidb-docs-8.1:releases/release-7.4.0.md#scalability`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a07a2b6878231828032c8f6ab62efeb7aafd2338e0b5da359de1dc563be49ef1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.4.0#scalability
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.4.0 scalability details about DXF task placement, Partitioned Raft KV enhancements, or TiFlash disaggregated storage and compute architecture.
- Retrieval Keywords: Scalability, ADD INDEX, IMPORT INTO, Distributed eXecution Framework, DXF, tidb_service_scope, service scope, parallelly execute backend tasks, Partitioned Raft KV storage engine, multiple RocksDB instances, DM, Dumpling, TiDB Lightning, TiCDC, BR, PITR, mixed read and write workloads, write-heavy scenarios, 8 core CPUs, 8 TB data storage, 64 GB memory, TiFlash disaggregated storage and compute architecture, Compute Nodes, Write Nodes, S3 API, GA, cannot be used in the same cluster, cannot be converted to each other
- Follow-up Guidance: The source includes documentation links for tidb_service_scope, the TiDB Distributed eXecution Framework, Partitioned Raft KV, and TiFlash disaggregated storage and S3.
- Classification Note: This is a scalability release-detail chunk because it describes scaling-related changes in execution placement, storage engine capacity and compatibility, and TiFlash architecture.

## Official Source Content

### Scalability

* Support selecting the TiDB nodes to parallelly execute the backend `ADD INDEX` or `IMPORT INTO` tasks of the Distributed eXecution Framework (DXF) (experimental) [#46453](https://github.com/pingcap/tidb/pull/46453) @[ywqzzy](https://github.com/ywqzzy)

    Executing `ADD INDEX` or `IMPORT INTO` tasks in parallel in a resource-intensive cluster can consume a large amount of TiDB node resources, which can lead to cluster performance degradation. Starting from v7.4.0, you can use the system variable [`tidb_service_scope`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_service_scope-new-in-v740) to control the service scope of each TiDB node under the [TiDB Distributed eXecution Framework (DXF)](https://docs.pingcap.com/tidb/stable/tidb-distributed-execution-framework). You can select several existing TiDB nodes or set the TiDB service scope for new TiDB nodes, and all parallel `ADD INDEX` and `IMPORT INTO` tasks only run on these nodes. This mechanism can avoid performance impact on existing services.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/system-variables#tidb_service_scope-new-in-v740).

* Enhance the Partitioned Raft KV storage engine (experimental) [#11515](https://github.com/tikv/tikv/issues/11515) [#12842](https://github.com/tikv/tikv/issues/12842) @[busyjay](https://github.com/busyjay) @[tonyxuqqi](https://github.com/tonyxuqqi) @[tabokie](https://github.com/tabokie) @[bufferflies](https://github.com/bufferflies) @[5kbpers](https://github.com/5kbpers) @[SpadeA-Tang](https://github.com/SpadeA-Tang) @[nolouch](https://github.com/nolouch)

    TiDB v6.6.0 introduces the Partitioned Raft KV storage engine as an experimental feature, which uses multiple RocksDB instances to store TiKV Region data, and the data of each Region is independently stored in a separate RocksDB instance.

    In v7.4.0, TiDB further improves the compatibility and stability of the Partitioned Raft KV storage engine. Through large-scale data testing, the compatibility with TiDB ecosystem tools and features such as DM, Dumpling, TiDB Lightning, TiCDC, BR, and PITR is ensured. Additionally, the Partitioned Raft KV storage engine provides more stable performance under mixed read and write workloads, making it especially suitable for write-heavy scenarios. Furthermore, each TiKV node now supports 8 core CPUs and can be configured with 8 TB data storage, and 64 GB memory.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/partitioned-raft-kv).

* TiFlash supports the disaggregated storage and compute architecture (GA) [#6882](https://github.com/pingcap/tiflash/issues/6882) @[JaySon-Huang](https://github.com/JaySon-Huang) @[JinheLin](https://github.com/JinheLin) @[breezewish](https://github.com/breezewish) @[lidezhu](https://github.com/lidezhu) @[CalvinNeo](https://github.com/CalvinNeo) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)

    In v7.0.0, TiFlash introduces the disaggregated storage and compute architecture as an experimental feature. With a series of improvements, the disaggregated storage and compute architecture for TiFlash becomes GA starting from v7.4.0.

    In this architecture, TiFlash nodes are divided into two types (Compute Nodes and Write Nodes) and support object storage that is compatible with S3 API. Both types of nodes can be independently scaled for computing or storage capacities. In the disaggregated storage and compute architecture, you can use TiFlash in the same way as the coupled storage and compute architecture, such as creating TiFlash replicas, querying data, and specifying optimizer hints.

    Note that the TiFlash **disaggregated storage and compute architecture** and **coupled storage and compute architecture** cannot be used in the same cluster or converted to each other. You can configure which architecture to use when you deploy TiFlash.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-disaggregated-and-s3).
