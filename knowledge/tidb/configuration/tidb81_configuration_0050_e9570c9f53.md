# Production TiDB Cloud Dedicated ProxySQL installation prerequisites

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-proxysql-integration.md`
- Source Title: `ProxySQL Integration Guide`
- Source Heading Path: `Integrate TiDB with ProxySQL > Production environment | Integrate TiDB with ProxySQL > Production environment > Prerequisite | Integrate TiDB with ProxySQL > Production environment > Integrate TiDB Cloud with ProxySQL on CentOS | Integrate TiDB with ProxySQL > Production environment > Integrate TiDB Cloud with ProxySQL on CentOS > Step 1. Create a TiDB Cloud Dedicated cluster | Integrate TiDB with ProxySQL > Production environment > Integrate TiDB Cloud with ProxySQL on CentOS > Step 2. Install ProxySQL | Integrate TiDB with ProxySQL > Production environment > Integrate TiDB Cloud with ProxySQL on CentOS > Step 3. Configure ProxySQL`
- Source Line Ranges: `625-679`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `proxysql`, `production`, `centos`, `installation`, `prerequisites`, `dedicated`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0050_e9570c9f53`
- Source ID: `tidb-docs-8.1:develop/dev-guide-proxysql-integration.md#production-environment`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bbaa0d43974e2da4d66863d5ce88846c4326b8961441d0c90090a93bbb76cce0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-proxysql-integration#production-environment
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-proxysql-integration.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks for production-oriented TiDB Cloud Dedicated ProxySQL prerequisites and CentOS installation and initial configuration entry points, including MySQL client setup, YUM installation, and the two ProxySQL configuration methods.
- Retrieval Keywords: Production environment ProxySQL TiDB Cloud Dedicated, Prerequisite MySQL client, MySQL Shell, Integrate TiDB Cloud with ProxySQL on CentOS, proxysql.repo, https://repo.proxysql.com/ProxySQL/proxysql-2.4.x/centos/$releasever, yum install -y proxysql, systemctl start proxysql, Create a TiDB Cluster, execute SQL statements inside ProxySQL Admin Interface, configure ProxySQL using a configuration file, required configuration items of ProxySQL
- Follow-up Guidance: The chunk points to the next step of configuring ProxySQL either by executing SQL statements inside the ProxySQL Admin Interface or by using a configuration file.
- Classification Note: This is classified as cloud configuration because it introduces production-environment prerequisites and installation steps for using ProxySQL with a TiDB Cloud Dedicated cluster on CentOS.

## Official Source Content

## Production environment

For a production environment, it is recommended that you use [TiDB Cloud Dedicated](https://www.pingcap.com/tidb-cloud-dedicated/) directly for a fully-managed experience.
### Prerequisite

Download and install a MySQL client. For example, [MySQL Shell](https://dev.mysql.com/downloads/shell/).
### Integrate TiDB Cloud with ProxySQL on CentOS

ProxySQL can be installed on many different platforms. The following takes CentOS as an example.

For a full list of supported platforms and the corresponding version requirements, see [ProxySQL documentation](https://proxysql.com/documentation/installing-proxysql/).
#### Step 1. Create a TiDB Cloud Dedicated cluster

For detailed steps, see [Create a TiDB Cluster](https://docs.pingcap.com/tidbcloud/create-tidb-cluster).
#### Step 2. Install ProxySQL

1. Add ProxySQL to the YUM repository:

    ```bash
    cat > /etc/yum.repos.d/proxysql.repo << EOF
    [proxysql]
    name=ProxySQL YUM repository
    baseurl=https://repo.proxysql.com/ProxySQL/proxysql-2.4.x/centos/\$releasever
    gpgcheck=1
    gpgkey=https://repo.proxysql.com/ProxySQL/proxysql-2.4.x/repo_pub_key
    EOF
    ```

2. Install ProxySQL:

    ```bash
    yum install -y proxysql
    ```

3. Start ProxySQL:

    ```bash
    systemctl start proxysql
    ```

To learn more about the supported platforms of ProxySQL and their installation, refer to [ProxySQL README](https://github.com/sysown/proxysql#installation) or [ProxySQL installation documentation](https://proxysql.com/documentation/installing-proxysql/).
#### Step 3. Configure ProxySQL

To use ProxySQL as a proxy for TiDB, you need to configure ProxySQL. To do so, you can either [execute SQL statements inside ProxySQL Admin Interface](#option-1-configure-proxysql-using-the-admin-interface) (recommended) or use the [configuration file](#option-2-configure-proxysql-using-a-configuration-file).

> **Note:**
>
> The following sections list only the required configuration items of ProxySQL.
> For a comprehensive list of configurations, see [ProxySQL documentation](https://proxysql.com/documentation/proxysql-configuration/).
