# Software and hardware requirements for TiDB deployment

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/deploy-and-maintain-faq.md`
- Source Title: `TiDB Deployment FAQs`
- Source Heading Path: `TiDB Deployment FAQs | TiDB Deployment FAQs > Software and hardware requirements | TiDB Deployment FAQs > Software and hardware requirements > What operating systems does TiDB support? | TiDB Deployment FAQs > Software and hardware requirements > What is the recommended hardware configuration for a TiDB cluster in the development, test, or production environment? | TiDB Deployment FAQs > Software and hardware requirements > What's the purposes of 2 network cards of 10 gigabit? | TiDB Deployment FAQs > Software and hardware requirements > Is it feasible if we don't use RAID for SSD? | TiDB Deployment FAQs > Software and hardware requirements > What's the recommended configuration of TiDB components?`
- Source Line Ranges: `5-35`
- Source Scope: `all`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`
- Topic Tags: `operating-systems`, `hardware-requirements`, `server-recommendations`, `networking`, `raid`, `ssd`, `component-sizing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0280_986447ec12`
- Source ID: `tidb-docs-8.1:faq/deploy-and-maintain-faq.md#tidb-deployment-faqs`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b1bddf951edb2d4e74fce1a652f93efced3040e6e22339c0af7f515c9addc984`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/deploy-and-maintain-faq#tidb-deployment-faqs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/deploy-and-maintain-faq.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks about TiDB deployment operating systems, hardware recommendations, 10 gigabit network cards, SSD RAID feasibility, or component sizing for TiDB, PD, and TiKV.
- Retrieval Keywords: Software and Hardware Recommendations, server recommendations, operating systems does TiDB support, 64-bit generic hardware server platform, Intel x86-64, ARM architecture, 2 network cards of 10 gigabit, PD unique timestamps, bond of two network cards, RAID 10 for SSD, recommended configuration of TiDB components, TiDB Binlog, PD stores the cluster metadata, SSD disks, TiKV is required to use SSD
- Follow-up Guidance: For detailed supported operating systems and server hardware recommendations, the content points to Software and Hardware Recommendations and its Server recommendations section.
- Classification Note: This is reference content because it summarizes deployment prerequisites and recommended hardware characteristics for shared TiDB cluster components.

## Official Source Content

# TiDB Deployment FAQs

This document summarizes the FAQs related to TiDB deployment.
## Software and hardware requirements
### What operating systems does TiDB support?

For the TiDB-supported operating systems, see [Software and Hardware Recommendations](https://docs.pingcap.com/tidb/stable/hardware-and-software-requirements).
### What is the recommended hardware configuration for a TiDB cluster in the development, test, or production environment?

You can deploy and run TiDB on the 64-bit generic hardware server platform in the Intel x86-64 architecture or on the hardware server platform in the ARM architecture. For the requirements and recommendations about server hardware configuration for development, test, and production environments, see [Software and Hardware Recommendations - Server recommendations](https://docs.pingcap.com/tidb/stable/hardware-and-software-requirements#server-recommendations).
### What's the purposes of 2 network cards of 10 gigabit?

As a distributed cluster, TiDB has a high demand on time, especially for PD, because PD needs to distribute unique timestamps. If the time in the PD servers is not consistent, it takes longer waiting time when switching the PD server. The bond of two network cards guarantees the stability of data transmission, and 10 gigabit guarantees the transmission speed. Gigabit network cards are prone to meet bottlenecks, therefore it is strongly recommended to use 10 gigabit network cards.
### Is it feasible if we don't use RAID for SSD?

If the resources are adequate, it is recommended to use RAID 10 for SSD. If the resources are inadequate, it is acceptable not to use RAID for SSD.
### What's the recommended configuration of TiDB components?

- TiDB has a high requirement on CPU and memory. If you need to enable TiDB Binlog, the local disk space should be increased based on the service volume estimation and the time requirement for the GC operation. But the SSD disk is not a must.
- PD stores the cluster metadata and has frequent Read and Write requests. It demands a high I/O disk. A disk of low performance will affect the performance of the whole cluster. It is recommended to use SSD disks. In addition, a larger number of Regions has a higher requirement on CPU and memory.
- TiKV has a high requirement on CPU, memory and disk. It is required to use SSD.

For details, see [Software and Hardware Recommendations](https://docs.pingcap.com/tidb/stable/hardware-and-software-requirements).
