# Logical import mode overview, requirements, and backend limitation

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-logical-import-mode.md`
- Source Title: `Logical Import Mode Introduction`
- Source Heading Path: `Logical Import Mode Introduction | Logical Import Mode Introduction > Environment requirements | Logical Import Mode Introduction > Limitations`
- Source Line Ranges: `5-28`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tidb`, `tikv`
- Topic Tags: `logical-import`, `tidb-backend`, `acid`, `environment-requirements`, `cpu`, `memory`, `network`, `region-concurrency`, `limitations`, `mixed-backends`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0940_09917fe725`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-logical-import-mode.md#logical-import-mode-introduction`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4443cc2360d18f2c7ca76f7886fa4c56fb00349d7b5e53e9df4c6387ca92dec9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-logical-import-mode#logical-import-mode-introduction
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-logical-import-mode.md

## Retrieval Guidance

- Use When: Use this chunk when looking for what TiDB Lightning logical import mode is, which backend it uses, the environment requirements, or the limitation about importing to the same target with mixed backends.
- Retrieval Keywords: logical import mode, TiDB Lightning logical import mode, backend `tidb`, encodes data into SQL statements, ACID compliance, Environment requirements, fresh CentOS 7 instances, dedicated server, region-concurrency, 75% of the logical CPU, more than 4 cores, memory greater than 8 GiB, no more than 5 GiB, 1 Gbps or 10 Gbps Ethernet card, Limitations, do not mix the backends, physical import mode and logical import mode, same target, single TiDB cluster
- Follow-up Guidance: The source also states that if the TiDB cluster already contains data and provides service for external applications, importing in logical import mode is recommended because its behavior is the same as executing normal SQL statements.
- Classification Note: This is reference content because it defines logical import mode, names the `tidb` backend, lists environment requirements, and states a usage limitation for mixed backends.

## Official Source Content

# Logical Import Mode Introduction

The logical import mode is one of the two import modes supported by TiDB Lightning. In the logical import mode, TiDB Lightning first encodes data into SQL statements and then runs the SQL statements to import data.

If your TiDB cluster already contains data and provides service for external applications, it is recommended to import data in the logical import mode. The behavior of the logical import mode is the same as executing normal SQL statements, and thus it guarantees ACID compliance.

The backend for the logical import mode is `tidb`.
## Environment requirements

**Operating system**:

It is recommended to use fresh CentOS 7 instances. You can deploy a virtual machine either on your local host or in the cloud. Because TiDB Lightning consumes as much CPU resources as needed by default, it is recommended that you deploy it on a dedicated server. If this is not possible, you can deploy it on a single server together with other TiDB components (for example, tikv-server) and then configure `region-concurrency` to limit the CPU usage from TiDB Lightning. Usually, you can configure the size to 75% of the logical CPU.

**Memory and CPU**:

It is recommended that you allocate CPU more than 4 cores and memory greater than 8 GiB to get better performance. It is verified that TiDB Lightning does not have significant memory usage (no more than 5 GiB) in the logical import mode. However, if you increase the value of `region-concurrency`, TiDB Lightning might consume more memory.

**Network**: A 1 Gbps or 10 Gbps Ethernet card is recommended.
## Limitations

When you use multiple TiDB Lightning to import data to the same target, do not mix the backends. That is, do not use the physical import mode and the logical import mode to import data to a single TiDB cluster at the same time.
