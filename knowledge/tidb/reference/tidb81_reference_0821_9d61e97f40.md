# Network, data, and audit security controls in TiDB Cloud

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/security-concepts.md`
- Source Title: `Security`
- Source Heading Path: `Security > Network access control | Security > Network access control > Private endpoints | Security > Network access control > TLS (Transport Layer Security) | Security > Network access control > VPC peering | Security > Network access control > IP access list | Security > Data access control | Security > Audit logging | Security > Audit logging > Console audit logging | Security > Audit logging > Database audit logging`
- Source Line Ranges: `161-243`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`, `sql`
- Topic Tags: `security`, `network-access-control`, `private-endpoints`, `tls`, `vpc-peering`, `ip-access-list`, `data-access-control`, `cmek`, `encryption-at-rest`, `audit-logging`, `console-audit-logging`, `database-audit-logging`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0821_9d61e97f40`
- Source ID: `tidb-docs-8.1:tidb-cloud/security-concepts.md#network-access-control`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fd29b1cf1fe53d2f7382047837d32f07f06ac36b0cd49dbe7e88ae018ba0748c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/security-concepts#network-access-control
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/security-concepts.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiDB Cloud network access controls, encryption at rest with CMEK, or audit logging for console and database activity.
- Retrieval Keywords: Network access control, Private endpoints, AWS PrivateLink, Azure Private Link, Google Cloud Private Service Connect, TLS, Transport Layer Security, VPC peering, IP access list, Data access control, Customer-Managed Encryption Key, CMEK, encryption at rest, escrow keys, Console audit logging, Database audit logging, executed SQL statements, user access, SIEM
- Follow-up Guidance: The source links to setup pages for private endpoint connections, TLS connections, VPC peering, IP access lists, encryption at rest using Customer-Managed Encryption Keys, Console Audit Logging, and Database Audit Logging.
- Classification Note: This is classified as reference because the content enumerates specific TiDB Cloud security controls and logging capabilities, including private connectivity, TLS, VPC peering, IP filtering, CMEK behavior, and audit log coverage.

## Official Source Content

## Network access control

TiDB Cloud ensures secure cluster connectivity and data transmission through robust network access controls. Key features include:
### Private endpoints

- Enables secure connectivity for SQL clients within your Virtual Private Cloud (VPC) to TiDB Cloud Dedicated clusters.

- Supported by [AWS PrivateLink](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections), [Azure Private Link](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections-on-azure), and [Google Cloud Private Service Connect](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections-on-google-cloud).

**Best practices:** Use private endpoints in production to minimize public exposure and review configurations regularly.
### TLS (Transport Layer Security)

- Encrypts communication between clients and servers to secure data transmission.

- Setup guides available for both [Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/secure-connections-to-serverless-clusters) and [Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-tls-connect-to-dedicated) clusters.

**Best practices:** Ensure TLS certificates are current and rotate them periodically.
### VPC peering

- Establishes private connections between Virtual Private Clouds, enabling secure, seamless communication.

- For more information, see [Connect to TiDB Cloud Dedicated via VPC Peering](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections).

**Best practices:** Use for critical workloads to avoid public internet exposure and monitor performance.
### IP access list

- Acts as a firewall to restrict cluster access to trusted IP addresses.

- For more information, see [Configure an IP Access List](https://docs.pingcap.com/tidb/stable/tidb-cloud/configure-ip-access-list).

**Best practices:** Regularly audit and update the access list to maintain security.
## Data access control

TiDB Cloud safeguards static data with advanced encryption capabilities, ensuring security and compliance with industry regulations.

**Customer-Managed Encryption Key (CMEK)**

- Provides organizations full control over encryption for TiDB Cloud Dedicated clusters.

- Encrypts static data and backups with CMEK keys when enabled.

- For TiDB Cloud Dedicated clusters without CMEK, TiDB Cloud uses escrow keys; TiDB Cloud Serverless clusters rely exclusively on escrow keys.

**Best practices:**

- Regularly rotate CMEK keys to enhance security and meet compliance standards.

- Encrypt backups consistently with CMEK keys for added protection.

- Leverage CMEK for industries requiring strict compliance, such as HIPAA and GDPR.

For more information, see [Encryption at Rest Using Customer-Managed Encryption Keys](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-encrypt-cmek).
## Audit logging

TiDB Cloud provides comprehensive audit logging to monitor user activities and database operations, ensuring security, accountability, and compliance.
### Console audit logging

Tracks key actions on the TiDB Cloud console, such as inviting users or managing clusters.

**Best practices:**

- Integrate logs with SIEM tools for real-time monitoring and alerts.

- Set retention policies to meet compliance requirements.
### Database audit logging

Records detailed database operations, including executed SQL statements and user access.

**Best practices:**

- Regularly review logs for unusual activity or unauthorized access.

- Use logs for compliance reporting and forensic analysis.

For more information, see [Console Audit Logging](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-console-auditing) and [Database Audit Logging](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-auditing).
