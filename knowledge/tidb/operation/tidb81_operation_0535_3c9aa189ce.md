# Force upgrade by skipping leader transfer and eviction

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/upgrade-tidb-using-tiup.md`
- Source Title: `Upgrade TiDB Using TiUP`
- Source Heading Path: `Upgrade TiDB Using TiUP > FAQ > The evict leader has waited too long during the upgrade. How to skip this step for a quick upgrade?`
- Source Line Ranges: `355-364`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `pd`, `tikv`, `tidb`
- Topic Tags: `upgrade`, `force-upgrade`, `leader-transfer`, `leader-eviction`, `restart`, `faq`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0535_3c9aa189ce`
- Source ID: `tidb-docs-8.1:upgrade-tidb-using-tiup.md#the-evict-leader-has-waited-too-long-during-the-upgrade-how-to-skip-this-step-for-a-quick-upgrade`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2b69b07f229397cab0aed229802effd01c711621799a854bfe0c2769990cd2f0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/upgrade-tidb-using-tiup#the-evict-leader-has-waited-too-long-during-the-upgrade-how-to-skip-this-step-for-a-quick-upgrade
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/upgrade-tidb-using-tiup.md

## Retrieval Guidance

- Use When: Use this chunk when asking how to skip the PD leader transfer and TiKV leader eviction steps during a TiUP cluster upgrade because evict leader is waiting too long.
- Retrieval Keywords: tiup cluster upgrade <cluster-name> <version> --force, --force, evict leader has waited too long, skip leader transfer, skip leader eviction, transferring PD leader, evicting TiKV leader, cluster is directly restarted to update the version, quick upgrade
- Follow-up Guidance: The content notes that using --force skips transferring PD leader and evicting TiKV leader, and directly restarts the cluster to update the version, which has a great impact on the cluster that runs online.
- Classification Note: This is an operation-focused FAQ item for the self-managed TiUP upgrade flow involving TiUP, PD, TiKV, and TiDB.

## Official Source Content

### The evict leader has waited too long during the upgrade. How to skip this step for a quick upgrade?

You can specify `--force`. Then the processes of transferring PD leader and evicting TiKV leader are skipped during the upgrade. The cluster is directly restarted to update the version, which has a great impact on the cluster that runs online. In the following command, `<version>` is the version to upgrade to, such as `v8.1.2`.

```shell
tiup cluster upgrade <cluster-name> <version> --force
```
