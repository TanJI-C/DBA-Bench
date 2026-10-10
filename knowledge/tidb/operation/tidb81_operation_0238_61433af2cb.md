# Titan garbage collection, regular GC, and Level Merge

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/storage-engine/titan-overview.md`
- Source Title: `Titan Overview`
- Source Heading Path: `Titan Overview > Garbage Collection | Titan Overview > Garbage Collection > Regular GC | Titan Overview > Garbage Collection > Regular GC > TablePropertiesCollector | Titan Overview > Garbage Collection > Regular GC > EventListener | Titan Overview > Garbage Collection > Level Merge`
- Source Line Ranges: `72-118`
- Source Scope: `shared`
- Primary Component: `tikv`
- Related Components: `shared`
- Topic Tags: `garbage-collection`, `regular-gc`, `tablepropertiescollector`, `eventlistener`, `discardable-size`, `snapshots`, `level-merge`, `compaction`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0238_61433af2cb`
- Source ID: `tidb-docs-8.1:storage-engine/titan-overview.md#garbage-collection`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `61b8c386da8efdf6e1c535c608596fcf5eb8b6c5be6a40ca5b91ab10beab7f16`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/storage-engine/titan-overview#garbage-collection
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/storage-engine/titan-overview.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how Titan garbage collection works, including regular GC with TablePropertiesCollector and EventListener, discardable size tracking, snapshot safety, and the Level Merge algorithm.
- Retrieval Keywords: Garbage Collection, regular GC, Level Merge, TablePropertiesCollector, BlobFileSizeCollector, BlobFileSizeProperties, EventListener, compaction events, inputs outputs blob file size properties, discardable size, greatest discardable size, space amplification, blob index, WriteCallback, MergeOperator, oldest snapshot, sequence number, lowest two levels of LSM-tree, scan performance, write amplification
- Follow-up Guidance: If the user needs background on Titan trade-offs or enabling conditions, the same source also provides overview, usage scenarios, and prerequisites.
- Classification Note: This is operation content because it describes the runtime mechanisms Titan uses to reclaim space and integrate GC with compaction.

## Official Source Content

## Garbage Collection

Titan uses Garbage Collection (GC) to reclaim space. As the keys are being reclaimed in the LSM-tree compaction, some values stored in blob files are not deleted at the same time. Therefore, Titan needs to perform GC periodically to delete outdated values. Titan provides the following two types of GC:

+ Blob files are periodically integrated and rewritten to delete outdated values. This is the regular way of performing GC.
+ Blob files are rewritten while the LSM-tree compaction is performed at the same time. This is the feature of Level Merge.
### Regular GC

Titan uses the TablePropertiesCollector and EventListener components of RocksDB to collect the information for GC.
#### TablePropertiesCollector

RocksDB supports using BlobFileSizeCollector, a custom table property collector, to collect properties from the SST which are written into corresponding SST files. The collected properties are named BlobFileSizeProperties. The following figure shows the BlobFileSizeCollector workflow and data formats:

![BlobFileSizeProperties](/media/titan/titan-4.png)

On the left is the SST index format. The first column is the blob file ID; the second column is the offset for the blob record in the blob file; the third column is the blob record size.

On the right is the BlobFileSizeProperties format. Each line represents a blob file and how much data is saved in this blob file. The first column is the blob file ID; the second column is the size of the data.
#### EventListener

RocksDB uses compaction to discard old data and reclaim space. After each compaction, some blob files in Titan might contain partly or entirely outdated data. Therefore, you can trigger GC by listening to compaction events. During compaction, you can collect and compare the input/output blob file size properties of SST to determine which blob files require GC. The following figure shows the general process:

![EventListener](/media/titan/titan-5.png)

+ *inputs* stands for the blob file size properties for all SSTs that participate in the compaction.
+ *outputs* stands for the blob file size properties for all SSTs generated in the compaction.
+ *discardable size* is the size of the file to be discarded for each blob file, calculated based on inputs and outputs. The first column is the blob file ID. The second column is the size of the file to be discarded.

For each valid blob file, Titan maintains a discardable size variable in memory. After each compaction, this variable is accumulated for the corresponding blob file. Each time when GC starts, it picks the blob file with the greatest discardable size as the candidate file for GC. To reduce write amplification, a certain level of space amplification is allowed, which means GC can be started on a blob file only when the discardable file has reached a specific proportion in size.

For the selected blob file, Titan checks whether the blob index of the key corresponding to each value exists or has been updated to determine whether this value is outdated. If the value is not outdated, Titan merges and sorts the value into a new blob file, and writes the updated blob index into SST using WriteCallback or MergeOperator. Then, Titan records the latest sequence number of RocksDB and does not delete the old blob file until the sequence of the oldest snapshot exceeds the recorded sequence number. The reason is that after the blob index is written back to SST, the old blob index is still accessible via the previous snapshot. Therefore, we need to ensure that no snapshot will access the old blob index before GC can safely deletes the corresponding blob file.
### Level Merge

Level Merge is a newly introduced algorithm in Titan. According to the implementation principle of Level Merge, Titan merges and rewrites blob file that corresponds to the SST file, and generates new blob file while compactions are performed in LSM-tree. The following figure shows the general process:

![LevelMerge General Process](/media/titan/titan-6.png)

When compactions are performed on the SSTs of level z-1 and level z, Titan reads and writes Key-Value pairs in order. Then it writes the values of the selected blob files into new blob files in order, and updates the blob indexes of keys when new SSTs are generated. For the keys deleted in compactions, the corresponding values will not be written to the new blob file, which works similar to GC.

Compared with the regular way of GC, the Level Merge approach completes the blob GC while compactions are performed in LSM-tree. In this way, Titan no longer needs to check the status of blob index in LSM-tree or to write the new blob index into LSM-tree. This reduces the impact of GC on the foreground operations. As the blob file is repeatedly rewritten, fewer files overlap with each other, which makes the whole system in better order and improves the performance of scan.

However, layering blob files similar to tiering compaction brings write amplification. Because 99% of the data in LSM-tree is stored at the lowest two levels, Titan performs the Level Merge operation on the blob files corresponding to the data that is compacted only to the lowest two levels of LSM-tree.
