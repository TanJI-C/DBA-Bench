# TiDB Cloud cluster tier selection, plans, quotas, and naming requirements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/select-cluster-tier.md`
- Source Title: `Select Your Cluster Tier`
- Source Heading Path: `Select Your Cluster Tier | Select Your Cluster Tier > TiDB Cloud Serverless | Select Your Cluster Tier > TiDB Cloud Serverless > Cluster plans | Select Your Cluster Tier > TiDB Cloud Serverless > Cluster plans > Free cluster plan | Select Your Cluster Tier > TiDB Cloud Serverless > Cluster plans > Scalable cluster plan | Select Your Cluster Tier > TiDB Cloud Serverless > Usage quota | Select Your Cluster Tier > TiDB Cloud Serverless > User name prefix | Select Your Cluster Tier > TiDB Cloud Serverless > TiDB Cloud Serverless special terms and conditions | Select Your Cluster Tier > TiDB Cloud Dedicated`
- Source Line Ranges: `6-102`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`, `tiflash`, `shared`
- Topic Tags: `cluster-tier`, `serverless`, `dedicated`, `cluster-plans`, `free-plan`, `scalable-plan`, `usage-quota`, `request-units`, `username-prefix`, `tls`, `limitations`, `high-availability`, `htap`, `billing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0822_fb436bcd39`
- Source ID: `tidb-docs-8.1:tidb-cloud/select-cluster-tier.md#select-your-cluster-tier`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ba5c707df1d3ef76f1f2896a20ca503f6c9b7cacf12def16d8e7a76d91f1c24b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#select-your-cluster-tier
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/select-cluster-tier.md

## Retrieval Guidance

- Use When: Use this chunk when comparing TiDB Cloud Serverless and TiDB Cloud Dedicated, checking Serverless free or scalable plan quotas and billing conditions, or finding the required user name prefix and TLS connection details for a Serverless cluster.
- Retrieval Keywords: Select Your Cluster Tier, TiDB Cloud Serverless, TiDB Cloud Dedicated, Free cluster plan, Scalable cluster plan, usage quota, five free clusters, 5 GiB row-based storage, 5 GiB columnar storage, 50 million RUs per month, Request Units, RU, denies any new connection attempts, throttling, User name prefix, mysql -u '3pTAoNNegb47Uc8.root', --ssl-mode=VERIFY_IDENTITY, CREATE USER '3pTAoNNegb47Uc8.jeffrey', TLS connection, TiDB Cloud Serverless Limitations, cross-zone high availability, horizontal scaling, HTAP, TiDB, TiKV, TiFlash, cannot decrease the node storage
- Follow-up Guidance: The source also points to TiDB Cloud Serverless Pricing Details for RU consumption and throttling information, to TiDB Cloud Serverless Limitations for unsupported features, and to pages about payment method, PoC trial, secure connections, and multi-AZ high availability.
- Classification Note: This is classified as reference content because it defines cluster tier options, Serverless plan features and quotas, user name prefix requirements, and Dedicated cluster characteristics and constraints.

## Official Source Content

# Select Your Cluster Tier

The cluster tier determines the throughput and performance of your cluster.

TiDB Cloud provides the following two options of cluster tiers. Before creating a cluster, you need to consider which option suits your need better.

- [TiDB Cloud Serverless](#tidb-cloud-serverless)
- [TiDB Cloud Dedicated](#tidb-cloud-dedicated)
## TiDB Cloud Serverless

<!--To be confirmed-->
TiDB Cloud Serverless is a fully managed, multi-tenant TiDB offering. It delivers an instant, autoscaling MySQL-compatible database and offers a generous free tier and consumption based billing once free limits are exceeded.
### Cluster plans

TiDB Cloud Serverless offers two service plans to meet different user requirements. Whether you are just getting started or scaling to meet the increasing application demands, these service plans provide the flexibility and capability you need.
#### Free cluster plan

The free cluster plan is ideal for those who are getting started with TiDB Cloud Serverless. It provides developers and small teams with the following essential features:

- **No cost**: This plan is completely free, with no credit card required to get started.
- **Storage**: Provides an initial 5 GiB of row-based storage and 5 GiB of columnar storage.
- **Request Units**: Includes 50 million [Request Units (RUs)](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-glossary#request-unit) for database operations.
- **Easy upgrade**: Offers a smooth transition to the [scalable cluster plan](#scalable-cluster-plan) as your needs grow.
#### Scalable cluster plan

For applications experiencing growing workloads and needing scalability in real time, the scalable cluster plan provides the flexibility and performance to keep pace with your business growth with the following features:

- **Enhanced capabilities**: Includes all capabilities of the free cluster plan, along with the capacity to handle larger and more complex workloads, as well as advanced security features.
- **Automatic scaling**: Automatically adjusts storage and computing resources to efficiently meet changing workload demands.
- **Predictable pricing**: Although this plan requires a credit card, you are only charged for the resources you use, ensuring cost-effective scalability.
### Usage quota

For each organization in TiDB Cloud, you can create a maximum of five [free clusters](#free-cluster-plan) by default. To create more TiDB Cloud Serverless clusters, you need to add a credit card and create [scalable clusters](#scalable-cluster-plan) for the usage.

For the first five TiDB Cloud Serverless clusters in your organization, whether they are free or scalable, TiDB Cloud provides a free usage quota for each of them as follows:

- Row-based storage: 5 GiB
- Columnar storage: 5 GiB
- Request Units (RUs): 50 million RUs per month

A Request Unit (RU) is a unit of measure used to represent the amount of resources consumed by a single request to the database. The amount of RUs consumed by a request depends on various factors, such as the operation type or the amount of data being retrieved or modified.

Once a cluster reaches its usage quota, it immediately denies any new connection attempts until you [increase the quota](https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-serverless-spend-limit#update-spending-limit) or the usage is reset upon the start of a new month. Existing connections established before reaching the quota will remain active but will experience throttling. For example, when the row-based storage of a cluster exceeds 5 GiB for a free cluster, the cluster automatically restricts any new connection attempts.

To learn more about the RU consumption of different resources (including read, write, SQL CPU, and network egress), the pricing details, and the throttled information, see [TiDB Cloud Serverless Pricing Details](https://www.pingcap.com/tidb-cloud-serverless-pricing-details).
### User name prefix

<!--Important: Do not update the section name "User name prefix" because this section is referenced by TiDB backend error messages.-->

For each TiDB Cloud Serverless cluster, TiDB Cloud generates a unique prefix to distinguish it from other clusters.

Whenever you use or set a database user name, you must include the prefix in the user name. For example, assume that the prefix of your cluster is `3pTAoNNegb47Uc8`.

- To connect to your cluster:

    ```shell
    mysql -u '3pTAoNNegb47Uc8.root' -h <host> -P 4000 -D test --ssl-mode=VERIFY_IDENTITY --ssl-ca=<CA_root_path> -p
    ```

    > **Note:**
    >
    > TiDB Cloud Serverless requires TLS connection. To find the CA root path on your system, see [Root certificate default path](https://docs.pingcap.com/tidb/stable/tidb-cloud/secure-connections-to-serverless-clusters#root-certificate-default-path).

- To create a database user:

    ```sql
    CREATE USER '3pTAoNNegb47Uc8.jeffrey';
    ```

To get the prefix for your cluster, take the following steps:

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page.
2. Click the name of your target cluster to go to its overview page, and then click **Connect** in the upper-right corner. A connection dialog is displayed.
3. In the dialog, get the prefix from the connection string.
### TiDB Cloud Serverless special terms and conditions

Some of TiDB Cloud features are partially supported or not supported on TiDB Cloud Serverless. See [TiDB Cloud Serverless Limitations](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-limitations) for details.
## TiDB Cloud Dedicated

TiDB Cloud Dedicated is for production use with the benefits of cross-zone high availability, horizontal scaling, and [HTAP](https://en.wikipedia.org/wiki/Hybrid_transactional/analytical_processing).

For TiDB Cloud Dedicated clusters, you can customize the cluster size of TiDB, TiKV, and TiFlash easily according to your business need. For each TiKV node and TiFlash node, the data on the node is replicated and distributed in different availability zones for [high availability](https://docs.pingcap.com/tidb/stable/tidb-cloud/high-availability-with-multi-az).

To create a TiDB Cloud Dedicated cluster, you need to [add a payment method](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing#payment-method) or [apply for a Proof of Concept (PoC) trial](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-poc).

> **Note:**
>
> You cannot decrease the node storage after your cluster is created.
