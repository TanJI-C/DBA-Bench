# Development setup and TiDB Cloud ProxySQL configuration generation

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-proxysql-integration.md`
- Source Title: `ProxySQL Integration Guide`
- Source Heading Path: `Integrate TiDB with ProxySQL > Development environment | Integrate TiDB with ProxySQL > Development environment > Prerequisites | Integrate TiDB with ProxySQL > Development environment > Option 1: Integrate TiDB Cloud with ProxySQL | Integrate TiDB with ProxySQL > Development environment > Option 1: Integrate TiDB Cloud with ProxySQL > Step 1. Create a {{{ .starter }}} cluster | Integrate TiDB with ProxySQL > Development environment > Option 1: Integrate TiDB Cloud with ProxySQL > Step 2. Generate ProxySQL configuration files`
- Source Line Ranges: `38-235`
- Source Scope: `developer`
- Primary Component: `cloud`
- Related Components: `ecosystem`, `tidb`, `shared`
- Topic Tags: `development-environment`, `prerequisites`, `docker`, `python`, `mysql-client`, `git`, `starter-cluster`, `proxysql-config`, `configuration-files`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0047_7e2a710943`
- Source ID: `tidb-docs-8.1:develop/dev-guide-proxysql-integration.md#development-environment`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2d58baa4b918551933eef3fc0a66cb326dce5b9c173706e6c7111db72a538e9c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-proxysql-integration#development-environment
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-proxysql-integration.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the development-environment prerequisites or the exact steps to generate ProxySQL configuration files for integrating TiDB Cloud with ProxySQL.
- Retrieval Keywords: Development environment, Prerequisites, Git, Docker, Python 3, Docker Compose, MySQL Client, Option 1: Integrate TiDB Cloud with ProxySQL, Starter cluster, port 16033, Create a free Starter cluster, Endpoint, Port, User, integration example code repository, tidb-proxysql-integration, tidb-cloud-connect, proxysql-config.py, tidb-cloud-connect.cnf, proxysql-prepare.sql, proxysql-connect.py, ProxySQL Docker image, Serverless Tier Host
- Follow-up Guidance: After creating the Starter cluster, the document says to copy the Endpoint, Port, and User from the Connection pane and then run proxysql-config.py in example/tidb-cloud-connect to generate three configuration files.
- Classification Note: This is classified as configuration because the content lists setup prerequisites and exact commands and inputs for generating ProxySQL configuration files in a development environment.

## Official Source Content

## Development environment

This section describes how to integrate TiDB with ProxySQL in a development environment. To get started with the ProxySQL integration, you can choose either of the following options depending on your TiDB cluster type after you have all the [prerequisites](#prerequisite) in place.

- Option 1: [Integrate TiDB Cloud with ProxySQL](#option-1-integrate-tidb-cloud-with-proxysql)
- Option 2: [Integrate TiDB (self-hosted) with ProxySQL](#option-2-integrate-tidb-self-hosted-with-proxysql)
### Prerequisites

Depending on the option you choose, you might need the following packages:

- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [Docker](https://docs.docker.com/get-docker/)
- [Python 3](https://www.python.org/downloads/)
- [Docker Compose](https://docs.docker.com/compose/install/linux/)
- [MySQL Client](https://dev.mysql.com/doc/refman/8.0/en/mysql.html)

You can follow the installation instructions as below:

<div label="macOS" value="macOS">

1. [Download](https://docs.docker.com/get-docker/) and start Docker (the Docker Desktop already includes the Docker Compose).
2. Run the following command to install Python and `mysql-client`:

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    brew install python mysql-client
    ```

</div>

<div label="CentOS" value="CentOS">

```bash
curl -fsSL https://get.docker.com | bash -s docker
yum install -y git python39 docker-ce docker-ce-cli containerd.io docker-compose-plugin mysql
systemctl start docker
```

</div>

<div label="Windows" value="Windows">

- Download and install Git.

    1. Download the **64-bit Git for Windows Setup** package from the [Git Windows Download](https://git-scm.com/download/win) page.
    2. Install the Git package by following the setup wizard. You can click **Next** for a few times to use the default installation settings.

        ![proxysql-windows-git-install](/media/develop/proxysql-windows-git-install.png)

- Download and install MySQL Shell.

    1. Download the ZIP file of MySQL Installer from the [MySQL Community Server Download](https://dev.mysql.com/downloads/mysql/) page.
    2. Unzip the file, and locate `mysql.exe` in the `bin` folder. You need to add the path of the `bin` folder to the system variable and set it into the `PATH` variable at Git Bash:

        ```bash
        echo 'export PATH="(your bin folder)":$PATH' >>~/.bash_profile
        source ~/.bash_profile
        ```

        For example:

        ```bash
        echo 'export PATH="/c/Program Files (x86)/mysql-8.0.31-winx64/bin":$PATH' >>~/.bash_profile
        source ~/.bash_profile
        ```

- Download and install Docker.

    1. Download Docker Desktop installer from the [Docker Download](https://www.docker.com/products/docker-desktop/) page.
    2. Double-click the installer to run it. After the installation is completed, you will be prompted for a restart.

        ![proxysql-windows-docker-install](/media/develop/proxysql-windows-docker-install.png)

- Download the latest Python 3 installer from the [Python Download](https://www.python.org/downloads/) page and run it.

</div>
### Option 1: Integrate TiDB Cloud with ProxySQL

For this integration, you will be using the [ProxySQL Docker image](https://hub.docker.com/r/proxysql/proxysql) along with a {{{ .starter }}} cluster. The following steps will set up ProxySQL on port `16033`, so make sure this port is available.
#### Step 1. Create a {{{ .starter }}} cluster

1. [Create a free {{{ .starter }}} cluster](https://docs.pingcap.com/tidbcloud/tidb-cloud-quickstart#step-1-create-a-tidb-cluster). Remember the root password that you set for your cluster.
2. Get your cluster hostname, port, and username for later use.

    1. On the [Clusters](https://tidbcloud.com/project/clusters) page, click your cluster name to go to the cluster overview page.
    2. On the cluster overview page, locate the **Connection** pane, and then copy the `Endpoint`, `Port`, and `User` fields, where the `Endpoint` is your cluster hostname.
#### Step 2. Generate ProxySQL configuration files

1. Clone the [integration example code repository](https://github.com/pingcap-inc/tidb-proxysql-integration) for TiDB and ProxySQL:

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

2. Change to the `tidb-cloud-connect` folder:

    <div label="macOS" value="macOS">

    ```bash
    cd tidb-proxysql-integration/example/tidb-cloud-connect
    ```

    </div>

    <div label="CentOS" value="CentOS">

    ```bash
    cd tidb-proxysql-integration/example/tidb-cloud-connect
    ```

    </div>

    <div label="Windows (Git Bash)" value="Windows">

    ```bash
    cd tidb-proxysql-integration/example/tidb-cloud-connect
    ```

    </div>

3. Generate ProxySQL configuration files by running `proxysql-config.py`:

    <div label="macOS" value="macOS">

    ```bash
    python3 proxysql-config.py
    ```

    </div>

    <div label="CentOS" value="CentOS">

    ```bash
    python3 proxysql-config.py
    ```

    </div>

    <div label="Windows (Git Bash)" value="Windows">

    ```bash
    python proxysql-config.py
    ```

    </div>

    When prompted, enter the endpoint of your cluster for `Serverless Tier Host`, and then enter the username and the password of your cluster.

    The following is an example output. You will see that three configuration files are generated under the current `tidb-cloud-connect` folder.

    ```
    [Begin] generating configuration files..
    tidb-cloud-connect.cnf generated successfully.
    proxysql-prepare.sql generated successfully.
    proxysql-connect.py generated successfully.
    [End] all files generated successfully and placed in the current folder.
    ```
