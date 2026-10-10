# Configure Auth0 as TiDB Dashboard SSO provider

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-session-sso.md`
- Source Title: `Configure SSO for TiDB Dashboard`
- Source Heading Path: `Configure SSO for TiDB Dashboard > Example 2: Use Auth0 for TiDB Dashboard SSO sign-in | Configure SSO for TiDB Dashboard > Example 2: Use Auth0 for TiDB Dashboard SSO sign-in > Step 1: Configure Auth0 | Configure SSO for TiDB Dashboard > Example 2: Use Auth0 for TiDB Dashboard SSO sign-in > Step 2: Obtain OIDC information and fill in TiDB Dashboard`
- Source Line Ranges: `157-206`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `shared`
- Topic Tags: `sso`, `oidc`, `auth0`, `identity-provider`, `callback-url`, `logout-url`, `client-id`, `domain`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0035_2035109b26`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-session-sso.md#example-2-use-auth0-for-tidb-dashboard-sso-sign-in`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d68ead117d670816a1b4d0a9c02458ed5550cc2de79c1c9ce4fb7327a48e03b4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-session-sso#example-2-use-auth0-for-tidb-dashboard-sso-sign-in
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-session-sso.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs Auth0-specific application settings and the exact fields used to configure Auth0 as the TiDB Dashboard SSO provider.
- Retrieval Keywords: Auth0 TiDB Dashboard SSO, Create App Integration, Single Page Web Applications, Allowed Callback URLs, Allowed Logout URLs, http://DASHBOARD_IP:PORT/dashboard/?sso_callback=1, http://DASHBOARD_IP:PORT/dashboard/, Client ID, Domain, OIDC Client ID, OIDC Discovery URL, https://example.us.auth0.com/
- Follow-up Guidance: The chunk specifies that TiDB Dashboard OIDC Client ID uses the Auth0 Client ID and OIDC Discovery URL uses the Domain value prefixed with https:// and suffixed with /.
- Classification Note: This is classified as dashboard configuration because it documents the Auth0 identity-provider settings and field mapping for TiDB Dashboard SSO.

## Official Source Content

## Example 2: Use Auth0 for TiDB Dashboard SSO sign-in

Similar to Okta, [Auth0](https://auth0.com/) also provides OIDC SSO identity service. The following steps describe how to configure Auth0 and TiDB Dashboard so that Auth0 can be used as the TiDB Dashboard SSO provider.
### Step 1: Configure Auth0

1. Access the Auth0 administration site.

2. Navigate on the left sidebar **Applications** > **Applications**.

3. Click **Create App Integration**.

    ![Create Application](/media/dashboard/dashboard-session-sso-auth0-create-app.png)

    In the popped-up dialog, fill **Name**, for example, "TiDB Dashboard". Choose **Single Page Web Applications** in **Choose an application type**. Click **Create**.

4. Click **Settings**.

    ![Settings](/media/dashboard/dashboard-session-sso-auth0-settings-1.png)

5. Fill **Allowed Callback URLs** as follows:

    ```
    http://DASHBOARD_IP:PORT/dashboard/?sso_callback=1
    ```

    Replace `DASHBOARD_IP:PORT` with the actual domain (or IP address) and port that you use to access the TiDB Dashboard in your browser.

6. Fill **Allowed Logout URLs** as follows:

    ```
    http://DASHBOARD_IP:PORT/dashboard/
    ```

    Similarly, replace `DASHBOARD_IP:PORT` with the actual domain (or IP address) and port.

    ![Settings](/media/dashboard/dashboard-session-sso-auth0-settings-2.png)

7. Keep the default values for other settings and click **Save Changes**.
### Step 2: Obtain OIDC information and fill in TiDB Dashboard

1. Fill **OIDC Client ID** of TiDB Dashboard with **Client ID** in **Basic Information** under the **Settings** tab of Auth0.

2. Fill **OIDC Discovery URL** with the **Domain** field value prefixed with `https://` and suffixed with `/`, for example, `https://example.us.auth0.com/`. Complete authorization and save the configuration.

    ![Settings](/media/dashboard/dashboard-session-sso-auth0-settings-3.png)

Now TiDB Dashboard has been configured to use Auth0 SSO for sign-in.
