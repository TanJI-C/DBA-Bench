# Self-hosted TiDB development integration with ProxySQL

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-proxysql-integration.md`
- Source Title: `ProxySQL Integration Guide`
- Source Heading Path: `Integrate TiDB with ProxySQL > Development environment > Option 2: Integrate TiDB (self-hosted) with ProxySQL`
- Source Line Ranges: `430-624`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `ecosystem`, `sql`
- Topic Tags: `proxysql`, `docker`, `self-hosted`, `connection`, `validation`, `mysql-client`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0049_46d736e6e1`
- Source ID: `tidb-docs-8.1:develop/dev-guide-proxysql-integration.md#option-2-integrate-tidb-self-hosted-with-proxysql`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9415043124805503c8827d51902272d6ea42c7aa09109015ecd12cbb6104d7ff`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-proxysql-integration#option-2-integrate-tidb-self-hosted-with-proxysql
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-proxysql-integration.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants the self-hosted TiDB development workflow for integrating ProxySQL with Docker, including ports 6033 and 4000, mysql connection syntax, and SELECT VERSION() validation.
- Retrieval Keywords: Integrate TiDB self-hosted with ProxySQL, tidb-proxysql-integration, git clone https://github.com/pingcap-inc/tidb-proxysql-integration.git, docker compose pull, docker compose up -d, ProxySQL 6033, TiDB 4000, mysql -u root -h 127.0.0.1 -P 6033, root username with an empty password, SELECT VERSION();, docker compose down
- Follow-up Guidance: The chunk also states that the integrated environment uses TiDB and ProxySQL Docker images and that ports 6033 and 4000 need to be available.
- Classification Note: This is classified as self-managed configuration because it covers a Docker-based integration of self-hosted TiDB with ProxySQL rather than TiDB Cloud.

## Official Source Content

### Option 2: Integrate TiDB (self-hosted) with ProxySQL

For this integration, you will set up an environment using Docker images of [TiDB](https://hub.docker.com/r/pingcap/tidb) and [ProxySQL](https://hub.docker.com/r/proxysql/proxysql). You are encouraged to try [other ways of installing TiDB (self-hosted)](https://docs.pingcap.com/tidb/stable/quick-start-with-tidb) in your own interest.

The following steps will set up ProxySQL and TiDB on ports `6033` and `4000` respectively, so make sure these ports are available.

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

2. Clone the [integration example code repository](https://github.com/pingcap-inc/tidb-proxysql-integration) for TiDB and ProxySQL:

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

3. Pull the latest images of ProxySQL and TiDB:

    <div label="macOS" value="macOS">

    ```bash
    cd tidb-proxysql-integration && docker compose pull
    ```

    </div>

    <div label="CentOS" value="CentOS">

    ```bash
    cd tidb-proxysql-integration && docker compose pull
    ```

    </div>

    <div label="Windows (Git Bash)" value="Windows">

    ```bash
    cd tidb-proxysql-integration && docker compose pull
    ```

    </div>

4. Start an integrated environment using both TiDB and ProxySQL running as containers:

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

    To log in to the ProxySQL `6033` port, you can use the `root` username with an empty password.

5. Connect to TiDB via ProxySQL:

    <div label="macOS" value="macOS">

    ```bash
    mysql -u root -h 127.0.0.1 -P 6033
    ```

    </div>

    <div label="CentOS" value="CentOS">

    ```bash
    mysql -u root -h 127.0.0.1 -P 6033
    ```

    </div>

    <div label="Windows (Git Bash)" value="Windows">

    ```bash
    mysql -u root -h 127.0.0.1 -P 6033
    ```

    </div>

6. After connecting to your TiDB cluster, you can use the following SQL statement to validate the connection:

    ```sql
    SELECT VERSION();
    ```

    If the TiDB version is displayed, you are successfully connected to your TiDB containers through ProxySQL.

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
