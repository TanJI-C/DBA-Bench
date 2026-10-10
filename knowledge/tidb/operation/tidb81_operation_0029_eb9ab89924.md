# PingCAP Clinic overview and prerequisites for TiUP clusters

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/clinic/clinic-user-guide-for-tiup.md`
- Source Title: `Troubleshoot Clusters Using PingCAP Clinic`
- Source Heading Path: `Troubleshoot Clusters Using PingCAP Clinic | Troubleshoot Clusters Using PingCAP Clinic > User scenarios | Troubleshoot Clusters Using PingCAP Clinic > Prerequisites`
- Source Line Ranges: `5-122`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`, `dm`, `shared`
- Topic Tags: `clinic`, `diag`, `prerequisites`, `token`, `region`, `offline-install`, `log-redaction`, `remote-troubleshooting`, `quick-check`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0029_eb9ab89924`
- Source ID: `tidb-docs-8.1:clinic/clinic-user-guide-for-tiup.md#troubleshoot-clusters-using-pingcap-clinic`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `33a60f77c22812978b920f564b09bcdbc53434a8ba8d9ab38ed89e3528b4b534`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/clinic/clinic-user-guide-for-tiup#troubleshoot-clusters-using-pingcap-clinic
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/clinic/clinic-user-guide-for-tiup.md

## Retrieval Guidance

- Use When: Use this chunk when identifying whether PingCAP Clinic with Diag applies to a TiUP-deployed self-hosted TiDB or DM cluster and what prerequisites are needed before uploading diagnostic data.
- Retrieval Keywords: PingCAP Clinic, Diag client, Clinic Server, TiUP clusters, DM clusters, self-hosted environment, TiDB Operator on Kubernetes, TiDB Ansible, tiup install diag, tiup update diag, clinic.token, Get Access Token For Diag Tool, tiup diag config clinic.token, clinic.region, tiup diag config clinic.region US, tiup diag config clinic.region CN, offline install, Deploy TiUP offline: Method 2, log redaction
- Follow-up Guidance: The source also points to using Diag for remote troubleshooting data collection and to the local quick check feature that only checks configuration.
- Classification Note: This is classified as operation because the content defines supported scope and prerequisites such as installing Diag, setting clinic.token and clinic.region, and optionally enabling log redaction.

## Official Source Content

# Troubleshoot Clusters Using PingCAP Clinic

For TiDB clusters and DM clusters deployed using TiUP, you can use PingCAP Clinic Diagnostic Service (PingCAP Clinic) to troubleshoot cluster problems remotely and perform a quick check on cluster status locally using [Diag client (Diag)](https://github.com/pingcap/diag) and Clinic Server.

> **Note:**
>
> - This document **only** applies to clusters deployed using TiUP in a self-hosted environment. For clusters deployed using TiDB Operator on Kubernetes, see [PingCAP Clinic for TiDB Operator environments](https://docs.pingcap.com/tidb-in-kubernetes/stable/clinic-user-guide).
>
> - PingCAP Clinic **does not support** collecting data from clusters deployed using TiDB Ansible.
## User scenarios

- [Troubleshoot cluster problems remotely](#troubleshoot-cluster-problems-remotely)

    - When your cluster has some problems, if you need to [get support](https://docs.pingcap.com/tidb/stable/support) from PingCAP, you can perform the following operations to facilitate the remote troubleshooting: collect diagnostic data with Diag, upload the collected data to the Clinic Server, and provide the data access link to the technical support staff.
    - When your cluster has some problems, if you cannot analyze the problems immediately, you can use Diag to collect and save the data for later analysis.

- [Perform a quick check on the cluster status locally](#perform-a-quick-check-on-the-cluster-status-locally)

    Even if your cluster is running stably for now, it is necessary to periodically check the cluster to detect potential stability risks. You can identify potential health risks of a cluster using the local quick check feature provided by PingCAP Clinic. The local check only checks configuration. To check more items, such as metrics and logs, it is recommended to upload the diagnostic data to the Clinic Server and use the Health Report feature.
## Prerequisites

Before using PingCAP Clinic, you need to install Diag (a component to collect data provided by PingCAP Clinic) and prepare the environment to upload data.

1. Install Diag.

    - If you have installed TiUP on your control machine, run the following command to install Diag:

        ```bash
        tiup install diag
        ```

    - If you have installed Diag, you can use the following command to upgrade Diag to the latest version:

        ```bash
        tiup update diag
        ```

    > **Note:**
    >
    > - For clusters without an internet connection, you need to deploy Diag offline. For details, refer to [Deploy TiUP offline: Method 2](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup#deploy-tiup-offline).
    > - Diag is **only** provided in the TiDB Server offline mirror package of v5.4.0 or later.

2. Get and set an access token (token) to upload data.

    When uploading collected data through Diag, you need a token for user authentication. If you already set a token Diag, you can reuse the token and skip this step.

    To get a token, perform the following steps:

    - Log in to the Clinic Server.

        <div label="Clinic Server for international users" value="clinic-us">

        [Clinic Server for international users](https://clinic.pingcap.com): Data is stored in AWS in US regions.

        </div>
        <div label="Clinic Server for users in the Chinese mainland" value="clinic-cn">

        [Clinic Server for users in the Chinese mainland](https://clinic.pingcap.com.cn): Data is stored in AWS in China (Beijing) regions.

        </div>

    - Click the icon in the lower-right corner of the Cluster page, select **Get Access Token For Diag Tool**, and click **+** in the pop-up window. Make sure that you have copied and saved the token that is displayed.

        ![Get the Token](/media/clinic-get-token.png)

    > **Note:**
    >
    > - When accessing Clinic Server for the first time, before getting a token, you need to prepare the environment by referring to [Quick Start with PingCAP Clinic](https://docs.pingcap.com/tidb/stable/clinic/quick-start-with-clinic#prerequisites).
    > - For data security, TiDB only displays the token upon the token creation. If you have lost the token, delete the old token and create a new one.
    > - A token is only used for uploading data.

    - Then, set the token in Diag. For example:

        ```bash
        tiup diag config clinic.token ${token-value}
        ```

3. Set the `region` in Diag.

    `region` determines the encryption certificate used for packing data and the target service when uploading the data. For example:

    > **Note:**
    >
    > - Diag v0.9.0 and later versions support setting `region`.
    > - For versions earlier than Diag v0.9.0, data is uploaded to Clinic Server in the Chinese region by default. To set `region` in these versions, run the `tiup update diag` command to upgrade Diag to the latest version and then set `region` in Diag.

    <div label="Clinic Server for international users" value="clinic-us">

    When using Clinic Server for international users, set `region` to `US` using the following command:

    ```bash
    tiup diag config clinic.region US
    ```

    </div>
    <div label="Clinic Server for users in the Chinese mainland" value="clinic-cn">

    When using Clinic Server for users in the Chinese mainland, set `region` to `CN` using the following command:

    ```bash
    tiup diag config clinic.region CN
    ```

    </div>

4. (Optional) Enable log redaction.

    When TiDB provides detailed log information, it might print sensitive information (for example, user data) in the log. If you want to avoid leaking sensitive information in the local log and Clinic Server, you can enable log redaction in the TiDB side. For more information, see [log redaction](https://docs.pingcap.com/tidb/stable/log-redaction#log-redaction-in-tidb-side).
