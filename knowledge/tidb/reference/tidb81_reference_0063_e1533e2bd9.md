# Placement rules overview and rule model

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/configure-placement-rules.md`
- Source Title: `Placement Rules`
- Source Heading Path: `Placement Rules | Placement Rules > Rule system | Placement Rules > Rule system > Rule fields | Placement Rules > Rule system > Fields of the rule group`
- Source Line Ranges: `5-64`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tidb`, `shared`
- Topic Tags: `placement-rules`, `replica-scheduling`, `rule-groups`, `rule-fields`, `label-constraints`, `topology-labels`, `isolation-level`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0063_e1533e2bd9`
- Source ID: `tidb-docs-8.1:configure-placement-rules.md#placement-rules`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `da439f2df170e25e66e8281a7bb9e5dc3c6376daaa7eeca739573af9f5617667`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/configure-placement-rules#placement-rules
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/configure-placement-rules.md

## Retrieval Guidance

- Use When: Use this content when you need the PD placement rule model, rule matching behavior, or the exact meanings of rule fields and rule group fields.
- Retrieval Keywords: Placement Rules, Rule system, GroupID, ID, Index, Override, StartKey, EndKey, Role, Count, LabelConstraint, LocationLabels, IsolationLevel, rule group, voter, leader, follower, learner, in, notIn, exists, notExists, topology labels, physical isolation, zone rack host
- Follow-up Guidance: The document also points to Cluster topology configuration for more detail on IsolationLevel behavior with topology labels.
- Classification Note: This is reference content because it defines the placement rule system, overlapping rule behavior, group concept, and the field-level semantics for rules and rule groups.

## Official Source Content

# Placement Rules

> **Note:**
>
> This document introduces how to manually specify placement rules in Placement Driver (PD). It is now recommended to use [Placement Rules in SQL](https://docs.pingcap.com/tidb/stable/placement-rules-in-sql). This offers a more convenient way to configure the placement of tables and partitions.

Placement Rules, introduced in v5.0, is a replica rule system that guides PD to generate corresponding schedules for different types of data. By combining different scheduling rules, you can finely control the attributes of any continuous data range, such as the number of replicas, the storage location, the host type, whether to participate in Raft election, and whether to act as the Raft leader.

The Placement Rules feature is enabled by default in v5.0 and later versions of TiDB. To disable it, refer to [Disable Placement Rules](#disable-placement-rules). 
## Rule system

The configuration of the whole rule system consists of multiple rules. Each rule can specify attributes such as the number of replicas, the Raft role, the placement location, and the key range in which this rule takes effect. When PD is performing schedule, it first finds the rule corresponding to the Region in the rule system according to the key range of the Region, and then generates the corresponding schedule to make the distribution of the Region replica comply with the rule.

The key ranges of multiple rules can have overlapping parts, which means that a Region can match multiple rules. In this case, PD decides whether the rules overwrite each other or take effect at the same time according to the attributes of rules. If multiple rules take effect at the same time, PD will generate schedules in sequence according to the stacking order of the rules for rule matching.

In addition, to meet the requirement that rules from different sources are isolated from each other, these rules can be organized in a more flexible way. Therefore, the concept of "Group" is introduced. Generally, users can place rules in different groups according to different sources.

![Placement rules overview](/media/placement-rules-1.png)
### Rule fields

The following table shows the meaning of each field in a rule:

| Field name           | Type and restriction                      | Description                                |
| :---            | :---                           | :---                                |
| `GroupID`         | `string`                         |  The group ID that marks the source of the rule.                |
| `ID`              | `string`                         |  The unique ID of a rule in a group.                        |
| `Index`           | `int`                            |   The stacking sequence of rules in a group.                     |
| `Override`        | `true`/`false`                     | Whether to overwrite rules with smaller index (in a group).  |
| `StartKey`        | `string`, in hexadecimal form                |  Applies to the starting key of a range.                |
| `EndKey`          | `string`, in hexadecimal form                |  Applies to the ending key of a range.                |
| `Role`            | `string` | Replica roles, including voter/leader/follower/learner.                           |
| `Count`           | `int`, positive integer                     |  The number of replicas.                            |
| `LabelConstraint` | `[]Constraint`                    |  Filters nodes based on the label.               |
| `LocationLabels`  | `[]string`                        |  Used for physical isolation.                       |
| `IsolationLevel`  | `string`                          |  Used to set the minimum physical isolation level

`LabelConstraint` is similar to the function in Kubernetes that filters labels based on these four primitives: `in`, `notIn`, `exists`, and `notExists`. The meanings of these four primitives are as follows:

+ `in`: the label value of the given key is included in the given list.
+ `notIn`: the label value of the given key is not included in the given list.
+ `exists`: includes the given label key.
+ `notExists`: does not include the given label key.

The meaning and function of `LocationLabels` are the same with those earlier than v4.0. For example, if you have deployed `[zone,rack,host]` that defines a three-layer topology: the cluster has multiple zones (Availability Zones), each zone has multiple racks, and each rack has multiple hosts. When performing schedule, PD first tries to place the Region's peers in different zones. If this try fails (such as there are three replicas but only two zones in total), PD guarantees to place these replicas in different racks. If the number of racks is not enough to guarantee isolation, then PD tries the host-level isolation.

The meaning and function of `IsolationLevel` is elaborated in [Cluster topology configuration](https://docs.pingcap.com/tidb/stable/schedule-replicas-by-topology-labels). For example, if you have deployed `[zone,rack,host]` that defines a three-layer topology with `LocationLabels` and set `IsolationLevel` to `zone`, then PD ensures that all peers of each Region are placed in different zones during the scheduling. If the minimum isolation level restriction on `IsolationLevel` cannot be met (for example, 3 replicas are configured but there are only 2 data zones in total), PD will not try to make up to meet this restriction. The default value of `IsolationLevel` is an empty string, which means that it is disabled.
### Fields of the rule group

The following table shows the description of each field in a rule group:

| Field name | Type and restriction  | Description |
| :--- | :--- | :--- |
| `ID` | `string` | The group ID that marks the source of the rule. |
| `Index` | `int` | The stacking sequence of different groups. |
| `Override` | `true`/`false` | Whether to override groups with smaller indexes. |
