# Jq queries for pd-ctl store and region JSON output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pd-control.md`
- Source Title: `PD Control User Guide`
- Source Heading Path: `PD Control User Guide > Jq formatted JSON output usage | PD Control User Guide > Jq formatted JSON output usage > Simplify the output of `store` | PD Control User Guide > Jq formatted JSON output usage > Query the remaining space of the node | PD Control User Guide > Jq formatted JSON output usage > Query all nodes whose status is not `Up` | PD Control User Guide > Jq formatted JSON output usage > Query all TiFlash nodes | PD Control User Guide > Jq formatted JSON output usage > Query the distribution status of the Region replicas | PD Control User Guide > Jq formatted JSON output usage > Filter Regions according to the number of replicas | PD Control User Guide > Jq formatted JSON output usage > Filter Regions according to the store ID of replicas | PD Control User Guide > Jq formatted JSON output usage > Look for relevant Regions when restoring data`
- Source Line Ranges: `1171-1286`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tiflash`, `tikv`
- Topic Tags: `jq`, `json-output`, `store-query`, `region-query`, `replica-distribution`, `space-usage`, `node-status`, `restore-analysis`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0474_5230ce2871`
- Source ID: `tidb-docs-8.1:pd-control.md#jq-formatted-json-output-usage`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `60100818355a1ff3213c46efb8999b5625f9a3d8df5b3850f2ff7af3da02a0a1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pd-control#jq-formatted-json-output-usage
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pd-control.md

## Retrieval Guidance

- Use When: Use this content when you need example --jq queries against pd-ctl store or region JSON output to inspect node state, available space, TiFlash nodes, replica distribution, or Regions related to restore analysis.
- Retrieval Keywords: --jq, jq formatted JSON output usage, store --jq, .stores[].store | { id, address, state_name}, available: .status.available, select(.state_name!="Up"), engine tiflash, contains([{"key":"engine","value":"tiflash"}]), region --jq, .regions[] | {id: .id, peer_stores: [.peers[].store_id]}, select(length != 3), select(any(.==30)), select(any(.==(30,31))), Look for relevant Regions when restoring data, remove-peer Operator, DownPeer, remaining space of the node, distribution status of the Region replicas
- Follow-up Guidance: The content includes jq examples for filtering Regions by replica count, by replica store IDs, and by conditions used when restoring data or creating a remove-peer Operator.
- Classification Note: This is classified as reference because it provides example jq query patterns for retrieving and filtering pd-ctl JSON output rather than a single operational procedure.

## Official Source Content

## Jq formatted JSON output usage
### Simplify the output of `store`

```bash
>> store --jq=".stores[].store | { id, address, state_name}"
{"id":1,"address":"127.0.0.1:20161","state_name":"Up"}
{"id":30,"address":"127.0.0.1:20162","state_name":"Up"}
...
```
### Query the remaining space of the node

```bash
>> store --jq=".stores[] | {id: .store.id, available: .status.available}"
{"id":1,"available":"10 GiB"}
{"id":30,"available":"10 GiB"}
...
```
### Query all nodes whose status is not `Up`

```bash
store --jq='.stores[].store | select(.state_name!="Up") | { id, address, state_name}'
```

```
{"id":1,"address":"127.0.0.1:20161""state_name":"Offline"}
{"id":5,"address":"127.0.0.1:20162""state_name":"Offline"}
...
```
### Query all TiFlash nodes

```bash
store --jq='.stores[].store | select(.labels | length>0 and contains([{"key":"engine","value":"tiflash"}])) | { id, address, state_name}'
```

```
{"id":1,"address":"127.0.0.1:20161""state_name":"Up"}
{"id":5,"address":"127.0.0.1:20162""state_name":"Up"}
...
```
### Query the distribution status of the Region replicas

```bash
>> region --jq=".regions[] | {id: .id, peer_stores: [.peers[].store_id]}"
{"id":2,"peer_stores":[1,30,31]}
{"id":4,"peer_stores":[1,31,34]}
...
```
### Filter Regions according to the number of replicas

For example, to filter out all Regions whose number of replicas is not 3:

```bash
>> region --jq=".regions[] | {id: .id, peer_stores: [.peers[].store_id] | select(length != 3)}"
{"id":12,"peer_stores":[30,32]}
{"id":2,"peer_stores":[1,30,31,32]}
```
### Filter Regions according to the store ID of replicas

For example, to filter out all Regions that have a replica on store30:

```bash
>> region --jq=".regions[] | {id: .id, peer_stores: [.peers[].store_id] | select(any(.==30))}"
{"id":6,"peer_stores":[1,30,31]}
{"id":22,"peer_stores":[1,30,32]}
...
```

You can also find out all Regions that have a replica on store30 or store31 in the same way:

```bash
>> region --jq=".regions[] | {id: .id, peer_stores: [.peers[].store_id] | select(any(.==(30,31)))}"
{"id":16,"peer_stores":[1,30,34]}
{"id":28,"peer_stores":[1,30,32]}
{"id":12,"peer_stores":[30,32]}
...
```
### Look for relevant Regions when restoring data

For example, when [store1, store30, store31] is unavailable at its downtime, you can find all Regions whose Down replicas are more than normal replicas:

```bash
>> region --jq=".regions[] | {id: .id, peer_stores: [.peers[].store_id] | select(length as $total | map(if .==(1,30,31) then . else empty end) | length>=$total-length) }"
{"id":2,"peer_stores":[1,30,31,32]}
{"id":12,"peer_stores":[30,32]}
{"id":14,"peer_stores":[1,30,32]}
...
```

Or when [store1, store30, store31] fails to start, you can find Regions where the data can be manually removed safely on store1. In this way, you can filter out all Regions that have a replica on store1 but don't have other DownPeers:

```bash
>> region --jq=".regions[] | {id: .id, peer_stores: [.peers[].store_id] | select(length>1 and any(.==1) and all(.!=(30,31)))}"
{"id":24,"peer_stores":[1,32,33]}
```

When [store30, store31] is down, find out all Regions that can be safely processed by creating the `remove-peer` Operator, that is, Regions with one and only DownPeer:

```bash
>> region --jq=".regions[] | {id: .id, remove_peer: [.peers[].store_id] | select(length>1) | map(if .==(30,31) then . else empty end) | select(length==1)}"
{"id":12,"remove_peer":[30]}
{"id":4,"remove_peer":[31]}
{"id":22,"remove_peer":[30]}
...
```
