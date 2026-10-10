# TiDB Cloud Dedicated log redaction management

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-log-redaction.md`
- Source Title: `User-Controlled Log Redaction`
- Source Heading Path: `User-Controlled Log Redaction | User-Controlled Log Redaction > Prerequisites | User-Controlled Log Redaction > Disable log redaction | User-Controlled Log Redaction > Check the updated logs | User-Controlled Log Redaction > Enable log redaction`
- Source Line Ranges: `5-74`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`
- Topic Tags: `log-redaction`, `sensitive-data`, `security-settings`, `cluster-logs`, `execution-logs`, `slow-query-log`, `session-connections`, `permissions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0303_9cf8bbd682`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-log-redaction.md#user-controlled-log-redaction`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1595bed105e516d39c5fba7e2fe2de6812ec198e143ec58f3b30006828f406b7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-log-redaction#user-controlled-log-redaction
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-log-redaction.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about managing Execution Log Redaction in a TiDB Cloud Dedicated cluster, including prerequisites, default state, connection impact, or checking whether sensitive data is redacted in logs.
- Retrieval Keywords: User-Controlled Log Redaction, TiDB Cloud Dedicated, Execution Log Redaction, Settings > Security, Organization Owner, Project Owner, paused state, Disable log redaction, Enable log redaction, new database connections, Existing connections are unaffected, Reconnect to the database, slow query log, running logs, execution plans, SELECT *, SLEEP(2) FROM users WHERE email LIKE "%useremail%";
- Follow-up Guidance: The source also states that after changing the setting, only new sessions reflect the change and you need to reconnect existing connections or the database session for it to take effect.
- Classification Note: This is classified as configuration content because it describes how to enable or disable the Execution Log Redaction setting in the TiDB Cloud console and notes the prerequisites and effects of that setting.

## Official Source Content

# User-Controlled Log Redaction

User-controlled log redaction lets you manage the visibility of sensitive data in your [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) cluster logs. By toggling this redaction feature, you can protect your information, balance operational needs with security, and control what appears in your cluster logs.

Log redaction is enabled by default, ensuring that sensitive information in running logs and execution plans is concealed. If you need more detailed log information for cluster maintenance or SQL tuning, you can disable this feature at any time.

> **Note:**
>
> The log redaction feature is only supported for TiDB Cloud Dedicated clusters.
## Prerequisites

* You must be in the **Organization Owner** or **Project Owner** role of your organization in TiDB Cloud.
* Log redaction cannot be enabled or disabled when the cluster is in the `paused` state.
## Disable log redaction

> **Warning:**
>
> Disabling log redaction might expose sensitive information and increase the risk of data leakage. Ensure that you understand and acknowledge this risk before proceeding. Remember to re-enable it as soon as you complete your diagnostic or maintenance task.

To disable log redaction, do the following:

1. Log in to the [TiDB Cloud console](https://tidbcloud.com/).
2. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

    > **Tip:**
    >
    > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

3. In the left navigation pane, click **Settings** > **Security**.
4. In the **Execution Log Redaction** section, you can see that the redaction feature is **Enabled** by default.
5. Click **Disable**. A warning appears, explaining the risks of disabling log redaction. 
6. Confirm the disabling.

After disabling log redaction, note the following:

* The change only applies to new database connections.
* Existing connections are unaffected. You need to reconnect them for the changes to take effect.
* Logs for new sessions will no longer be redacted.
## Check the updated logs

To check the updated logs after log redaction is disabled, do the following:

1. Simulate a performance issue caused by a slow query. For example, execute the following SQL statement:

    ```sql
    SELECT *, SLEEP(2) FROM users WHERE email LIKE "%useremail%";
    ```

2. Wait a few minutes for the slow query log to update.
3. Review the log to confirm that the sensitive data is not redacted.
## Enable log redaction

To maintain data security, **enable log redaction** as soon as you complete your diagnostic or maintenance task as follows.

1. Log in to the [TiDB Cloud console](https://tidbcloud.com/).
2. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

    > **Tip:**
    >
    > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

3. In the left navigation pane, click **Settings** > **Security**.
4. In the **Execution Log Redaction** section, you can see that the redaction feature is **Disabled**.
5. Click **Enable** to enable it.
6. Reconnect to the database for the change to take effect on new sessions.
