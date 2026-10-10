# Physical import mode overview and implementation flow

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-physical-import-mode.md`
- Source Title: `Physical Import Mode`
- Source Heading Path: `Physical Import Mode | Physical Import Mode > Implementation`
- Source Line Ranges: `5-47`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tikv`, `pd`, `tidb`, `sql`
- Topic Tags: `physical-import`, `local-backend`, `import-mode`, `engine-files`, `scheduling`, `checksum`, `auto-increment`, `parallel-import`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0102_2956cf3558`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-physical-import-mode.md#physical-import-mode`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7c5206b926caa7dd5849ea3749fa3960b1047f23955279e15cf20364b16bb9c5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode#physical-import-mode
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-physical-import-mode.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how TiDB Lightning physical import mode with backend = "local" works end to end, including import mode, engine files, scheduling behavior, checksum, ANALYZE, and AUTO_INCREMENT handling.
- Retrieval Keywords: Physical import mode, backend = "local", tidb-lightning.toml, tikv-importer, local backend, import mode, normal mode, pause-pd-scheduler-scope, global scheduling, table schemas, add-index-by-sql, blocks, engine file, data engine, index engine, key-value pairs, checksum, ANALYZE, AUTO_INCREMENT, parallel importing
- Follow-up Guidance: The chunk also states that before using the physical import mode, you should read the requirements and restrictions section.
- Classification Note: This is classified as architecture because the content describes the implementation flow of physical import mode across TiDB Lightning, TiKV, PD, and TiDB.

## Official Source Content

# Physical Import Mode

Physical import mode is an efficient and fast import mode that inserts data directly into TiKV nodes as key-value pairs without going through the SQL interface. When using the physical import mode, a single instance of Lightning can import up to 10 TiB of data. The supported amount of imported data theoretically increases as the number of Lightning instances increases. It is verified by users that [parallel importing](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-distributed-import) based on Lightning can effectively handle up to 50 TiB of data.

Before you use the physical import mode, make sure to read [Requirements and restrictions](#requirements-and-restrictions).

The backend for the physical import mode is `local`. You can modify it in `tidb-lightning.toml`:

 ```toml
 [tikv-importer]
 # Set the import mode to "local" to use the physical import mode.
 backend = "local"
 ```
## Implementation

1. Before importing data, TiDB Lightning automatically switches the TiKV nodes to "import mode", which improves write performance and stops auto-compaction. TiDB Lightning determines whether to pause global scheduling according to the TiDB Lightning version.

    - Starting from v7.1.0, you can control the scope of pausing scheduling by using the TiDB Lightning parameter [`pause-pd-scheduler-scope`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration).
    - For TiDB Lightning versions between v6.2.0 and v7.0.0, the behavior of pausing global scheduling depends on the TiDB cluster version. When the TiDB cluster >= v6.1.0, TiDB Lightning pauses scheduling for the Region that stores the target table data. After the import is completed, TiDB Lightning recovers scheduling. For other versions, TiDB Lightning pauses global scheduling.
    - When TiDB Lightning < v6.2.0, TiDB Lightning pauses global scheduling.

2. TiDB Lightning creates table schemas in the target database and fetches the metadata.

    If you set `add-index-by-sql` to `true`, `tidb-lightning` adds indexes via the SQL interface, and drops all secondary indexes from the target table before importing the data. The default value is `false`, which is consistent with earlier versions.

3. Each table is divided into multiple contiguous **blocks**, so that TiDB Lightning can import data from large tables (greater than 200 GB) in parallel.

4. TiDB Lightning prepares an "engine file" for each block to handle key-value pairs. TiDB Lightning reads the SQL dump in parallel, converts the data source to key-value pairs in the same encoding as TiDB, sorts the key-value pairs and writes them to a local temporary storage file.

5. When an engine file is written, TiDB Lightning starts to split and schedule data on the target TiKV cluster, and then imports data to TiKV cluster.

    The engine file contains two types of engines: **data engine** and **index engine**. Each engine corresponds to a type of key-value pairs: row data and secondary index. Normally, row data is completely ordered in the data source, and the secondary index is unordered. Therefore, the data engine files are imported immediately after the corresponding block is written, and all index engine files are imported only after the entire table is encoded.

    Note that when `tidb-lightning` adds indexes via the SQL interface (that is, you set `add-index-by-sql` to `true`), the index engine will not write data because the secondary indexes of the target table have already been dropped in step 2.

6. After all engine files are imported, TiDB Lightning compares the checksum between the local data source and the downstream cluster, and ensures that the imported data is not corrupted. Then TiDB Lightning adds the previously dropped secondary indexes in step 2, or lets TiDB analyze the new data (`ANALYZE`) to optimize future operations. Meanwhile, `tidb-lightning` adjusts the `AUTO_INCREMENT` value to prevent conflicts in the future.

    The auto-increment ID is estimated by the **upper bound** of the number of rows, and is proportional to the total size of the table data file. Therefore, the auto-increment ID is usually larger than the actual number of rows. This is normal because the auto-increment ID [is not necessarily contiguous](https://docs.pingcap.com/tidb/stable/mysql-compatibility#auto-increment-id).

7. After all steps are completed, TiDB Lightning automatically switches the TiKV nodes to "normal mode". If global scheduling is paused, TiDB Lightning also recovers global scheduling. After that, the TiDB cluster can provide services normally.
