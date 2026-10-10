# Prepare Diag, Clinic Server login, token, and region

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/clinic/quick-start-with-clinic.md`
- Source Title: `Quick Start Guide for PingCAP Clinic`
- Source Heading Path: `Quick Start Guide for PingCAP Clinic > Prerequisites`
- Source Line Ranges: `22-107`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `cloud`, `shared`, `tidb`
- Topic Tags: `installation`, `authentication`, `organization`, `access-token`, `region`, `sso`, `log-redaction`, `version-dependency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0021_14aa48db13`
- Source ID: `tidb-docs-8.1:clinic/quick-start-with-clinic.md#prerequisites`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `106ff80fc56b6cb47ef3d6ee7045af35978854f6cea1169be662ef715269b2f2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/clinic/quick-start-with-clinic#prerequisites
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/clinic/quick-start-with-clinic.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the prerequisite setup for PingCAP Clinic, including installing Diag, logging in to Clinic Server, creating an organization, getting an access token, setting clinic.token and clinic.region, or understanding the region-related version note.
- Retrieval Keywords: tiup install diag, Clinic Server for international users, Clinic Server for users in the Chinese mainland, Continue with TiDB Account, Continue with AskTUG, organization, Get Access Token For Diag Tool, clinic.token, tiup diag config clinic.token, clinic.region, tiup diag config clinic.region US, tiup diag config clinic.region CN, Diag v0.9.0, tiup update diag, log redaction
- Follow-up Guidance: The source adds that log redaction can be enabled on the TiDB side and links to the log redaction documentation for more information.
- Classification Note: This is classified as configuration because the content is a prerequisite setup flow with installation, authentication, token preparation, region settings, and an optional log redaction setting.

## Official Source Content

## Prerequisites

Before using PingCAP Clinic, you need to install Diag and prepare an environment for uploading data.

1. On your control machine with TiUP installed, run the following command to install Diag:

    ```bash
    tiup install diag
    ```

2. Log in to Clinic Server.

    <div label="Clinic Server for international users" value="clinic-us">

    Go to the [Clinic Server for international users](https://clinic.pingcap.com) and select **Continue with TiDB Account** to enter the TiDB Cloud login page. If you do not have a TiDB Cloud account, create one on that page.

    > **Note:**
    >
    > A TiDB Cloud account is only used for logging in to Clinic Server in SSO mode and is not mandatory for accessing the TiDB Cloud service.

    </div>

    <div label="Clinic Server for users in the Chinese mainland" value="clinic-cn">

    Go to the [Clinic Server for users in the Chinese mainland](https://clinic.pingcap.com.cn) and select **Continue with AskTUG** to enter the AskTUG community login page. If you do not have an AskTUG account, create one on that page

    </div>

3. Create an organization on the Clinic Server. Organization is a collection of TiDB clusters. You can upload diagnostic data on the created organization.

4. Get an access token to upload data. When uploading collected data through Diag, you need a token for user authentication to ensure the data is isolated securely. If you already get a token from the Clinic Server, you can reuse the token.

    To get a token, click the icon in the lower-right corner of the Cluster page, select **Get Access Token For Diag Tool**, and click **+** in the pop-up window. Make sure that you have copied and saved the token that is displayed.

    ![An example of a token](/media/clinic-get-token.png)

    > **Note:**
    >
    > - For data security, TiDB only displays the token information when it is created. If you lost the information, you can delete the old token and create a new one.
    > - A token is only used for uploading data.

5. Set the token and `region` in Diag.

    - Run the following command to set the `clinic.token`:

        ```bash
        tiup diag config clinic.token ${token-value}
        ```

    - Run the following command to set the `clinic.region`:

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

6. (Optional) Enable log redaction.

    When TiDB provides detailed log information, it might print sensitive information (for example, user data) in the log. If you want to avoid leaking sensitive information in the local log and Clinic Server, you can enable log redaction in the TiDB side. For more information, see [log redaction](https://docs.pingcap.com/tidb/stable/log-redaction#log-redaction-in-tidb-side).
