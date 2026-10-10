# PD Recover overview and installation sources

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pd-recover.md`
- Source Title: `PD Recover User Guide`
- Source Heading Path: `PD Recover User Guide | PD Recover User Guide > Compile from source code | PD Recover User Guide > Download TiDB Toolkit`
- Source Line Ranges: `5-24`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `ecosystem`
- Topic Tags: `overview`, `installation`, `source-build`, `toolkit`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0475_69e98d4d59`
- Source ID: `tidb-docs-8.1:pd-recover.md#pd-recover-user-guide`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8626ba2bdbbb5be3c823eec3aef9c86d49cddd398bb9e25eae4178cf3840a0eb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pd-recover#pd-recover-user-guide
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pd-recover.md

## Retrieval Guidance

- Use When: Use this chunk when looking for what PD Recover is, how to compile `pd-recover` from the PD project source, or where the installation package is provided in TiDB Toolkit.
- Retrieval Keywords: PD Recover User Guide, pd-recover, disaster recovery tool of PD, Compile from source code, Go 1.21 or later, make pd-recover, bin/pd-recover, PD project, PD Control tool, released binary or Docker, Download TiDB Toolkit, Download TiDB Tools
- Follow-up Guidance: The source then introduces two methods to recover a PD cluster: recover from a surviving PD node and rebuild a PD cluster entirely.
- Classification Note: This is reference content because it describes the purpose of PD Recover and its installation or build sources without performing a recovery procedure.

## Official Source Content

# PD Recover User Guide

PD Recover is a disaster recovery tool of PD, used to recover the PD cluster which cannot start or provide services normally.
## Compile from source code

+ [Go](https://golang.org/) 1.21 or later is required because the Go modules are used.
+ In the root directory of the [PD project](https://github.com/pingcap/pd), use the `make pd-recover` command to compile and generate `bin/pd-recover`.

> **Note:**
>
> Generally, you do not need to compile source code because the PD Control tool already exists in the released binary or Docker. However, developer users can refer to the instructions above for compiling source code.
## Download TiDB Toolkit

The PD Recover installation package is included in the TiDB Toolkit. To download the TiDB Toolkit, see [Download TiDB Tools](https://docs.pingcap.com/tidb/stable/download-ecosystem-tools).

The following sections introduce two methods to recover a PD cluster: recover from a surviving PD node and rebuild a PD cluster entirely.
