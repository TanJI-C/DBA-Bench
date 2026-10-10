# Configure Casdoor as TiDB Dashboard SSO provider

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-session-sso.md`
- Source Title: `Configure SSO for TiDB Dashboard`
- Source Heading Path: `Configure SSO for TiDB Dashboard > Example 3: Use Casdoor for TiDB Dashboard SSO sign-in | Configure SSO for TiDB Dashboard > Example 3: Use Casdoor for TiDB Dashboard SSO sign-in > Step 1: Configure Casdoor | Configure SSO for TiDB Dashboard > Example 3: Use Casdoor for TiDB Dashboard SSO sign-in > Step 2: Obtain OIDC information and fill in TiDB Dashboard`
- Source Line Ranges: `207-244`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `shared`
- Topic Tags: `sso`, `oidc`, `casdoor`, `identity-provider`, `redirect-url`, `client-id`, `domain`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0036_fc25721193`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-session-sso.md#example-3-use-casdoor-for-tidb-dashboard-sso-sign-in`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `044291b4484fe933c0db05ef9b088db0f68fac23514810ab23bae8f2d6df2185`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-session-sso#example-3-use-casdoor-for-tidb-dashboard-sso-sign-in
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-session-sso.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants Casdoor-specific setup details, including the redirect URL and field mapping required to use Casdoor as the TiDB Dashboard SSO provider.
- Retrieval Keywords: Casdoor TiDB Dashboard SSO, Applications - Add, Redirect URLs, http://DASHBOARD_IP:PORT/dashboard/?sso_callback=1, Client ID, Domain, OIDC Client ID, OIDC Discovery URL, https://casdoor.example.com/, Save & Exit
- Follow-up Guidance: The chunk states that TiDB Dashboard OIDC Client ID should use the saved Casdoor Client ID and OIDC Discovery URL should use the Domain value prefixed with https:// and suffixed with /.
- Classification Note: This is classified as dashboard configuration because it describes configuring Casdoor as an OIDC SSO provider for TiDB Dashboard.

## Official Source Content

## Example 3: Use Casdoor for TiDB Dashboard SSO sign-in

[Casdoor](https://casdoor.org/) is an open-source SSO platform that can be deployed in your own hosts. It is compatible with the SSO feature of TiDB Dashboard. The following steps describe how to configure Casdoor and TiDB Dashboard so that Casdoor can be used as the TiDB Dashboard SSO provider.
### Step 1: Configure Casdoor

1. Deploy and access the Casdoor administration site.

2. Navigate from the top sidebar **Applications**.

3. Click **Applications - Add**.
    ![Settings](/media/dashboard/dashboard-session-sso-casdoor-settings-1.png)

4. Fill **Name** and **Display name**, for example, **TiDB Dashboard**.

5. Add **Redirect URLs** as follows:

    ```
    http://DASHBOARD_IP:PORT/dashboard/?sso_callback=1
    ```

    Replace `DASHBOARD_IP:PORT` with the actual domain (or IP address) and port that you use to access the TiDB Dashboard in your browser.

    ![Settings](/media/dashboard/dashboard-session-sso-casdoor-settings-2.png)

6. Keep the default values for other settings and click **Save & Exit**.

7. Save the **Client ID** seen on the page.
### Step 2: Obtain OIDC information and fill in TiDB Dashboard

1. Fill **OIDC Client ID** of TiDB dashboard with **Client ID** saved in the previous step.

2. Fill **OIDC Discovery URL** with the **Domain** field value prefixed with `https://` and suffixed with `/`, for example, `https://casdoor.example.com/`. Complete authorization and save the configuration.

    ![Settings](/media/dashboard/dashboard-session-sso-casdoor-settings-3.png)

Now TiDB Dashboard has been configured to use Casdoor SSO for sign-in.
