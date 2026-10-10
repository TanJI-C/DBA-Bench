# Damaged SST inspection and RegionReadProgress diagnostics

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-control.md`
- Source Title: `TiKV Control User Guide`
- Source Heading Path: `TiKV Control User Guide > Subcommands, some options and flags > Print information related to damaged SST files | TiKV Control User Guide > Subcommands, some options and flags > Get the state of a Region's `RegionReadProgress``
- Source Line Ranges: `617-691`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `pd`, `dashboard`
- Topic Tags: `damaged-sst`, `panic-analysis`, `region-overlap`, `resolver`, `regionreadprogress`, `safe-ts`, `stale-read`, `logs`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0122_8d1d182e3c`
- Source ID: `tidb-docs-8.1:tikv-control.md#print-information-related-to-damaged-sst-files`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b4ffb9484fbf03abb4beb755dac629a3e97c1a7ec3479d69fc7d93f16caca2a3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-control#print-information-related-to-damaged-sst-files
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-control.md

## Retrieval Guidance

- Use When: Use this content when diagnosing TiKV panic or corruption related to damaged SST files, or when checking a Region's RegionReadProgress and resolver details for Stale Read and safe-ts issues.
- Retrieval Keywords: bad-ssts, damaged SST files, panic, unsafe_remove_sst_file, tombstone, overlap region, PD server, get-region-read-progress, RegionReadProgress, Resolver, safe_ts, resolved_ts, DataIsNotReady, Min Resolved TS Region, Min Safe TS Region, --log, --min-start-ts, Stale Read
- Follow-up Guidance: The content says to stop the running TiKV instance before running bad-ssts, and notes that get-region-read-progress requires a Region ID and a TiKV that can be obtained from Grafana or DataIsNotReady logs.
- Classification Note: This is classified as diagnosis because the official content focuses on inspecting corruption information, overlap Region metadata, and resolver or safe-ts state to troubleshoot TiKV failures and stale read behavior.

## Official Source Content

### Print information related to damaged SST files

Damaged SST files in TiKV might cause TiKV processes to panic. Before TiDB v6.1.0, these files cause TiKV to panic immediately. Since TiDB v6.1.0, TiKV processes panic 1 hour after SST files are damaged.

To clean up the damaged SST files, you can run the `bad-ssts` command in TiKV Control to show the needed information. The following is an example command and output.

> **Note:**
>
> Before running this command, stop the running TiKV instance.

```shell
tikv-ctl --data-dir </path/to/tikv> bad-ssts --pd <endpoint>
```

```
--------------------------------------------------------
corruption info:
data/tikv-21107/db/000014.sst: Corruption: Bad table magic number: expected 9863518390377041911, found 759105309091689679 in data/tikv-21107/db/000014.sst

sst meta:
14:552997[1 .. 5520]['0101' seq:1, type:1 .. '7A7480000000000000FF0F5F728000000000FF0002160000000000FAFA13AB33020BFFFA' seq:2032, type:1] at level 0 for Column family "default"  (ID 0)
it isn't easy to handle local data, start key:0101

overlap region:
RegionInfo { region: id: 4 end_key: 7480000000000000FF0500000000000000F8 region_epoch { conf_ver: 1 version: 2 } peers { id: 5 store_id: 1 }, leader: Some(id: 5 store_id: 1) }

refer operations:
tikv-ctl ldb --db=/path/to/tikv/db unsafe_remove_sst_file 000014
tikv-ctl --data-dir=/path/to/tikv tombstone -r 4 --pd <endpoint>
--------------------------------------------------------
corruption analysis has completed
```

From the output above, you can see that the information of the damaged SST file is printed first and then the meta-information is printed.

+ In the `sst meta` part, `14` means the SST file number; `552997` means the file size, followed by the smallest and largest sequence numbers and other meta-information.
+ The `overlap region` part shows the information of the Region involved. This information is obtained through the PD server.
+ The `suggested operations` part provides you suggestion to clean up the damaged SST file. You can take the suggestion to clean up files and restart the TiKV instance.
### Get the state of a Region's `RegionReadProgress`

Starting from v6.5.4 and v7.3.0, TiKV introduces the `get-region-read-progress` subcommand to get up-to-date details of the resolver and `RegionReadProgress`. You need to specify a Region ID and a TiKV, which can be obtained from Grafana (`Min Resolved TS Region` and `Min Safe TS Region`) or `DataIsNotReady` logs.

- `--log` (optional): If specified, TiKV logs the smallest `start_ts` of locks in the Region's resolver in this TiKV at `INFO` level. This option helps you identify locks that might block resolved-ts in advance.

- `--min-start-ts` (optional): If specified, TiKV filters out locks with smaller `start_ts` than this value in logs. You can use this to specify a transaction of interest for logging. It defaults to `0`, which means no filter.

The following is an example:

```
./tikv-ctl --host 127.0.0.1:20160 get-region-read-progress -r 14 --log --min-start-ts 0
```

The output is as follows:

```
Region read progress:
    exist: true,
    safe_ts: 0,
    applied_index: 92,
    pending front item (oldest) ts: 0,
    pending front item (oldest) applied index: 0,
    pending back item (latest) ts: 0,
    pending back item (latest) applied index: 0,
    paused: false,
Resolver:
    exist: true,
    resolved_ts: 0,
    tracked index: 92,
    number of locks: 0,
    number of transactions: 0,
    stopped: false,
```

The subcommand is useful in diagnosing issues related to Stale Read and safe-ts. For details, see [Understanding Stale Read and safe-ts in TiKV](https://docs.pingcap.com/tidb/stable/troubleshoot-stale-read).
