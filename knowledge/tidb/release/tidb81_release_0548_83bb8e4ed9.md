# TiDB 7.5.6 overview, compatibility changes, and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.6.md`
- Source Title: `TiDB 7.5.6 Release Notes`
- Source Heading Path: `TiDB 7.5.6 Release Notes | TiDB 7.5.6 Release Notes > Compatibility changes | TiDB 7.5.6 Release Notes > Improvements`
- Source Line Ranges: `5-46`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `br`, `lightning`
- Topic Tags: `release-notes`, `compatibility`, `os-support`, `improvements`, `statistics`, `timestamp-validation`, `ttl`, `gc`, `slow-logs`, `restart-stability`, `tls`, `backup`, `restore`, `csv-parsing`, `oom-prevention`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0548_83bb8e4ed9`
- Source ID: `tidb-docs-8.1:releases/release-7.5.6.md#tidb-7-5-6-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `58176461a2751f1d191a32ac6c64cde2b6bed15c714cbe36022c04347400d873`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.6#tidb-7-5-6-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.6.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.5.6 compatibility changes and improvement items across TiDB, TiKV, TiFlash, BR, and TiDB Lightning.
- Retrieval Keywords: TiDB 7.5.6 Release Notes, Compatibility changes, openEuler 22.03 LTS SP3/SP4, OS and platform requirements, statistics TopN modified row count, timestamp validity check, GC for TTL tables owner node, invalid max_ts updates, slow logs for peer and store messages, restarting TiKV stability, TLS enabled certificates TiFlash panic, BR --checksum=false, non-full restore same name table check, TiDB Lightning CSV row width check, OOM issues
- Follow-up Guidance: The chunk also points to Quick start, Production deployment, and OS and platform requirements for related official documentation.
- Classification Note: This is a self-managed release-notes chunk summarizing TiDB 7.5.6 overview content, including one compatibility change and multiple improvements across core components and tools.

## Official Source Content

# TiDB 7.5.6 Release Notes

Release date: March 14, 2025

TiDB version: 7.5.6

Quick access: [Quick start](https://docs.pingcap.com/tidb/v7.5/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v7.5/production-deployment-using-tiup)
## Compatibility changes

- Support the openEuler 22.03 LTS SP3/SP4 operating system. For more information, see [OS and platform requirements](https://docs.pingcap.com/tidb/v7.5/hardware-and-software-requirements#os-and-platform-requirements).
## Improvements

+ TiDB

    - Adjust estimation results from 0 to 1 for equality conditions that do not hit TopN when statistics are entirely composed of TopN and the modified row count in the corresponding table statistics is non-zero [#47400](https://github.com/pingcap/tidb/issues/47400) @[terry1purcell](https://github.com/terry1purcell)
    - Enhance the timestamp validity check [#57786](https://github.com/pingcap/tidb/issues/57786) @[MyonKeminta](https://github.com/MyonKeminta)
    - Limit the execution of GC for TTL tables and related statistics collection tasks to the owner node, thereby reducing overhead [#59357](https://github.com/pingcap/tidb/issues/59357) @[lcwangchao](https://github.com/lcwangchao)

+ TiKV

    - Add the detection mechanism for invalid `max_ts` updates [#17916](https://github.com/tikv/tikv/issues/17916) @[ekexium](https://github.com/ekexium)
    - Add slow logs for peer and store messages [#16600](https://github.com/tikv/tikv/issues/16600) @[Connor1996](https://github.com/Connor1996)
    - Optimize the jittery access delay when restarting TiKV due to waiting for the log to be applied, improving the stability of TiKV [#15874](https://github.com/tikv/tikv/issues/15874) @[LykxSassinator](https://github.com/LykxSassinator)

+ TiFlash

    - Mitigate the issue that TiFlash might panic due to updating certificates after TLS is enabled [#8535](https://github.com/pingcap/tiflash/issues/8535) @[windtalker](https://github.com/windtalker)

+ Tools

    + Backup & Restore (BR)

        - Disable the table-level checksum calculation during full backups by default (`--checksum=false`) to improve backup performance [#56373](https://github.com/pingcap/tidb/issues/56373) @[Tristan1900](https://github.com/Tristan1900)
        - Add a check to verify whether the target cluster contains a table with the same name for non-full restore [#55087](https://github.com/pingcap/tidb/issues/55087) @[RidRisR](https://github.com/RidRisR)

    + TiDB Lightning

        - Add a row width check when parsing CSV files to prevent OOM issues [#58590](https://github.com/pingcap/tidb/issues/58590) @[D3Hunter](https://github.com/D3Hunter)
