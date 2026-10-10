# Inspect Raft state, Region size, and MVCC data

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-control.md`
- Source Title: `TiKV Control User Guide`
- Source Heading Path: `TiKV Control User Guide > Subcommands, some options and flags > View information of the Raft state machine | TiKV Control User Guide > Subcommands, some options and flags > View the Region size | TiKV Control User Guide > Subcommands, some options and flags > Scan to view MVCC of a specific range | TiKV Control User Guide > Subcommands, some options and flags > View MVCC of a given key`
- Source Line Ranges: `138-251`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `raft`, `region`, `region-size`, `mvcc`, `scan`, `raw-key`, `column-families`, `state-machine`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0120_34227726ca`
- Source ID: `tidb-docs-8.1:tikv-control.md#view-information-of-the-raft-state-machine`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `167904d672225ff14c0300183eda9d41111867a89880ce9c85aac10997f742fa`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-control#view-information-of-the-raft-state-machine
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-control.md

## Retrieval Guidance

- Use When: Use this chunk when you need tikv-ctl commands and examples for inspecting Raft state, querying Regions by ID or key range, checking Region size, or viewing MVCC data for a range or a specific key.
- Retrieval Keywords: raft region -r, --all-regions, --limit, --start, --end, RegionLocalState, RaftLocalState, RegionApplyState, tikv-ctl --host 127.0.0.1:20160 raft region -r 1239, size -r 2, scan --from --to --show-cf, mvcc -k, lock,default,write, escaped form of raw key, region size, view MVCC of a given key
- Follow-up Guidance: The content notes that the `mvcc` command is similar to `scan`, and that the key used with `mvcc -k` is the escaped form of raw key.
- Classification Note: The official content is diagnostic because it focuses on viewing internal Raft state, Region boundaries and sizes, and MVCC records through inspection commands and output examples.

## Official Source Content

### View information of the Raft state machine

Use the `raft` subcommand to view the status of the Raft state machine at a specific moment. The status information includes two parts: three structs (**RegionLocalState**, **RaftLocalState**, and **RegionApplyState**) and the corresponding Entries of a certain piece of log.

Use the `region` and `log` subcommands to obtain the above information respectively. The two subcommands both support the remote mode and the local mode at the same time.

For the `region` subcommand:

- To specify the Regions to be viewed, use the `-r` option. Multiple Regions are separated by `,`. You can also use the `--all-regions` option to view all Regions. Note that `-r` and `--all-regions` cannot be used at the same time.
- To limit the number of Regions to be printed, use the `--limit` option (default: `16`).
- To query which Regions are included in a certain key range, use the `--start` and `--end` options (default: no range limit, in Hex format).

For example, to print the Region with the ID `1239`, use the following command:

```shell
tikv-ctl --host 127.0.0.1:20160 raft region -r 1239
```

The output is as follows:

```
"region id": 1239
"region state": {
    id: 1239,
    start_key: 7480000000000000FF4E5F728000000000FF1443770000000000FA,
    end_key: 7480000000000000FF4E5F728000000000FF21C4420000000000FA,
    region_epoch: {conf_ver: 1 version: 43},
    peers: [ {id: 1240 store_id: 1 role: Voter} ]
}
"raft state": {
    hard_state {term: 8 vote: 5 commit: 7}
    last_index: 8)
}
"apply state": {
    applied_index: 8 commit_index: 8 commit_term: 8
    truncated_state {index: 5 term: 5}
}
```

To query which Regions are included in a certain key range, use the following command:

- If the key range is in a Region range, the Region information is output.
- If the key range is the same as a Region range, for example, when the given key range is the same as the Region `1239`, because the Region range is a left-closed and right-open interval, and Region `1009` takes the `end_key` of Region `1239` as the `start_key`, the Region `1009` information is also output.

```shell
tikv-ctl --host 127.0.0.1:20160 raft region --start 7480000000000000FF4E5F728000000000FF1443770000000000FA --end 7480000000000000FF4E5F728000000000FF21C4420000000000FA
```

The output is as follows:

```
"region state": {
    id: 1009
    start_key: 7480000000000000FF4E5F728000000000FF21C4420000000000FA,
    end_key: 7480000000000000FF5000000000000000F8,
    ...
}
"region state": {
    id: 1239
    start_key: 7480000000000000FF4E5F728000000000FF06C6D60000000000FA,
    end_key: 7480000000000000FF4E5F728000000000FF1443770000000000FA,
    ...
}
```
### View the Region size

Use the `size` command to view the Region size:

```shell
tikv-ctl --data-dir /path/to/tikv size -r 2
```

The output is as follows:

```
region id: 2
cf default region size: 799.703 MB
cf write region size: 41.250 MB
cf lock region size: 27616
```
### Scan to view MVCC of a specific range

The `--from` and `--to` options of the `scan` command accept two escaped forms of raw key, and use the `--show-cf` flag to specify the column families that you need to view.

```shell
tikv-ctl --data-dir /path/to/tikv scan --from 'zm' --limit 2 --show-cf lock,default,write
```

```
key: zmBootstr\377a\377pKey\000\000\377\000\000\373\000\000\000\000\000\377\000\000s\000\000\000\000\000\372
         write cf value: start_ts: 399650102814441473 commit_ts: 399650102814441475 short_value: "20"
key: zmDB:29\000\000\377\000\374\000\000\000\000\000\000\377\000H\000\000\000\000\000\000\371
         write cf value: start_ts: 399650105239273474 commit_ts: 399650105239273475 short_value: "\000\000\000\000\000\000\000\002"
         write cf value: start_ts: 399650105199951882 commit_ts: 399650105213059076 short_value: "\000\000\000\000\000\000\000\001"
```
### View MVCC of a given key

Similar to the `scan` command, the `mvcc` command can be used to view MVCC of a given key.

```shell
tikv-ctl --data-dir /path/to/tikv mvcc -k "zmDB:29\000\000\377\000\374\000\000\000\000\000\000\377\000H\000\000\000\000\000\000\371" --show-cf=lock,write,default
```

```
key: zmDB:29\000\000\377\000\374\000\000\000\000\000\000\377\000H\000\000\000\000\000\000\371
         write cf value: start_ts: 399650105239273474 commit_ts: 399650105239273475 short_value: "\000\000\000\000\000\000\000\002"
         write cf value: start_ts: 399650105199951882 commit_ts: 399650105213059076 short_value: "\000\000\000\000\000\000\000\001"
```

In this command, the key is also the escaped form of raw key.
