# TiDB Cloud OAuth 2.0 overview, grant types, access, and app authorization management

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/oauth2.md`
- Source Title: `OAuth 2.0`
- Source Heading Path: `OAuth 2.0 | OAuth 2.0 > OAuth grant types | OAuth 2.0 > OAuth grant types > Device Code grant type | OAuth 2.0 > OAuth grant types > Authorization Code grant type | OAuth 2.0 > Use OAuth to access TiDB Cloud | OAuth 2.0 > View and revoke authorized OAuth apps`
- Source Line Ranges: `5-47`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `oauth2`, `authentication`, `authorization`, `device-code`, `authorization-code`, `cli-access`, `partner-apps`, `authorized-apps`, `revoke-access`, `account-settings`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0251_711460f8e6`
- Source ID: `tidb-docs-8.1:tidb-cloud/oauth2.md#oauth-2-0`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5f64c1d2d5a34b43af1cbdeefd1b28dd7f7cc38143e1db4b90326689921896e3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/oauth2#oauth-2-0
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/oauth2.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiDB Cloud OAuth 2.0 support, supported grant types, CLI access via OAuth, partner app access requests, or viewing and revoking authorized OAuth apps in the console.
- Retrieval Keywords: OAuth 2.0, TiDB Cloud, OAuth grant types, Device Code grant type, Authorization Code grant type, Use OAuth to access TiDB Cloud, ticloud auth login, ticloud auth logout, Cloud & Technology Partner, Authorized OAuth Apps, Account Settings, Revoke
- Follow-up Guidance: The content also points to the TiDB Cloud console path Account Settings > Authorized OAuth Apps and states that authorization can be revoked with Revoke.
- Classification Note: This is classified as configuration because the content describes how OAuth 2.0 access is used and managed in TiDB Cloud, including grant types, CLI authentication entry points, and authorized app management.

## Official Source Content

# OAuth 2.0

This document describes how to access TiDB Cloud using OAuth 2.0.

OAuth, which stands for Open Authorization, is an open standard authentication protocol that allows secure access to resources on behalf of a user. It provides a way for third-party applications to access user resources without exposing their credentials.

[OAuth 2.0](https://oauth.net/2/), the latest version of OAuth, has become the industry-standard protocol for authorization. Key benefits of OAuth 2.0 include:

- Security: By using token-based authentication, OAuth 2.0 minimizes the risk of password theft and unauthorized access.
- Convenience: You can grant and revoke access to your data without managing multiple credentials.
- Access control: You can specify the exact level of access granted to third-party applications, ensuring only necessary permissions are given.
## OAuth grant types

The OAuth framework specifies several grant types for different use cases. TiDB Cloud supports two most common OAuth grant types: Device Code and Authorization Code.
### Device Code grant type

It is usually used by browserless or input-constrained devices in the device flow to exchange a previously obtained device code for an access token.
### Authorization Code grant type

It is the most common OAuth 2.0 grant type, which enables both web apps and native apps to get an access token after a user authorizes an app.
## Use OAuth to access TiDB Cloud

You can access TiDB Cloud CLI using the OAuth 2.0 Device Code grant type:

- [ticloud auth login](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-auth-login): Authenticate with TiDB Cloud
- [ticloud auth logout](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-auth-logout): Log out of TiDB Cloud

If your app needs to access TiDB Cloud using OAuth, submit a request to [become a Cloud & Technology Partner](https://www.pingcap.com/partners/become-a-partner/) (select **Cloud & Technology Partner** in **Partner Program**). We will reach out to you.
## View and revoke authorized OAuth apps

You can view the records for authorized OAuth applications in the TiDB Cloud console as follows:

1. In the [TiDB Cloud console](https://tidbcloud.com/), click <MDSvgIcon name="icon-top-account-settings" /> in the lower-left corner.
2. Click **Account Settings**.
3. Click the **Authorized OAuth Apps** tab. You can view authorized OAuth applications.

You can click **Revoke** to revoke your authorization at any time.
