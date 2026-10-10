# TiDB Cloud SQL users and roles management in console

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/configure-sql-users.md`
- Source Title: `Manage Database Users and Roles`
- Source Heading Path: `Manage Database Users and Roles | Manage Database Users and Roles > Roles of database users | Manage Database Users and Roles > Prerequisites | Manage Database Users and Roles > View SQL users | Manage Database Users and Roles > Create a SQL user | Manage Database Users and Roles > Edit a SQL user | Manage Database Users and Roles > Delete a SQL user`
- Source Line Ranges: `5-102`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `tidb`
- Topic Tags: `sql-users`, `roles`, `rbac`, `permissions`, `console`, `prerequisites`, `view-users`, `create-user`, `edit-user`, `delete-user`, `password-management`, `built-in-roles`, `custom-roles`, `beta-feature`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0290_1aa71fdc32`
- Source ID: `tidb-docs-8.1:tidb-cloud/configure-sql-users.md#manage-database-users-and-roles`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `17dab316e07126f0eafbf66006c0d184a959ff2eb14e0d3ff9dcf46988543f21`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/configure-sql-users#manage-database-users-and-roles
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/configure-sql-users.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about managing TiDB Cloud database SQL users or roles in the TiDB Cloud console, including viewing, creating, editing, deleting users, prerequisites, or built-in and custom role assignment on the SQL Users page.
- Retrieval Keywords: SQL Users page, TiDB Cloud console, Manage Database Users and Roles, database users and roles, View SQL users, Create SQL User, Edit a SQL user, Delete a SQL user, Built-in Role, Custom Role, Database Admin, Database Read-Write, Database Read-Only, CREATE ROLE, Organization Owner, Project Owner, Project Data Access Read-Write, Project Data Access Read-Only, <prefix>.root, beta, Request Support, Apply for the SQL Users page
- Follow-up Guidance: The content also states that SQL users and roles can be managed with a SQL client using SQL statements, and it notes special restrictions for the default `<prefix>.root` user on role modification and deletion.
- Classification Note: This is classified as an operation topic because the content provides console-based procedures and prerequisites for viewing, creating, editing, and deleting SQL users and assigning built-in or custom roles in TiDB Cloud.

## Official Source Content

# Manage Database Users and Roles

This document describes how to manage database users and roles using the **SQL Users** page in the [TiDB Cloud console](https://tidbcloud.com/).

> **Note:**
>
> - The **SQL Users** page is in beta and is only available upon request. To request this feature, click **?** in the lower-right corner of the [TiDB Cloud console](https://tidbcloud.com) and click **Request Support**. Then, fill in "Apply for the SQL Users page" in the **Description** field and click **Submit**.
> - Database users and roles are independent of [organization and project users and roles](https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-user-access). Database users are used to access databases in a TiDB cluster, while organization and project users are used to access organizations and projects in the [TiDB Cloud console](https://tidbcloud.com/).
> - In addition to the **SQL Users** page, you can also manage database users and roles by connecting to your cluster with a SQL client and writing SQL statements. For more information, see [TiDB User Account Management](https://docs.pingcap.com/tidb/dev/user-account-management).
## Roles of database users

In TiDB Cloud, you can grant both a built-in role and multiple custom roles (if available) to a SQL user for role-based access control.

- Built-in roles

    TiDB Cloud provides the following built-in roles to help you control the database access of SQL users. You can grant one of the built-in roles to a SQL user.

    - `Database Admin`
    - `Database Read-Write`
    - `Database Read-Only`

- Custom roles

    In addition to a built-in role, if your cluster has custom roles that are created using the [`CREATE ROLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-role) statement, you can also grant these custom roles to a SQL user when you create or edit SQL users in the TiDB Cloud console.

After a SQL user is granted both a built-in role and multiple custom roles, the user's permissions will be the union of all the permissions derived from these roles.
## Prerequisites

- To manage database users and roles using the **SQL Users** page, you must be in the `Organization Owner` role of your organization or the `Project Owner` role of your project.
- If you are in the `Project Data Access Read-Write` or `Project Data Access Read-Only` role of a project, you can only view database users on the **SQL Users** page of that project.
## View SQL users

To view SQL users of a cluster, take the following steps:

1. On the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, click the name of your target cluster to go to its overview page.

    > **Tip:**
    >
    > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

2. In the left navigation pane, click **Settings** > **SQL Users**.
## Create a SQL user

To create a SQL user for a cluster, take the following steps:

1. Navigate to the [**SQL Users**](https://docs.pingcap.com/tidb/stable/tidb-cloud/configure-sql-users#view-sql-users) page of your cluster.

2. Click **Create SQL User** in the upper-right corner.

    A dialog for the SQL user configuration is displayed.

3. In the dialog, provide the information of the SQL user as follows:

    1. Enter the name of the SQL user.
    2. Either create a password for the SQL user or let TiDB Cloud automatically generate a password for the user.
    3. Grant roles to the SQL user.

        - **Built-in Role**: you need to select a built-in role for the SQL user in the **Built-in Role** drop-down list.

        - **Custom Role**: if your cluster has custom roles that are created using the [`CREATE ROLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-role) statement, you can grant custom roles to the SQL user by selecting the roles from the **Custom Role** drop-down list. Otherwise, the **Custom Roles** drop-down list is invisible here.

      For each SQL user, you can grant a built-in role and multiple custom roles (if any).

4. Click **Create**.
## Edit a SQL user

To edit the password or roles of a SQL user, take the following steps:

1. Navigate to the [**SQL Users**](https://docs.pingcap.com/tidb/stable/tidb-cloud/configure-sql-users#view-sql-users) page of your cluster.

2. In the row of the SQL user to be edited, click **...** in the **Action** column, and then click **Edit**.

    A dialog for the SQL user configuration is displayed.

3. In the dialog, you can edit the user password and roles as needed, and then click **Update**.

    > **Note:**
    >
    > The roles of the default `<prefix>.root` user do not support modification. You can only change the password.
## Delete a SQL user

To delete a SQL user, take the following steps:

1. Navigate to the [**SQL Users**](https://docs.pingcap.com/tidb/stable/tidb-cloud/configure-sql-users#view-sql-users) page of your cluster.
2. In the row of the SQL user to be deleted, click **...** in the **Action** column, and then click **Delete**.

    > **Note:**
    >
    > The default `<prefix>.root` user does not support deletion.

3. Confirm the deletion.
