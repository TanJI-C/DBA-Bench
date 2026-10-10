# TiFlash disaggregated architecture restrictions and migration limits

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tiflash-disaggregated-and-s3.md`
- Source Title: `TiFlash Disaggregated Storage and Compute Architecture and S3 Support`
- Source Heading Path: `TiFlash Disaggregated Storage and Compute Architecture and S3 Support > Restrictions`
- Source Line Ranges: `172-178`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`
- Topic Tags: `restrictions`, `architecture-switching`, `migration`, `replication`, `s3`, `object-storage`, `encryption-at-rest`, `cluster-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0952_779e2ebbca`
- Source ID: `tidb-docs-8.1:tiflash/tiflash-disaggregated-and-s3.md#restrictions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9bcb04f0726a6e9648d17698ed97fd02c012cbd83717e165a38a55469956039f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tiflash-disaggregated-and-s3#restrictions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tiflash-disaggregated-and-s3.md

## Retrieval Guidance

- Use When: Use this chunk when checking TiFlash disaggregated architecture restrictions, architecture migration limits, cluster coexistence rules, S3-only storage support, or Encryption at Rest limitations with S3 storage.
- Retrieval Keywords: TiFlash disaggregated storage and compute architecture, coupled storage and compute architecture, in-place switching not supported, remove all existing TiFlash nodes, TiFlash data needs to be replicated again, same architecture in the same TiDB cluster, Two architectures cannot coexist in one cluster, S3 API object storage, local storage, Encryption at Rest cannot be used
- Follow-up Guidance: The content states that after migration from one architecture to another, all TiFlash data needs to be replicated again.
- Classification Note: This is reference content because it lists explicit restrictions and compatibility limits for TiFlash architectures, storage types, and Encryption at Rest usage.

## Official Source Content

## Restrictions

- TiFlash does not support in-place switching between the **disaggregated storage and compute architecture** and the **coupled storage and compute architecture**. Before switching to the disaggregated architecture, you must remove all existing TiFlash nodes deployed using the coupled architecture.
- After the migration from one architecture to another, all TiFlash data needs to be replicated again.
- Only TiFlash nodes with the same architecture are allowed in the same TiDB cluster. Two architectures cannot coexist in one cluster.
- The disaggregated storage and compute architecture only supports object storage using the S3 API, while the coupled storage and compute architecture only supports local storage.
- When using S3 storage, TiFlash nodes cannot obtain the keys of files not on their own nodes, so the [Encryption at Rest](https://docs.pingcap.com/tidb/stable/encryption-at-rest) feature cannot be used.
