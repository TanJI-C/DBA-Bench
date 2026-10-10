# PROXY protocol allowed networks

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-configuration-file.md`
- Source Title: `TiDB Configuration File`
- Source Heading Path: `TiDB Configuration File > proxy-protocol | TiDB Configuration File > proxy-protocol > `networks``
- Source Line Ranges: `1039-1053`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `dashboard`, `shared`
- Topic Tags: `proxy-protocol`, `network-access`, `client-ip`, `reverse-proxy`, `security-warning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0327_5e93f7554d`
- Source ID: `tidb-docs-8.1:tidb-configuration-file.md#proxy-protocol`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `facbf335ab8224af7a135c6fead311ce273b0db9547b180f63a5d906977b7a36`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-configuration-file#proxy-protocol
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiDB proxy-protocol networks configuration that controls which source IP addresses can connect using the PROXY protocol.
- Retrieval Keywords: proxy-protocol, networks, PROXY protocol, reverse proxy, real client IP address, HAProxy, source IP address, CIDR, 192.168.1.0/24, 192.168.1.50, *, connection will be denied, TiDB Dashboard
- Follow-up Guidance: The content warns that using * might introduce security risks and might cause internal components that directly connect to TiDB, such as TiDB Dashboard, to be unavailable.
- Classification Note: This is classified as configuration because it defines the proxy-protocol networks parameter, its accepted values, and its connection behavior.

## Official Source Content

## proxy-protocol

Configuration items related to the PROXY protocol.
### `networks`

- The list of proxy server's IP addresses allowed to connect to TiDB using the [PROXY protocol](https://www.haproxy.org/download/1.8/doc/proxy-protocol.txt)
- Default value: ""
- In general cases, when you access TiDB behind a reverse proxy, TiDB takes the IP address of the reverse proxy server as the IP address of the client. By enabling the PROXY protocol, reverse proxies that support this protocol, such as HAProxy, can pass the real client IP address to TiDB.
- After configuring this parameter, TiDB allows the configured source IP address to connect to TiDB using the PROXY protocol; if a protocol other than PROXY is used, this connection will be denied. If this parameter is left empty, no IP address can connect to TiDB using the PROXY protocol. The value can be an IP address (192.168.1.50) or CIDR (192.168.1.0/24) with `,` as the separator. `*` means any IP addresses.

> **Warning:**
>
> Use `*` with caution because it might introduce security risks by allowing a client of any IP address to report its IP address. In addition, using `*` might also cause the internal component that directly connects to TiDB (such as TiDB Dashboard) to be unavailable.
