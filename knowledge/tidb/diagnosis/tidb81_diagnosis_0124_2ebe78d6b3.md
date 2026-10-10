# TiUP command troubleshooting for list refresh and download issues

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-troubleshooting-guide.md`
- Source Title: `TiUP Troubleshooting Guide`
- Source Heading Path: `TiUP Troubleshooting Guide | TiUP Troubleshooting Guide > Troubleshoot TiUP commands | TiUP Troubleshooting Guide > Troubleshoot TiUP commands > Can't see the latest component list using `tiup list` | TiUP Troubleshooting Guide > Troubleshoot TiUP commands > Can't see the latest version information of a component using `tiup list <component>` | TiUP Troubleshooting Guide > Troubleshoot TiUP commands > Component downloading process is interrupted | TiUP Troubleshooting Guide > Troubleshoot TiUP commands > A checksum error occurs during component downloading process`
- Source Line Ranges: `5-27`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `component-list`, `version-cache`, `mirror-server`, `downloads`, `cdn`, `checksum`, `network-troubleshooting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0124_2ebe78d6b3`
- Source ID: `tidb-docs-8.1:tiup/tiup-troubleshooting-guide.md#tiup-troubleshooting-guide`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `93da23feef2a8063183f206990a62a2a12e238bebe674ea49cb23215a6085401`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-troubleshooting-guide#tiup-troubleshooting-guide
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-troubleshooting-guide.md

## Retrieval Guidance

- Use When: Use this chunk when troubleshooting TiUP command issues involving stale `tiup list` output, interrupted component downloads, or checksum mismatches during component downloading.
- Retrieval Keywords: tiup list, tiup list <component>, latest component list, latest version information, mirror server, local cache, component downloading process is interrupted, checksum error, CDN server, checksum file, component package
- Follow-up Guidance: If repeated download attempts still fail or the checksum file still does not match the component package after 5 minutes, the content says to report the issue in the Github TiUP repository.
- Classification Note: This is classified as diagnosis because the content explains why `tiup list` or `tiup list <component>` might not show new information and why downloads or checksum validation can fail, along with the stated troubleshooting methods.

## Official Source Content

# TiUP Troubleshooting Guide

This document introduces some common issues when you use TiUP and the troubleshooting methods. If this document does not include the issues you bump into, [file a new issue](https://github.com/pingcap/tiup/issues) in the Github TiUP repository.
## Troubleshoot TiUP commands
### Can't see the latest component list using `tiup list`

TiUP does not update the latest component list from the mirror server every time. You can forcibly refresh the component list by running `tiup list`.
### Can't see the latest version information of a component using `tiup list <component>`

Same as the previous issue, the component version information is only obtained from the mirror server when there is no local cache. You can refresh the component list by running `tiup list <component>`.
### Component downloading process is interrupted

Unstable network might result in an interrupted component downloading process. You can try to download the component again. If you cannot download it after trying multiple times, it might be caused by the CDN server and you can report the issue [here](https://github.com/pingcap/tiup/issues).
### A checksum error occurs during component downloading process

Because the CDN server has a short cache time, the new checksum file might not match the component package. Try to download again after 5 minutes. If the new checksum file still does not match the component package, report the issue [here](https://github.com/pingcap/tiup/issues).
