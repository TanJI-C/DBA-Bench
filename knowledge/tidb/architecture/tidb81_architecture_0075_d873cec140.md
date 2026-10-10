# TiDB Cloud architecture, deployment options, and management interfaces

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/architecture-concepts.md`
- Source Title: `Architecture`
- Source Heading Path: `Architecture | Architecture > TiDB Cloud Serverless | Architecture > TiDB Cloud Dedicated | Architecture > TiDB Cloud console | Architecture > TiDB Cloud CLI (Beta) | Architecture > TiDB Cloud API (Beta)`
- Source Line Ranges: `5-53`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `architecture`, `serverless`, `dedicated`, `high-availability`, `console`, `cli`, `api`, `management`, `deployment-options`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0075_d873cec140`
- Source ID: `tidb-docs-8.1:tidb-cloud/architecture-concepts.md#architecture`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b0ded5d1e8915e4d51ceaf2d651c5413e6df4275b120f1a598cf15eda1ec8310`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/architecture-concepts#architecture
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/architecture-concepts.md

## Retrieval Guidance

- Use When: Use this chunk when explaining TiDB Cloud architecture, comparing TiDB Cloud Serverless and TiDB Cloud Dedicated, or identifying the TiDB Cloud console, CLI, and API management interfaces.
- Retrieval Keywords: TiDB Cloud architecture, TiDB Cloud Serverless, TiDB Cloud Dedicated, fully-managed Database-as-a-Service, DBaaS, AWS Azure Google Cloud, HTAP, MySQL-compatible, auto-scaling, cost-efficient workloads, enterprise-grade applications, Zonal High Availability, Regional High Availability, multiple availability zones, TiDB Cloud console, TiDB Cloud CLI, ticloud, TiDB Cloud API, REST-based interface, projects clusters backups restores data imports billing, TiDB Cloud Data Service
- Follow-up Guidance: For command-line and programmatic management details, the source points to the TiDB Cloud CLI Reference and TiDB Cloud API Overview.
- Classification Note: This is classified as cloud architecture because the content describes TiDB Cloud deployment options, high-availability layouts, and the console, CLI, and API used to manage TiDB Cloud resources.

## Official Source Content

# Architecture

TiDB Cloud is a fully-managed Database-as-a-Service (DBaaS) that brings the flexibility and power of [TiDB](https://docs.pingcap.com/tidb/stable/overview), an open-source HTAP (Hybrid Transactional and Analytical Processing) database, to AWS, Azure, and Google Cloud.

TiDB is MySQL-compatible, making it easy to migrate and work with existing applications, while offering seamless scalability to handle everything from small workloads to massive, high-performance clusters. It supports both transactional (OLTP) and analytical (OLAP) workloads in one system, simplifying operations and enabling real-time insights.

TiDB Cloud provides two deployment options: **TiDB Cloud** **Serverless**, for auto-scaling, cost-efficient workloads, and **TiDB Cloud Dedicated**, for enterprise-grade applications with dedicated resources and advanced capabilities. TiDB Cloud makes it easy to scale your database, handle complex management tasks, and stay focused on developing reliable, high-performing applications.
## TiDB Cloud Serverless

TiDB Cloud Serverless is a fully managed serverless solution that provides HTAP capabilities similar to traditional TiDB, while offering auto-scaling to alleviate users' burdens related to capacity planning and management complexities. It includes a free tier for basic usage, with consumption-based billing for any usage that exceeds the free limits. TiDB Cloud Serverless offers two types of high availability to address varying operational requirements.

By default, clusters utilizing the Zonal High Availability option have all components located within the same availability zone, which results in lower network latency.

![TiDB Cloud Serverless zonal high availability](/media/tidb-cloud/serverless-zonal-high-avaliability-aws.png)

For applications that require maximum infrastructure isolation and redundancy, the Regional High Availability option distributes nodes across multiple availability zones.

![TiDB Cloud Serverless regional high availability](/media/tidb-cloud/serverless-regional-high-avaliability-aws.png)
## TiDB Cloud Dedicated

TiDB Cloud Dedicated is designed for mission-critical businesses, offering high availability across multiple availability zones, horizontal scaling, and full HTAP capabilities.

Built on isolated cloud resources such as VPCs, VMs, managed Kubernetes services, and cloud storage, it leverages the infrastructure of major cloud providers. TiDB Cloud Dedicated clusters support the complete TiDB feature set, enabling rapid scaling, reliable backups, deployment within specific VPCs, and geographic-level disaster recovery.

![TiDB Cloud Dedicated Architecture](/media/tidb-cloud/tidb-cloud-dedicated-architecture.png)
## TiDB Cloud console

The [TiDB Cloud console](https://tidbcloud.com/) is the web-based management interface for both TiDB Cloud Serverless and TiDB Cloud Dedicated. It provides tools to manage clusters, import or migrate data, monitor performance metrics, configure backups, set up security controls, and integrate with other cloud services, all from a single, user-friendly platform.
## TiDB Cloud CLI (Beta)

The TiDB Cloud CLI, `ticloud`, allows you to manage TiDB Cloud Serverless and TiDB Cloud Dedicated directly from your terminal with simple commands. You can perform tasks such as:

- Creating, deleting, and listing clusters.
- Importing data into clusters.
- Exporting data from clusters.

For more information, see [TiDB Cloud CLI Reference](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference).
## TiDB Cloud API (Beta)

The TiDB Cloud API is a REST-based interface that provides programmatic access to manage resources across TiDB Cloud Serverless and TiDB Cloud Dedicated. It enables automated and efficient handling of tasks such as managing projects, clusters, backups, restores, data imports, billing, and other resources in [TiDB Cloud Data Service](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-overview).

For more information, see [TiDB Cloud API Overview](https://docs.pingcap.com/tidb/stable/tidb-cloud/api-overview).
