# Online unsafe recovery overview and prerequisites

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/online-unsafe-recovery.md`
- Source Title: `Online Unsafe Recovery`
- Source Heading Path: `Online Unsafe Recovery | Online Unsafe Recovery > Feature description | Online Unsafe Recovery > User scenarios | Online Unsafe Recovery > Usage | Online Unsafe Recovery > Usage > Prerequisites`
- Source Line Ranges: `5-38`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`, `tidb`
- Topic Tags: `lossy-recovery`, `data-loss`, `region-unavailability`, `replica-failure`, `prerequisites`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0028_855ead530b`
- Source ID: `tidb-docs-8.1:online-unsafe-recovery.md#online-unsafe-recovery`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e22a8f5dc653877f4f04a7e4b7b43f5d8018ee66707808132659a35f6b360c34`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/online-unsafe-recovery#online-unsafe-recovery
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/online-unsafe-recovery.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the overview, data-loss warning, suitable scenarios, or prerequisites for Online Unsafe Recovery after permanently damaged replicas make some TiKV data unreadable and unwritable.
- Retrieval Keywords: Online Unsafe Recovery, lossy recovery, integrity of data and data indexes cannot be guaranteed, permanently damaged replicas, Region becomes temporarily unavailable, unreadable and unwritable, PD automatically pauses Region scheduling, split and merge, collects the metadata of data shards, global perspective, real-time and complete recovery plan, surviving stores, prerequisites, offline stores indeed cause some pieces of data to be unavailable, offline stores cannot be automatically recovered or restarted
- Follow-up Guidance: The source continues with usage steps for specifying failed stores and checking recovery progress with PD Control.
- Classification Note: This chunk is classified as recovery for PD because it describes the Online Unsafe Recovery feature, its lossy nature, user scenarios, and prerequisites, with PD coordinating the recovery plan across TiKV stores.

## Official Source Content

# Online Unsafe Recovery

> **Warning:**
>
> Online Unsafe Recovery is a type of lossy recovery. If you use this feature, the integrity of data and data indexes cannot be guaranteed.

When permanently damaged replicas cause part of data on TiKV to be unreadable and unwritable, you can use the Online Unsafe Recovery feature to perform a lossy recovery operation.
## Feature description

In TiDB, the same data might be stored in multiple stores at the same time according to the replica rules defined by users. This guarantees that data is still readable and writable even if a single or a few stores are temporarily offline or damaged. However, when most or all replicas of a Region go offline during a short period of time, the Region becomes temporarily unavailable and cannot be read or written.

Suppose that multiple replicas of a data range encounter issues like permanent damage (such as disk damage), and these issues cause the stores to stay offline. In this case, this data range is temporarily unavailable. If you want the cluster back in use and also accept data rewind or data loss, in theory, you can re-form the majority of replicas by manually removing the failed replicas from the group. This allows application-layer services to read and write this data range (might be stale or empty) again.

In this case, if some stores with loss-tolerant data are permanently damaged, you can perform a lossy recovery operation by using Online Unsafe Recovery. When you use this feature, PD automatically pauses Region scheduling (including split and merge), collects the metadata of data shards from all stores, and then, under its global perspective, generates a real-time and complete recovery plan. Then, PD distributes the plan to all surviving stores to make them perform data recovery tasks. In addition, once the data recovery plan is distributed, PD periodically monitors the recovery progress and re-send the plan when necessary.
## User scenarios

The Online Unsafe Recovery feature is suitable for the following scenarios:

* The data for application services is unreadable and unwritable, because permanently damaged stores cause the stores to fail to restart.
* You can accept data loss and want the affected data to be readable and writable.
* You want to perform a one-stop online data recovery operation.
## Usage
### Prerequisites

Before using Online Unsafe Recovery, make sure that the following requirements are met:

* The offline stores indeed cause some pieces of data to be unavailable.
* The offline stores cannot be automatically recovered or restarted.
