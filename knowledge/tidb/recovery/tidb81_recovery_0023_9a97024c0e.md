# Rebuild primary and secondary clusters after switchover

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dr-secondary-cluster.md`
- Source Title: `DR Solution Based on Primary and Secondary Clusters`
- Source Heading Path: `DR Solution Based on Primary and Secondary Clusters > Set up primary and secondary clusters based on TiCDC > Perform DR switchover > Rebuild the primary and secondary clusters`
- Source Line Ranges: `362-375`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `ticdc`
- Topic Tags: `disaster-recovery`, `cluster-rebuild`, `switchover`, `data-consistency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0023_9a97024c0e`
- Source ID: `tidb-docs-8.1:dr-secondary-cluster.md#rebuild-the-primary-and-secondary-clusters`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `01ff0b55ffd221091217813f055c93a940ac5a7d85b0dd03b235839f105dad6a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dr-secondary-cluster#rebuild-the-primary-and-secondary-clusters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dr-secondary-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when asking how to rebuild the DR setup after a switchover or after the primary cluster disaster is resolved or cannot be recovered temporarily.
- Retrieval Keywords: Rebuild the primary and secondary clusters, rebuild DR cluster, deploy a new cluster, new DR system, Set up primary and secondary clusters, Replicate data from the primary cluster to the secondary cluster, Primary and secondary switchover, data inconsistency between the primary and secondary clusters
- Follow-up Guidance: The source points to Set up primary and secondary clusters, Replicate data from the primary cluster to the secondary cluster, and Primary and secondary switchover for the detailed rebuild flow.
- Classification Note: This is classified as recovery because the content describes rebuilding the primary and secondary clusters to restore DR reliability after a disaster or switchover.

## Official Source Content

#### Rebuild the primary and secondary clusters

After the disaster encountered by the primary cluster is resolved or the primary cluster cannot be recovered temporarily, the TiDB cluster is fragile because only the secondary cluster is in service as the primary cluster. To maintain the reliability of the system, you need to rebuild the DR cluster.

To rebuild the TiDB primary and secondary clusters, you can deploy a new cluster to form a new DR system. For details, see the following documents:

- [Set up primary and secondary clusters](#set-up-primary-and-secondary-clusters-based-on-ticdc)
- [Replicate data from the primary cluster to the secondary cluster](#replicate-data-from-the-primary-cluster-to-the-secondary-cluster)
- After the preceding steps are completed, to make the new primary cluster, see [Primary and secondary switchover](#planned-primary-and-secondary-switchover).

> **Note:**
>
> If data inconsistency between the primary and secondary clusters can be resolved, you can use the repaired cluster to rebuild the DR system instead of deploying a new cluster.
