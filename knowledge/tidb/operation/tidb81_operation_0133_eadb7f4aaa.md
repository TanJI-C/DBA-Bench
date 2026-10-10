# Planned DR switchover for user tables and PD leaders

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dr-multi-replica.md`
- Source Title: `DR Solution Based on Multiple Replicas in a Single Cluster`
- Source Heading Path: `DR Solution Based on Multiple Replicas in a Single Cluster > Perform a DR switchover | DR Solution Based on Multiple Replicas in a Single Cluster > Perform a DR switchover > Planned switchover`
- Source Line Ranges: `161-189`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `sql`, `tikv`
- Topic Tags: `disaster-recovery`, `switchover`, `planned-switchover`, `placement-policy`, `leader-transfer`, `pd-leader`, `grafana`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0133_eadb7f4aaa`
- Source ID: `tidb-docs-8.1:dr-multi-replica.md#perform-a-dr-switchover`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1930913ea45c75daf88841975e422f9514c4a255d30c97bab8d6c6b626177bda`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dr-multi-replica#perform-a-dr-switchover
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dr-multi-replica.md

## Retrieval Guidance

- Use When: Use this when looking for the documented planned DR switchover procedure that moves user table leaders and PD leaders from the primary region to the secondary region.
- Retrieval Keywords: planned switchover, Perform a DR switchover, secondary_rule_for_region2, ALTER TABLE tpcc.warehouse PLACEMENT POLICY=secondary_rule_for_region2, ALTER TABLE tpcc.district PLACEMENT POLICY=secondary_rule_for_region2, pd member leader_priority pd-1 2, pd member leader_priority pd-2 1, pd member leader_priority pd-3 4, pd member leader_priority pd-4 3, Grafana, leaders transferred to the target region
- Follow-up Guidance: The source says to observe PD and TiKV nodes in Grafana and ensure that leaders of the PD and user tables have been transferred to the target region.
- Classification Note: Classified as operation because the content describes a scheduled switchover procedure using placement policy changes and PD leader priority adjustments.

## Official Source Content

## Perform a DR switchover

This section describes how to perform a DR switchover, including planned switchover and unplanned switchover.
### Planned switchover

A planned switchover is a scheduled switchover between the primary and secondary regions based on the maintenance needs. It can be used to verify whether the DR system works properly. This section describes how to perform a planned switchover.

1. Run the following command to switch all user tables and PD leaders to region 2:

    ```sql
    -- Apply the rule secondary_rule_for_region2 to the corresponding user tables.
    ALTER TABLE tpcc.warehouse PLACEMENT POLICY=secondary_rule_for_region2;
    ALTER TABLE tpcc.district PLACEMENT POLICY=secondary_rule_for_region2;
    ```

    Note: You can modify the database name, table name, and placement rule name as needed.

    Run the following commands to lower the priority of PD nodes in region 1 and increase that of PD nodes in region 2.

    ``` shell
    tiup ctl:v6.4.0 pd member leader_priority pd-1 2
    tiup ctl:v6.4.0 pd member leader_priority pd-2 1
    tiup ctl:v6.4.0 pd member leader_priority pd-3 4
    tiup ctl:v6.4.0 pd member leader_priority pd-4 3
    ```

2. Observe the PD and TiKV nodes in Grafana and ensure that leaders of the PD and user tables have been transferred to the target region. The steps for switching back to the original region are the same as the preceding steps and are therefore not covered in this document.
