# Start and verify a TiDB cluster with TiUP

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/production-deployment-using-tiup.md`
- Source Title: `Deploy a TiDB Cluster Using TiUP`
- Source Heading Path: `Deploy a TiDB Cluster Using TiUP > Step 7. Start a TiDB cluster | Deploy a TiDB Cluster Using TiUP > Step 8. Verify the running status of the TiDB cluster | Deploy a TiDB Cluster Using TiUP > See also`
- Source Line Ranges: `387-453`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`, `tiflash`, `ticdc`
- Topic Tags: `cluster-start`, `safe-start`, `root-password`, `status-check`, `verification`, `post-deployment`, `related-documents`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0198_8103c818bc`
- Source ID: `tidb-docs-8.1:production-deployment-using-tiup.md#step-7-start-a-tidb-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `328ae7f62a38fb7d6a5dca9111f3a829c40b8b61d5629cefdcff0d21c85e9f4c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup#step-7-start-a-tidb-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/production-deployment-using-tiup.md

## Retrieval Guidance

- Use When: Use this chunk when you need the official TiUP commands to start a TiDB cluster, understand safe start versus standard start, check the generated root password behavior, or verify that the cluster status is Up.
- Retrieval Keywords: tiup cluster start tidb-test --init, safe start, standard start, TiUP cluster v1.9.0, root password, Started cluster `tidb-test` successfully., The new password is, tiup cluster display tidb-test, Up status, Forget the `root` password, TiFlash, TiCDC
- Follow-up Guidance: If TiFlash or TiCDC is deployed with the TiDB cluster, the source points to Use TiFlash, Maintain a TiFlash Cluster, TiFlash Alert Rules and Solutions, Troubleshoot TiFlash, Changefeed Overview, Manage Changefeed, Troubleshoot TiCDC, and TiCDC FAQs.
- Classification Note: This is classified as a self-managed TiUP operation chunk because the official content covers starting a TiDB cluster, handling safe-start root password output, and verifying running status with TiUP commands.

## Official Source Content

## Step 7. Start a TiDB cluster

Since TiUP cluster v1.9.0, safe start is introduced as a new start method. Starting a database using this method improves the security of the database. It is recommended that you use this method.

After safe start, TiUP automatically generates a password for the TiDB root user and returns the password in the command-line interface.

> **Note:**
>
> - After safe start of a TiDB cluster, you cannot log in to TiDB using a root user without a password. Therefore, you need to record the password returned in the command output for future logins.
>
> - The password is generated only once. If you do not record it or you forgot it, refer to [Forget the `root` password](https://docs.pingcap.com/tidb/stable/user-account-management#forget-the-root-password) to change the password.

Method 1: Safe start

```shell
tiup cluster start tidb-test --init
```

If the output is as follows, the start is successful:

```shell
Started cluster `tidb-test` successfully.
The root password of TiDB database has been changed.
The new password is: 'y_+3Hwp=*AWz8971s6'.
Copy and record it to somewhere safe, it is only displayed once, and will not be stored.
The generated password can NOT be got again in future.
```

Method 2: Standard start

```shell
tiup cluster start tidb-test
```

If the output log includes ```Started cluster `tidb-test` successfully```, the start is successful. After standard start, you can log in to a database using a root user without a password.
## Step 8. Verify the running status of the TiDB cluster

```shell
tiup cluster display tidb-test
```

If the output log shows `Up` status, the cluster is running properly.
## See also

If you have deployed [TiFlash](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview) along with the TiDB cluster, see the following documents:

- [Use TiFlash](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview#use-tiflash)
- [Maintain a TiFlash Cluster](https://docs.pingcap.com/tidb/stable/tiflash/maintain-tiflash)
- [TiFlash Alert Rules and Solutions](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-alert-rules)
- [Troubleshoot TiFlash](https://docs.pingcap.com/tidb/stable/tiflash/troubleshoot-tiflash)

If you have deployed [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview) along with the TiDB cluster, see the following documents:

- [Changefeed Overview](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-overview)
- [Manage Changefeed](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-manage-changefeed)
- [Troubleshoot TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/troubleshoot-ticdc)
- [TiCDC FAQs](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-faq)
