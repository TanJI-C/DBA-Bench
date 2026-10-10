# TIKV_REGION_PEERS table schema, example query, and field definitions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-tikv-region-peers.md`
- Source Title: `TIKV_REGION_PEERS`
- Source Heading Path: `TIKV_REGION_PEERS`
- Source Line Ranges: `5-64`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `sql`, `tidb`, `cloud`
- Topic Tags: `information_schema`, `region`, `peer`, `leader`, `learner`, `store`, `schema`, `sql`, `status`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0427_a76594bb4e`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-tikv-region-peers.md#tikv-region-peers`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4293c692410fb2c8fdc61cd9462671af62154b02e21a0e4bc4f81a37476cc161`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tikv-region-peers#tikv-region-peers
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-tikv-region-peers.md

## Retrieval Guidance

- Use When: Use this chunk when you need the INFORMATION_SCHEMA.TIKV_REGION_PEERS schema, field meanings, peer status values, or the example SQL that joins Region peers with TIKV_STORE_STATUS and tikv_region_status.
- Retrieval Keywords: TIKV_REGION_PEERS, INFORMATION_SCHEMA, DESC TIKV_REGION_PEERS, REGION_ID, PEER_ID, STORE_ID, IS_LEARNER, IS_LEADER, STATUS, DOWN_SECONDS, PENDING, DOWN, NORMAL, TIKV_STORE_STATUS, tikv_region_status, written_bytes, top 3 Regions with the maximum value of WRITTEN_BYTES, peer.is_leader = 1, region.region_id = peer.region_id, peer.store_id = tikv.store_id
- Follow-up Guidance: The source includes an example query that retrieves the TiKV addresses for the top 3 Regions by WRITTEN_BYTES by joining TIKV_REGION_PEERS, TIKV_STORE_STATUS, and tikv_region_status.
- Classification Note: This is reference content because it defines the TIKV_REGION_PEERS table schema, lists each field and status meaning, and provides a sample SQL query.

## Official Source Content

# TIKV_REGION_PEERS

The `TIKV_REGION_PEERS` table shows detailed information of a single Region node in TiKV, such as whether it is a learner or leader.

> **Note:**
>
> This table is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

```sql
USE INFORMATION_SCHEMA;
DESC TIKV_REGION_PEERS;
```

The output is as follows:

```sql
+--------------+-------------+------+------+---------+-------+
| Field        | Type        | Null | Key  | Default | Extra |
+--------------+-------------+------+------+---------+-------+
| REGION_ID    | bigint(21)  | YES  |      | NULL    |       |
| PEER_ID      | bigint(21)  | YES  |      | NULL    |       |
| STORE_ID     | bigint(21)  | YES  |      | NULL    |       |
| IS_LEARNER   | tinyint(1)  | NO   |      | 0       |       |
| IS_LEADER    | tinyint(1)  | NO   |      | 0       |       |
| STATUS       | varchar(10) | YES  |      | 0       |       |
| DOWN_SECONDS | bigint(21)  | YES  |      | 0       |       |
+--------------+-------------+------+------+---------+-------+
7 rows in set (0.01 sec)
```

For example, you can query the specific TiKV addresses for the top 3 Regions with the maximum value of `WRITTEN_BYTES` using the following SQL statement:

```sql
SELECT
  address,
  tikv.address,
  region.region_id
FROM
  TIKV_STORE_STATUS tikv,
  TIKV_REGION_PEERS peer,
  (SELECT * FROM tikv_region_status ORDER BY written_bytes DESC LIMIT 3) region
WHERE
  region.region_id = peer.region_id
  AND peer.is_leader = 1
  AND peer.store_id = tikv.store_id;
```

Fields in the `TIKV_REGION_PEERS` table are described as follows:

* REGION_ID: The Region ID.
* PEER_ID: The ID of the Region peer.
* STORE_ID: The ID of the TiKV store where the Region is located.
* IS_LEARNER: Whether the peer is learner.
* IS_LEADER: Whether the peer is leader.
* STATUS: The statuses of a peer:
    * PENDING: Temporarily unavailable.
    * DOWN: Offline and converted. This peer no longer provides service.
    * NORMAL: Running normally.
* DOWN_SECONDS: The duration of being offline, in seconds.
