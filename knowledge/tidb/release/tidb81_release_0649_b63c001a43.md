# Serverless version upgrade behavior FAQ

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-faqs.md`
- Source Title: `TiDB Cloud Serverless FAQs`
- Source Heading Path: `TiDB Cloud Serverless FAQs > Maintenance FAQ | TiDB Cloud Serverless FAQs > Maintenance FAQ > Can I upgrade the version of TiDB that my cluster is running on?`
- Source Line Ranges: `149-153`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`
- Topic Tags: `maintenance`, `version`, `upgrade`, `automatic-upgrades`, `release-notes`, `sql-check`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0649_b63c001a43`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-faqs.md#maintenance-faq`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2064116feaeafc1869a52319a36bcafdddb399276d747b0427b474046cda7e88`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-faqs#maintenance-faq
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-faqs.md

## Retrieval Guidance

- Use When: Use this chunk when answering questions about whether a TiDB Cloud Serverless cluster can be manually upgraded and how to check its TiDB version.
- Retrieval Keywords: Can I upgrade the version of TiDB that my cluster is running on, TiDB Cloud Serverless clusters are upgraded automatically, new TiDB versions on TiDB Cloud, TiDB Cloud console check version, release note, SELECT version(), SELECT tidb_version()
- Follow-up Guidance: You can check the TiDB version in the TiDB Cloud console, in the latest release note, or by running SELECT version() or SELECT tidb_version().
- Classification Note: This is release content because it explains the version upgrade behavior for TiDB Cloud Serverless and the supported ways to view the running TiDB version.

## Official Source Content

## Maintenance FAQ
### Can I upgrade the version of TiDB that my cluster is running on?

No. TiDB Cloud Serverless clusters are upgraded automatically as we roll out new TiDB versions on TiDB Cloud. You can see what version of TiDB your cluster is running in the [TiDB Cloud console](https://tidbcloud.com/project/clusters) or in the latest [release note](https://docs.pingcap.com/tidbcloud/tidb-cloud-release-notes). Alternatively, you can also connect to your cluster and use `SELECT version()` or `SELECT tidb_version()` to check the TiDB version.
