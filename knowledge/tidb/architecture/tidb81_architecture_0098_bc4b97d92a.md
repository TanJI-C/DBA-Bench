# Global Sort implementation principles and execution steps

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-global-sort.md`
- Source Title: `TiDB Global Sort`
- Source Heading Path: `TiDB Global Sort > Implementation principles | TiDB Global Sort > Implementation principles > Step 1: Scan and prepare data | TiDB Global Sort > Implementation principles > Step 2: Sort and distribute data`
- Source Line Ranges: `69-92`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `pd`, `shared`, `cloud`
- Topic Tags: `algorithm`, `scan`, `kv-encoding`, `local-sort`, `statistics-files`, `range-splitting`, `scatter`, `parallel-subtasks`, `ingest`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0098_bc4b97d92a`
- Source ID: `tidb-docs-8.1:tidb-global-sort.md#implementation-principles`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a6daa7b4e02891915c115dde49ba7f6983052ab24cd33f04206bfe84ddfd01b7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-global-sort#implementation-principles
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-global-sort.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks how Global Sort works internally, including scan, KV encoding, local sorting, statistics files, range splitting, parallel subtasks, and ingest into TiKV.
- Retrieval Keywords: Implementation principles, Step 1: Scan and prepare data, Step 2: Sort and distribute data, CSV data, table data in TiKV, Key-Value pairs, locally sorted, statistics file, cloud storage, PD, split and scatter, nearly equal-sized ranges, subtasks, parallel, ingests them into TiKV without overlap
- Follow-up Guidance: The source describes a two-step flow where TiDB scans data into locally sorted segment files with statistics files, then sorts statistics records into ranges and distributes parallel subtasks for ingest.
- Classification Note: This chunk is classified as architecture because it explains the Global Sort algorithm and execution flow across TiDB, PD, cloud storage, and TiKV.

## Official Source Content

## Implementation principles

The algorithm of the Global Sort feature is as follows:

![Algorithm of Global Sort](/media/dist-task/global-sort.jpeg)

The detailed implementation principles are as follows:
### Step 1: Scan and prepare data

1. After TiDB nodes scan a specific range of data (the data source can be either CSV data or table data in TiKV):

    1. TiDB nodes encode them into Key-Value pairs.
    2. TiDB nodes sort Key-Value pairs into several block data segments (the data segments are locally sorted), where each segment is one file and is uploaded into the cloud storage.

2. The TiDB node also records a serial actual Key-Value ranges for each segment (referred to as a statistics file), which is a key preparation for scalable sort implementation. These files are then uploaded into the cloud storage along with the real data.
### Step 2: Sort and distribute data

From step 1, the Global Sort program obtains a list of sorted blocks and their corresponding statistics files, which provide the number of locally sorted blocks. The program also has a real data scope that can be used by PD to split and scatter. The following steps are performed:

1. Sort the records in the statistics file to divide them into nearly equal-sized ranges, which are subtasks that will be executed in parallel.
2. Distribute the subtasks to TiDB nodes for execution.
3. Each TiDB node independently sorts the data of subtasks into ranges and ingests them into TiKV without overlap.
