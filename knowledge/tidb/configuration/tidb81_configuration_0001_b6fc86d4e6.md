# Security setup for root, passwords, Grafana, and TiDB Dashboard access

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices-for-security-configuration.md`
- Source Title: `Best Practices for TiDB Security Configuration`
- Source Heading Path: `Best Practices for TiDB Security Configuration | Best Practices for TiDB Security Configuration > Set the initial password for the root user | Best Practices for TiDB Security Configuration > Enable password complexity checks | Best Practices for TiDB Security Configuration > Change the default Grafana password | Best Practices for TiDB Security Configuration > Enhance TiDB Dashboard security | Best Practices for TiDB Security Configuration > Enhance TiDB Dashboard security > Use a least privilege user | Best Practices for TiDB Security Configuration > Enhance TiDB Dashboard security > Restrict access control`
- Source Line Ranges: `5-62`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `dashboard`, `pd`, `tiup`, `operator`, `sql`
- Topic Tags: `security`, `root-password`, `password-policy`, `grafana`, `dashboard`, `least-privilege`, `access-control`, `firewall`, `reverse-proxy`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0001_b6fc86d4e6`
- Source ID: `tidb-docs-8.1:best-practices-for-security-configuration.md#best-practices-for-tidb-security-configuration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `be322b0b350c261f6f55fc395ae9590b6c1866b56aaf93dc7a2aaf0dee70ee9b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices-for-security-configuration#best-practices-for-tidb-security-configuration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices-for-security-configuration.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving guidance about securing a new TiDB deployment by setting the root password, enabling password complexity checks, changing the default Grafana password, or tightening TiDB Dashboard access.
- Retrieval Keywords: root user, initial password, TiUP, TiDB Operator, Set initial account and password, password complexity policy, Grafana, admin/admin, change the default Grafana password, TiDB Dashboard, least privilege user, TiDB SQL user permissions, read-only access, restrict access control, 2379 port, firewall, trusted domains, reverse proxy
- Follow-up Guidance: The content also notes that TiDB Dashboard access can be provided to external users by configuring a reverse proxy on a different port, and that internal component access to the PD client port must not be blocked.
- Classification Note: This is classified as configuration because the content provides deployment-time security configuration guidance for accounts, passwords, Grafana access, and TiDB Dashboard network exposure.

## Official Source Content

# Best Practices for TiDB Security Configuration

The security of TiDB is crucial for protecting data integrity and confidentiality. This document provides guidelines for configuring TiDB clusters securely during deployment. By following these best practices, you can effectively reduce potential security risks, prevent data breaches, and ensure the continuous, stable, and reliable operation of your TiDB database system.

> **Note:**
>
> This document offers general recommendations on TiDB security configurations. PingCAP does not guarantee the completeness or accuracy of the information, and it assumes no responsibility for any issues arising from the use of this guide. Users should assess these recommendations based on their specific needs and consult professionals for tailored advice.
## Set the initial password for the root user

By default, the root user in a newly created TiDB cluster has no password, which poses a potential security risk. If a password is not set, anyone can attempt to log in to the TiDB database as the root user, potentially gaining access to and modifying data.

To avoid this risk, it is recommended to set a root password during deployment:

- For deployments using TiUP, refer to [Deploy TiDB Cluster Using TiUP](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup#step-7-start-a-tidb-cluster) to generate a random password for the root user.
- For deployments using TiDB Operator, refer to [Set initial account and password](https://docs.pingcap.com/tidb-in-kubernetes/stable/initialize-a-cluster#set-initial-account-and-password) to set the root password.
## Enable password complexity checks

By default, TiDB does not enforce password complexity policies, which might lead to the use of weak or empty passwords, increasing security risks.

To ensure that database users create strong passwords, it is recommended to configure a reasonable [password complexity policy](https://docs.pingcap.com/tidb/stable/password-management#password-complexity-policy). For example, configure a policy that requires passwords to include a combination of uppercase letters, lowercase letters, numbers, and special characters. By enforcing password complexity checks, you can improve database security, prevent brute force attacks, reduce internal threats, ensure compliance with regulations, and lower the risk of data breaches, thus enhancing overall security.
## Change the default Grafana password

TiDB installation includes the Grafana component by default, and the default username and password are typically `admin`/`admin`. If the password is not changed promptly, attackers could exploit this to gain control of the system.

It is recommended to immediately change the Grafana password to a strong one during the TiDB deployment, and regularly update the password to ensure system security. Here are the steps to change the Grafana password:

- Upon first login to Grafana, follow the prompts to change the password.

    ![Grafana Password Reset Guide](/media/grafana-password-reset1.png)

- Access the Grafana personal configuration center to change the password.

    ![Grafana Password Reset Guide](/media/grafana-password-reset2.png)
## Enhance TiDB Dashboard security
### Use a least privilege user

TiDB Dashboard shares the account system with TiDB SQL users, and TiDB Dashboard authorization is based on TiDB SQL user permissions. TiDB Dashboard requires minimal permissions and can even operate with read-only access.

To enhance security, it is recommended to create a [least-privilege SQL user](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-user) for accessing the TiDB Dashboard and to avoid using high-privilege users.
### Restrict access control

By default, TiDB Dashboard is designed for trusted users. The default port includes additional API interfaces besides TiDB Dashboard. If you want to allow access to TiDB Dashboard from external networks or untrusted users, take the following measures to avoid security vulnerabilities:

- Use a firewall or other mechanisms to restrict the default `2379` port to trusted domains, preventing access by external users.

    > **Note:**
    >
    > TiDB, TiKV, and other components need to communicate with the PD component via the PD client port. Do not block internal network access between components, which will make the cluster unavailable.

- [Configure a reverse proxy](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-ops-reverse-proxy#use-tidb-dashboard-behind-a-reverse-proxy) to securely provide TiDB Dashboard services to external users on a different port.
