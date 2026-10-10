# BR disaster recovery overview and backup-restore architecture

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dr-backup-restore.md`
- Source Title: `DR Solution Based on BR`
- Source Heading Path: `DR Solution Based on BR | DR Solution Based on BR > Perform backup and restore`
- Source Line Ranges: `5-33`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `shared`, `tidb`
- Topic Tags: `disaster-recovery`, `backup`, `restore`, `rpo`, `rto`, `dr-storage`, `architecture`, `pitr`, `snapshot`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0031_527f9b0647`
- Source ID: `tidb-docs-8.1:dr-backup-restore.md#dr-solution-based-on-br`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dd81a34dd6e8519034a5710339c2e2b95c3701bbd53e5d693c2662614fce362a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dr-backup-restore#dr-solution-based-on-br
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dr-backup-restore.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the official overview of a disaster recovery solution based on TiDB Backup & Restore (BR), including backup to independent DR storage, restore architecture, and stated RPO/RTO characteristics.
- Retrieval Keywords: DR Solution Based on BR, Backup & Restore (BR), BR disaster recovery overview, Perform backup and restore, independent disaster recovery (DR) storage device, Recovery Point Objective (RPO) of up to 5 minutes, Recovery Time Objective (RTO) between tens of minutes and a few hours, block storage snapshots, BR log backup and PITR architecture, Usage Overview of TiDB Backup and Restore, Backup & Restore FAQs, Overview of TiDB Backup & Restore Architecture
- Follow-up Guidance: The source points to related documentation on Usage Overview of TiDB Backup and Restore, Backup & Restore FAQs, and Overview of TiDB Backup & Restore Architecture.
- Classification Note: This chunk is classified as architecture for the br component because it describes the BR-based DR architecture, backup and restore flow to DR storage, and high-level recovery characteristics rather than step-by-step operations.

## Official Source Content

# DR Solution Based on BR

A TiDB cluster has multiple replicas, which allows it to tolerate the failure of a single data center or region and continue to provide services. In the case of a natural disaster, software vulnerability, hardware failure, virus attack, or misoperations, which impacts an area larger than a single data center or region, TiDB's Backup & Restore (BR) feature can back up data to an independent disaster recovery (DR) storage device to protect user data from damage. Compared with other DR solutions, the BR feature is more flexible, reliable, recoverable, and cost-effective:

- Flexibility: You can back up data any time with any frequency. This makes backup and restore flexible and better adapts to different business scenarios.
- Reliability: Backup data is usually stored on an independent storage device and this means enhanced data security.
- Recoverability: Any loss or damage to the original data caused by any unexpected situation can be recovered by restoring the backup data. This makes the BR feature highly recoverable and ensures the normal use of your database.
- Cost effectiveness: You can get your database protected using BR without spending too much.

Generally speaking, BR is the last resort for data safety. It improves the safety and reliability of the databases without requiring too much cost. BR protects data in various unexpected situations so that you can use the database safely without worrying about the risk of data loss or damage.
## Perform backup and restore

![BR log backup and PITR architecture](/media/dr/dr-backup-and-restore.png)

As shown in the preceding architecture, you can back up data to a DR storage device located in other regions, and recover data from the backup data as needed. This means that the cluster can tolerate the failure of a single region with a Recovery Point Objective (RPO) of up to 5 minutes and a Recovery Time Objective (RTO) between tens of minutes and a few hours. However, if the database size is large, the RTO might be longer.

> **Note:**
>
> The term "region" in this document means a physical location.

Meanwhile, TiDB provides backup and restore based on block storage snapshots. This feature reduces the recovery time to hours or even less than one hour. TiDB is continuously improving and optimizing the backup and restore capabilities so as to provide you better services.

TiDB also provides detailed documentation to help you understand how to use the backup and restore feature in DR scenarios. Among them,

- [Usage Overview of TiDB Backup and Restore](https://docs.pingcap.com/tidb/stable/br/br-use-overview) is an overview of the BR feature, including the backup strategy and the organization of backup data.
- [Backup & Restore FAQs](https://docs.pingcap.com/tidb/stable/faq/backup-and-restore-faq) lists the frequently asked questions (FAQs) and the solutions of TiDB Backup & Restore (BR).
- [Overview of TiDB Backup & Restore Architecture](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-design) describes the design architecture of the BR feature, including the backup and restore processes and the design of backup files.
