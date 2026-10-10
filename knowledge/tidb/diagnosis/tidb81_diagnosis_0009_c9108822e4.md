# PD leader switching slowdown with massive Region metadata

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/massive-regions-best-practices.md`
- Source Title: `Best Practices for TiKV Performance Tuning with Massive Regions`
- Source Heading Path: `Best Practices for TiKV Performance Tuning with Massive Regions > Other problems and solutions | Best Practices for TiKV Performance Tuning with Massive Regions > Other problems and solutions > Switching PD Leader is slow`
- Source Line Ranges: `154-163`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`
- Topic Tags: `pd-leader`, `etcd`, `region-meta`, `region-routing`, `leveldb`, `leader-switching`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0009_c9108822e4`
- Source ID: `tidb-docs-8.1:best-practices/massive-regions-best-practices.md#other-problems-and-solutions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `db582a5f176c69b434edd92cc7a528ea35fdc667a0ff43058c99b38c53ce3ca7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/massive-regions-best-practices#other-problems-and-solutions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/massive-regions-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when investigating slow PD leader switching in clusters with many Regions and searching for how Region Meta storage affects recovery of Region routing services.
- Retrieval Keywords: Switching PD Leader is slow, PD Leader, Region Meta, etcd, use-region-storage, LevelDB, Region routing services, millions of Regions, more than ten seconds, tens of seconds
- Follow-up Guidance: The source states that use-region-storage is enabled by default in PD since TiDB v3.0 and stores Region Meta information on local LevelDB while synchronizing it among PD nodes through other mechanisms.
- Classification Note: This chunk is classified as diagnosis because it describes the cause of slow PD leader switching with massive Region metadata and identifies the relevant PD storage feature mentioned in the official content.

## Official Source Content

## Other problems and solutions

This section describes some other problems and solutions.
### Switching PD Leader is slow

PD needs to persist Region Meta information on etcd to ensure that PD can quickly resume to provide Region routing services after switching the PD Leader node. As the number of Regions increases, the performance problem of etcd appears, making it slower for PD to get Region Meta information from etcd when PD is switching the Leader. With millions of Regions, it might take more than ten seconds or even tens of seconds to get the meta information from etcd.

To address this problem, `use-region-storage` is enabled by default in PD since TiDB v3.0. With this feature enabled, PD stores Region Meta information on local LevelDB and synchronizes the information among PD nodes through other mechanisms.
