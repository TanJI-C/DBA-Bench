# Configure Organization SSO authentication methods and OIDC

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-org-sso-authentication.md`
- Source Title: `Organization SSO Authentication`
- Source Heading Path: `Organization SSO Authentication > Step 2. Configure authentication methods | Organization SSO Authentication > Step 2. Configure authentication methods > Configure username and password, Google, GitHub, or Microsoft authentication methods | Organization SSO Authentication > Step 2. Configure authentication methods > Configure the OIDC authentication method`
- Source Line Ranges: `93-155`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `sso`, `authentication-methods`, `google`, `github`, `microsoft`, `username-password`, `oidc`, `allowed-email-domains`, `auto-provision`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0305_4d02027a05`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-org-sso-authentication.md#step-2-configure-authentication-methods`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `48611e221eb89d0217a00adda4dbeaa0c739384d704b05cbad9b85ae52ccd7bb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-org-sso-authentication#step-2-configure-authentication-methods
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-org-sso-authentication.md

## Retrieval Guidance

- Use When: Use this chunk when someone needs the exact TiDB Cloud settings for Organization SSO authentication methods, including Google, GitHub, Microsoft, username and password, or OIDC configuration details.
- Retrieval Keywords: Step 2. Configure authentication methods, Authentication Methods, Google, GitHub, Microsoft, username and password, OIDC, Issuer URL, Client ID, Client Secret, Allowed Email Domains, Auto-provision Accounts, Organization Settings, Authentication tab, Save
- Follow-up Guidance: The source says that for enabled methods you can configure Auto-provision Accounts and Allowed Email Domains, and for OIDC you also configure Name, Issuer URL, Client ID, and Client Secret before clicking Save.
- Classification Note: This is classified as configuration because the content is a procedural setup reference for enabling and editing authentication method details in TiDB Cloud Organization SSO.

## Official Source Content

## Step 2. Configure authentication methods

Enabling an authentication method in TiDB Cloud allows members using that method to log in to TiDB Cloud using your custom URL.
### Configure username and password, Google, GitHub, or Microsoft authentication methods

After enabling Cloud Organization Cloud, you can configure username and password, Google, GitHub, or Microsoft authentication methods as follows:

1. On the **Organization Settings** page, enable or disable the Google, GitHub, or Microsoft authentication methods according to your need.
2. For an enabled authentication method, you can click <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 20H21M3.00003 20H4.67457C5.16376 20 5.40835 20 5.63852 19.9447C5.84259 19.8957 6.03768 19.8149 6.21663 19.7053C6.41846 19.5816 6.59141 19.4086 6.93732 19.0627L19.5001 6.49998C20.3285 5.67156 20.3285 4.32841 19.5001 3.49998C18.6716 2.67156 17.3285 2.67156 16.5001 3.49998L3.93729 16.0627C3.59139 16.4086 3.41843 16.5816 3.29475 16.7834C3.18509 16.9624 3.10428 17.1574 3.05529 17.3615C3.00003 17.5917 3.00003 17.8363 3.00003 18.3255V20Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg> to configure the method details.
3. In the method details, you can configure the following:

    - [**Auto-provision Accounts**](#decide-whether-to-enable-auto-provision)

        It is disabled by default. You can enable it according to your need. For security considerations, if you choose to enable auto-provision, it is recommended to limit the allowed email domains for authentication.

    - **Allowed Email Domains**

        After this field is configured, only the specified email domains of this authentication method can log in to TiDB Cloud using the custom URL. When filling in domain names, you need to exclude the `@` symbol and separate them with commas. For example, `company1.com,company2.com`.

        > **Note:**
        >
        > If you have configured email domains, before saving the settings, make sure that you add the email domain that you currently use for login, to avoid that you are locked out by TiDB Cloud.

4. Click **Save**.
### Configure the OIDC authentication method

If you have an identity provider that uses the OIDC identity protocol, you can enable the OIDC authentication method for TiDB Cloud login.

In TiDB Cloud, the OIDC authentication method is disabled by default. After enabling Cloud Organization Cloud, you can enable and configure the OIDC authentication method as follows:

1. Get the following information from your identity provider for TiDB Cloud Organization SSO:

    - Issuer URL
    - Client ID
    - Client secret

2. On the **Organization Settings** page, click the **Authentication** tab, locate the row of OIDC in the **Authentication Methods** area, and then click <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 20H21M3.00003 20H4.67457C5.16376 20 5.40835 20 5.63852 19.9447C5.84259 19.8957 6.03768 19.8149 6.21663 19.7053C6.41846 19.5816 6.59141 19.4086 6.93732 19.0627L19.5001 6.49998C20.3285 5.67156 20.3285 4.32841 19.5001 3.49998C18.6716 2.67156 17.3285 2.67156 16.5001 3.49998L3.93729 16.0627C3.59139 16.4086 3.41843 16.5816 3.29475 16.7834C3.18509 16.9624 3.10428 17.1574 3.05529 17.3615C3.00003 17.5917 3.00003 17.8363 3.00003 18.3255V20Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg> to show the OIDC method details.
3. In the method details, you can configure the following:

    - **Name**

        Specify a name for the OIDC authentication method to be displayed on your custom login page.

    - **Issuer URL**, **Client ID**, and **Client Secret**

        Paste the corresponding values that you get from your IdP.

    - [**Auto-provision Accounts**](#decide-whether-to-enable-auto-provision)

        It is disabled by default. You can enable it according to your need. For security considerations, if you choose to enable auto-provision, it is recommended to limit the allowed email domains for authentication.

    - **Allowed Email Domains**

        After this field is configured, only the specified email domains of this authentication method can log in to TiDB Cloud using the custom URL. When filling in domain names, you need to exclude the `@` symbol and separate them with commas. For example, `company1.com,company2.com`.

        > **Note:**
        >
        > If you have configured email domains, before saving the settings, make sure that you add the email domain that you currently use for login, to avoid that you are locked out by TiDB Cloud.

4. Click **Save**.
