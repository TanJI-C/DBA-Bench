# TiDB Cloud development ProxySQL setup and connection

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-proxysql-integration.md`
- Source Title: `ProxySQL Integration Guide`
- Source Heading Path: `Integrate TiDB with ProxySQL > Development environment > Option 1: Integrate TiDB Cloud with ProxySQL > Step 3. Configure ProxySQL | Integrate TiDB with ProxySQL > Development environment > Option 1: Integrate TiDB Cloud with ProxySQL > Step 4. Connect to your TiDB cluster through ProxySQL`
- Source Line Ranges: `236-429`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`, `sql`
- Topic Tags: `proxysql`, `docker`, `admin-interface`, `connection`, `validation`, `mysql-client`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0048_9e2ce73391`
- Source ID: `tidb-docs-8.1:develop/dev-guide-proxysql-integration.md#step-3-configure-proxysql`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `11630474ce3c127d3da8c1b416c649e7c1642657b87ec011cab3b6167a41dca7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-proxysql-integration#step-3-configure-proxysql
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-proxysql-integration.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the TiDB Cloud development steps to configure ProxySQL with Docker, run proxysql-prepare.sql through the ProxySQL Admin Interface, connect with proxysql-connect.py, and validate connectivity with SELECT VERSION().
- Retrieval Keywords: TiDB Cloud ProxySQL development environment, docker compose up -d, docker compose exec proxysql, mysql -uadmin -padmin -h127.0.0.1 -P6032, proxysql-prepare.sql, ProxySQL Admin Interface, proxysql-connect.py, SELECT VERSION();, tidb-cloud-connect.cnf, gateway01.us-west-2.prod.aws.tidbcloud.com, use_ssl: 1, docker compose down
- Follow-up Guidance: The chunk also includes debugging guidance to check tidb-cloud-connect.cnf, proxysql-prepare.sql, and proxysql-connect.py if connection to the cluster fails.
- Classification Note: This is classified as cloud configuration because it describes configuring and testing a TiDB Cloud cluster connection through ProxySQL in a development environment.

## Official Source Content

#### Step 3. Configure ProxySQL

1. Start Docker. If Docker has already started, skip this step:

    <div label="macOS" value="macOS">

    Double-click the icon of the installed Docker to start it.

    </div>

    <div label="CentOS" value="CentOS">

    ```bash
    systemctl start docker
    ```

    </div>

    <div label="Windows" value="Windows">

    Double-click the icon of the installed Docker to start it.

    </div>

2. Pull the ProxySQL image and start a ProxySQL container in the background:

    <div label="macOS" value="macOS">

    ```bash
    docker compose up -d
    ```

    </div>

    <div label="CentOS" value="CentOS">

    ```bash
    docker compose up -d
    ```

    </div>

    <div label="Windows (Git Bash)" value="Windows">

    ```bash
    docker compose up -d
    ```

    </div>

3. Integrate with ProxySQL by running the following command, which executes `proxysql-prepare.sql` inside **ProxySQL Admin Interface**:

    <div label="macOS" value="macOS">

    ```bash
    docker compose exec proxysql sh -c "mysql -uadmin -padmin -h127.0.0.1 -P6032 < ./proxysql-prepare.sql"
    ```

    </div>

    <div label="CentOS" value="CentOS">

    ```bash
    docker compose exec proxysql sh -c "mysql -uadmin -padmin -h127.0.0.1 -P6032 < ./proxysql-prepare.sql"
    ```

    </div>

    <div label="Windows (Git Bash)" value="Windows">

    ```bash
    docker compose exec proxysql sh -c "mysql -uadmin -padmin -h127.0.0.1 -P6032 < ./proxysql-prepare.sql"
    ```

    </div>

    > **Note:**
    >
    > The `proxysql-prepare.sql` script does the following:
    >
    > 1. Adds a user using the username and password of your cluster.
    > 2. Assigns the user to the monitoring account.
    > 3. Adds your {{{ .starter }}} cluster to the list of hosts.
    > 4. Enables a secure connection between ProxySQL and the {{{ .starter }}} cluster.
    >
    > To have a better understanding, it is strongly recommended that you check the `proxysql-prepare.sql` file. To learn more about ProxySQL configuration, see [ProxySQL documentation](https://proxysql.com/documentation/proxysql-configuration/).

    The following is an example output. You will see that the hostname of your cluster is shown in the output, which means that the connectivity between ProxySQL and the {{{ .starter }}} cluster is established.

    ```
    *************************** 1. row ***************************
        hostgroup_id: 0
            hostname: gateway01.us-west-2.prod.aws.tidbcloud.com
                port: 4000
            gtid_port: 0
                status: ONLINE
                weight: 1
            compression: 0
        max_connections: 1000
    max_replication_lag: 0
                use_ssl: 1
        max_latency_ms: 0
                comment:
    ```
#### Step 4. Connect to your TiDB cluster through ProxySQL

1. To connect to your TiDB cluster, run `proxysql-connect.py`. The script will automatically launch the MySQL client and use the username and password you specified in [Step 2](#step-2-generate-proxysql-configuration-files) for connection.

    <div label="macOS" value="macOS">

    ```bash
    python3 proxysql-connect.py
    ```

    </div>

    <div label="CentOS" value="CentOS">

    ```bash
    python3 proxysql-connect.py
    ```

    </div>

    <div label="Windows (Git Bash)" value="Windows">

    ```bash
    python proxysql-connect.py
    ```

    </div>

2. After connecting to your TiDB cluster, you can use the following SQL statement to validate the connection:

    ```sql
    SELECT VERSION();
    ```

    If the TiDB version is displayed, you are successfully connected to your {{{ .starter }}} cluster through ProxySQL. To exit from the MySQL client anytime, enter `quit` and press <kbd>enter</kbd>.

    > **Note:**
    >
    > ***For Debugging:*** If you are unable to connect to the cluster, check the files `tidb-cloud-connect.cnf`, `proxysql-prepare.sql`, and `proxysql-connect.py`. Make sure that the server information you provided is available and correct.

3. To stop and remove containers, and go to the previous directory, run the following command:

    <div label="macOS" value="macOS">

    ```bash
    docker compose down
    cd -
    ```

    </div>

    <div label="CentOS" value="CentOS">

    ```bash
    docker compose down
    cd -
    ```

    </div>

    <div label="Windows (Git Bash)" value="Windows">

    ```bash
    docker compose down
    cd -
    ```

    </div>
