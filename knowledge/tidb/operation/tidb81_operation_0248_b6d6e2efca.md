# Stopping bidirectional replication and documented limitations

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-bidirectional-replication.md`
- Source Title: `Bidirectional Replication`
- Source Heading Path: `Bidirectional Replication > Stop bi-directional replication | Bidirectional Replication > Limitations`
- Source Line Ranges: `140-167`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tidb`
- Topic Tags: `stop replication`, `consistency check`, `unset bdr role`, `limitations`, `auto_increment`, `auto_random`, `write conflicts`, `multi-cluster topology`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0248_b6d6e2efca`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-bidirectional-replication.md#stop-bi-directional-replication`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5833a7fdd2d0041d465980222e140852e61a678293b6f24dded34f3663b7ca7c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-bidirectional-replication#stop-bi-directional-replication
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-bidirectional-replication.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how to stop bidirectional replication safely, how to verify consistency before stopping, or what limitations apply to BDR roles, `AUTO_INCREMENT` or `AUTO_RANDOM`, write conflicts, and multi-cluster topologies.
- Retrieval Keywords: Stop bi-directional replication, special record, data in two clusters are consistent, stop the changefeed, ADMIN UNSET BDR ROLE, Limitations, 1 PRIMARY cluster and n SECONDARY clusters, AUTO_INCREMENT, AUTO_RANDOM, auto_increment_increment, auto_increment_offset, write conflicts, cascading mode, TiDB A -> TiDB B -> TiDB C -> TiDB A
- Follow-up Guidance: The source states that after application writes stop, you can insert a special record into each cluster, verify both special records for consistency, then stop the changefeed and execute `ADMIN UNSET BDR ROLE` on all TiDB clusters.
- Classification Note: This is classified as operation because the content covers the shutdown procedure for bidirectional replication and operational limitations for BDR role usage, key allocation settings, write conflict handling, and supported multi-cluster topology.

## Official Source Content

## Stop bi-directional replication

After the application has stopped writing data, you can insert a special record into each cluster. By checking the two special records, you can make sure that data in two clusters are consistent.

After the check is completed, you can stop the changefeed to stop bi-directional replication, and execute `ADMIN UNSET BDR ROLE` on all TiDB clusters.
## Limitations

- Use BDR role only in the following scenarios:

    - 1 `PRIMARY` cluster and n `SECONDARY` clusters (replication scenarios of replicable DDLs)
    - n clusters that have no BDR roles (replication scenarios in which you can manually execute non-replicable DDLs on each cluster)

    > **Note:**
    >
    > Do not set the BDR role in other scenarios, for example, setting `PRIMARY`, `SECONDARY`, and no BDR roles at the same time. If you set the BDR role incorrectly, TiDB cannot guarantee data correctness and consistency during data replication.

- Usually do not use `AUTO_INCREMENT` or `AUTO_RANDOM` to avoid data conflicts in the replicated tables. If you need to use `AUTO_INCREMENT` or `AUTO_RANDOM`, you can set different `auto_increment_increment` and `auto_increment_offset` for different clusters to ensure that different clusters can be assigned different primary keys. For example, if there are three TiDB clusters (A, B, and C) in bi-directional replication, you can set them as follows:

    - In Cluster A, set `auto_increment_increment=3` and `auto_increment_offset=2000`
    - In Cluster B, set `auto_increment_increment=3` and `auto_increment_offset=2001`
    - In Cluster C, set `auto_increment_increment=3` and `auto_increment_offset=2002`

    This way, A, B, and C will not conflict with each other in the implicitly assigned `AUTO_INCREMENT` ID and `AUTO_RANDOM` ID. If you need to add a cluster in BDR mode, you need to temporarily stop writing data of the related application, set the appropriate values for `auto_increment_increment` and `auto_increment_offset` on all clusters, and then resume writing data of the related application.

- Bi-directional replication clusters cannot detect write conflicts, which might cause undefined behaviors. Therefore, you must ensure that there are no write conflicts from the application side.

- Bi-directional replication supports more than two clusters, but does not support multiple clusters in cascading mode, that is, a cyclic replication like TiDB A -> TiDB B -> TiDB C -> TiDB A. In such a topology, if one cluster fails, the whole data replication will be affected. Therefore, to enable bi-directional replication among multiple clusters, you need to connect each cluster with every other clusters, for example, `TiDB A <-> TiDB B`, `TiDB B <-> TiDB C`, `TiDB C <-> TiDB A`.
