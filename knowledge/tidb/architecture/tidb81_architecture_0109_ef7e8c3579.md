# TiFlash data validation mechanism and usage

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tiflash-data-validation.md`
- Source Title: `TiFlash Data Validation`
- Source Heading Path: `TiFlash Data validation | TiFlash Data validation > Validation mechanism | TiFlash Data validation > Validation mechanism > Use data validation | TiFlash Data validation > Validation mechanism > Validation tool`
- Source Line Ranges: `5-44`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: none
- Topic Tags: `data-validation`, `checksum`, `dtfile`, `hash-algorithm`, `manual-validation`, `automatic-validation`, `version-compatibility`, `data-integrity`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0109_ef7e8c3579`
- Source ID: `tidb-docs-8.1:tiflash/tiflash-data-validation.md#tiflash-data-validation`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `403112697f5888a8fa92aae919fafcfc5b96f11cbe0cafdd4e38d8ddae881c00`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tiflash-data-validation#tiflash-data-validation
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tiflash-data-validation.md

## Retrieval Guidance

- Use When: Use this chunk when searching for how TiFlash validates data integrity, including DTFile validation mechanisms, default hash algorithms, automatic versus manual validation, and version compatibility of V2 and V3 formats.
- Retrieval Keywords: TiFlash Data validation, data validation, DTFile, DeltaTree File, stable folder, dmf_<file id>, City128, XXH3, V1, V2, V3, automatic data validation, manual data validation, DTTool inspect, DTTool migrate, validation mechanism, data integrity, checksum, validation frame, TiFlash immediately reports an error and exits
- Follow-up Guidance: For manual checking and switching DTFile versions, the source points to `DTTool inspect` and `DTTool migrate`, and for manually switching the validation mechanism it points to the TiFlash configuration file documentation.
- Classification Note: This chunk is classified as architecture because it explains the TiFlash DTFile-based data validation design, the V1/V2/V3 validation mechanisms, and how automatic and manual validation are used.

## Official Source Content

# TiFlash Data validation

This document introduces the data validation mechanism and tools for TiFlash.

Data corruptions are usually caused by serious hardware failures. In such cases, even if you attempt to manually recover data, your data become less reliable.

To ensure data integrity, by default, TiFlash performs basic data validation on data files, using the `City128` algorithm. In the event of any data validation failure, TiFlash immediately reports an error and exits, avoiding secondary disasters caused by inconsistent data. At this time, you need to manually intervene and replicate the data again before you can restore the TiFlash node.

Starting from v5.4.0, TiFlash introduces more advanced data validation features. TiFlash uses the `XXH3` algorithm by default and allows you to customize the validation frame and algorithm.
## Validation mechanism

The validation mechanism builds upon the DeltaTree File (DTFile). DTFile is the storage file that persists TiFlash data. DTFile has three formats:

| Version | State | Validation mechanism | Notes |
| :-- | :-- | :-- |:-- |
| V1 | Deprecated | Hashes are embedded in data files. | |
| V2 | Default for versions < v6.0.0 | Hashes are embedded in data files. | Compared to V1, V2 adds statistics of column data. |
| V3 | Default for versions >= v6.0.0 | V3 contains metadata and token data checksum, and supports multiple hash algorithms. | New in v5.4.0. |

DTFile is stored in the `stable` folder in the data file directory. All formats currently enabled are in folder format, which means the data is stored in multiple files under a folder with a name like `dmf_<file id>`.
### Use data validation

TiFlash supports both automatic and manual data validation:

* Automatic data validation:
    * v6.0.0 and later versions use the V3 validation mechanism by default.
    * Versions earlier than v6.0.0 use the V2 validation mechanism by default.
    * To manually switch the validation mechanism, refer to [TiFlash configuration file](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-the-tiflashtoml-file). However, the default configuration is verified by tests and therefore recommended.
* Manual data validation. Refer to [`DTTool inspect`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-command-line-flags#dttool-inspect).

> **Warning:**
>
> After you enable the V3 validation mechanism, the newly generated DTFile cannot be directly read by TiFlash earlier than v5.4.0. Since v5.4.0, TiFlash supports both V2 and V3 and does not actively upgrade or downgrade versions. If you need to upgrade or downgrade versions for existing files, you need to manually [switch versions](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-command-line-flags#dttool-migrate).
### Validation tool

In addition to automatic data validation performed when TiFlash reads data, a tool for manually checking data integrity is introduced in v5.4.0. For details, refer to [DTTool](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-command-line-flags#dttool-inspect).
