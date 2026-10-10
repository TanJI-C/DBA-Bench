# Configure ProxySQL for TiDB Cloud on CentOS

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-proxysql-integration.md`
- Source Title: `ProxySQL Integration Guide`
- Source Heading Path: `Integrate TiDB with ProxySQL > Production environment > Integrate TiDB Cloud with ProxySQL on CentOS > Step 3. Configure ProxySQL > Option 1: Configure ProxySQL using the Admin Interface | Integrate TiDB with ProxySQL > Production environment > Integrate TiDB Cloud with ProxySQL on CentOS > Step 3. Configure ProxySQL > Option 2: Configure ProxySQL using a configuration file`
- Source Line Ranges: `680-792`
- Source Scope: `cloud`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`
- Topic Tags: `proxysql`, `admin-interface`, `configuration-file`, `hostgroup`, `mysql-users`, `runtime-load`, `disk-save`, `credentials`, `restart`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0051_7960b1e230`
- Source ID: `tidb-docs-8.1:develop/dev-guide-proxysql-integration.md#option-1-configure-proxysql-using-the-admin-interface`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6c46cbb28fda00ec37704bc63bd0d4294495525c64cd8c0999c5277fb3151e2c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-proxysql-integration#option-1-configure-proxysql-using-the-admin-interface
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-proxysql-integration.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how to configure ProxySQL for a TiDB Cloud Dedicated cluster on CentOS through the ProxySQL Admin interface or `/etc/proxysql.cnf`, including hostgroup, `mysql_servers`, `mysql_users`, runtime load, disk save, and restart details.
- Retrieval Keywords: ProxySQL Admin interface, port 6032, mysql -u admin -padmin -h 127.0.0.1 -P6032, INSERT INTO mysql_servers(hostgroup_id, hostname, port), LOAD mysql servers TO runtime, SAVE mysql servers TO DISK, INSERT INTO mysql_users, LOAD mysql users TO runtime, SAVE mysql users TO DISK, hostgroup_id, default_hostgroup, transaction_persistent, TiDB Cloud Dedicated cluster host, TiDB Cloud Dedicated cluster port, /etc/proxysql.cnf, rm /var/lib/proxysql/proxysql.db, mysql_servers, mysql_users, systemctl restart proxysql, admin_credentials
- Follow-up Guidance: The source also includes warnings about deleting `/var/lib/proxysql/proxysql.db` and about not running ProxySQL with default credentials in production, noting that `admin_credentials` can be changed in `/etc/proxysql.cnf` before starting the `proxysql` service.
- Classification Note: This is classified as configuration because the content provides concrete ProxySQL setup methods, SQL statements, configuration file fields, credential placeholders, and service restart details for integrating with TiDB Cloud.

## Official Source Content

##### Option 1: Configure ProxySQL using the Admin Interface

1. Reconfigure ProxySQL's internals using the standard ProxySQL Admin interface, accessible via any MySQL command line client (available by default on port `6032`):

    ```bash
    mysql -u admin -padmin -h 127.0.0.1 -P6032 --prompt 'ProxySQL Admin> '
    ```

    The above step will take you to the ProxySQL admin prompt.

2. Configure the TiDB clusters to be used, where you can add one or multiple TiDB clusters to ProxySQL. The following statement will add one TiDB Cloud Dedicated cluster for example. You need to replace `<tidb cloud dedicated cluster host>` and `<tidb cloud dedicated cluster port>` with your TiDB Cloud endpoint and port (the default port is `4000`).

    ```sql
    INSERT INTO mysql_servers(hostgroup_id, hostname, port) 
    VALUES 
      (
        0,
        '<tidb cloud dedicated cluster host>', 
        <tidb cloud dedicated cluster port>
      );
    LOAD mysql servers TO runtime;
    SAVE mysql servers TO DISK;
    ```

    > **Note:**
    >
    > - `hostgroup_id`:  specify an ID of the hostgroup. ProxySQL manages clusters using hostgroup. To distribute SQL traffic to these clusters evenly, you can configure several clusters that need load balancing to the same hostgroup. To distinguish the clusters, such as for read and write purposes, you can configure them to use different hostgroups.
    > - `hostname`: the endpoint of the TiDB cluster.
    > - `port`: the port of the TiDB cluster.

3. Configure Proxy login users to make sure that the users have appropriate permissions on the TiDB cluster. In the following statements, you need to replace '*tidb cloud dedicated cluster username*' and '*tidb cloud dedicated cluster password*' with the actual username and password of your cluster.

    ```sql
    INSERT INTO mysql_users(
      username, password, active, default_hostgroup, 
      transaction_persistent
    ) 
    VALUES 
      (
        '<tidb cloud dedicated cluster username>', 
        '<tidb cloud dedicated cluster password>', 
        1, 0, 1
      );
    LOAD mysql users TO runtime;
    SAVE mysql users TO DISK;
    ```

    > **Note:**
    >
    > - `username`: TiDB username.
    > - `password`: TiDB password.
    > - `active`: controls whether the user is active. `1` indicates that the user is **active** and can be used for login, while `0` indicates that the user is inactive.
    > - `default_hostgroup`: the default hostgroup used by the user, where SQL traffic is distributed unless the query rule overrides the traffic to a specific hostgroup.
    > - `transaction_persistent`: `1` indicates a persistent transaction. When a user starts a transaction within a connection, all query statements are routed to the same hostgroup until the transaction is committed or rolled back.
##### Option 2: Configure ProxySQL using a configuration file

This option should only be considered as an alternate method for configuring ProxySQL. For more information, see [Configuring ProxySQL through the config file](https://github.com/sysown/proxysql#configuring-proxysql-through-the-config-file).

1. Delete any existing SQLite database (where configurations are stored internally):

    ```bash
    rm /var/lib/proxysql/proxysql.db
    ```

    > **Warning:**
    >
    > If you delete the SQLite database file, any configuration changes made using ProxySQL Admin interface will be lost.

2. Modify the configuration file `/etc/proxysql.cnf` according to your need. For example:

    ```
    mysql_servers:
    (
        {
            address="<tidb cloud dedicated cluster host>"
            port=<tidb cloud dedicated cluster port>
            hostgroup=0
            max_connections=2000
        }
    )

    mysql_users:
    (
        {
            username = "<tidb cloud dedicated cluster username>"
            password = "<tidb cloud dedicated cluster password>"
            default_hostgroup = 0
            max_connections = 1000
            default_schema = "test"
            active = 1
            transaction_persistent = 1
        }
    )
    ```

    In the preceding example:

    - `address` and `port`: specify the endpoint and port of your TiDB Cloud cluster.
    - `username` and `password`: specify the username and password of your TiDB Cloud cluster.

3. Restart ProxySQL:

    ```bash
    systemctl restart proxysql
    ```

    After the restart, the SQLite database will be created automatically.

> **Warning:**
>
> Do not run ProxySQL with default credentials in production. Before starting the `proxysql` service, you can change the defaults in the `/etc/proxysql.cnf` file by changing the `admin_credentials` variable.
