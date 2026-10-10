# Configure and use OIDC SSO in TiDB Dashboard

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-session-sso.md`
- Source Title: `Configure SSO for TiDB Dashboard`
- Source Heading Path: `Configure SSO for TiDB Dashboard | Configure SSO for TiDB Dashboard > Configure OIDC SSO | Configure SSO for TiDB Dashboard > Configure OIDC SSO > Enable SSO | Configure SSO for TiDB Dashboard > Configure OIDC SSO > Disable SSO | Configure SSO for TiDB Dashboard > Configure OIDC SSO > Re-enter the password after a password change | Configure SSO for TiDB Dashboard > Sign in via SSO`
- Source Line Ranges: `5-94`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `sql`, `shared`
- Topic Tags: `sso`, `oidc`, `authentication`, `signin`, `impersonation`, `password`, `authorization`, `user-management`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0033_a7280df685`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-session-sso.md#configure-sso-for-tidb-dashboard`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `62c442b5d4ec541dc00785d413c2b94a374a24d76eba67d29ae5485c020f61b5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-session-sso#configure-sso-for-tidb-dashboard
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-session-sso.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the built-in TiDB Dashboard OIDC SSO workflow, including enabling or disabling SSO, required permission, stored SQL password impersonation, password re-authorization after a password change, or signing in with the company account button.
- Retrieval Keywords: TiDB Dashboard OIDC SSO, Enable to use SSO when sign into TiDB Dashboard, Single Sign-On, OIDC Client ID, OIDC Discovery URL, Authorize Impersonation, Authorize and Save, SYSTEM_VARIABLES_ADMIN, Sign in via Company Account, re-enter the password after a password change, stored SQL password, impersonate a normal SQL sign-in
- Follow-up Guidance: The chunk also states that some SSO services require additional configuration such as trusted sign-in and sign-out URIs, and that SSO sign-in fails after the SQL user password is changed until the password is re-entered.
- Classification Note: This is classified as dashboard configuration because it describes configuring OIDC-based Single Sign-On settings and sign-in behavior in TiDB Dashboard.

## Official Source Content

# Configure SSO for TiDB Dashboard

TiDB Dashboard supports [OIDC](https://openid.net/connect/)-based Single Sign-On (SSO). After enabling the SSO feature of TiDB Dashboard, the configured SSO service is used for your sign-in authentication and then you can access TiDB Dashboard without entering the SQL user password.
## Configure OIDC SSO
### Enable SSO

1. Sign into TiDB Dashboard.

2. Click the username in the left sidebar to access the configuration page.

3. In the **Single Sign-On** section, select **Enable to use SSO when sign into TiDB Dashboard**.

    > **Note:**
    >
    > If your account does not have the `SYSTEM_VARIABLES_ADMIN` permission, the **Enable to use SSO when sign into TiDB Dashboard** option is disabled. For more information on permissions, see [TiDB Dashboard User Management](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-user).

4. Fill the **OIDC Client ID** and the **OIDC Discovery URL** fields in the form.

    Generally, you can obtain the two fields from the SSO service provider:

    - OIDC Client ID is also called OIDC Token Issuer.
    - OIDC Discovery URL is also called OIDC Token Audience.

5. Click **Authorize Impersonation** and input the SQL password.

    TiDB Dashboard will store this SQL password and use it to impersonate a normal SQL sign-in after an SSO sign-in is finished.

    ![Sample Step](/media/dashboard/dashboard-session-sso-enable-1.png)

    > **Note:**
    >
    > The password you have entered will be encrypted and stored. The SSO sign-in will fail after the password of the SQL user is changed. In this case, you can re-enter the password to bring SSO back.

6. Click **Authorize and Save**.

    ![Sample Step](/media/dashboard/dashboard-session-sso-enable-2.png)

7. Click **Update** (Update) to save the configuration.

    ![Sample Step](/media/dashboard/dashboard-session-sso-enable-3.png)

Now SSO sign-in has been enabled for TiDB Dashboard.

> **Note:**
>
> For security reasons, some SSO services require additional configuration for the SSO service, such as the trusted sign-in and sign-out URIs. Refer to the documentation of the SSO service for further information.
### Disable SSO

You can disable the SSO, which will completely erase the stored SQL password:

1. Sign into TiDB Dashboard.

2. Click the username in the left sidebar to access the configuration page.

3. In the **Single Sign-On** section, deselect **Enable to use SSO when sign into TiDB Dashboard**.

4. Click **Update** (Update) to save the configuration.

    ![Sample Step](/media/dashboard/dashboard-session-sso-disable.png)
### Re-enter the password after a password change

The SSO sign-in will fail once the password of the SQL user is changed. In this case, you can bring back the SSO sign-in by re-entering the SQL password:

1. Sign into TiDB Dashboard.

2. Click the username in the left sidebar to access the configuration page.

3. In the **Single Sign-On** section, Click **Authorize Impersonation** and input the updated SQL password.

    ![Sample Step](/media/dashboard/dashboard-session-sso-reauthorize.png)

4. Click **Authorize and Save**.
## Sign in via SSO

Once SSO is configured for TiDB Dashboard, you can sign in via SSO by taking following steps:

1. In the sign-in page of TiDB Dashboard, click **Sign in via Company Account**.

    ![Sample Step](/media/dashboard/dashboard-session-sso-signin.png)

2. Sign into the system with SSO service configured.

3. You are redirected back to TiDB Dashboard to finish the sign-in.
