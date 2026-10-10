# Configure SAML SSO and SCIM provisioning for TiDB Cloud organization authentication

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-org-sso-authentication.md`
- Source Title: `Organization SSO Authentication`
- Source Heading Path: `Organization SSO Authentication > Step 2. Configure authentication methods > Configure the SAML authentication method | Organization SSO Authentication > Step 2. Configure authentication methods > Configure the SAML authentication method > Configure SCIM provisioning`
- Source Line Ranges: `156-251`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `saml`, `sso`, `scim`, `identity-provider`, `authentication-methods`, `auto-provision`, `email-domains`, `group-sync`, `role-mapping`, `organization-authentication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0306_5eb79dbb95`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-org-sso-authentication.md#configure-the-saml-authentication-method`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `509d739dbcaba104c95cb2090f8ff10e664fca814b8b903f9510bb4c4c438e15`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-org-sso-authentication#configure-the-saml-authentication-method
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-org-sso-authentication.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how to enable and configure SAML SSO for a TiDB Cloud organization and optionally set up SCIM provisioning for synchronized groups and role mapping.
- Retrieval Keywords: SAML authentication method, SCIM Provisioning Accounts, Organization Settings, Authentication, Authentication Methods, Sign on URL, Signing Certificate, Allowed Email Domains, Auto-provision Accounts, email attribute, email addresses as unique identifiers, SCIM connector base URL, Unique identifier field for users, Authentication Mode, Groups tab, By organization, By project, group push, Okta, custom login page
- Follow-up Guidance: The content also covers viewing pushed groups on the Groups tab, granting organization or project roles to those groups, and how membership changes in the identity provider are dynamically synchronized to TiDB Cloud.
- Classification Note: This is classified as configuration because the content describes enabling the SAML authentication method, entering IdP details, setting account provisioning and allowed email domains, and configuring SCIM provisioning in TiDB Cloud and the identity provider.

## Official Source Content

### Configure the SAML authentication method

If you have an identity provider that uses the SAML identity protocol, you can enable the SAML authentication method for TiDB Cloud login.

> **Note:**
>
> TiDB Cloud uses email addresses as unique identifiers for different users. Therefore, ensure that the `email` attribute for your organization members is configured in your identity provider.

In TiDB Cloud, the SAML authentication method is disabled by default. After enabling Cloud Organization Cloud, you can enable and configure the SAML authentication method as follows:

1. Get the following information from your identity provider for TiDB Cloud Organization SSO:

    - Sign on URL
    - Signing Certificate

2. On the **Organization Settings** page, click the **Authentication** tab in the left navigation pane, locate the row of SAML in the **Authentication Methods** area, and then click <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 20H21M3.00003 20H4.67457C5.16376 20 5.40835 20 5.63852 19.9447C5.84259 19.8957 6.03768 19.8149 6.21663 19.7053C6.41846 19.5816 6.59141 19.4086 6.93732 19.0627L19.5001 6.49998C20.3285 5.67156 20.3285 4.32841 19.5001 3.49998C18.6716 2.67156 17.3285 2.67156 16.5001 3.49998L3.93729 16.0627C3.59139 16.4086 3.41843 16.5816 3.29475 16.7834C3.18509 16.9624 3.10428 17.1574 3.05529 17.3615C3.00003 17.5917 3.00003 17.8363 3.00003 18.3255V20Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg> to show the SAML method details.
3. In the method details, you can configure the following:

    - **Name**

        Specify a name for the SAML authentication method to be displayed on your custom login page.

    - **Sign on URL**

        Paste the URL that you get from your IdP.

    - **Signing Certificate**

        Paste the entire signing certificate from your IdP, including the starting line `---begin certificate---` and the end line `---end certificate---`.

    - [**Auto-provision Accounts**](#decide-whether-to-enable-auto-provision)

        It is disabled by default. You can enable it according to your need. For security considerations, if you choose to enable auto-provision, it is recommended to limit the allowed email domains for authentication.

    - **Allowed Email Domains**

        After this field is configured, only the specified email domains of this authentication method can log in to TiDB Cloud using the custom URL. When filling in domain names, you need to exclude the `@` symbol and separate them with commas. For example, `company1.com,company2.com`.

        > **Note:**
        >
        > If you have configured email domains, before saving the settings, make sure that you add the email domain that you currently use for login, to avoid that you are locked out by TiDB Cloud.

    - **SCIM Provisioning Accounts**

        It is disabled by default. You can enable it if you want to centralize and automate provisioning, deprovisioning, and identity management for TiDB Cloud organization users and groups from your identity provider. For detailed configuration steps, see [Configure SCIM provisioning](#configure-scim-provisioning).

4. Click **Save**.
#### Configure SCIM provisioning

[System for Cross-domain Identity Management (SCIM)](https://www.rfc-editor.org/rfc/rfc7644) is an open standard that automates the exchange of user identity information between identity domains and IT systems. By configuring SCIM provisioning, user groups from your identity provider can be automatically synchronized to TiDB Cloud, and you can centrally manage roles for these groups in TiDB Cloud.

> **Note:**
>
> SCIM provisioning can be enabled only on the [SAML authentication method](#configure-the-saml-authentication-method).

1. In TiDB Cloud, enable the **SCIM Provisioning Accounts** option of the [SAML authentication method](#configure-the-saml-authentication-method), and then record the following information for later use.

    - SCIM connector base URL
    - Unique identifier field for users
    - Authentication Mode

2. In your identity provider, configure SCIM provisioning for TiDB Cloud.

    1. In your identity provider, add SCIM provisioning for your TiDB Cloud organization to your SAML app integration.

        For example, if your identity provider is Okta, see [Add SCIM provisioning to app integrations](https://help.okta.com/en-us/content/topics/apps/apps_app_integration_wizard_scim.htm).

    2. Assign your SAML app integration to the desired groups in your identity provider so members in the groups can access and use the app integration.

        For example, if your identity provider is Okta, see [Assign an app integration to a group](https://help.okta.com/en-us/content/topics/provisioning/lcm/lcm-assign-app-groups.htm).

   3. Push user groups from your identity provider to TiDB Cloud.

        For example, if your identity provider is Okta, see [Manage group push](https://help.okta.com/en-us/content/topics/users-groups-profiles/usgp-group-push-main.htm).

3. In TiDB Cloud, view groups pushed from your identity provider.

    1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target organization using the combo box in the upper-left corner.
    2. In the left navigation pane, click **Organization Settings** > **Authentication**.
    3. Click the **Groups** tab. The groups synchronized from your identity provider are displayed.
    4. To view users in a group, click **View**.

4. In TiDB Cloud, grant roles to the groups pushed from your identity provider.

    > **Note:**
    >
    > Granting a role to a group means all members in the group gain that role. If a group includes members already in your TiDB Cloud organization, these members also gain the new role of the group.

    1. To grant organization roles to the groups, click **By organization**, and then configure the roles in the **Organization Role** column. To learn about permissions of organization roles, see [Organization roles](https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-user-access#organization-roles).
    2. To grant project roles to the groups, click **By project**, and then configure the roles in the **Project Role** column. To learn about permissions of the project roles, see [Project roles](https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-user-access#project-roles).

5. If you change the members of the pushed groups in your identity provider, these changes are dynamically synchronized to the corresponding groups in TiDB Cloud.

    - If new members are added to the groups in your identity provider, these members gain the roles of the corresponding groups.
    - If some members are removed from the groups in your identity provider, these members are also removed from the corresponding groups in TiDB Cloud.
