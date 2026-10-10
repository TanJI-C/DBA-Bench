# TiDB Lightning compatibility with Placement Rules in SQL

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-faq.md`
- Source Title: `TiDB Lightning FAQs`
- Source Heading Path: `TiDB Lightning FAQs > Why is TiDB Lightning not compatible with Placement Rules in SQL?`
- Source Line Ranges: `140-176`
- Source Scope: `shared`
- Primary Component: `lightning`
- Related Components: `pd`, `tikv`, `sql`, `tidb`
- Topic Tags: `placement-rules`, `topology`, `replica-placement`, `policy-creation`, `workaround`, `cluster-labels`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0100_32ca624dad`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-faq.md#why-is-tidb-lightning-not-compatible-with-placement-rules-in-sql`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `258c5fb5d5c559284a118fe6d2788cb217efedaf9a6b4ce45663992c56411c1b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-faq#why-is-tidb-lightning-not-compatible-with-placement-rules-in-sql
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-faq.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks why TiDB Lightning is not compatible with Placement Rules in SQL or how placement policies interact with differing source and target cluster topology during import.
- Retrieval Keywords: TiDB Lightning not compatible with Placement Rules in SQL, placement policies, CREATE PLACEMENT POLICY p1 PRIMARY_REGION="us-east" REGIONS="us-east,us-west";, source cluster and target cluster have different topology, semantics in the target cluster is wrong, does not have the region "us-west" in the topology, related labels and objects have been created in the target TiDB cluster before import, PD and TiKV layer, plan the data distribution topology, configure the required labels for TiKV and PD, create the placement rule policy and apply the created policy to the target table
- Follow-up Guidance: The chunk includes a workaround with four grounded steps: plan the data distribution topology, configure TiKV and PD labels, create and apply the placement policy to the target table, and then import with TiDB Lightning.
- Classification Note: This is classified as architecture because it explains an incompatibility caused by placement-rule semantics across PD, TiKV, and cluster topology rather than a simple command reference.

## Official Source Content

## Why is TiDB Lightning not compatible with Placement Rules in SQL?

TiDB Lightning is not compatible with [Placement Rules in SQL](https://docs.pingcap.com/tidb/stable/placement-rules-in-sql). When TiDB Lightning imports data that contains placement policies, TiDB Lightning reports an error.

The reason is explained as follows:

The purpose of placement rule in SQL is to control the data location of certain TiKV nodes at the table or partition level. TiDB Lightning imports data in text files into the target TiDB cluster. If the data files is exported with the definition of placement rules, during the import process, TiDB Lightning must create the corresponding placement rule policy in the target cluster based on the definition. When the source cluster and the target cluster have different topology, this might cause problems.

Suppose the source cluster has the following topology:

![TiDB Lightning FAQ - source cluster topology](/media/lightning-faq-source-cluster-topology.jpg)

The source cluster has the following placement policy:

```sql
CREATE PLACEMENT POLICY p1 PRIMARY_REGION="us-east" REGIONS="us-east,us-west";
```

**Situation 1:** The target cluster has 3 replicas, and the topology is different from the source cluster. In such cases, when TiDB Lightning creates the placement policy in the target cluster, it will not report an error. However, the semantics in the target cluster is wrong.

![TiDB Lightning FAQ - situation 1](/media/lightning-faq-situation-1.jpg)

**Situation 2:** The target cluster locates the follower replica in another TiKV node in region "us-mid" and does not have the region "us-west" in the topology. In such cases, when creating the placement policy in the target cluster, TiDB Lightning will report an error.

![TiDB Lightning FAQ - situation 2](/media/lightning-faq-situation-2.jpg)

**Workaround:**

To use placement rules in SQL with TiDB Lightning, you need to make sure that the related labels and objects have been created in the target TiDB cluster **before** you import data into the target table. Because the placement rules in SQL acts at the PD and TiKV layer, TiDB Lightning can get the necessary information to find out which TiKV should be used to store the imported data. In this way, this placement rule in SQL is transparent to TiDB Lightning.

The steps are as follows:

1. Plan the data distribution topology.
2. Configure the required labels for TiKV and PD.
3. Create the placement rule policy and apply the created policy to the target table.
4. Use TiDB Lightning to import data into the target table.
