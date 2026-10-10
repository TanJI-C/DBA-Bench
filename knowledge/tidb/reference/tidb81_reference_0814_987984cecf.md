# Organizations, projects, and user roles

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/manage-user-access.md`
- Source Title: `Identity Access Management`
- Source Heading Path: `Identity Access Management | Identity Access Management > Organizations and projects | Identity Access Management > Organizations and projects > Organizations | Identity Access Management > Organizations and projects > Projects | Identity Access Management > User roles | Identity Access Management > User roles > Organization roles | Identity Access Management > User roles > Project roles`
- Source Line Ranges: `5-118`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `identity-access`, `organizations`, `projects`, `user-roles`, `permissions`, `billing`, `audit-logging`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0814_987984cecf`
- Source ID: `tidb-docs-8.1:tidb-cloud/manage-user-access.md#identity-access-management`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `90a3329e01b319ef9778dce21c3f712ae65863742f02b92557dcff286fa4992a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-user-access#identity-access-management
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/manage-user-access.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the TiDB Cloud organization and project hierarchy or wants to know the permissions of roles such as `Organization Owner`, `Organization Billing Manager`, `Organization Billing Viewer`, `Organization Console Audit Manager`, `Organization Viewer`, `Project Owner`, `Project Data Access Read-Write`, `Project Data Access Read-Only`, and `Project Viewer`.
- Retrieval Keywords: Identity Access Management, Organizations and projects, User roles, Organization Owner, Organization Billing Manager, Organization Billing Viewer, Organization Console Audit Manager, Organization Viewer, Project Owner, Project Data Access Read-Write, Project Data Access Read-Only, Project Viewer, billing at the organization level, manage organization settings, invite users to or remove users from an organization, manage cluster operations in the project, database audit logging, console audit logging, SQL Editor, Data Service, changefeeds, recovery groups, spending limit
- Follow-up Guidance: The source also links role permissions to related topics including console audit logging, database audit logging, spending limit, Data Service, changefeeds, recovery groups, and SQL Editor.
- Classification Note: This is reference content because it defines the TiDB Cloud access model and enumerates organization-level and project-level permissions for each role.

## Official Source Content

# Identity Access Management

This document describes how to manage access to organizations, projects, roles, and user profiles in TiDB Cloud.

Before accessing TiDB Cloud, [create a TiDB Cloud account](https://tidbcloud.com/free-trial). You can either sign up with email and password so that you can [manage your password using TiDB Cloud](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-password-authentication), or choose your Google, GitHub, or Microsoft account for single sign-on (SSO) to TiDB Cloud.
## Organizations and projects

TiDB Cloud provides a hierarchical structure based on organizations and projects to facilitate the management of TiDB Cloud users and clusters. If you are an organization owner, you can create multiple projects in your organization.

For example:

```
- Your organization
    - Project 1
        - Cluster 1
        - Cluster 2
    - Project 2
        - Cluster 3
        - Cluster 4
    - Project 3
        - Cluster 5
        - Cluster 6
```

Under this structure:

- To access an organization, a user must be a member of that organization.
- To access a project in an organization, a user must at least have the read access to the project in that organization.
- To manage clusters in a project, a user must be in the `Project Owner` role.

For more information about user roles and permissions, see [User Roles](#user-roles).
### Organizations

An organization can contain multiple projects.

TiDB Cloud calculates billing at the organization level and provides the billing details for each project.

If you are an organization owner, you have the highest permission in your organization.

For example, you can do the following:

- Create different projects (such as development, staging, and production) for different purposes.
- Assign different users with different organization roles and project roles.
- Configure organization settings. For example, configure the time zone for your organization.
### Projects

A project can contain multiple clusters.

If you are a project owner, you can manage clusters and project settings for your project.

For example, you can do the following:

- Create multiple clusters according to your business need.
- Assign different users with different project roles.
- Configure project settings. For example, configure different alert settings for different projects.
## User roles

TiDB Cloud defines different user roles to manage different permissions of TiDB Cloud users in organizations, projects, or both.

You can grant roles to a user at the organization level or at the project level. Make sure to carefully plan the hierarchy of your organizations and projects for security considerations.
### Organization roles

At the organization level, TiDB Cloud defines four roles, in which `Organization Owner` can invite members and grant organization roles to members.

| Permission  | `Organization Owner` | `Organization Billing Manager` | `Organization Billing Viewer` | `Organization Console Audit Manager` | `Organization Viewer` |
|---|---|---|---|---|---|
| Manage organization settings, such as projects, API keys, and time zones. | ✅ | ❌ | ❌ | ❌ | ❌ |
| Invite users to or remove users from an organization, and edit organization roles of users. | ✅ | ❌ | ❌ | ❌ | ❌ |
| All the permissions of `Project Owner` for all projects in the organization. | ✅ | ❌ | ❌ | ❌ | ❌ |
| Create projects with Customer-Managed Encryption Key (CMEK) enabled. | ✅ | ❌ | ❌ | ❌ | ❌ |
| Edit payment information for the organization. | ✅ | ✅ | ❌ | ❌ | ❌ |
| View bills and use [cost explorer](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing#cost-explorer). | ✅ | ✅ | ✅ | ❌ | ❌ |
| Manage TiDB Cloud [console audit logging](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-console-auditing) for the organization. | ✅ | ❌ | ❌ | ✅ | ❌ |
| View users in the organization and projects in which the member belong to. | ✅ | ✅ | ✅ | ✅ | ✅ |

> **Note:**
>
> - The `Organization Console Audit Manager` role (renamed from `Organization Console Audit Admin`) is used to manage audit logging in the TiDB Cloud console, instead of database audit logging. To manage database auditing, use the `Project Owner` role at the project level.
> - The `Organization Billing Manager` role is renamed from `Organization Billing Admin`, and the `Organization Viewer` role is renamed from `Organization Member`.
### Project roles

At the project level, TiDB Cloud defines three roles, in which `Project Owner` can invite members and grant project roles to members.

> **Note:**
>
> - `Organization Owner` has all the permissions of <code>Project Owner</code> for all projects so `Organization Owner` can invite project members and grant project roles to members too.
> - Each project role has all the permissions of <code>Organization Viewer</code> by default.
> - If a user in your organization does not belong to any projects, the user does not have any project permissions.

| Permission  | `Project Owner` | `Project Data Access Read-Write` | `Project Data Access Read-Only` | `Project Viewer` |
|---|---|---|---|---|
| Manage project settings | ✅ | ❌ | ❌ | ❌ |
| Invite users to or remove users from a project, and edit project roles of users. | ✅ | ❌ | ❌ | ❌ |
| Manage [database audit logging](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-auditing) of the project. | ✅ | ❌ | ❌ | ❌ |
| Manage [spending limit](https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-serverless-spend-limit) for all TiDB Cloud Serverless clusters in the project. | ✅ | ❌ | ❌ | ❌ |
| Manage cluster operations in the project, such as cluster creation, modification, and deletion. | ✅ | ❌ | ❌ | ❌ |
| Manage branches for TiDB Cloud Serverless clusters in the project, such as branch creation, connection, and deletion. | ✅ | ❌ | ❌ | ❌ |
| Manage [recovery groups](https://docs.pingcap.com/tidb/stable/tidb-cloud/recovery-group-overview) for TiDB Cloud Dedicated clusters in the project, such as recovery group creation and deletion. | ✅ | ❌ | ❌ | ❌ |
| Manage cluster data such as data import, data backup and restore, and data migration. | ✅ | ✅ | ❌ | ❌ |
| Manage [Data Service](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-overview) for data read-only operations such as using or creating endpoints to read data. | ✅ | ✅ | ✅ | ❌ |
| Manage [Data Service](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-overview) for data read and write operations. | ✅ | ✅ | ❌ | ❌ |
| View cluster data using [SQL Editor](https://docs.pingcap.com/tidb/stable/tidb-cloud/explore-data-with-chat2query). | ✅ | ✅ | ✅ | ❌ |
| Modify and delete cluster data using [SQL Editor](https://docs.pingcap.com/tidb/stable/tidb-cloud/explore-data-with-chat2query). | ✅ | ✅ | ❌ | ❌ |
| Manage [changefeeds](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-overview). | ✅ | ✅ | ✅ | ❌ |
| Review and reset cluster passwords. | ✅ | ❌ | ❌ | ❌ |
| View cluster overview, backup records, metrics, events, and [changefeeds](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-overview) in the project. | ✅ | ✅ | ✅ | ✅ |
