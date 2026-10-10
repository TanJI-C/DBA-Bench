# TiDB Cloud security overview and IAM concepts

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/security-concepts.md`
- Source Title: `Security`
- Source Heading Path: `Security | Security > Identity and access management (IAM) | Security > Identity and access management (IAM) > TiDB Cloud user accounts | Security > Identity and access management (IAM) > Database access control | Security > Identity and access management (IAM) > Database user accounts | Security > Identity and access management (IAM) > SQL Proxy accounts | Security > Identity and access management (IAM) > TiDB privileges and roles | Security > Identity and access management (IAM) > Organization and projects | Security > Identity and access management (IAM) > Example structure | Security > Identity and access management (IAM) > Key features | Security > Identity and access management (IAM) > Identity and Access Management (IAM) Roles`
- Source Line Ranges: `5-160`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `tidb`
- Topic Tags: `security`, `iam`, `user-accounts`, `sso`, `database-access-control`, `database-users`, `sql-proxy`, `privileges`, `roles`, `rbac`, `organizations`, `projects`, `clusters`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0084_3d1745e917`
- Source ID: `tidb-docs-8.1:tidb-cloud/security-concepts.md#security`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e35b29fb744fc54f8dc9165ecbc9cc50e70c57682932308a65db9e40a5361513`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/security-concepts#security
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/security-concepts.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiDB Cloud IAM concepts, TiDB Cloud user accounts, database access control, SQL Proxy accounts, TiDB privileges and roles, or the organization-project-cluster hierarchy.
- Retrieval Keywords: Identity and Access Management (IAM), TiDB Cloud user accounts, Standard SSO authentication, Organization SSO authentication, OIDC, SAML, Database access control, mysql.user, 'root'@'%', SQL Proxy accounts, role_admin, JWT tokens, TiDB privileges and roles, MySQL 5.7, MySQL 8.0, RBAC, dynamic privileges, BACKUP_ADMIN, organizations projects clusters, organization-level roles, project-level roles
- Follow-up Guidance: The source points to Standard SSO Authentication, Organization SSO Authentication, TiDB User Account Management, and manage-user-access pages for more details.
- Classification Note: This is classified as architecture because the content describes the TiDB Cloud security framework structure, IAM model, account types, privilege model, and hierarchical organization of organizations, projects, and clusters.

## Official Source Content

# Security

TiDB Cloud provides a robust and flexible security framework designed to protect data, enforce access control, and meet modern compliance standards. This framework combines advanced security features with operational efficiency to support organizational needs at scale.

**Key components**

- **Identity and Access Management (IAM)**: Secure and flexible authentication and permission management for both the TiDB Cloud console and database environments.

- **Network access control**: Configurable connectivity options, including private endpoints, VPC peering, TLS encryption, and IP access lists.

- **Data access control**: Advanced encryption capabilities, such as Customer-Managed Encryption Keys (CMEK), to safeguard data at rest.

- **Audit logging**: Comprehensive activity tracking for both console actions and database operations, ensuring accountability and transparency.

By integrating these capabilities, TiDB Cloud empowers organizations to safeguard sensitive data, streamline access control, and optimize security operations.
## Identity and access management (IAM)

TiDB Cloud employs Identity and Access Management (IAM) to securely and efficiently manage user identities and permissions across both the console and database environments. IAM features are designed to meet organizational security and compliance needs through a combination of authentication options, role-based access control, and a hierarchical resource structure.
### TiDB Cloud user accounts

TiDB Cloud user accounts are the foundation for managing identity and access to resources. Each account represents an individual or entity within the platform and supports multiple authentication methods to suit organizational needs:

- **Default username and password**

    - Users create accounts with an email address and password.

    - Suitable for small teams or individuals without an external identity provider.

- **Standard SSO authentication**

    - Users log in via GitHub, Google, or Microsoft accounts.

    - Enabled by default for all organizations.

    - **Best practice**: Use for smaller teams or those without strict compliance needs.

    - For more information, see [Standard SSO Authentication](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-sso-authentication).

- **Organization SSO authentication**

    - Integrates with corporate identity providers (IdPs) using OIDC or SAML protocols.

    - Enables features like MFA enforcement, password expiration policies, and domain restrictions.

    - **Best practice**: Ideal for larger organizations with advanced security and compliance requirements.

    - For more information, see [Organization SSO Authentication](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-org-sso-authentication).
### Database access control

TiDB Cloud provides granular database access control through user-based and role-based permissions. These mechanisms allow administrators to securely manage access to data objects and schemas while ensuring compliance with organizational security policies.

- **Best practices:**

    - Implement the principle of least privilege by granting users only the permissions they need for their roles.

    - Regularly audit and update user access to align with changing organizational requirements.
### Database user accounts

Database user accounts are stored in the `mysql.user` system table and uniquely identified by a username and client host.

During database initialization, TiDB automatically creates a default account: `'root'@'%'`.

For more information, see [TiDB User Account Management](https://docs.pingcap.com/tidb/stable/user-account-management#user-names-and-passwords).
### SQL Proxy accounts

SQL Proxy accounts are special-purpose accounts automatically generated by TiDB Cloud. Key characteristics of these accounts include the following:

- **Linked to TiDB Cloud user accounts:** Each SQL Proxy account corresponds to a specific TiDB Cloud user.

- **Mapped to roles:** SQL Proxy accounts are granted the `role_admin` role.

- **Token-based:** SQL Proxy accounts use secure JWT tokens instead of passwords, ensuring seamless, restricted access through the TiDB Cloud Data Service or SQL Editor.
### TiDB privileges and roles

TiDB's privilege management system is based on MySQL 5.7, which enables fine-grained access to database objects. At the same time, TiDB also introduces MySQL 8.0's RBAC and dynamic privilege mechanism. This enables fine-grained and convenient management of database privileges.

**Static privileges**

- Supports fine-grained access control based on database objects, including tables, views, indexes, users, and other objects.

- *Example: Grant SELECT privileges on a specific table to a user.*

**Dynamic privileges**

- Supports reasonable splitting of database management privileges to achieve fine-grained control of system management privileges.

- Example: Assign `BACKUP_ADMIN` to accounts managing database backups without broader administrative permissions.

**SQL roles (RBAC)**

- Group permissions into roles that can be assigned to users, enabling streamlined privilege management and dynamic updates.

- Example: Assign a read-write role to analysts to simplify user access control.

This system ensures flexibility and precision in managing user access while aligning with organizational policies.
### Organization and projects

TiDB Cloud manages users and resources with a hierarchical structure: organizations, projects, and clusters.

**Organizations**

- The top-level entity for managing resources, roles, and billing.

- The organization owner has full permissions, including project creation and role assignment.

**Projects**

- Subdivisions of an organization containing clusters and project-specific configurations.

- Managed by project owners responsible for clusters within their scope.

**Clusters**

- Individual database instances within a project.
### Example structure

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
### Key features

- **Granular permissions**:
    - Assign specific roles at both the organization and project levels for precise access control.

    - Ensure flexibility and security by carefully planning role assignments.

- **Billing management**:
    - Billing is consolidated at the organization level, with detailed breakdowns available for each project.
### Identity and Access Management (IAM) Roles

TiDB Cloud provides role-based access control to manage permissions across organizations and projects:

- **[Organization-Level roles](https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-user-access#organization-roles)**: Grant permissions to manage the entire organization, including billing and project creation.

- **[Project-Level roles](https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-user-access#project-roles)**: Assign permissions to manage specific projects, including clusters and configurations.
