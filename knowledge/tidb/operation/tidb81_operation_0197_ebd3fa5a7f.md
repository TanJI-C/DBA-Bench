# Deploy cluster and verify managed cluster status

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/production-deployment-using-tiup.md`
- Source Title: `Deploy a TiDB Cluster Using TiUP`
- Source Heading Path: `Deploy a TiDB Cluster Using TiUP > Step 4. Run the deployment command | Deploy a TiDB Cluster Using TiUP > Step 5. Check the clusters managed by TiUP | Deploy a TiDB Cluster Using TiUP > Step 6. Check the status of the deployed TiDB cluster`
- Source Line Ranges: `314-386`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`
- Topic Tags: `deployment`, `precheck`, `auto-repair`, `authentication`, `cluster-list`, `cluster-status`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0197_ebd3fa5a7f`
- Source ID: `tidb-docs-8.1:production-deployment-using-tiup.md#step-4-run-the-deployment-command`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9805ae225504dd9333ca66e241c8ccd7514c51f1f5265ba3877d2839aa5a547c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup#step-4-run-the-deployment-command
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/production-deployment-using-tiup.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiUP commands for pre-deployment checks, automatic repair, cluster deployment, listing managed clusters, or displaying deployed cluster status.
- Retrieval Keywords: tiup cluster check ./topology.yaml --user root, tiup cluster check ./topology.yaml --apply --user root, tiup cluster deploy tidb-test v8.1.2 ./topology.yaml --user root, tiup list tidb, Deployed cluster `tidb-test` successfully, tiup cluster list, tiup cluster display tidb-test, --identity_file, -i, -p, --skip-create-user, Down, inactive
- Follow-up Guidance: The content states that `tiup cluster list` shows managed clusters and that `tiup cluster display tidb-test` shows instance ID, role, host, listening port, status, and directory information.
- Classification Note: This is classified as operation because the official content focuses on running deployment-related TiUP commands, authentication options, verification steps, and checking cluster management and status output.

## Official Source Content

## Step 4. Run the deployment command

> **Note:**
>
> You can use secret keys or interactive passwords for security authentication when you deploy TiDB using TiUP:
>
> - If you use secret keys, specify the path of the keys through `-i` or `--identity_file`.
> - If you use passwords, add the `-p` flag to enter the password interaction window.
> - If password-free login to the target machine has been configured, no authentication is required.
>
> In general, TiUP creates the user and group specified in the `topology.yaml` file on the target machine, with the following exceptions:
>
> - The user name configured in `topology.yaml` already exists on the target machine.
> - You have used the `--skip-create-user` option in the command line to explicitly skip the step of creating the user.

Before you run the `deploy` command, use the `check` and `check --apply` commands to detect and automatically repair potential risks in the cluster:

1. Check for potential risks:

    ```shell
    tiup cluster check ./topology.yaml --user root [-p] [-i /home/root/.ssh/gcp_rsa]
    ```

2. Enable automatic repair:

    ```shell
    tiup cluster check ./topology.yaml --apply --user root [-p] [-i /home/root/.ssh/gcp_rsa]
    ```

3. Deploy a TiDB cluster:

    ```shell
    tiup cluster deploy tidb-test v8.1.2 ./topology.yaml --user root [-p] [-i /home/root/.ssh/gcp_rsa]
    ```

In the `tiup cluster deploy` command above:

- `tidb-test` is the name of the TiDB cluster to be deployed.
- `v8.1.2` is the version of the TiDB cluster to be deployed. You can see the latest supported versions by running `tiup list tidb`.
- `topology.yaml` is the initialization configuration file.
- `--user root` indicates logging into the target machine as the `root` user to complete the cluster deployment. The `root` user is expected to have `ssh` and `sudo` privileges to the target machine. Alternatively, you can use other users with `ssh` and `sudo` privileges to complete the deployment.
- `[-i]` and `[-p]` are optional. If you have configured login to the target machine without password, these parameters are not required. If not, choose one of the two parameters. `[-i]` is the private key of the root user (or other users specified by `--user`) that has access to the target machine. `[-p]` is used to input the user password interactively.

At the end of the output log, you will see ```Deployed cluster `tidb-test` successfully```. This indicates that the deployment is successful.
## Step 5. Check the clusters managed by TiUP

```shell
tiup cluster list
```

TiUP supports managing multiple TiDB clusters. The preceding command outputs information of all the clusters currently managed by TiUP, including the cluster name, deployment user, version, and secret key information:
## Step 6. Check the status of the deployed TiDB cluster

For example, run the following command to check the status of the `tidb-test` cluster:

```shell
tiup cluster display tidb-test
```

Expected output includes the instance ID, role, host, listening port, and status (because the cluster is not started yet, so the status is `Down`/`inactive`), and directory information.
