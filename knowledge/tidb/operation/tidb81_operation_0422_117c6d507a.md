# Finish PoC, clean up environment, and review FAQ on backup, scaling, credits, and support

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-poc.md`
- Source Title: `Perform a Proof of Concept (PoC) with TiDB Cloud`
- Source Heading Path: `Perform a Proof of Concept (PoC) with TiDB Cloud > Step 8. Clean up the environment and finish the PoC | Perform a Proof of Concept (PoC) with TiDB Cloud > FAQ | Perform a Proof of Concept (PoC) with TiDB Cloud > FAQ > 1. How long does it take to back up and restore my data? | Perform a Proof of Concept (PoC) with TiDB Cloud > FAQ > 2. When do I need to scale out and scale in? | Perform a Proof of Concept (PoC) with TiDB Cloud > FAQ > 3. How to make the best use of my PoC credits? | Perform a Proof of Concept (PoC) with TiDB Cloud > FAQ > 4. Can I take more than 2 weeks to complete a PoC? | Perform a Proof of Concept (PoC) with TiDB Cloud > FAQ > 5. I'm stuck with a technical problem. How do I get help for my PoC?`
- Source Line Ranges: `189-240`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tikv`
- Topic Tags: `cleanup`, `cluster-deletion`, `backup-restore`, `scaling`, `capacity-planning`, `credits`, `billing`, `trial-extension`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0422_117c6d507a`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-poc.md#step-8-clean-up-the-environment-and-finish-the-poc`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `94f67a3c8a96f002be5cfe30889ff928d99583fbdc41922584a74c39e2d6e754`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-poc#step-8-clean-up-the-environment-and-finish-the-poc
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-poc.md

## Retrieval Guidance

- Use When: Use this chunk when someone needs TiDB Cloud PoC cleanup guidance or FAQ details about backup and restore timing, scaling conditions, credits usage, trial extension, or support contacts.
- Retrieval Keywords: Step 8, Clean up the environment and finish the PoC, Delete a TiDB Cluster, TiDB Cloud Dedicated, node storage sizes, TiDB Cloud Support, TiDB Cloud Feedback form, automatic backup, manual backup, full database, backup and restoring rate, 50 MB/s, single TiKV node, 10% to 50%, QPS, transaction latency, scale out, scale in, capacity metrics, dashboard, peak hours, data import, 10%-20% of CPU usage, Scale Your TiDB Cluster, data rebalancing, TiDB Cloud Billing, credits, Clusters page, Billing, Credits tab, cannot stop a cluster, backups are up to date, extend the PoC trial period, contact PingCAP, technical problem
- Follow-up Guidance: The content also explains that scale-in requires contacting TiDB Cloud Support, scaling can affect performance due to data rebalancing, and unused credits can continue paying TiDB cluster fees until they expire.
- Classification Note: This is classified as cloud operation content because it covers end-of-PoC environment removal and operational FAQ topics such as backup impact, scaling behavior, credits management, trial duration, and support channels in TiDB Cloud.

## Official Source Content

## Step 8. Clean up the environment and finish the PoC

You have completed the full cycle of a PoC after you test TiDB Cloud using real workloads and get the testing results. These results help you determine if TiDB Cloud meets your expectations. Meanwhile, you have accumulated best practices for using TiDB Cloud.

If you want to try TiDB Cloud on a larger scale, for a new round of deployments and tests, such as deploying with other node storage sizes offered by TiDB Cloud, get full access to TiDB Cloud by creating a [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) cluster.

If your credits are running out and you want to continue with the PoC, contact the [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) for consultation.

You can end the PoC and remove the test environment anytime. For more information, see [Delete a TiDB Cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/delete-tidb-cluster).

Any feedback to our support team is highly appreciated by filling in the [TiDB Cloud Feedback form](https://www.surveymonkey.com/r/L3VVW8R), such as the PoC process, the feature requests, and how we can improve the products.
## FAQ
### 1. How long does it take to back up and restore my data?

TiDB Cloud provides two types of database backup: automatic backup and manual backup. Both methods back up the full database.

The time it takes to back up and restore data might vary, depending on the number of tables, the number of mirror copies, and the CPU-intensive level. The backup and restoring rate in one single TiKV node is approximately 50 MB/s.

Database backup and restore operations are typically CPU-intensive, and always require additional CPU resources. They might have an impact (10% to 50%) on QPS and transaction latency, depending on how CPU-intensive this environment is.
### 2. When do I need to scale out and scale in?

The following are some considerations about scaling:

- During peak hours or data import, if you observe that the capacity metrics on the dashboard have reached the upper limits (see [Monitor a TiDB Cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-tidb-cluster)), you might need to scale out the cluster.
- If you observe that the resource usage is persistently low, for example, only 10%-20% of CPU usage, you can scale in the cluster to save resources.

You can scale out clusters on the console by yourself. If you need to scale in a cluster, you need to contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) for help. For more information about scaling, see [Scale Your TiDB Cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/scale-tidb-cluster). You can keep in touch with the support team to track the exact progress. You must wait for the scaling operation to finish before starting your test because it can impact the performance due to data rebalancing.
### 3. How to make the best use of my PoC credits?

Once your application for the PoC is approved, you will receive credits in your account. Generally, the credits are sufficient for a 14-day PoC. The credits are charged by the type of nodes and the number of nodes, on an hourly basis. For more information, see [TiDB Cloud Billing](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing#credits).

To check the credits left for your PoC, go to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your target project, as shown in the following screenshot.

![TiDB Cloud PoC Credits](/media/tidb-cloud/poc-points.png)

Alternatively, you can also switch to your target organization using the combo box in the upper-left corner of the TiDB Cloud console, click **Billing** in the left navigation pane, and then click the **Credits** tab to view the credit information.

To save credits, remove the cluster that you are not using. Currently, you cannot stop a cluster. You need to ensure that your backups are up to date before removing a cluster, so you can restore the cluster later when you want to resume your PoC.

If you still have unused credits after your PoC process is completed, you can continue using the credits to pay TiDB cluster fees as long as these credits are not expired.
### 4. Can I take more than 2 weeks to complete a PoC?

If you want to extend the PoC trial period or are running out of credits, [contact PingCAP](https://www.pingcap.com/contact-us/) for help.
### 5. I'm stuck with a technical problem. How do I get help for my PoC?

You can always [contact TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) for help.
