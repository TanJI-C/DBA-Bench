# TiProxy compatibility with other components

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiproxy/tiproxy-overview.md`
- Source Title: `TiProxy Overview`
- Source Heading Path: `TiProxy Overview > Compatibility with other components`
- Source Line Ranges: `141-148`
- Source Scope: `shared`
- Primary Component: `shared`
- Related Components: `tidb`, `dashboard`, `tiup`, `operator`, `lightning`
- Topic Tags: `compatibility`, `version-support`, `tls`, `component-support`, `lightning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0963_566eb1859b`
- Source ID: `tidb-docs-8.1:tiproxy/tiproxy-overview.md#compatibility-with-other-components`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4f9daa354df51bc73913bc57cd95bd77e0981428afbc6d9df59d8f6efc3be4d3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-overview#compatibility-with-other-components
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiproxy/tiproxy-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about TiProxy compatibility, minimum supported versions, TLS compatibility notes, or whether TiDB Dashboard, Grafana, TiUP, TiDB Operator, or TiDB Lightning work with TiProxy.
- Retrieval Keywords: Compatibility with other components, TiProxy only supports TiDB v6.5.0 and later versions, TLS connection has incompatible features with TiDB, Security, TiDB Dashboard support TiProxy from v7.6.0, Grafana support TiProxy from v7.6.0, TiUP supports TiProxy from v1.14.1, TiDB Operator supports TiProxy from v1.5.1, TiDB Lightning, status port of TiProxy is different from that of TiDB server, target database should be the address of TiDB server not the address of TiProxy
- Follow-up Guidance: The source directs readers to the Security section for details about TLS incompatibilities and notes that TiDB Lightning should use the TiDB server address instead of the TiProxy address.
- Classification Note: This is classified as reference because it lists support boundaries and cross-component compatibility details, including version support and component-specific limitations.

## Official Source Content

## Compatibility with other components

- TiProxy only supports TiDB v6.5.0 and later versions.
- TiProxy's TLS connection has incompatible features with TiDB. For details, see [Security](#security).
- TiDB Dashboard and Grafana support TiProxy from v7.6.0.
- TiUP supports TiProxy from v1.14.1, and TiDB Operator supports TiProxy from v1.5.1.
- Because the interface provided by the status port of TiProxy is different from that of TiDB server, when you use [TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview) to import data, the target database should be the address of TiDB server, not the address of TiProxy.
