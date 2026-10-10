# Server hardware recommendations for development, test, and production

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/hardware-and-software-requirements.md`
- Source Title: `Software and Hardware Recommendations`
- Source Heading Path: `Software and Hardware Recommendations > Server recommendations | Software and Hardware Recommendations > Server recommendations > Development and test environments | Software and Hardware Recommendations > Server recommendations > Production environment`
- Source Line Ranges: `166-214`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`, `tiflash`, `ticdc`
- Topic Tags: `server-sizing`, `development-environment`, `test-environment`, `production-environment`, `cpu`, `memory`, `storage`, `network`, `instance-counts`, `ssd`, `nvme`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0367_aaf771d57b`
- Source ID: `tidb-docs-8.1:hardware-and-software-requirements.md#server-recommendations`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d13c8e9e705b5f076c421fe3b1f2ea373d7487200ef7bfa3f15aaecd13915c47`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/hardware-and-software-requirements#server-recommendations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/hardware-and-software-requirements.md

## Retrieval Guidance

- Use When: Use this chunk when sizing servers for TiDB, PD, TiKV, TiFlash, TiCDC, or Monitor in development, test, or production environments, including CPU, memory, storage, network, and minimum instance counts.
- Retrieval Keywords: Server recommendations, Development and test environments, Production environment, TiDB 8 core+ 16 GB+, PD 4 core+ 8 GB+, TiKV 8 core+ 32 GB+, TiFlash 32 core+ 64 GB+, TiCDC 8 core+ 16 GB+, TiDB 16 core+ 48 GB+, PD 8 core+ 16 GB+, TiKV 16 core+ 64 GB+, TiFlash 48 core+ 128 GB+, TiCDC 16 core+ 64 GB+, Monitor 8 core+ 16 GB+, Gigabit network card, 10 Gigabit network card (2 preferred), NVMe SSDs, AVX2 instruction set, cat /proc/cpuinfo | grep avx2, ARMv8 instruction set architecture, cat /proc/cpuinfo | grep 'crc32' | grep 'asimd', TiFlash multi-disk deployment, PCIe SSD, TiKV hard disk within 4 TB, regular SSDs 1.5 TB, cloud disks for TiKV nodes, TiCDC PCIe SSD disks larger than 500 GB
- Follow-up Guidance: The source includes deployment notes such as TiDB and PD co-location options, TiFlash CPU instruction set checks and disk planning guidance, and the recommendation that TiCDC use PCIe SSD disks larger than 500 GB.
- Classification Note: This is reference content because it gives hardware sizing tables and deployment notes for multiple TiDB components across development, test, and production environments.

## Official Source Content

## Server recommendations

You can deploy and run TiDB on the 64-bit generic hardware server platform in the Intel x86-64 architecture or on the hardware server platform in the ARM architecture. The requirements and recommendations about server hardware configuration (ignoring the resources occupied by the operating system itself) for development, test, and production environments are as follows:
### Development and test environments

| Component | CPU     | Memory | Local Storage  | Network  | Number of Instances (Minimum Requirement) |
| :------: | :-----: | :-----: | :----------: | :------: | :----------------: |
| TiDB    | 8 core+   | 16 GB+  | [Storage requirements](#storage-requirements) | Gigabit network card | 1 (can be deployed on the same machine with PD)      |
| PD      | 4 core+   | 8 GB+  | SAS, 200 GB+ | Gigabit network card | 1 (can be deployed on the same machine with TiDB)       |
| TiKV    | 8 core+   | 32 GB+  | SAS, 200 GB+ | Gigabit network card | 3       |
| TiFlash | 32 core+  | 64 GB+  | SSD, 200 GB+ | Gigabit network card | 1     |
| TiCDC | 8 core+ | 16 GB+ | SAS, 200 GB+ | Gigabit network card | 1 |

> **Note:**
>
> - In the test environment, the TiDB and PD instances can be deployed on the same server.
> - For performance-related test, do not use low-performance storage and network hardware configuration, in order to guarantee the correctness of the test result.
> - For the TiKV server, it is recommended to use NVMe SSDs to ensure faster reads and writes.
> - If you only want to test and verify the features, follow [Quick Start Guide for TiDB](https://docs.pingcap.com/tidb/stable/quick-start-with-tidb) to deploy TiDB on a single machine.
> - Starting from v6.3.0, to deploy TiFlash under the Linux AMD64 architecture, the CPU must support the AVX2 instruction set. Ensure that `cat /proc/cpuinfo | grep avx2` has output. To deploy TiFlash under the Linux ARM64 architecture, the CPU must support the ARMv8 instruction set architecture. Ensure that `cat /proc/cpuinfo | grep 'crc32' | grep 'asimd'` has output. By using the instruction set extensions, TiFlash's vectorization engine can deliver better performance.
### Production environment

| Component | CPU | Memory | Hard Disk Type | Network | Number of Instances (Minimum Requirement) |
| :-----: | :------: | :------: | :------: | :------: | :-----: |
| TiDB  | 16 core+ | 48 GB+ | SSD | 10 Gigabit network card (2 preferred) | 2 |
| PD | 8 core+ | 16 GB+ | SSD | 10 Gigabit network card (2 preferred) | 3 |
| TiKV | 16 core+ | 64 GB+ | SSD | 10 Gigabit network card (2 preferred) | 3 |
| TiFlash | 48 core+ | 128 GB+ | 1 or more SSDs | 10 Gigabit network card (2 preferred) | 2 |
| TiCDC | 16 core+ | 64 GB+ | SSD | 10 Gigabit network card (2 preferred) | 2 |
| Monitor | 8 core+ | 16 GB+ | SAS | Gigabit network card | 1 |

> **Note:**
>
> - In the production environment, the TiDB and PD instances can be deployed on the same server. If you have a higher requirement for performance and reliability, try to deploy them separately.
> - It is strongly recommended to configure TiDB, TiKV, and TiFlash with at least 8 CPU cores each in the production environment. To get better performance, a higher configuration is recommended.
> - It is recommended to keep the size of TiKV hard disk within 4 TB if you are using PCIe SSDs or within 1.5 TB if you are using regular SSDs.
> - If you deploy TiKV on a cloud provider, such as AWS, Google Cloud, or Azure, it is recommended to use cloud disks for TiKV nodes. Data on local disks might be lost if the TiKV instance crashes in the cloud environment.

Before you deploy TiFlash, note the following items:

- TiFlash can be [deployed on multiple disks](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#multi-disk-deployment).
- It is recommended to use a high-performance SSD as the first disk of the TiFlash data directory to buffer the real-time replication of TiKV data. The performance of this disk should not be lower than that of TiKV, such as PCIe SSD. The disk capacity should be no less than 10% of the total capacity; otherwise, it might become the bottleneck of this node. You can deploy ordinary SSDs for other disks, but note that a better PCIe SSD brings better performance.
- It is recommended to deploy TiFlash on different nodes from TiKV. If you must deploy TiFlash and TiKV on the same node, increase the number of CPU cores and memory, and try to deploy TiFlash and TiKV on different disks to avoid interfering each other.
- The total capacity of the TiFlash disks is calculated in this way: `the data volume of the entire TiKV cluster to be replicated / the number of TiKV replicas * the number of TiFlash replicas`. For example, if the overall planned capacity of TiKV is 1 TB, the number of TiKV replicas is 3, and the number of TiFlash replicas is 2, then the recommended total capacity of TiFlash is `1024 GB / 3 * 2`. You can replicate only the data of some tables. In such case, determine the TiFlash capacity according to the data volume of the tables to be replicated.

Before you deploy TiCDC, note that it is recommended to deploy TiCDC on PCIe SSD disks larger than 500 GB.
