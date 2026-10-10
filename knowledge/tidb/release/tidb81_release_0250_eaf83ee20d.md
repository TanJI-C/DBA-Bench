# Bug fixes for TiFlash, BR, and TiCDC section start

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.2.4.md`
- Source Title: `TiDB 5.2.4 Release Notes`
- Source Heading Path: `TiDB 5.2.4 Release Notes > Bug fixes`
- Source Line Ranges: `134-167`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `br`, `ticdc`, `tidb`, `tikv`
- Topic Tags: `bug-fixes`, `mpp`, `thread-leak`, `query-result`, `casting`, `decimal`, `collation`, `tls`, `memory-limit`, `metadata-corruption`, `join`, `execution-plan`, `backup`, `rawkv`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0250_eaf83ee20d`
- Source ID: `tidb-docs-8.1:releases/release-5.2.4.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6773b9b6506ff8292062b247dac6019fccdb0a7e371e4bc9a75656f7cf55a8ad`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.2.4#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.2.4.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 5.2.4 bug fixes in TiFlash or BR involving MPP, wrong query results, casting to DECIMAL, collation, TLS, memory limit, JOIN hangs, metadata corruption, or BR RawKV backup failures.
- Retrieval Keywords: TiDB 5.2.4 bug fixes TiFlash BR, MPP tasks might leak threads forever, #4238, result of IN is incorrect in multi-value expressions, #4016, date format identifies \n as an invalid separator, #4036, STR_TO_DATE leading zeros parsing microseconds, #3557, casting INT to DECIMAL might cause overflow, #3920, casting DATETIME to DECIMAL wrong result, #4151, casting FLOAT to DECIMAL overflow, #3998, CastStringAsReal behavior is inconsistent, #3475, CastStringAsDecimal behavior is inconsistent, #3619, EstablishMPPConnection error after it is restarted, #3615, obsolete data cannot be reclaimed after setting the number of TiFlash replicas to 0, #3659, new_collations_enabled_on_first_bootstrap wrong results, #3388, #3391, panic issue that occurs when TLS is enabled, #4196, panic issue that occurs when the memory limit is enabled, #3902, Unexpected type of column: Nullable(Nothing), #3351, metadata corruption caused by Region merge on a lagging Region peer, #4437, query containing JOIN might be hung if an error occurs, #4195, MPP queries incorrect execution plans wrong results, #3389, BR fails to back up RawKV, #32607
- Follow-up Guidance: The chunk ends at the TiCDC subsection header and does not include TiCDC bug-fix details.
- Classification Note: This chunk is classified as a release note for the TiFlash primary component because the official content is a TiDB 5.2.4 bug-fix list dominated by TiFlash items and includes a BR item before the TiCDC section starts.

## Official Source Content

- Fix a bug that MPP tasks might leak threads forever [#4238](https://github.com/pingcap/tiflash/issues/4238)
    - Fix the issue that the result of `IN` is incorrect in multi-value expressions [#4016](https://github.com/pingcap/tiflash/issues/4016)
    - Fix the issue that the date format identifies `'\n'` as an invalid separator [#4036](https://github.com/pingcap/tiflash/issues/4036)
    - Fix the potential query error after adding columns under heavy read workload [#3967](https://github.com/pingcap/tiflash/issues/3967)
    - Fix the bug that invalid storage directory configurations lead to unexpected behaviors [#4093](https://github.com/pingcap/tiflash/issues/4093)
    - Fix the bug that some exceptions are not handled properly [#4101](https://github.com/pingcap/tiflash/issues/4101)
    - Fix the bug that the `STR_TO_DATE()` function incorrectly handles leading zeros when parsing microseconds [#3557](https://github.com/pingcap/tiflash/issues/3557)
    - Fix the issue that casting `INT` to `DECIMAL` might cause overflow [#3920](https://github.com/pingcap/tiflash/issues/3920)
    - Fix the wrong result that occurs when casting `DATETIME` to `DECIMAL` [#4151](https://github.com/pingcap/tiflash/issues/4151)
    - Fix the overflow that occurs when casting `FLOAT` to `DECIMAL` [#3998](https://github.com/pingcap/tiflash/issues/3998)
    - Fix the issue that the `CastStringAsReal` behavior is inconsistent in TiFlash and in TiDB or TiKV [#3475](https://github.com/pingcap/tiflash/issues/3475)
    - Fix the issue that the `CastStringAsDecimal` behavior is inconsistent in TiFlash and in TiDB or TiKV [#3619](https://github.com/pingcap/tiflash/issues/3619)
    - Fix the issue that TiFlash might return the `EstablishMPPConnection` error after it is restarted [#3615](https://github.com/pingcap/tiflash/issues/3615)
    - Fix the issue that obsolete data cannot be reclaimed after setting the number of TiFlash replicas to 0 [#3659](https://github.com/pingcap/tiflash/issues/3659)
    - Fix potential data inconsistency when widening the primary key column with the primary key being `handle` [#3569](https://github.com/pingcap/tiflash/issues/3569)
    - Fix possible parsing errors when an SQL statement contains extremely long nested expressions [#3354](https://github.com/pingcap/tiflash/issues/3354)
    - Fix possible wrong results when a query contains the `where <string>` clause [#3447](https://github.com/pingcap/tiflash/issues/3447)
    - Fix possible wrong results when `new_collations_enabled_on_first_bootstrap` is enabled [#3388](https://github.com/pingcap/tiflash/issues/3388), [#3391](https://github.com/pingcap/tiflash/issues/3391)
    - Fix the panic issue that occurs when TLS is enabled [#4196](https://github.com/pingcap/tiflash/issues/4196)
    - Fix the panic issue that occurs when the memory limit is enabled [#3902](https://github.com/pingcap/tiflash/issues/3902)
    - Fix the issue that TiFlash crashes occasionally when an MPP query is stopped [#3401](https://github.com/pingcap/tiflash/issues/3401)
    - Fix the unexpected error of `Unexpected type of column: Nullable(Nothing)` [#3351](https://github.com/pingcap/tiflash/issues/3351)
    - Fix possible metadata corruption caused by Region merge on a lagging Region peer [#4437](https://github.com/pingcap/tiflash/issues/4437)
    - Fix the issue that a query containing `JOIN` might be hung if an error occurs [#4195](https://github.com/pingcap/tiflash/issues/4195)
    - Fix possible wrong results returned for MPP queries due to incorrect execution plans [#3389](https://github.com/pingcap/tiflash/issues/3389)

+ Tools

    + Backup & Restore (BR)

        - Fix the issue that BR fails to back up RawKV [#32607](https://github.com/pingcap/tidb/issues/32607)

    + TiCDC
