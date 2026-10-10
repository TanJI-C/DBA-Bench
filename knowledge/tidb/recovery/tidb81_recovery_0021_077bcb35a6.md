# Unplanned DR switchover after region failure

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dr-multi-replica.md`
- Source Title: `DR Solution Based on Multiple Replicas in a Single Cluster`
- Source Heading Path: `DR Solution Based on Multiple Replicas in a Single Cluster > Perform a DR switchover > Unplanned switchover`
- Source Line Ranges: `190-211`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tiup`, `pd`, `tikv`, `tidb`, `sql`
- Topic Tags: `disaster-recovery`, `unplanned-switchover`, `failover`, `region-outage`, `leader-transfer`, `placement-policy`, `service-stop`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0021_077bcb35a6`
- Source ID: `tidb-docs-8.1:dr-multi-replica.md#unplanned-switchover`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6d8aaad74f592d18c52be6cc5365ef7612c492198fe8ed7ae24f4bf2c5b77f94`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dr-multi-replica#unplanned-switchover
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dr-multi-replica.md

## Retrieval Guidance

- Use When: Use this when looking for the official unplanned DR switchover steps after a region failure, including stopping region 1 nodes and transferring user table leaders to region 2.
- Retrieval Keywords: unplanned switchover, region failure, disaster occurs, tiup cluster stop drtest -N, tidb-dr-test1:20160, tidb-dr-test2:20160, tidb-dr-test1:2379, tidb-dr-test2:2379, secondary_rule_for_region2, ALTER TABLE tpcc.warehouse PLACEMENT POLICY=secondary_rule_for_region2, ALTER TABLE tpcc.district PLACEMENT POLICY=secondary_rule_for_region2, SELECT STORE_ID, address, leader_count, label FROM TIKV_STORE_STATUS ORDER BY store_id
- Follow-up Guidance: The source states that after region 1 recovers, you can use similar commands to switch the leaders of user tables back to region 1.
- Classification Note: Classified as recovery because the content covers switchover steps during a disaster scenario and verification of leader transfer after a region outage.

## Official Source Content

### Unplanned switchover

An unplanned switchover means a switchover between primary and secondary regions when a disaster occurs. It can also be a primary-secondary region switchover initiated to simulate disaster scenarios so as to verify the effectiveness of DR systems.

1. Run the following command to stop all TiKV, TiDB, and PD nodes in region 1:

    ``` shell
    tiup cluster stop drtest -N tidb-dr-test1:20160,tidb-dr-test2:20160,tidb-dr-test1:2379,tidb-dr-test2:2379
    ```

2. Run the following commands to switch the leaders of all user tables to region 2:

    ```sql
    -- Apply the rule secondary_rule_for_region2 to the corresponding user tables.
    ALTER TABLE tpcc.warehouse PLACEMENT POLICY=secondary_rule_for_region2;
    ALTER TABLE tpcc.district PLACEMENT POLICY=secondary_rule_for_region2;

    --- Confirm whether the leaders have been transferred by executing the following query to check the number of leaders in each region.
    SELECT STORE_ID, address, leader_count, label FROM TIKV_STORE_STATUS ORDER BY store_id;
    ```

    After region 1 recovers, you can use commands similar to the preceding ones to switch the leaders of user tables back to region 1.
