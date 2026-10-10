# Deploy, start, verify, and manage a DM cluster with TiUP

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/deploy-a-dm-cluster-using-tiup.md`
- Source Title: `Deploy a DM Cluster Using TiUP`
- Source Heading Path: `Deploy a DM Cluster Using TiUP > Step 3: Execute the deployment command | Deploy a DM Cluster Using TiUP > Step 4: Check the clusters managed by TiUP | Deploy a DM Cluster Using TiUP > Step 5: Check the status of the deployed DM cluster | Deploy a DM Cluster Using TiUP > Step 6: Start the DM cluster | Deploy a DM Cluster Using TiUP > Step 7: Verify the running status of the DM cluster | Deploy a DM Cluster Using TiUP > Step 8: Managing migration tasks using dmctl | Deploy a DM Cluster Using TiUP > Step 9: Encrypt the database password`
- Source Line Ranges: `150-237`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`
- Topic Tags: `deployment-command`, `authentication`, `cluster-list`, `status-check`, `start`, `verification`, `dmctl`, `password-encryption`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0082_eff9003ca2`
- Source ID: `tidb-docs-8.1:dm/deploy-a-dm-cluster-using-tiup.md#step-3-execute-the-deployment-command`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5b76af91bbca846f2a3d557fb9518f2e6b08ecb945f7ec571041c87967a5cf7c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/deploy-a-dm-cluster-using-tiup#step-3-execute-the-deployment-command
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/deploy-a-dm-cluster-using-tiup.md

## Retrieval Guidance

- Use When: Use this chunk when you need the official TiUP commands to deploy, list, display, start, verify, or manage a DM cluster after topology configuration.
- Retrieval Keywords: tiup dm deploy ${name} ${version} ./topology.yaml -u ${ssh_user}, -p, --password, -i, --identity_file, tiup list dm-master, Deployed cluster `dm-test` successfully, tiup dm list, tiup dm display dm-test, Status Down, Status inactive, tiup dm start dm-test, Started cluster `dm-test` successfully, Status Up, dmctl, use dmctl via TiUP, Encrypt the database password
- Follow-up Guidance: For password encryption after deployment, the source points to the documentation for `Encrypt the database password`.
- Classification Note: This is classified as an operation chunk because the content provides operational TiUP and dmctl commands for deploying, checking, starting, and verifying a DM cluster.

## Official Source Content

## Step 3: Execute the deployment command

> **Note:**
>
> You can use secret keys or interactive passwords for security authentication when you deploy TiDB using TiUP:
>
> - If you use secret keys, you can specify the path of the keys through `-i` or `--identity_file`;
> - If you use passwords, add the `-p` flag to enter the password interaction window;
> - If password-free login to the target machine has been configured, no authentication is required.

```shell
tiup dm deploy ${name} ${version} ./topology.yaml -u ${ssh_user} [-p] [-i /home/root/.ssh/gcp_rsa]
```

The parameters used in this step are as follows.

|Parameter|Description|
|-|-|
|`${name}` | The name of the DM cluster, eg: dm-test|
|`${version}` | The version of the DM cluster. You can see other supported versions by running `tiup list dm-master`. |
|`./topology.yaml`| The path of the topology configuration file.|
|`-u` or `--user`| Log in to the target machine as the root user or other user account with ssh and sudo privileges to complete the cluster deployment.|
|`-p` or `--password`| The password of target hosts. If specified, password authentication is used.|
|`-i` or `--identity_file`| The path of the SSH identity file. If specified, public key authentication is used (default "/root/.ssh/id_rsa").|

At the end of the output log, you will see ```Deployed cluster `dm-test` successfully```. This indicates that the deployment is successful.
## Step 4: Check the clusters managed by TiUP

```shell
tiup dm list
```

TiUP supports managing multiple DM clusters. The command above outputs information of all the clusters currently managed by TiUP, including the name, deployment user, version, and secret key information:

```log
Name  User  Version  Path                                  PrivateKey
----  ----  -------  ----                                  ----------
dm-test  tidb  ${version}  /root/.tiup/storage/dm/clusters/dm-test  /root/.tiup/storage/dm/clusters/dm-test/ssh/id_rsa
```
## Step 5: Check the status of the deployed DM cluster

To check the status of the `dm-test` cluster, execute the following command:

```shell
tiup dm display dm-test
```

Expected output includes the instance ID, role, host, listening port, and status (because the cluster is not started yet, so the status is `Down`/`inactive`), and directory information.
## Step 6: Start the DM cluster

```shell
tiup dm start dm-test
```

If the output log includes ```Started cluster `dm-test` successfully```, the start is successful.
## Step 7: Verify the running status of the DM cluster

Check the DM cluster status using TiUP:

```shell
tiup dm display dm-test
```

If the `Status` is `Up` in the output, the cluster status is normal.
## Step 8: Managing migration tasks using dmctl

dmctl is a command-line tool used to control DM clusters. You are recommended to [use dmctl via TiUP](https://docs.pingcap.com/tidb/stable/dm/maintain-dm-using-tiup#dmctl).

dmctl supports both the command mode and the interactive mode. For details, see [Maintain DM Clusters Using dmctl](https://docs.pingcap.com/tidb/stable/dm/dmctl-introduction#maintain-dm-clusters-using-dmctl).
## Step 9: Encrypt the database password

After deployment, you can configure DM tasks to encrypt the database password. For more information, see [Encrypt the database password](https://docs.pingcap.com/tidb/stable/dm/dm-manage-source#encrypt-the-database-password).
