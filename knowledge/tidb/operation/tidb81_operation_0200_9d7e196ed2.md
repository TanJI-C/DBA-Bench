# Deploy and access a local TiUP Playground test cluster

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/quick-start-with-tidb.md`
- Source Title: `Quick Start Guide for the TiDB Database Platform`
- Source Heading Path: `Quick Start Guide for the TiDB Database Platform > Deploy a local test cluster`
- Source Line Ranges: `23-280`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `dashboard`
- Topic Tags: `local-cluster`, `playground`, `installation`, `startup`, `connection`, `monitoring`, `grafana`, `prometheus`, `cleanup`, `network-binding`, `version-specific`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0200_9d7e196ed2`
- Source ID: `tidb-docs-8.1:quick-start-with-tidb.md#deploy-a-local-test-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `76835f9c8e3ecfb304c9d3577172797afde18421aa99f86304f4f84bd95faa7b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/quick-start-with-tidb#deploy-a-local-test-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/quick-start-with-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when someone needs the exact TiUP Playground commands and access details to deploy, connect to, monitor, persist, or clean up a local TiDB test cluster on macOS or Linux.
- Retrieval Keywords: Deploy a local test cluster, TiUP Playground, curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh, source ${your_shell_profile}, tiup playground, tiup playground v8.1.2 --db 2 --pd 3 --kv 3, tiup playground --tag ${tag_name}, tiup list tidb, tiup client, mysql --host 127.0.0.1 --port 4000 -u root, http://127.0.0.1:9090, http://127.0.0.1:2379/dashboard, http://127.0.0.1:3000, tiup clean --all, --host, 127.0.0.1, Apple M1 chip
- Follow-up Guidance: The chunk also provides the default TiDB Dashboard credentials, Grafana credentials, Prometheus and Dashboard URLs, the `--tag` option for persisting data, and the `--host` parameter for external accessibility.
- Classification Note: The classification is operation because the content gives step-by-step commands and runtime access details for deploying and using a local TiUP Playground cluster.

## Official Source Content

## Deploy a local test cluster

- Scenario: Quickly deploy a local TiDB cluster for testing using a single macOS or Linux server. By deploying such a cluster, you can learn the basic architecture of TiDB and the operation of its components, such as TiDB, TiKV, PD, and the monitoring components.

<div label="macOS">

As a distributed system, a basic TiDB test cluster usually consists of 2 TiDB instances, 3 TiKV instances, 3 PD instances, and optional TiFlash instances. With TiUP Playground, you can quickly build the test cluster by following these steps:

1. Download and install TiUP:

    ```shell
    curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh
    ```

    If the following message is displayed, you have successfully installed TiUP:

    ```log
    Successfully set mirror to https://tiup-mirrors.pingcap.com
    Detected shell: zsh
    Shell profile:  /Users/user/.zshrc
    /Users/user/.zshrc has been modified to add tiup to PATH
    open a new terminal or source /Users/user/.zshrc to use it
    Installed path: /Users/user/.tiup/bin/tiup
    ===============================================
    Have a try:     tiup playground
    ===============================================
    ```

    Note the Shell profile path in the output above. You need to use the path in the next step.

2. Declare the global environment variable:

    > **Note:**
    >
    > After the installation, TiUP displays the absolute path of the corresponding Shell profile file. You need to modify `${your_shell_profile}` in the following `source` command according to the path. In this case, `${your_shell_profile}` is `/Users/user/.zshrc` from the output of Step 1.

    ```shell
    source ${your_shell_profile}
    ```

3. Start the cluster in the current session:

    > **Note:**
    >
    > - For the playground operated in the following way, after the deployment and testing are finished, TiUP will automatically clean up the cluster data. You will get a new cluster after re-running the command.
    > - If you want to persist data on storage, then add the `--tag` flag when you start the cluster. For details, see [Specify a tag when starting the TiDB cluster to store the data](https://docs.pingcap.com/tidb/stable/tiup/tiup-playground#specify-a-tag-when-starting-the-tidb-cluster-to-store-the-data).
    >
    >     ```shell
    >     tiup playground --tag ${tag_name}
    >     ```

    - To start a TiDB cluster of the latest version with 1 TiDB instance, 1 TiKV instance, 1 PD instance, and 1 TiFlash instance, run the following command:

        ```shell
        tiup playground
        ```

    - To specify the TiDB version and the number of instances of each component, run a command like this:

        ```shell
        tiup playground v8.1.2 --db 2 --pd 3 --kv 3
        ```

        The command downloads a version cluster to the local machine and starts it, such as v8.1.2. To view the latest version, run `tiup list tidb`.

        This command returns the access methods of the cluster:

        ```log
        CLUSTER START SUCCESSFULLY, Enjoy it ^-^
        To connect TiDB: mysql --comments --host 127.0.0.1 --port 4001 -u root -p (no password)
        To connect TiDB: mysql --comments --host 127.0.0.1 --port 4000 -u root -p (no password)
        To view the dashboard: http://127.0.0.1:2379/dashboard
        PD client endpoints: [127.0.0.1:2379 127.0.0.1:2382 127.0.0.1:2384]
        To view Prometheus: http://127.0.0.1:9090
        To view Grafana: http://127.0.0.1:3000
        ```

        > **Note:**
        >
        > Starting from v5.2.0, TiDB supports running `tiup playground` on the machine that uses the Apple M1 chip.

4. Start a new session to access TiDB:

    + Use the TiUP client to connect to TiDB.

        ```shell
        tiup client
        ```

    + Alternatively, you can use the MySQL client to connect to TiDB.

        ```shell
        mysql --host 127.0.0.1 --port 4000 -u root
        ```

5. Access the Prometheus dashboard of TiDB at <http://127.0.0.1:9090>.

6. Access the [TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-intro) at <http://127.0.0.1:2379/dashboard>. The default username is `root`, and the password is empty.

7. Access the Grafana dashboard of TiDB through <http://127.0.0.1:3000>. Both the default username and password are `admin`.

8. (Optional) [Load data to TiFlash](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview#use-tiflash) for analysis.

9. Clean up the cluster after the test deployment:

    1. Stop the above TiDB service by pressing <kbd>Control+C</kbd>.

    2. Run the following command after the service is stopped:

        ```shell
        tiup clean --all
        ```

> **Note:**
>
> TiUP Playground listens on `127.0.0.1` by default, and the service is only locally accessible. If you want the service to be externally accessible, specify the listening address using the `--host` parameter to bind the network interface card (NIC) to an externally accessible IP address.

</div>
<div label="Linux">

As a distributed system, a basic TiDB test cluster usually consists of 2 TiDB instances, 3 TiKV instances, 3 PD instances, and optional TiFlash instances. With TiUP Playground, you can quickly build the test cluster by following these steps:

1. Download and install TiUP:

    ```shell
    curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh
    ```

    If the following message is displayed, you have successfully installed TiUP:

    ```log
    Successfully set mirror to https://tiup-mirrors.pingcap.com
    Detected shell: zsh
    Shell profile:  /Users/user/.zshrc
    /Users/user/.zshrc has been modified to add tiup to PATH
    open a new terminal or source /Users/user/.zshrc to use it
    Installed path: /Users/user/.tiup/bin/tiup
    ===============================================
    Have a try:     tiup playground
    ===============================================
    ```

    Note the Shell profile path in the output above. You need to use the path in the next step.

2. Declare the global environment variable:

    > **Note:**
    >
    > After the installation, TiUP displays the absolute path of the corresponding Shell profile file. You need to modify `${your_shell_profile}` in the following `source` command according to the path.

    ```shell
    source ${your_shell_profile}
    ```

3. Start the cluster in the current session:

    > **Note:**
    >
    > - For the playground operated in the following way, after the deployment and testing are finished, TiUP will automatically clean up the cluster data. You will get a new cluster after re-running the command.
    > - If you want to persist data on storage, then add the `--tag` flag when you start the cluster. For details, see [Specify a tag when starting the TiDB cluster to store the data](https://docs.pingcap.com/tidb/stable/tiup/tiup-playground#specify-a-tag-when-starting-the-tidb-cluster-to-store-the-data).
    >
    >     ```shell
    >     tiup playground --tag ${tag_name}
    >     ```

    - To start a TiDB cluster of the latest version with 1 TiDB instance, 1 TiKV instance, 1 PD instance, and 1 TiFlash instance, run the following command:
        ```shell
        tiup playground
        ```

    - To specify the TiDB version and the number of instances of each component, run a command like this:

        ```shell
        tiup playground v8.1.2 --db 2 --pd 3 --kv 3
        ```

        The command downloads a version cluster to the local machine and starts it, such as v8.1.2. To view the latest version, run `tiup list tidb`.

        This command returns the access methods of the cluster:

        ```log
        CLUSTER START SUCCESSFULLY, Enjoy it ^-^
        To connect TiDB: mysql --host 127.0.0.1 --port 4000 -u root -p (no password) --comments
        To view the dashboard: http://127.0.0.1:2379/dashboard
        PD client endpoints: [127.0.0.1:2379]
        To view the Prometheus: http://127.0.0.1:9090
        To view the Grafana: http://127.0.0.1:3000
        ```

4. Start a new session to access TiDB:

    + Use the TiUP client to connect to TiDB.

        ```shell
        tiup client
        ```

    + Alternatively, you can use the MySQL client to connect to TiDB.

        ```shell
        mysql --host 127.0.0.1 --port 4000 -u root
        ```

5. Access the Prometheus dashboard of TiDB at <http://127.0.0.1:9090>.

6. Access the [TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-intro) at <http://127.0.0.1:2379/dashboard>. The default username is `root`, and the password is empty.

7. Access the Grafana dashboard of TiDB through <http://127.0.0.1:3000>. Both the default username and password are `admin`.

8. (Optional) [Load data to TiFlash](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview#use-tiflash) for analysis.

9. Clean up the cluster after the test deployment:

    1. Stop the process by pressing <kbd>Control+C</kbd>.

    2. Run the following command after the service is stopped:

        ```shell
        tiup clean --all
        ```

> **Note:**
>
> TiUP Playground listens on `127.0.0.1` by default, and the service is only locally accessible. If you want the service to be externally accessible, specify the listening address using the `--host` parameter to bind the network interface card (NIC) to an externally accessible IP address.

</div>
