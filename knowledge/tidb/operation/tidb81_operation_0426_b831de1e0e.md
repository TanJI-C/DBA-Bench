# TiDB Cloud standard SSO sign-in with Google GitHub and Microsoft

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-sso-authentication.md`
- Source Title: `Standard SSO Authentication`
- Source Heading Path: `Standard SSO Authentication | Standard SSO Authentication > Sign in with Google SSO | Standard SSO Authentication > Sign in with GitHub SSO | Standard SSO Authentication > Sign in with Microsoft SSO`
- Source Line Ranges: `5-65`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `sso`, `authentication`, `login`, `google`, `github`, `microsoft`, `console`, `two-factor-authentication`, `terms-acceptance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0426_b831de1e0e`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-sso-authentication.md#standard-sso-authentication`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1921636644aa25281523a9206b65a9c1e20502cf4122520053a146727a2b3c82`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-sso-authentication#standard-sso-authentication
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-sso-authentication.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how to sign in to the TiDB Cloud console with Google, GitHub, or Microsoft SSO, or what happens on first login and with two-factor verification.
- Retrieval Keywords: TiDB Cloud console, Standard SSO Authentication, Sign in with Google, Sign in with GitHub, Sign in with Microsoft, Google SSO, GitHub SSO, Microsoft SSO, TiDB Cloud login page, accept TiDB Cloud terms, welcome page, 2-Step Verification, two-factor authentication, two-step verification, verification code, cannot modify account password, cannot enable multi-factor authentication (MFA) using the TiDB console
- Follow-up Guidance: The source also notes that if you want to log into TiDB Cloud through username and password, see Password Authentication.
- Classification Note: This is an operation chunk because the content describes the login flow in the TiDB Cloud console for Google, GitHub, and Microsoft SSO, including first-time terms acceptance and verification code prompts.

## Official Source Content

# Standard SSO Authentication

This document describes how to log in to the [TiDB Cloud console](https://tidbcloud.com/) via basic Single Sign-on (SSO) authentication, which is quick and convenient.

TiDB Cloud supports SSO authentication for Google, GitHub, and Microsoft accounts. If you log in to TiDB Cloud via SSO authentication, because your ID and credentials are stored on the third-party Google, GitHub, and Microsoft platforms, you will not be able to modify your account password and enable multi-factor authentication (MFA) using the TiDB console.

> **Note:**
>
> If you want to log into TiDB Cloud through username and password, see [Password Authentication](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-password-authentication).
## Sign in with Google SSO 

To sign in with your Google account, take the following steps:

1. Go to the TiDB Cloud [login](https://tidbcloud.com/) page.

2. Click **Sign in with Google**. You will be directed to the Google login page.

3. Follow the on-screen instructions to enter your Google username and password. 

    If the login is successful, you will be directed to the TiDB Cloud console.

    > **Note:**
    >
    > - If this is the first time you sign in with Google, you will be asked whether to accept TiDB Cloud terms. After you read and agree with the terms, you will see the TiDB Cloud welcome page and then be directed to the TiDB Cloud console.
   > - If you have enabled 2-Step Verification (also called two-factor authentication) for your Google account, you will also need to provide the verification code after entering your username and password.
## Sign in with GitHub SSO

To sign in with your GitHub account, take the following steps:

1. Go to the TiDB Cloud [login](https://tidbcloud.com/) page.

2. Click **Sign in with GitHub**. You will be directed to the GitHub login page.

3. Follow the on-screen instructions to enter your GitHub username and password.

    If the login is successful, you will be directed to the TiDB Cloud console.

     > **Note:**
     >
     > - If this is the first time you sign in with GitHub, you will be asked whether to accept TiDB Cloud terms. After you read and agree with the terms, you will see the TiDB Cloud welcome page and then be directed to the TiDB Cloud console.
     > - If you have configured two-factor authentication for your GitHub account, you will also need to provide the verification code after entering your username and password.
## Sign in with Microsoft SSO

To sign in with your Microsoft account, take the following steps:

1. Go to the TiDB Cloud [login](https://tidbcloud.com/) page.

2. Click **Sign in with Microsoft**. You will be directed to the Microsoft login page.

3. Follow the on-screen instructions to enter your Microsoft username and password.

    If the login is successful, you will be directed to the TiDB Cloud console.

     > **Note:**
     >
     > - If this is the first time you sign in with Microsoft, you will be asked whether to accept TiDB Cloud terms. After you read and agree with the terms, you will see the TiDB Cloud welcome page and then be directed to the TiDB Cloud console.
     > - If you have set up two-step verification for your Microsoft account, you will also need to provide the verification code after entering your username and password.
