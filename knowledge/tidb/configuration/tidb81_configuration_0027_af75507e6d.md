# Manage placement rule bundles and apply typical rule scenarios

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/configure-placement-rules.md`
- Source Title: `Placement Rules`
- Source Heading Path: `Placement Rules > Configure rules > Use pd-ctl to batch update groups and rules in groups | Placement Rules > Configure rules > Use pd-ctl to view and modify all configurations | Placement Rules > Configure rules > Use tidb-ctl to query the table-related key range | Placement Rules > Typical usage scenarios | Placement Rules > Typical usage scenarios > Scenario 1: Use three replicas for normal tables and five replicas for the metadata to improve cluster disaster tolerance | Placement Rules > Typical usage scenarios > Scenario 2: Place five replicas in three data centers in the proportion of 2:2:1, and the Leader should not be in the third data center | Placement Rules > Typical usage scenarios > Scenario 3: Add two TiFlash replicas for a table | Placement Rules > Typical usage scenarios > Scenario 4: Add two follower replicas for a table in the Beijing node with high-performance disks | Placement Rules > Typical usage scenarios > Scenario 5: Migrate a table to the nodes with SSD disks`
- Source Line Ranges: `250-492`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tiup`, `tidb`, `tiflash`, `tikv`
- Topic Tags: `placement-rules`, `pd-ctl`, `rule-bundle`, `batch-update`, `configuration-files`, `tidb-ctl`, `keyrange`, `metadata-range`, `replicas`, `label-constraints`, `tiflash-replicas`, `follower-replicas`, `override-rules`, `table-migration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0027_af75507e6d`
- Source ID: `tidb-docs-8.1:configure-placement-rules.md#use-pd-ctl-to-batch-update-groups-and-rules-in-groups`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f97d1cb6ea361aa8769fc22fb6d42c586aa9db7899bc577b5b68090b6d03ad7b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/configure-placement-rules#use-pd-ctl-to-batch-update-groups-and-rules-in-groups
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/configure-placement-rules.md

## Retrieval Guidance

- Use When: Use this chunk when you need commands and examples for managing PD placement rule bundles, querying table key ranges with tidb-ctl, or applying common placement rule scenarios such as metadata replicas, zone-based replica distribution, TiFlash replicas, follower replicas, or SSD override rules.
- Retrieval Keywords: pd-ctl config placement-rules rule-bundle get pd, pd-ctl config placement-rules rule-bundle set pd --in="group.json", pd-ctl config placement-rules rule-bundle load --out="rules.json", pd-ctl config placement-rules rule-bundle save --in="rules.json", tidb-ctl keyrange --database test --table ttt --encode, keyrange, rule-bundle, group_id, group_override, start_key, end_key, label_constraints, location_labels, Scenario 1 metadata count 5, Scenario 2 zone1 zone2 zone3 follower, Scenario 3 engine tiflash learner count 2, Scenario 4 follower-read bj1 bj2 nvme, Scenario 5 ssd-override override true index 1024
- Follow-up Guidance: The content notes that DDL and other operations can cause table ID changes, so the corresponding rules need to be updated at the same time.
- Classification Note: This is classified as configuration for PD because it centers on placement rule definitions and rule-bundle operations, with related examples involving TiDB, TiFlash, TiKV, TiUP, and tidb-ctl.

## Official Source Content

### Use pd-ctl to batch update groups and rules in groups

To view and modify the rule groups and all rules in the groups at the same time, execute the `rule-bundle` subcommand.

In this subcommand, `get {group_id}` is used to query a group, and the output result shows the rule group and rules of the group in a nested form:

```bash
pd-ctl config placement-rules rule-bundle get pd
```

The output of the above command:

```json
{
  "group_id": "pd",
  "group_index": 0,
  "group_override": false,
  "rules": [
    {
      "group_id": "pd",
      "id": "default",
      "start_key": "",
      "end_key": "",
      "role": "voter",
      "count": 3
    }
  ]
}
```

To write the output to a file, add the `--out` argument to the `rule-bundle get` subcommand, which is convenient for subsequent modification and saving.

```bash
pd-ctl config placement-rules rule-bundle get pd --out="group.json"
```

After the modification is finished, you can use the `rule-bundle set` subcommand to save the configuration in the file to the PD server. Unlike the `save` command described in [Set rules using pd-ctl](#set-rules-using-pd-ctl), this command replaces all the rules of this group on the server side.

```bash
pd-ctl config placement-rules rule-bundle set pd --in="group.json"
```
### Use pd-ctl to view and modify all configurations

You can also view and modify all configuration using pd-ctl. To do that, save all configuration to a file, edit the configuration file, and then save the file to the PD server to overwrite the previous configuration. This operation also uses the `rule-bundle` subcommand.

For example, to save all configuration to the `rules.json` file, execute the following command:

```bash
pd-ctl config placement-rules rule-bundle load --out="rules.json"
```

After editing the file, execute the following command to save the configuration to the PD server:

```bash
pd-ctl config placement-rules rule-bundle save --in="rules.json"
```
### Use tidb-ctl to query the table-related key range

If you need special configuration for metadata or a specific table, you can execute the [`keyrange` command](https://github.com/pingcap/tidb-ctl/blob/master/doc/tidb-ctl_keyrange.md) in [tidb-ctl](https://github.com/pingcap/tidb-ctl) to query related keys. Remember to add `--encode` at the end of the command.

```bash
tidb-ctl keyrange --database test --table ttt --encode
```

```text
global ranges:
  meta: (6d00000000000000f8, 6e00000000000000f8)
  table: (7400000000000000f8, 7500000000000000f8)
table ttt ranges: (NOTE: key range might be changed after DDL)
  table: (7480000000000000ff2d00000000000000f8, 7480000000000000ff2e00000000000000f8)
  table indexes: (7480000000000000ff2d5f690000000000fa, 7480000000000000ff2d5f720000000000fa)
    index c2: (7480000000000000ff2d5f698000000000ff0000010000000000fa, 7480000000000000ff2d5f698000000000ff0000020000000000fa)
    index c3: (7480000000000000ff2d5f698000000000ff0000020000000000fa, 7480000000000000ff2d5f698000000000ff0000030000000000fa)
    index c4: (7480000000000000ff2d5f698000000000ff0000030000000000fa, 7480000000000000ff2d5f698000000000ff0000040000000000fa)
  table rows: (7480000000000000ff2d5f720000000000fa, 7480000000000000ff2e00000000000000f8)
```

> **Note:**
>
> DDL and other operations can cause table ID changes, so you need to update the corresponding rules at the same time.
## Typical usage scenarios

This section introduces the typical usage scenarios of Placement Rules.
### Scenario 1: Use three replicas for normal tables and five replicas for the metadata to improve cluster disaster tolerance

You only need to add a rule that limits the key range to the range of metadata, and set the value of `count` to `5`. Here is an example of this rule:

```json
{
  "group_id": "pd",
  "id": "meta",
  "index": 1,
  "override": true,
  "start_key": "6d00000000000000f8",
  "end_key": "6e00000000000000f8",
  "role": "voter",
  "count": 5,
  "location_labels": ["zone", "rack", "host"]
}
```
### Scenario 2: Place five replicas in three data centers in the proportion of 2:2:1, and the Leader should not be in the third data center

Create three rules. Set the number of replicas to `2`, `2`, and `1` respectively. Limit the replicas to the corresponding data centers through `label_constraints` in each rule. In addition, change `role` to `follower` for the data center that does not need a Leader.

```json
[
    {
        "group_id": "pd",
        "id": "zone1",
        "start_key": "",
        "end_key": "",
        "role": "voter",
        "count": 2,
        "label_constraints": [
            {"key": "zone", "op": "in", "values": ["zone1"]}
        ],
        "location_labels": ["rack", "host"]
    },
    {
        "group_id": "pd",
        "id": "zone2",
        "start_key": "",
        "end_key": "",
        "role": "voter",
        "count": 2,
        "label_constraints": [
            {"key": "zone", "op": "in", "values": ["zone2"]}
        ],
        "location_labels": ["rack", "host"]
    },
    {
        "group_id": "pd",
        "id": "zone3",
        "start_key": "",
        "end_key": "",
        "role": "follower",
        "count": 1,
        "label_constraints": [
            {"key": "zone", "op": "in", "values": ["zone3"]}
        ],
        "location_labels": ["rack", "host"]
    }
]
```
### Scenario 3: Add two TiFlash replicas for a table

Add a separate rule for the row key of the table and limit `count` to `2`. Use `label_constraints` to ensure that the replicas are generated on the node of `engine = tiflash`. Note that a separate `group_id` is used here to ensure that this rule does not overlap or conflict with rules from other sources in the system.

```json
{
  "group_id": "tiflash",
  "id": "learner-replica-table-ttt",
  "start_key": "7480000000000000ff2d5f720000000000fa",
  "end_key": "7480000000000000ff2e00000000000000f8",
  "role": "learner",
  "count": 2,
  "label_constraints": [
    {"key": "engine", "op": "in", "values": ["tiflash"]}
  ],
  "location_labels": ["host"]
}
```
### Scenario 4: Add two follower replicas for a table in the Beijing node with high-performance disks

The following example shows a more complicated `label_constraints` configuration. In this rule, the replicas must be placed in the `bj1` or `bj2` machine room, and the disk type must be `nvme`.

```json
{
  "group_id": "follower-read",
  "id": "follower-read-table-ttt",
  "start_key": "7480000000000000ff2d00000000000000f8",
  "end_key": "7480000000000000ff2e00000000000000f8",
  "role": "follower",
  "count": 2,
  "label_constraints": [
    {"key": "zone", "op": "in", "values": ["bj1", "bj2"]},
    {"key": "disk", "op": "in", "values": ["nvme"]}
  ],
  "location_labels": ["host"]
}
```
### Scenario 5: Migrate a table to the nodes with SSD disks

Different from scenario 3, this scenario is not to add new replica(s) on the basis of the existing configuration, but to forcibly override the other configuration of a data range. So you need to specify an `index` value large enough and set `override` to `true` in the rule group configuration to override the existing rule.

The rule:

```json
{
  "group_id": "ssd-override",
  "id": "ssd-table-45",
  "start_key": "7480000000000000ff2d5f720000000000fa",
  "end_key": "7480000000000000ff2e00000000000000f8",
  "role": "voter",
  "count": 3,
  "label_constraints": [
    {"key": "disk", "op": "in", "values": ["ssd"]}
  ],
  "location_labels": ["rack", "host"]
}
```

The rule group:

```json
{
  "id": "ssd-override",
  "index": 1024,
  "override": true,
}
```
