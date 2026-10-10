# PD Recover FAQ and common execution issues

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pd-recover.md`
- Source Title: `PD Recover User Guide`
- Source Heading Path: `PD Recover User Guide > FAQ | PD Recover User Guide > FAQ > Multiple cluster IDs are found when getting the cluster ID | PD Recover User Guide > FAQ > The error `dial tcp 10.0.1.13:2379: connect: connection refused` is returned when executing `pd-recover``
- Source Line Ranges: `159-167`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: none
- Topic Tags: `faq`, `cluster-id`, `connection-refused`, `prerequisites`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0060_2a2b595f6a`
- Source ID: `tidb-docs-8.1:pd-recover.md#faq`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2cebfbfd157a08cef6a54c224a4feb6c3a96365f7254f043b890db6158112018`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pd-recover#faq
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pd-recover.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing PD Recover FAQ issues such as multiple cluster IDs in logs or `connect: connection refused` while executing `pd-recover`.
- Retrieval Keywords: FAQ, Multiple cluster IDs are found when getting the cluster ID, cluster ID of the old cluster, viewing the log, dial tcp 10.0.1.13:2379: connect: connection refused, pd-recover, PD service is required, Deploy and start the PD cluster before you use PD Recover
- Follow-up Guidance: The source states that the PD service is required when you execute `pd-recover`, so the PD cluster must be deployed and started before using PD Recover.
- Classification Note: This is diagnosis content because it addresses common execution issues and clarifies prerequisites and log interpretation for PD Recover.

## Official Source Content

## FAQ
### Multiple cluster IDs are found when getting the cluster ID

When a PD cluster is created, a new cluster ID is generated. You can determine the cluster ID of the old cluster by viewing the log.
### The error `dial tcp 10.0.1.13:2379: connect: connection refused` is returned when executing `pd-recover`

The PD service is required when you execute `pd-recover`. Deploy and start the PD cluster before you use PD Recover.
