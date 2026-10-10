# Scenario overview, deployment guidance, and import tuning

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/tidb-best-practices.md`
- Source Title: `TiDB Best Practices`
- Source Heading Path: `TiDB Best Practices > Scenarios and practices | TiDB Best Practices > Scenarios and practices > Deployment | TiDB Best Practices > Scenarios and practices > Data import`
- Source Line Ranges: `138-151`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`, `tikv`
- Topic Tags: `deployment`, `software-requirements`, `hardware-requirements`, `cluster-management`, `data-import`, `memory-tuning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0012_64b3a34c86`
- Source ID: `tidb-docs-8.1:best-practices/tidb-best-practices.md#scenarios-and-practices`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f825cd7216155b4356e5a54da6a104f7634a86fec18fab2d089e5cc99ddfae06`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/tidb-best-practices#scenarios-and-practices
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/tidb-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about deployment guidance with TiUP, reading software and hardware requirements before deployment, or tuning TiKV memory parameters to improve data import write performance.
- Retrieval Keywords: Scenarios and practices, Deployment, Data import, Software and Hardware Requirements, TiUP, production deployment using TiUP, manual deploy, Tune TiKV Memory Parameter Performance, write performance during the import process, TiKV memory parameter
- Follow-up Guidance: The source directs readers to `Software and Hardware Requirements`, `production deployment using TiUP`, and `Tune TiKV Memory Parameter Performance` for the related details.
- Classification Note: This is classified as operation for TiUP because the content focuses on deployment method guidance and import-related operational tuning references.

## Official Source Content

## Scenarios and practices

In the last section, we discussed some basic implementation mechanisms of TiDB and their influence on usage. This section introduces specific usage scenarios and operation practices, from deployment to application usage.
### Deployment

Before deployment, read [Software and Hardware Requirements](https://docs.pingcap.com/tidb/stable/hardware-and-software-requirements).

It is recommended to deploy the TiDB cluster using [TiUP](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup). This tool can deploy, stop, destroy, and upgrade the whole cluster, which is quite convenient. It is not recommended to manually deploy the TiDB cluster, which might be troublesome to maintain and upgrade later.
### Data import

To improve the write performance during the import process, you can tune TiKV's parameters as stated in [Tune TiKV Memory Parameter Performance](https://docs.pingcap.com/tidb/stable/tune-tikv-memory-performance).
