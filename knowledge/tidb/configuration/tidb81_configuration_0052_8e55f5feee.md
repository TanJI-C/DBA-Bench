# ProxySQL query rules setup and verification with TiDB containers

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-proxysql-integration.md`
- Source Title: `ProxySQL Integration Guide`
- Source Heading Path: `Integrate TiDB with ProxySQL > Typical scenario > Query rules`
- Source Line Ranges: `797-1128`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `sql`
- Topic Tags: `proxysql`, `query-rules`, `docker-compose`, `routing`, `regex`, `transactions`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0052_8e55f5feee`
- Source ID: `tidb-docs-8.1:develop/dev-guide-proxysql-integration.md#query-rules`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `38eb018b30ff075adb69a3a42218299f730f44241349e17264153675320431f6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-proxysql-integration#query-rules
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-proxysql-integration.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the documented ProxySQL query rules example that sets up TiDB containers, configures regex-based routing with proxysql-prepare.sql, and verifies which hostgroup handles SELECT, SELECT ... FOR UPDATE, and transaction statements.
- Retrieval Keywords: ProxySQL query rules, proxysql-prepare.sql, docker compose up -d, proxy-rule-admin-interface, mysql -uadmin -padmin -h127.0.0.1 -P6032, mysql -u root -h 127.0.0.1 -P 6034, hostgroup 0, hostgroup 1, rule_id 1, rule_id 2, ^SELECT.*FOR UPDATE$, ^SELECT, default_hostgroup, transaction_persistent, test.tidb_server, tidb-server01-port-4001, tidb-server02-port-4002, SELECT * FROM test.tidb_server FOR UPDATE, BEGIN; INSERT INTO test.tidb_server
- Follow-up Guidance: The chunk also includes cleanup with docker compose down and cd -, plus references to ProxySQL documentation for mysql_query_rules and mysql-query_processor_regex.
- Classification Note: This is classified as configuration because the content walks through configuring ProxySQL Admin Interface query rules, users, hostgroups, and verification commands for routing SQL statements to TiDB containers.

## Official Source Content

### Query rules

Databases can be overloaded by high traffic, faulty code, or malicious spam. With query rules of ProxySQL, you can respond to these issues quickly and effectively by rerouting, rewriting, or rejecting queries.

![proxysql-client-side-rules](/media/develop/proxysql-client-side-rules.png)

> **Note:**
>
> In the following steps, you will be using the container images of TiDB and ProxySQL to configure query rules. If you have not pulled them, you can check the [integration section](#option-2-integrate-tidb-self-hosted-with-proxysql) for detailed steps.

1. Clone the [integration example code repository](https://github.com/pingcap-inc/tidb-proxysql-integration) for TiDB and ProxySQL. Skip this step if you have already cloned it in the previous steps.

    <div label="macOS" value="macOS">

    ```bash
    git clone https://github.com/pingcap-inc/tidb-proxysql-integration.git
    ```

    </div>

    <div label="CentOS" value="CentOS">

    ```bash
    git clone https://github.com/pingcap-inc/tidb-proxysql-integration.git
    ```

    </div>

    <div label="Windows (Git Bash)" value="Windows">

    ```bash
    git clone https://github.com/pingcap-inc/tidb-proxysql-integration.git
    ```

    </div>

2. Change to the example directory for ProxySQL rules:

    <div label="macOS" value="macOS">

    ```bash
    cd tidb-proxysql-integration/example/proxy-rule-admin-interface
    ```

    </div>

    <div label="CentOS" value="CentOS">

    ```bash
    cd tidb-proxysql-integration/example/proxy-rule-admin-interface
    ```

    </div>

    <div label="Windows (Git Bash)" value="Windows">

    ```bash
    cd tidb-proxysql-integration/example/proxy-rule-admin-interface
    ```

    </div>

3. Run the following command to start two TiDB containers and a ProxySQL container:

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

    If everything goes well, the following containers are started:

    - Two Docker containers of TiDB clusters exposed via ports `4001`, `4002`
    - One ProxySQL Docker container exposed via port `6034`.

4. In the two TiDB containers, using `mysql` to create a table with a similar schema definition and then insert different data (`'tidb-server01-port-4001'`, `'tidb-server02-port-4002'`) to identify these containers.

    <div label="macOS" value="macOS">

    ```bash
    mysql -u root -h 127.0.0.1 -P 4001 << EOF
    DROP TABLE IF EXISTS test.tidb_server;
    CREATE TABLE test.tidb_server (server_name VARCHAR(255));
    INSERT INTO test.tidb_server (server_name) VALUES ('tidb-server01-port-4001');
    EOF

    mysql -u root -h 127.0.0.1 -P 4002 << EOF
    DROP TABLE IF EXISTS test.tidb_server;
    CREATE TABLE test.tidb_server (server_name VARCHAR(255));
    INSERT INTO test.tidb_server (server_name) VALUES ('tidb-server02-port-4002');
    EOF
    ```

    </div>

    <div label="CentOS" value="CentOS">

    ```bash
    mysql -u root -h 127.0.0.1 -P 4001 << EOF
    DROP TABLE IF EXISTS test.tidb_server;
    CREATE TABLE test.tidb_server (server_name VARCHAR(255));
    INSERT INTO test.tidb_server (server_name) VALUES ('tidb-server01-port-4001');
    EOF

    mysql -u root -h 127.0.0.1 -P 4002 << EOF
    DROP TABLE IF EXISTS test.tidb_server;
    CREATE TABLE test.tidb_server (server_name VARCHAR(255));
    INSERT INTO test.tidb_server (server_name) VALUES ('tidb-server02-port-4002');
    EOF
    ```

    </div>

    <div label="Windows (Git Bash)" value="Windows">

    ```bash
    mysql -u root -h 127.0.0.1 -P 4001 << EOF
    DROP TABLE IF EXISTS test.tidb_server;
    CREATE TABLE test.tidb_server (server_name VARCHAR(255));
    INSERT INTO test.tidb_server (server_name) VALUES ('tidb-server01-port-4001');
    EOF

    mysql -u root -h 127.0.0.1 -P 4002 << EOF
    DROP TABLE IF EXISTS test.tidb_server;
    CREATE TABLE test.tidb_server (server_name VARCHAR(255));
    INSERT INTO test.tidb_server (server_name) VALUES ('tidb-server02-port-4002');
    EOF
    ```

    </div>

5. Configure ProxySQL by running the following command, which executes `proxysql-prepare.sql` inside ProxySQL Admin Interface to establish a proxy connection between the TiDB containers and ProxySQL.

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
    > The `proxysql-prepare.sql` does the following:
    >
    > - Adds the TiDB clusters in ProxySQL with `hostgroup_id` as `0` and `1`.
    > - Adds a user `root` with an empty password and sets `default_hostgroup` as `0`.
    > - Adds the rule `^SELECT.*FOR UPDATE$` with `rule_id` as `1` and `destination_hostgroup` as `0`. If a SQL statement matches this rule, the request will be forwarded to the TiDB cluster with `hostgroup` as `0`.
    > - Adds the rule `^SELECT` with `rule_id` as `2` and `destination_hostgroup` as `1`. If a SQL statement matches this rule, the request will be forwarded to the TiDB cluster with `hostgroup` as `1`.
    >
    > To have a better understanding, it is strongly recommended that you check the `proxysql-prepare.sql` file. To learn more about ProxySQL configuration, see [ProxySQL documentation](https://proxysql.com/documentation/proxysql-configuration/).

    The following is some additional information about how ProxySQL patterns match query rules:

    - ProxySQL tries to match the rules one by one in the ascending order of `rule_id`.
    - `^` symbol matches the beginning of a SQL statement and `$` matches the end.

    For more information about ProxySQL regular expression and pattern matching, see [mysql-query_processor_regex](https://proxysql.com/documentation/global-variables/mysql-variables/#mysql-query_processor_regex) in ProxySQL documentation.

    For a full list of parameters, see [mysql_query_rules](https://proxysql.com/documentation/main-runtime/#mysql_query_rules) in ProxySQL documentation.

6. Verify the configuration and check whether the query rules work.

    1. Log into ProxySQL MySQL Interface as the `root` user:

        <div label="macOS" value="macOS">

        ```bash
        mysql -u root -h 127.0.0.1 -P 6034
        ```

        </div>

        <div label="CentOS" value="CentOS">

        ```bash
        mysql -u root -h 127.0.0.1 -P 6034
        ```

        </div>

        <div label="Windows (Git Bash)" value="Windows">

        ```bash
        mysql -u root -h 127.0.0.1 -P 6034
        ```

        </div>

    2. Execute the following SQL statements:

        - Execute a `SELECT` statement:
            ```sql
            SELECT * FROM test.tidb_server;
            ```

            This statement will match rule_id `2` and forward the statement to the TiDB cluster on `hostgroup 1`.

        - Execute a `SELECT ... FOR UPDATE` statement:

            ```sql
            SELECT * FROM test.tidb_server FOR UPDATE;
            ```

            This statement will match rule_id `1` and forward the statement to the TiDB cluster on `hostgroup 0`.

        - Start a transaction:

            ```sql
            BEGIN;
            INSERT INTO test.tidb_server (server_name) VALUES ('insert this and rollback later');
            SELECT * FROM test.tidb_server;
            ROLLBACK;
            ```

            In this transaction, the `BEGIN` statement will not match any rules. It uses the default hostgroup (`hostgroup 0` in this example). Because ProxySQL enables user transaction_persistent by default, which will execute all statements within the same transaction in the same hostgroup, the `INSERT` and `SELECT * FROM test.tidb_server;` statements will also be forwarded to the TiDB cluster `hostgroup 0`.

        The following is an example output. If you get a similar output, you have successfully configured the query rules with ProxySQL.

        ```sql
        +-------------------------+
        | server_name             |
        +-------------------------+
        | tidb-server02-port-4002 |
        +-------------------------+
        +-------------------------+
        | server_name             |
        +-------------------------+
        | tidb-server01-port-4001 |
        +-------------------------+
        +--------------------------------+
        | server_name                    |
        +--------------------------------+
        | tidb-server01-port-4001        |
        | insert this and rollback later |
        +--------------------------------+
        ```

    3. To exit from the MySQL client anytime, enter `quit` and press <kbd>enter</kbd>.

7. To stop and remove containers, and go to the previous directory, run the following command:

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
