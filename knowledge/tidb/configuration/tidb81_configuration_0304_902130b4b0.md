# Cloud Organization SSO overview, prerequisites, and enablement

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-org-sso-authentication.md`
- Source Title: `Organization SSO Authentication`
- Source Heading Path: `Organization SSO Authentication | Organization SSO Authentication > Before you begin | Organization SSO Authentication > Before you begin > Decide a custom URL for the TiDB Cloud login page of your organization | Organization SSO Authentication > Before you begin > Decide authentication methods for your organization members | Organization SSO Authentication > Before you begin > Decide whether to enable auto-provision | Organization SSO Authentication > Before you begin > Notify your members about the Cloud Organization SSO migration plan | Organization SSO Authentication > Step 1. Enable Cloud Organization SSO`
- Source Line Ranges: `5-92`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `sso`, `organization`, `authentication`, `custom-login-url`, `prerequisites`, `auto-provision`, `member-migration`, `enablement`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0304_902130b4b0`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-org-sso-authentication.md#organization-sso-authentication`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `871927b5337ca6a52b30f8c63d4891fbb1fb72cbce4ea8747af48fb80e1a583b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-org-sso-authentication#organization-sso-authentication
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-org-sso-authentication.md

## Retrieval Guidance

- Use When: Use this chunk when someone needs the Cloud Organization SSO overview, prerequisites, custom login URL behavior, member migration considerations, or the exact steps to enable it in TiDB Cloud.
- Retrieval Keywords: Cloud Organization SSO, Organization SSO Authentication, custom login URL, https://tidbcloud.com/enterprise/signin/your-company-name, https://tidbcloud.com, Organization Owner, Organization Settings > Authentication, Enable Cloud Organization SSO, paid organizations, cannot be disabled, auto-provision, OIDC, SAML, re-invited and re-join
- Follow-up Guidance: After enablement, the source says members must use the custom URL, and if a list of users needs to be re-invited and re-join, TiDB Cloud automatically sends invitation emails for identity verification.
- Classification Note: This is classified as configuration because the content describes prerequisites, authentication choices, custom URL decisions, and the UI steps to enable Cloud Organization SSO in TiDB Cloud.

## Official Source Content

# Organization SSO Authentication

Single Sign-On (SSO) is an authentication scheme that enables members in your TiDB Cloud [organization](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-glossary#organization) to log in to TiDB Cloud using identities from an identity provider (IdP) instead of email addresses and passwords.

TiDB Cloud supports the following two types of SSO authentication:

- [Standard SSO](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-sso-authentication): members can log in to the [TiDB Cloud console](https://tidbcloud.com/) using their GitHub, Google, or Microsoft authentication methods. The standard SSO is enabled by default for all organizations in TiDB Cloud.

- Cloud Organization SSO: members can log in to a custom login page of TiDB Cloud using the authentication methods specified by your organization. The Cloud Organization SSO is disabled by default.

Compared with standard SSO, Cloud Organization SSO provides more flexibility and customization so you can better meet your organization's security and compliance requirements. For example, you can specify which authentication methods are displayed on the login page, limit which email address domains are allowed for login, and let your members log in to TiDB Cloud with your identity provider (IdP) that uses the [OpenID Connect (OIDC)](https://openid.net/connect/) or [Security Assertion Markup Language (SAML)](https://en.wikipedia.org/wiki/Security_Assertion_Markup_Language) identity protocol.

In this document, you will learn how to migrate the authentication scheme of your organization from standard SSO to Cloud Organization SSO.

> **Note:**
>
> The Cloud Organization SSO feature is only available for paid organizations.
## Before you begin

Before migrating to Cloud Organization SSO, check and confirm the items in this section for your organization.

> **Note:**
>
> - Once Cloud Organization SSO is enabled, it cannot be disabled.
> - To enable Cloud Organization SSO, you need to be in the `Organization Owner` role of your TiDB Cloud organization. For more information about roles, see [User roles](https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-user-access#user-roles).
### Decide a custom URL for the TiDB Cloud login page of your organization

When Cloud Organization SSO is enabled, your members must use your custom URL instead of the public login URL (`https://tidbcloud.com`) to log in to TiDB Cloud.

The custom URL cannot be changed after the enablement, so you need to decide which URL to be used in advance.

The format of the custom URL is `https://tidbcloud.com/enterprise/signin/your-company-name`, in which you can customize your company name.
### Decide authentication methods for your organization members

TiDB Cloud provides the following authentication methods for Organization SSO.

- Username and password
- Google
- GitHub
- Microsoft
- OIDC
- SAML

When you enable Cloud Organization SSO, the first four methods are enabled by default. If you want to enforce the use of SSO for your organization, you can disable the username and password authentication method.

All the enabled authentication methods will be displayed on your custom TiDB Cloud login page, so you need to decide which authentication methods to be enabled or disabled in advance.
### Decide whether to enable auto-provision

Auto-provision is a feature that allows members to automatically join an organization without requiring an invitation from the `Organization Owner` or `Project Owner`. In TiDB Cloud, it is disabled by default for all the supported authentication methods.

- When auto-provision is disabled for an authentication method, only users who have been invited by an `Organization Owner` or `Project Owner` can log in to your custom URL.
- When auto-provision is enabled for an authentication method, any users using this authentication method can log in to your custom URL. After login, they are automatically assigned the default **Member** role within the organization.

For security considerations, if you choose to enable auto-provision, it is recommended to limit the allowed email domains for authentication when you [configure the authentication method details](#step-2-configure-authentication-methods).
### Notify your members about the Cloud Organization SSO migration plan

Before enabling Cloud Organization SSO, make sure to inform your members about the following:

- The custom login URL of TiDB Cloud
- The time when to start using the custom login URL instead of `https://tidbcloud.com` for login
- The available authentication methods
- Whether members need invitations to log in to the custom URL
## Step 1. Enable Cloud Organization SSO

To enable Cloud Organization SSO, take the following steps:

1. Log in to the [TiDB Cloud console](https://tidbcloud.com) as a user with the `Organization Owner` role, and then switch to your target organization using the combo box in the upper-left corner.
2. In the left navigation pane, click **Organization Settings** > **Authentication**.
3. On the **Authentication** page, click **Enable**.
4. In the dialog, enter the custom URL for your organization, which must be unique in TiDB Cloud.

    > **Note:**
    >
    > The URL cannot be changed once Cloud Organization SSO is enabled. Members in your organization will only be able to log in to TiDB Cloud using your custom URL. If you need to change the configured URL later, contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) for assistance.

5. Click the **I understand and confirm** check box, and then click **Enable**.

    > **Note:**
    >
    > If the dialog includes a list of users to be re-invited and re-join for Cloud Organization SSO, TiDB Cloud will automatically send the invitation emails to those users after you enable Cloud Organization SSO. After receiving the invitation email, each user needs to click the link in the email to verify their identity, and the custom login page shows.
