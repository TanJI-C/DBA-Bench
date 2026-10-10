# TiDB Cloud overview, deployment options, and architecture

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-intro.md`
- Source Title: `What is TiDB Cloud`
- Source Heading Path: `What is TiDB Cloud | What is TiDB Cloud > Why TiDB Cloud | What is TiDB Cloud > Deployment options | What is TiDB Cloud > Architecture`
- Source Line Ranges: `6-91`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `operator`, `dashboard`
- Topic Tags: `overview`, `managed-service`, `deployment-options`, `serverless`, `dedicated`, `architecture`, `vpc`, `private-endpoint`, `vpc-peering`, `scaling`, `high-availability`, `mysql-compatibility`, `real-time-analytics`, `security`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0088_057d6f7a8b`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-intro.md#what-is-tidb-cloud`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `03f377df9ea92e98756d6532290d675420d5f8e98f983f503b30bdc3c8ec6d30`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-intro#what-is-tidb-cloud
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-intro.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks for a TiDB Cloud overview, its deployment options, core managed-service features, or the high-level architecture and connectivity model.
- Retrieval Keywords: TiDB Cloud, What is TiDB Cloud, fully-managed Database-as-a-Service, DBaaS, HTAP, Hybrid Transactional and Analytical Processing, Deployment options, TiDB Cloud Serverless, TiDB Cloud Dedicated, Architecture, TiDB VPC, TiDB Cloud Central Services, Your VPC, private endpoint connection, VPC peering connection, AWS, Google Cloud, Microsoft Azure, MySQL compatibility, Fast and Customized Scaling, High Availability and Reliability, Real-Time Analytics, Enterprise Grade Security, Fully-Managed Service, Multi-Cloud Support
- Follow-up Guidance: The source points to Set Up Private Endpoint Connections and Set up VPC Peering Connection for details about connecting your VPC to a TiDB cluster.
- Classification Note: This chunk is classified as architecture because the official content describes TiDB Cloud deployment options together with the high-level layout of TiDB VPC, Central Services, and customer VPC connectivity.

## Official Source Content

# What is TiDB Cloud

[TiDB Cloud](https://www.pingcap.com/tidb-cloud/) is a fully-managed Database-as-a-Service (DBaaS) that brings [TiDB](https://docs.pingcap.com/tidb/stable/overview), an open-source Hybrid Transactional and Analytical Processing (HTAP) database, to your cloud. TiDB Cloud offers an easy way to deploy and manage databases to let you focus on your applications, not the complexities of the databases. You can create TiDB Cloud clusters to quickly build mission-critical applications on Amazon Web Services (AWS), Google Cloud, and Microsoft Azure.

![TiDB Cloud Overview](/media/tidb-cloud/tidb-cloud-overview.png)
## Why TiDB Cloud

TiDB Cloud allows you with little or no training to handle complex tasks such as infrastructure management and cluster deployment easily.

- Developers and database administrators (DBAs) can handle a large amount of online traffic effortlessly and rapidly analyze a large volume of data across multiple datasets.

- Enterprises of all sizes can easily deploy and manage TiDB Cloud to adapt to your business growth without prepayment.

Watch the following video to learn more about TiDB Cloud:

<iframe width="600" height="450" src="https://www.youtube.com/embed/skCV9BEmjbo?enablejsapi=1" title="Why TiDB Cloud?" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

With TiDB Cloud, you can get the following key features:

- **Fast and Customized Scaling**

    Elastically and transparently scale to hundreds of nodes for critical workloads while maintaining ACID transactions. No need to bother with sharding. And you can scale your performance and storage nodes separately according to your business needs.

- **MySQL Compatibility**

    Increase productivity and shorten time-to-market for your applications with TiDB's MySQL compatibility. Easily migrate data from existing MySQL instances without the need to rewrite code.

- **High Availability and Reliability**

    Naturally high availability by design. Data replication across multiple Availability Zones, daily backups, and auto-failover ensure business continuity, regardless of hardware failure, network partition, or data center loss.

- **Real-Time Analytics**

    Get real-time analytical query results with a built-in analytics engine. TiDB Cloud runs consistent analytical queries on current data without disturbing mission-critical applications.

- **Enterprise Grade Security**

    Secure your data in dedicated networks and machines, with support for encryption both in-flight and at-rest. TiDB Cloud is certified by SOC 2 Type 2, ISO 27001:2013, ISO 27701, and fully compliant with GDPR.

- **Fully-Managed Service**

    Deploy, scale, monitor, and manage TiDB clusters with a few clicks, through an easy-to-use web-based management platform.

- **Multi-Cloud Support**

    Stay flexible without cloud vendor lock-in. TiDB Cloud is currently available on AWS, Azure, and Google Cloud.

- **Simple Pricing Plans**

    Pay only for what you use, with transparent and upfront pricing with no hidden fees.

- **World-Class Support**

    Get world-class support through our support portal, <a href="mailto:tidbcloud-support@pingcap.com">email</a>, chat, or video conferencing.
## Deployment options

TiDB Cloud provides the following two deployment options:

- [TiDB Cloud Serverless](https://www.pingcap.com/tidb-cloud-serverless)

    TiDB Cloud Serverless is a fully managed, multi-tenant TiDB offering. It delivers an instant, autoscaling MySQL-compatible database and offers a generous free tier and consumption based billing once free limits are exceeded.

- [TiDB Cloud Dedicated](https://www.pingcap.com/tidb-cloud-dedicated)

    TiDB Cloud Dedicated is for production use with the benefits of cross-zone high availability, horizontal scaling, and [HTAP](https://en.wikipedia.org/wiki/Hybrid_transactional/analytical_processing).

For feature comparison between TiDB Cloud Serverless and TiDB Cloud Dedicated, see [TiDB: An advanced, open source, distributed SQL database](https://www.pingcap.com/get-started-tidb).
## Architecture

![TiDB Cloud architecture](/media/tidb-cloud/tidb-cloud-architecture.png)

- TiDB VPC (Virtual Private Cloud)

    For each TiDB Cloud cluster, all TiDB nodes and auxiliary nodes, including TiDB Operator nodes and logging nodes, are deployed in the same VPC.

- TiDB Cloud Central Services

    Central Services, including billing, alerts, meta storage, dashboard UI, are deployed independently. You can access the dashboard UI to operate the TiDB cluster via the internet.

- Your VPC

    You can connect to your TiDB cluster via private endpoint connection or VPC peering connection. Refer to [Set Up Private Endpoint Connections](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections) or [Set up VPC Peering Connection](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections) for details.
