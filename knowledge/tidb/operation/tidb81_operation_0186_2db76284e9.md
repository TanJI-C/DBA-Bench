# PD-CTL operator, ping, and region inspection commands

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pd-control.md`
- Source Title: `PD Control User Guide`
- Source Heading Path: `PD Control User Guide > Command > `operator [check | show | add | remove]` | PD Control User Guide > Command > `ping` | PD Control User Guide > Command > `region <region_id> [--jq="<query string>"]` | PD Control User Guide > Command > `region key [--format=raw|encode|hex] <key>` | PD Control User Guide > Command > `region scan` | PD Control User Guide > Command > `region sibling <region_id>` | PD Control User Guide > Command > `region keys [--format=raw|encode|hex] <start_key> <end_key> <limit>` | PD Control User Guide > Command > `region store <store_id>` | PD Control User Guide > Command > `region topread [limit]` | PD Control User Guide > Command > `region topwrite [limit]` | PD Control User Guide > Command > `region topconfver [limit]` | PD Control User Guide > Command > `region topversion [limit]` | PD Control User Guide > Command > `region topsize [limit]` | PD Control User Guide > Command > `region check [miss-peer | extra-peer | down-peer | pending-peer | offline-peer | empty-region | hist-size | hist-keys] [--jq="<query string>"]``
- Source Line Ranges: `477-762`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`
- Topic Tags: `pd-ctl`, `operator`, `ping`, `region`, `region-scan`, `region-keys`, `hot-regions`, `abnormal-regions`, `jq`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0186_2db76284e9`
- Source ID: `tidb-docs-8.1:pd-control.md#operator-check-show-add-remove`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9fa8fdbef4bf0ea7a5bb2e4bf597ec8dbcfe34a6a1a39807a0f1224c6f1f3b64`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pd-control#operator-check-show-add-remove
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pd-control.md

## Retrieval Guidance

- Use When: Use this chunk when looking for pd-ctl commands to inspect Region information, query Regions by key or store, list hot or abnormal Regions, measure PD ping time, or view and control scheduling operators.
- Retrieval Keywords: operator show, operator add add-peer, operator add add-learner, operator add remove-peer, operator add transfer-leader, operator add transfer-region, operator add transfer-peer, operator add merge-region, operator add split-region --policy=approximate, operator add split-region --policy=scan, operator remove, operator check, ping, region <region_id>, region key --format=raw|encode|hex, region scan, region sibling, region keys, region store, region topread, region topwrite, region topconfver, region topversion, region topsize, region check miss-peer, region check extra-peer, region check down-peer, region check pending-peer, region check offline-peer, region check empty-region, region check hist-size, region check hist-keys, jq formatted output
- Follow-up Guidance: The content also points to jq-formatted JSON output usage for `region` and `region check` commands and explains the difference between `split-region` policies `scan` and `approximate`.
- Classification Note: This is classified as operation content because it documents pd-ctl command usage for viewing status, inspecting Regions, checking abnormal conditions, and controlling scheduling operations.

## Official Source Content

### `operator [check | show | add | remove]`

Use this command to view and control the scheduling operation.

Usage:

```bash
>> operator show                                        // Display all operators
>> operator show admin                                  // Display all admin operators
>> operator show leader                                 // Display all leader operators
>> operator show region                                 // Display all Region operators
>> operator add add-peer 1 2                            // Add a replica of Region 1 on store 2
>> operator add add-learner 1 2                         // Add a learner replica of Region 1 on store 2
>> operator add remove-peer 1 2                         // Remove a replica of Region 1 on store 2
>> operator add transfer-leader 1 2                     // Schedule the leader of Region 1 to store 2
>> operator add transfer-region 1 2 3 4                 // Schedule Region 1 to stores 2,3,4
>> operator add transfer-peer 1 2 3                     // Schedule the replica of Region 1 on store 2 to store 3
>> operator add merge-region 1 2                        // Merge Region 1 with Region 2
>> operator add split-region 1 --policy=approximate     // Split Region 1 into two Regions in halves, based on approximately estimated value
>> operator add split-region 1 --policy=scan            // Split Region 1 into two Regions in halves, based on accurate scan value
>> operator remove 1                                    // Remove the scheduling operation of Region 1
>> operator check 1                                     // Check the status of the operators related to Region 1
```

The splitting of Regions starts from the position as close as possible to the middle. You can locate this position using two strategies, namely "scan" and "approximate". The difference between them is that the former determines the middle key by scanning the Region, and the latter obtains the approximate position by checking the statistics recorded in the SST file. Generally, the former is more accurate, while the latter consumes less I/O and can be completed faster.
### `ping`

Use this command to view the time that `ping` PD takes.

Usage:

```bash
>> ping
time: 43.12698ms
```
### `region <region_id> [--jq="<query string>"]`

Use this command to view the Region information. For a jq formatted output, see [jq-formatted-json-output-usage](#jq-formatted-json-output-usage).

Usage:

```bash
>> region                               //　Display the information of all Regions
{
  "count": 1,
  "regions": [......]
}

>> region 2                             // Display the information of the Region with the ID of 2
{
  "id": 2,
  "start_key": "7480000000000000FF1D00000000000000F8",
  "end_key": "7480000000000000FF1F00000000000000F8",
  "epoch": {
    "conf_ver": 1,
    "version": 15
  },
  "peers": [
    {
      "id": 40,
      "store_id": 3
    }
  ],
  "leader": {
    "id": 40,
    "store_id": 3
  },
  "written_bytes": 0,
  "read_bytes": 0,
  "written_keys": 0,
  "read_keys": 0,
  "approximate_size": 1,
  "approximate_keys": 0
}
```
### `region key [--format=raw|encode|hex] <key>`

Use this command to query the Region that a specific key resides in. It supports the raw, encoding, and hex formats. And you need to use single quotes around the key when it is in the encoding format.

Hex format usage (default):

```bash
>> region key 7480000000000000FF1300000000000000F8
{
  "region": {
    "id": 2,
    ......
  }
}
```

Raw format usage:

```bash
>> region key --format=raw abc
{
  "region": {
    "id": 2,
    ......
  }
}
```

Encoding format usage:

```bash
>> region key --format=encode 't\200\000\000\000\000\000\000\377\035_r\200\000\000\000\000\377\017U\320\000\000\000\000\000\372'
{
  "region": {
    "id": 2,
    ......
  }
}
```
### `region scan`

Use this command to get all Regions.

Usage:

```bash
>> region scan
{
  "count": 20,
  "regions": [......],
}
```
### `region sibling <region_id>`

Use this command to check the adjacent Regions of a specific Region.

Usage:

```bash
>> region sibling 2
{
  "count": 2,
  "regions": [......],
}
```
### `region keys [--format=raw|encode|hex] <start_key> <end_key> <limit>`

Use this command to query all Regions in a given range `[startkey, endkey)`. Ranges without `endKey`s are supported.

The `limit` parameter limits the number of keys. The default value of `limit` is `16`, and the value of `-1` means unlimited keys.

Usage:

```bash
>> region keys --format=raw a         // Display all Regions that start from the key a with a default limit count of 16
{
  "count": 16,
  "regions": [......],
}

>> region keys --format=raw a z      // Display all Regions in the range [a, z) with a default limit count of 16
{
  "count": 16,
  "regions": [......],
}

>> region keys --format=raw a z -1   // Display all Regions in the range [a, z) without a limit count
{
  "count": ...,
  "regions": [......],
}

>> region keys --format=raw a "" 20   // Display all Regions that start from the key a with a limit count of 20
{
  "count": 20,
  "regions": [......],
}
```
### `region store <store_id>`

Use this command to list all Regions of a specific store.

Usage:

```bash
>> region store 2
{
  "count": 10,
  "regions": [......],
}
```
### `region topread [limit]`

Use this command to list Regions with top read flow. The default value of the limit is 16.

Usage:

```bash
>> region topread
{
  "count": 16,
  "regions": [......],
}
```
### `region topwrite [limit]`

Use this command to list Regions with top write flow. The default value of the limit is 16.

Usage:

```bash
>> region topwrite
{
  "count": 16,
  "regions": [......],
}
```
### `region topconfver [limit]`

Use this command to list Regions with top conf version. The default value of the limit is 16.

Usage:

```bash
>> region topconfver
{
  "count": 16,
  "regions": [......],
}
```
### `region topversion [limit]`

Use this command to list Regions with top version. The default value of the limit is 16.

Usage:

```bash
>> region topversion
{
  "count": 16,
  "regions": [......],
}
```
### `region topsize [limit]`

Use this command to list Regions with top approximate size. The default value of the limit is 16.

Usage:

```bash
>> region topsize
{
  "count": 16,
  "regions": [......],
}

```
### `region check [miss-peer | extra-peer | down-peer | pending-peer | offline-peer | empty-region | hist-size | hist-keys] [--jq="<query string>"]`

Use this command to check the Regions in abnormal conditions. For a jq formatted output, see [jq formatted JSON output usage](#jq-formatted-json-output-usage).

Description of various types:

- miss-peer: the Region without enough replicas
- extra-peer: the Region with extra replicas
- down-peer: the Region in which some replicas are Down
- pending-peer: the Region in which some replicas are Pending

Usage:

```bash
>> region check miss-peer
{
  "count": 2,
  "regions": [......],
}
```
