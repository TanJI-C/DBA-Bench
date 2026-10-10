# Configure Okta as TiDB Dashboard SSO provider

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-session-sso.md`
- Source Title: `Configure SSO for TiDB Dashboard`
- Source Heading Path: `Configure SSO for TiDB Dashboard > Example 1: Use Okta for TiDB Dashboard SSO sign-in | Configure SSO for TiDB Dashboard > Example 1: Use Okta for TiDB Dashboard SSO sign-in > Step 1: Configure Okta | Configure SSO for TiDB Dashboard > Example 1: Use Okta for TiDB Dashboard SSO sign-in > Step 2: Obtain OIDC information and fill in TiDB Dashboard`
- Source Line Ranges: `95-156`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `shared`
- Topic Tags: `sso`, `oidc`, `okta`, `identity-provider`, `redirect-uri`, `client-id`, `discovery-url`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0034_eb7ebf8f56`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-session-sso.md#example-1-use-okta-for-tidb-dashboard-sso-sign-in`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `44d0324cd85e40eab35e84da2919acbe52dc6d6558f48d3421dda61a903cec8b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-session-sso#example-1-use-okta-for-tidb-dashboard-sso-sign-in
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-session-sso.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants the Okta-specific mapping and redirect URI settings needed to use Okta as the TiDB Dashboard SSO provider.
- Retrieval Keywords: Okta TiDB Dashboard SSO, Create App Integration, OIDC - OpenID Connect, Single-Page Application, Sign-in redirect URIs, Sign-out redirect URIs, http://DASHBOARD_IP:PORT/dashboard/?sso_callback=1, http://DASHBOARD_IP:PORT/dashboard/, OpenID Connect ID Token, Issuer, Audience, OIDC Client ID, OIDC Discovery URL
- Follow-up Guidance: The chunk explains that in Okta the TiDB Dashboard OIDC Client ID is filled with the copied Issuer value and the OIDC Discovery URL is filled with the copied Audience value.
- Classification Note: This is classified as dashboard configuration because it provides a provider-specific Okta setup for TiDB Dashboard OIDC SSO.

## Official Source Content

## Example 1: Use Okta for TiDB Dashboard SSO sign-in

[Okta](https://www.okta.com/) is an OIDC SSO identity service, which is compatible with the SSO feature of TiDB Dashboard. The steps below demonstrate how to configure Okta and TiDB Dashboard so that Okta can be used as the TiDB Dashboard SSO provider.
### Step 1: Configure Okta

First, create an Okta Application Integration to integrate SSO.

1. Access the Okta administration site.

2. Navigate from the left sidebar **Applications** > **Applications**.

3. Click **Create App Integration**.

    ![Sample Step](/media/dashboard/dashboard-session-sso-okta-1.png)

4. In the popped up dialog, choose **OIDC - OpenID Connect** in **Sign-in method**.

5. Choose **Single-Page Application** in **Application Type**.

6. Click the **Next** button.

    ![Sample Step](/media/dashboard/dashboard-session-sso-okta-2.png)

7. Fill **Sign-in redirect URIs** as follows:

    ```
    http://DASHBOARD_IP:PORT/dashboard/?sso_callback=1
    ```

    Substitute `DASHBOARD_IP:PORT` with the actual domain (or IP address) and port that you use to access the TiDB Dashboard in the browser.

8. Fill **Sign-out redirect URIs** as follows:

    ```
    http://DASHBOARD_IP:PORT/dashboard/
    ```

    Similarly, substitute `DASHBOARD_IP:PORT` with the actual domain (or IP address) and port.

    ![Sample Step](/media/dashboard/dashboard-session-sso-okta-3.png)

9. Configure what type of users in your organization is allowed for SSO sign-in in the **Assignments** field, and then click **Save** to save the configuration.

    ![Sample Step](/media/dashboard/dashboard-session-sso-okta-4.png)
### Step 2: Obtain OIDC information and fill in TiDB Dashboard

1. In the Application Integration just created in Okta, click **Sign On**.

    ![Sample Step 1](/media/dashboard/dashboard-session-sso-okta-info-1.png)

2. Copy values of the **Issuer** and **Audience** fields from the **OpenID Connect ID Token** section.

    ![Sample Step 2](/media/dashboard/dashboard-session-sso-okta-info-2.png)

3. Open the TiDB Dashboard configuration page, fill **OIDC Client ID** with **Issuer** obtained from the last step and fill **OIDC Discovery URL** with **Audience**. Then finish the authorization and save the configuration. For example:

    ![Sample Step 3](/media/dashboard/dashboard-session-sso-okta-info-3.png)

Now TiDB Dashboard has been configured to use Okta SSO for sign-in.
