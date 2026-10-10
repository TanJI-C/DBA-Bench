# TiCDC glossary terms: capture, changed data, changefeed, owner, processor

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-glossary.md`
- Source Title: `TiCDC Glossary`
- Source Heading Path: `TiCDC Glossary | TiCDC Glossary > C | TiCDC Glossary > C > Capture | TiCDC Glossary > C > Changed data | TiCDC Glossary > C > Changefeed | TiCDC Glossary > O | TiCDC Glossary > O > Owner | TiCDC Glossary > P | TiCDC Glossary > P > Processor`
- Source Line Ranges: `5-36`
- Source Scope: `shared`
- Primary Component: `ticdc`
- Related Components: `shared`, `tidb`
- Topic Tags: `glossary`, `definitions`, `capture`, `changed-data`, `changefeed`, `owner`, `processor`, `replication`, `cluster`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0765_4174259caf`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-glossary.md#ticdc-glossary`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d3c06d500d149764c5c50e246a0ade1e216270011c9854325d39d36e96f9b43a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-glossary#ticdc-glossary
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-glossary.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants definitions of TiCDC glossary terms that appear in TiCDC logs, monitoring metrics, configurations, or documents, especially capture, changed data, changefeed, owner, and processor.
- Retrieval Keywords: TiCDC Glossary, Capture, Changed data, Changefeed, Owner, Processor, TiCDC instance, TiCDC cluster, incremental replication task, data change logs, designated downstream, owner is elected by captures, at most one owner, replication processing unit, pulling, sorting, restoring, and distributing changed data
- Follow-up Guidance: For TiDB-related terms and definitions, refer to the TiDB glossary.
- Classification Note: This is reference content because it defines TiCDC terms and roles rather than describing procedures or troubleshooting steps.

## Official Source Content

# TiCDC Glossary

This glossary provides TiCDC-related terms and definitions. These terms appear in TiCDC logs, monitoring metrics, configurations, and documents.

For TiDB-related terms and definitions, refer to [TiDB glossary](https://docs.pingcap.com/tidb/stable/glossary).
## C
### Capture

A single TiCDC instance on which the replication task of the cluster runs. Multiple captures form a TiCDC cluster.
### Changed data

The data to be written to TiCDC from the upstream TiDB cluster, including the DML-caused data changes and the DDL-caused table schema changes.
### Changefeed

An incremental replication task in TiCDC, which outputs the data change logs of several tables in a TiDB cluster to the designated downstream.
## O
### Owner

A [capture](#capture) of a special role that manages the TiCDC cluster and schedules replication tasks of the cluster. An owner is elected by captures and there is at most one owner at any time.
## P
### Processor

TiCDC replication tasks allocate data tables on TiCDC instances, and the processor refers to the replication processing unit of these tables. Processor tasks include pulling, sorting, restoring, and distributing changed data.
