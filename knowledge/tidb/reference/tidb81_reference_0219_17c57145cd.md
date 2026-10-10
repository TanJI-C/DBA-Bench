# DM software, hardware, and storage requirements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-hardware-and-software-requirements.md`
- Source Title: `Software and Hardware Requirements for TiDB Data Migration`
- Source Heading Path: `Software and Hardware Requirements for TiDB Data Migration | Software and Hardware Requirements for TiDB Data Migration > Recommended server requirements | Software and Hardware Requirements for TiDB Data Migration > Recommended server requirements > Development and test environments | Software and Hardware Requirements for TiDB Data Migration > Recommended server requirements > Production environment | Software and Hardware Requirements for TiDB Data Migration > Downstream storage space requirements`
- Source Line Ranges: `5-86`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tikv`, `sql`
- Topic Tags: `os-support`, `hardware-requirements`, `development-environment`, `test-environment`, `production-environment`, `disk-capacity`, `network-requirements`, `high-availability`, `storage-sizing`, `sql-estimation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0219_17c57145cd`
- Source ID: `tidb-docs-8.1:dm/dm-hardware-and-software-requirements.md#software-and-hardware-requirements-for-tidb-data-migration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `934fe48a45b753862066393fa8467149bff2f970672dce30baea1f2c327d1416`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-hardware-and-software-requirements#software-and-hardware-requirements-for-tidb-data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-hardware-and-software-requirements.md

## Retrieval Guidance

- Use When: Use this when you need DM Linux OS support, server sizing, or target TiKV storage capacity requirements for development, test, or production planning.
- Retrieval Keywords: TiDB Data Migration, DM software and hardware requirements, mainstream Linux operating systems, Red Hat Enterprise Linux 7.3 or later, CentOS 7.3 or later, Oracle Enterprise Linux 7.3 or later, Ubuntu LTS 16.04 or later, Intel x86-64, DM-master, DM-worker, Monitor, Gigabit network card, 10 Gigabit network card, target TiKV cluster, size of the data source x the number of replicas x 2, information_schema.tables, DATA_LENGTH, FORMAT_BYTES, Calculate the size of all schemas, Calculate the 5 largest tables
- Follow-up Guidance: If you need to estimate downstream storage, the content includes SQL statements that summarize `DATA_LENGTH` and identify the five largest tables.
- Classification Note: This chunk is a reference page for DM software, hardware, and storage requirements, including OS versions, recommended server resources, and downstream TiKV capacity sizing.

## Official Source Content

# Software and Hardware Requirements for TiDB Data Migration

TiDB Data Migration (DM) supports mainstream Linux operating systems. See the following table for specific version requirements:

| Linux OS       | Version         |
| :----------------------- | :----------:   |
| Red Hat Enterprise Linux | 7.3 or later   |
| CentOS                   | 7.3 or later   |
| Oracle Enterprise Linux  | 7.3 or later   |
| Ubuntu LTS               | 16.04 or later |

DM can be deployed and run on Intel architecture servers and mainstream virtualization environments.
## Recommended server requirements

DM can be deployed and run on a 64-bit generic hardware server platform (Intel x86-64 architecture). For servers used in the development, testing, and production environments, this section illustrates recommended hardware configurations (these do not include the resources used by the operating system).
### Development and test environments

| Component | CPU | Memory | Local Storage | Network | Number of Instances (Minimum Requirement) |
| --- | --- | --- | --- | --- | --- |
| DM-master | 4 core+ | 8 GB+ | SAS, 200 GB+ | Gigabit network card | 1 |
| DM-worker | 8 core+ | 16 GB+ | SAS, 200 GB+ (Greater than the size of the migrated data) | Gigabit network card | The number of upstream MySQL instances |

> **Note:**
>
> - In the test environment, DM-master and DM-worker used for functional verification can be deployed on the same server.
> - To prevent interference with the accuracy of the performance test results, it is **not recommended** to use low-performance storage and network hardware configurations.
> - If you need to verify the function only, you can deploy a DM-master on a single machine. The number of DM-worker deployed must be greater than or equal to the number of upstream MySQL instances. To ensure high availability, it is recommended to deploy more DM-workers.
> - DM-worker stores full data in the `dump` and `load` phases. Therefore, the disk space for DM-worker needs to be greater than the total amount of data to be migrated. If the relay log is enabled for the migration task, DM-worker needs additional disk space to store upstream binlog data.
### Production environment

| Component | CPU | Memory | Hard Disk Type | Network | Number of Instances (Minimum Requirement) |
| --- | --- | --- | --- | --- | --- |
| DM-master | 4 core+ | 8 GB+ | SAS, 200 GB+ | Gigabit network card | 3 |
| DM-worker | 16 core+ | 32 GB+ | SSD, 200 GB+ (Greater than the size of the migrated data) | 10 Gigabit network card | Greater than the number of upstream MySQL instances |
| Monitor | 8 core+ | 16 GB+ | SAS, 200 GB+ | Gigabit network card | 1 |

> **Note:**
>
> - In the production environment, it is not recommended to deploy and run DM-master and DM-worker on the same server, because when DM-worker writes data to disks, it might interfere with the use of disks by DM-master's high availability component.
> - If a performance issue occurs, you are recommended to modify the task configuration file according to the [Optimize Configuration of DM](https://docs.pingcap.com/tidb/stable/dm/dm-tune-configuration) document. If the performance is not effectively optimized by tuning the configuration file, you can try to upgrade the hardware of your server.
## Downstream storage space requirements

The target TiKV cluster must have enough disk space to store the imported data. In addition to the [standard hardware requirements](https://docs.pingcap.com/tidb/stable/hardware-and-software-requirements), the storage space of the target TiKV cluster must be larger than **the size of the data source x the number of replicas x 2**. For example, if the cluster uses 3 replicas by default, the target TiKV cluster must have a storage space larger than 6 times the size of the data source. The formula has `x 2` because:

- Indexes might take extra space.
- RocksDB has a space amplification effect.

You can estimate the data volume by using the following SQL statements to summarize the `DATA_LENGTH` field:

```sql
-- Calculate the size of all schemas
SELECT
  TABLE_SCHEMA,
  FORMAT_BYTES(SUM(DATA_LENGTH)) AS 'Data Size',
  FORMAT_BYTES(SUM(INDEX_LENGTH)) 'Index Size'
FROM
  information_schema.tables
GROUP BY
  TABLE_SCHEMA;

-- Calculate the 5 largest tables
SELECT 
  TABLE_NAME,
  TABLE_SCHEMA,
  FORMAT_BYTES(SUM(data_length)) AS 'Data Size',
  FORMAT_BYTES(SUM(index_length)) AS 'Index Size',
  FORMAT_BYTES(SUM(data_length+index_length)) AS 'Total Size'
FROM
  information_schema.tables
GROUP BY
  TABLE_NAME,
  TABLE_SCHEMA
ORDER BY
  SUM(DATA_LENGTH+INDEX_LENGTH) DESC
LIMIT
  5;
```
