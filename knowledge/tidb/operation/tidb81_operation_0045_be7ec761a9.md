# TiDB Dashboard SQL user privileges, least-privilege setup, RBAC, and sign-in

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-user.md`
- Source Title: `TiDB Dashboard User Management`
- Source Heading Path: `TiDB Dashboard User Management | TiDB Dashboard User Management > Required privileges | TiDB Dashboard User Management > Example: Create a least-privileged SQL user to access TiDB Dashboard | TiDB Dashboard User Management > Example: Authorize SQL user to access TiDB Dashboard via RBAC | TiDB Dashboard User Management > Sign in to TiDB Dashboard`
- Source Line Ranges: `5-113`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `sql`, `tidb`
- Topic Tags: `user-management`, `privileges`, `least-privilege`, `security-enhanced-mode`, `sem`, `rbac`, `roles`, `sign-in`, `sql-users`, `access-control`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0045_be7ec761a9`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-user.md#tidb-dashboard-user-management`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e540c166006477176c3e242d7684ed1c8e7a5184e6f2f4839bf626ed32f8d831`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-user#tidb-dashboard-user-management
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-user.md

## Retrieval Guidance

- Use When: Use this chunk when asking which TiDB SQL privileges or RBAC role grants are required for a user to sign in to TiDB Dashboard, including SEM, least-privilege setup, and Dashboard feature-specific privileges.
- Retrieval Keywords: TiDB Dashboard User Management, Required privileges, Security Enhanced Mode, SEM, DASHBOARD_CLIENT, PROCESS, SHOW DATABASES, CONFIG, RESTRICTED_TABLES_ADMIN, RESTRICTED_STATUS_ADMIN, RESTRICTED_VARIABLES_ADMIN, SYSTEM_VARIABLES_ADMIN, SUPER, Fast Bind Executions Plan, CREATE USER 'dashboardAdmin'@'%', GRANT PROCESS, CONFIG ON *.*, GRANT SHOW DATABASES ON *.*, GRANT DASHBOARD_CLIENT ON *.*, CREATE ROLE 'dashboard_access', SET DEFAULT ROLE dashboard_access, sign in to TiDB Dashboard, insufficient privileges
- Follow-up Guidance: The content also includes example SQL statements to create a least-privileged user or RBAC role and notes that users without the listed privileges fail to sign in to TiDB Dashboard.
- Classification Note: This is classified as an operation topic for the self-managed dashboard component because it describes user privilege requirements, SQL GRANT and role setup, and sign-in access control for TiDB Dashboard.

## Official Source Content

# TiDB Dashboard User Management

TiDB Dashboard uses the same user privilege system and sign-in authentication as TiDB. You can control and manage TiDB SQL users to limit their access to TiDB Dashboard. This document describes the least privileges required for TiDB SQL users to access TiDB Dashboard and exemplifies how to create a least-privileged SQL user and how to authorize via RBAC.

For details about how to control and manage TiDB SQL users, see [TiDB User Account Management](https://docs.pingcap.com/tidb/stable/user-account-management).
## Required privileges

- To access TiDB Dashboard when [Security Enhanced Mode (SEM)](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_enhanced_security) is not enabled on the connected TiDB server, the SQL user should have **all** the following privileges:

    - PROCESS
    - SHOW DATABASES
    - CONFIG
    - DASHBOARD_CLIENT

- To access TiDB Dashboard when [Security Enhanced Mode (SEM)](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_enhanced_security) is enabled on the connected TiDB server, the SQL user should have **all** the following privileges:

    - PROCESS
    - SHOW DATABASES
    - CONFIG
    - DASHBOARD_CLIENT
    - RESTRICTED_TABLES_ADMIN
    - RESTRICTED_STATUS_ADMIN
    - RESTRICTED_VARIABLES_ADMIN

- To modify the configurations on the interface after signing in to TiDB Dashboard, the SQL user must also have the following privilege:

    - SYSTEM_VARIABLES_ADMIN

- To use the [Fast Bind Executions Plan](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-statement-details#fast-plan-binding) feature on the interface after signing in to TiDB Dashboard, the SQL user must also have the following privileges:

    - SYSTEM_VARIABLES_ADMIN
    - SUPER

> **Note:**
>
> Users with high privileges such as `ALL PRIVILEGES` or `SUPER` can sign in to TiDB Dashboard as well. Therefore, to comply with the least privilege principle, it is highly recommended that you create users with the required privileges only to prevent unintended operations. See [Privilege Management](https://docs.pingcap.com/tidb/stable/privilege-management) for more information on these privileges.

If an SQL user does not meet the preceding privilege requirements, the user fails to sign in to TiDB Dashboard, as shown below.

![insufficient-privileges](/media/dashboard/dashboard-user-insufficient-privileges.png)
## Example: Create a least-privileged SQL user to access TiDB Dashboard

- When [Security Enhanced Mode (SEM)](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_enhanced_security) is not enabled on the connected TiDB server, to create an SQL user `dashboardAdmin` that can sign in to TiDB Dashboard, execute the following SQL statements:

    ```sql
    CREATE USER 'dashboardAdmin'@'%' IDENTIFIED BY '<YOUR_PASSWORD>';
    GRANT PROCESS, CONFIG ON *.* TO 'dashboardAdmin'@'%';
    GRANT SHOW DATABASES ON *.* TO 'dashboardAdmin'@'%';
    GRANT DASHBOARD_CLIENT ON *.* TO 'dashboardAdmin'@'%';

    -- To modify the configuration items on the interface after signing in to TiDB Dashboard, the user-defined SQL user must be granted with the following privilege.
    GRANT SYSTEM_VARIABLES_ADMIN ON *.* TO 'dashboardAdmin'@'%';
    
    -- To use the Fast Bind Executions Plan feature (https://docs.pingcap.com/tidb/dev/dashboard-statement-details#fast-plan-binding) on the interface after signing in to TiDB Dashboard, the user-defined SQL user must be granted with the following privileges.
    GRANT SYSTEM_VARIABLES_ADMIN ON *.* TO 'dashboardAdmin'@'%';
    GRANT SUPER ON *.* TO 'dashboardAdmin'@'%';
    ```

- When [Security Enhanced Mode (SEM)](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_enhanced_security) is enabled on the connected TiDB server, disable SEM first and execute the following SQL statements to create an SQL user `dashboardAdmin` that can sign in to TiDB Dashboard. After creating the user, enable SEM again:

    ```sql
    CREATE USER 'dashboardAdmin'@'%' IDENTIFIED BY '<YOUR_PASSWORD>';
    GRANT PROCESS, CONFIG ON *.* TO 'dashboardAdmin'@'%';
    GRANT SHOW DATABASES ON *.* TO 'dashboardAdmin'@'%';
    GRANT DASHBOARD_CLIENT ON *.* TO 'dashboardAdmin'@'%';
    GRANT RESTRICTED_STATUS_ADMIN ON *.* TO 'dashboardAdmin'@'%';
    GRANT RESTRICTED_TABLES_ADMIN ON *.* TO 'dashboardAdmin'@'%';
    GRANT RESTRICTED_VARIABLES_ADMIN ON *.* TO 'dashboardAdmin'@'%';

    -- To modify the configuration items on the interface after signing in to TiDB Dashboard, the user-defined SQL user must be granted with the following privilege.
    GRANT SYSTEM_VARIABLES_ADMIN ON *.* TO 'dashboardAdmin'@'%';
    
    -- To use the Fast Bind Executions Plan feature (https://docs.pingcap.com/tidb/dev/dashboard-statement-details#fast-plan-binding) on the interface after signing in to TiDB Dashboard, the user-defined SQL user must be granted with the following privileges.
    GRANT SYSTEM_VARIABLES_ADMIN ON *.* TO 'dashboardAdmin'@'%';
    GRANT SUPER ON *.* TO 'dashboardAdmin'@'%';
    ```
## Example: Authorize SQL user to access TiDB Dashboard via RBAC

The following example demonstrates how to create a role and a user to access TiDB Dashboard through the [role-based access control (RBAC)](https://docs.pingcap.com/tidb/stable/role-based-access-control) mechanism.

1. Create a `dashboard_access` role that meets all privilege requirements of TiDB Dashboard:

    ```sql
    CREATE ROLE 'dashboard_access';
    GRANT PROCESS, CONFIG ON *.* TO 'dashboard_access'@'%';
    GRANT SHOW DATABASES ON *.* TO 'dashboard_access'@'%';
    GRANT DASHBOARD_CLIENT ON *.* TO 'dashboard_access'@'%';
    GRANT SYSTEM_VARIABLES_ADMIN ON *.* TO 'dashboard_access'@'%';
    GRANT SUPER ON *.* TO 'dashboardAdmin'@'%';    
    ```

2. Grant the `dashboard_access` role to other users and set `dashboard_access` as the default role:

    ```sql
    CREATE USER 'dashboardAdmin'@'%' IDENTIFIED BY '<YOUR_PASSWORD>';
    GRANT 'dashboard_access' TO 'dashboardAdmin'@'%';
    -- You need to set dashboard_access as the default role to the user
    SET DEFAULT ROLE dashboard_access to 'dashboardAdmin'@'%';
    ```

After the above steps, you can use the `dashboardAdmin` user to sign in to TiDB Dashboard.
## Sign in to TiDB Dashboard

After creating an SQL user that meets the privilege requirements of TiDB Dashboard, you can use this user to [Sign in](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-access#sign-in) to TiDB Dashboard.
