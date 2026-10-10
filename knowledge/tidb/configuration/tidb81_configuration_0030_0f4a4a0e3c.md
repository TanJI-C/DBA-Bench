# Dashboard access and network exposure FAQs

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-faq.md`
- Source Title: `TiDB Dashboard FAQs`
- Source Heading Path: `TiDB Dashboard FAQs | TiDB Dashboard FAQs > Access-related FAQ | TiDB Dashboard FAQs > Access-related FAQ > When the firewall or reverse proxy is configured, I am redirected to an internal address other than TiDB Dashboard | TiDB Dashboard FAQs > Access-related FAQ > When TiDB Dashboard is deployed with dual network interface cards (NICs), TiDB Dashboard cannot be accessed using another NIC`
- Source Line Ranges: `5-25`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `pd`, `tiup`
- Topic Tags: `access`, `firewall`, `reverse-proxy`, `multi-pd`, `redirect`, `network-interface`, `nic`, `deployment`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0030_0f4a4a0e3c`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-faq.md#tidb-dashboard-faqs`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9f566e381888105176c40f13fc55eb0657c36177c77d49e91ffdee42ef399742`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-faq#tidb-dashboard-faqs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-faq.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing TiDB Dashboard access problems involving redirects to an internal address with multiple PD instances, firewall or reverse proxy configuration, or inability to access Dashboard through another NIC on a dual-NIC host.
- Retrieval Keywords: TiDB Dashboard, multiple Placement Driver instances, PD instances, redirected to an internal address, firewall, reverse proxy, TiDB Dashboard Multi-PD Instance Deployment, Use TiDB Dashboard through a Reverse Proxy, Secure TiDB Dashboard, dual network interface cards, dual NICs, only listens on one NIC, not on 0.0.0.0, cannot be accessed using another NIC, tiup cluster, tiup playground
- Follow-up Guidance: The source points to TiDB Dashboard Multi-PD Instance Deployment, Use TiDB Dashboard through a Reverse Proxy, Use TiDB Dashboard behind a Reverse Proxy, and Secure TiDB Dashboard for the related configuration details.
- Classification Note: This is classified as configuration because the content explains Dashboard access behavior under multi-PD deployment, firewall or reverse proxy setup, and NIC listening limitations.

## Official Source Content

# TiDB Dashboard FAQs

This document summarizes the frequently asked questions (FAQs) and answers about TiDB Dashboard. If a problem cannot be located or persists after you perform as instructed, [get support](https://docs.pingcap.com/tidb/stable/support) from PingCAP or the community.
## Access-related FAQ
### When the firewall or reverse proxy is configured, I am redirected to an internal address other than TiDB Dashboard

When multiple Placement Driver (PD) instances are deployed in a cluster, only one of the PD instances actually runs the TiDB Dashboard service. If you access other PD instances instead of this one, your browser redirects you to another address. If the firewall or reverse proxy is not properly configured for accessing TiDB Dashboard, when you visit the Dashboard, you might be redirected to an internal address that is protected by the firewall or reverse proxy.

- See [TiDB Dashboard Multi-PD Instance Deployment](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-ops-deploy) to learn the working principle of TiDB Dashboard with multiple PD instances.
- See [Use TiDB Dashboard through a Reverse Proxy](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-ops-reverse-proxy) to learn how to correctly configure a reverse proxy.
- See [Secure TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-ops-security) to learn how to correctly configure the firewall.
### When TiDB Dashboard is deployed with dual network interface cards (NICs), TiDB Dashboard cannot be accessed using another NIC

For security reasons, TiDB Dashboard on PD only monitors the IP addresses specified during deployment (that is, it only listens on one NIC), not on `0.0.0.0`. Therefore, when multiple NICs are installed on the host, you cannot access TiDB Dashboard using another NIC.

If you have deployed TiDB using the `tiup cluster` or `tiup playground` command, currently this problem cannot be solved. It is recommended that you use a reverse proxy to safely expose TiDB Dashboard to another NIC. For details, see [Use TiDB Dashboard behind a Reverse Proxy](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-ops-reverse-proxy).
