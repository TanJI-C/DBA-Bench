# Secure TiDB Dashboard user access hardening

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-ops-security.md`
- Source Title: `Secure TiDB Dashboard`
- Source Heading Path: `Secure TiDB Dashboard | Secure TiDB Dashboard > Enhance security of TiDB users | Secure TiDB Dashboard > Enhance security of TiDB users > Set a strong password for the TiDB `root` user | Secure TiDB Dashboard > Enhance security of TiDB users > Create a least-privileged user for TiDB Dashboard`
- Source Line Ranges: `5-23`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `tidb`, `sql`
- Topic Tags: `authentication`, `authorization`, `root-user`, `passwords`, `least-privilege`, `user-management`, `access-control`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0039_b389e38f52`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-ops-security.md#secure-tidb-dashboard`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b2f6133abc44d0fc1137062856edc4c9ac1b50d24ba2d2001714b3a07b1824d4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-ops-security#secure-tidb-dashboard
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-ops-security.md

## Retrieval Guidance

- Use When: Use this chunk when securing TiDB Dashboard sign-in by hardening TiDB SQL user accounts and limiting Dashboard access privileges.
- Retrieval Keywords: Secure TiDB Dashboard, Enhance security of TiDB users, TiDB Dashboard account system is consistent with TiDB SQL users, TiDB root user has no password, set a strong password for the TiDB root user, disable the TiDB root user, Create a least-privileged user for TiDB Dashboard, read-only privilege, principle of least privilege, TiDB Dashboard User Management, TiDB User Account Management
- Follow-up Guidance: The source points to TiDB User Account Management for setting a strong password or disabling the root user, and to TiDB Dashboard User Management for creating a least-privileged SQL user.
- Classification Note: This is classified as an operation topic for the dashboard component because it describes access-control hardening measures for signing in to TiDB Dashboard using TiDB SQL users.

## Official Source Content

# Secure TiDB Dashboard

Although you need to sign into TiDB Dashboard before accessing it, TiDB Dashboard is designed to be accessed by trusted user entities by default. When you want to provide TiDB Dashboard to external network users or untrusted users for access, take the following measures to avoid security vulnerabilities.
## Enhance security of TiDB users
### Set a strong password for the TiDB `root` user

The account system of TiDB Dashboard is consistent with that of TiDB SQL users. By default, TiDB's `root` user has no password, so accessing TiDB Dashboard does not require password authentication, which will give the malicious visitor high privileges, including executing privileged SQL statements.

It is recommended that you set a strong password for the TiDB `root` user. See [TiDB User Account Management](https://docs.pingcap.com/tidb/stable/user-account-management) for details. Alternatively, you can disable the TiDB `root` user.
### Create a least-privileged user for TiDB Dashboard

The account system of TiDB Dashboard is consistent with that of TiDB SQL. Users accessing TiDB Dashboard are authenticated and authorized based on TiDB SQL user's privileges. Therefore, TiDB Dashboard requires limited privileges, or merely the read-only privilege. You can configure users to access TiDB Dashboard based on the principle of least privilege, thus avoiding access of high-privileged users.

It is recommended that you create a least-privileged SQL user to access and sign in to TiDB Dashboard. This avoids access of high-privileged users and improves security. See [TiDB Dashboard User Management](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-user) for details.
