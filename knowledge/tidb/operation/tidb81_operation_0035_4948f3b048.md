# Access, sign in, language, and logout for TiDB Dashboard

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-access.md`
- Source Title: `Access TiDB Dashboard`
- Source Heading Path: `Access TiDB Dashboard | Access TiDB Dashboard > Access TiDB Dashboard when multiple PD instances are deployed | Access TiDB Dashboard > Browser compatibility | Access TiDB Dashboard > Sign in | Access TiDB Dashboard > Switch language | Access TiDB Dashboard > Logout`
- Source Line Ranges: `5-66`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `pd`, `tidb`, `operator`, `sql`
- Topic Tags: `access`, `browser-compatibility`, `sign-in`, `sso`, `sql-user`, `session`, `language-switch`, `logout`, `reverse-proxy`, `firewall`, `kubernetes`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0035_4948f3b048`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-access.md#access-tidb-dashboard`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ba82bd497fd3b4f67d5acdd273fefea372a30b1ccdb881a413207d1aa7e6b017`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-access#access-tidb-dashboard
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-access.md

## Retrieval Guidance

- Use When: Use this when you need TiDB Dashboard access details, sign-in options, browser compatibility, language switching, session length, or logout behavior.
- Retrieval Keywords: Access TiDB Dashboard, 127.0.0.1:2379/dashboard, PD instance address and port, multiple PD instances, firewall or reverse proxy, Chrome >= 77, Firefox >= 68, Edge >= 17, TiDB root account, Single Sign-On (SSO), User-defined SQL User, 24 hours, Switch Language, Logout
- Follow-up Guidance: See the related TiDB Dashboard pages for reverse proxy and SSO configuration if you need those setup details.
- Classification Note: The chunk is an access and sign-in guide for TiDB Dashboard, covering how to open the page, authenticate, switch language, and log out.

## Official Source Content

# Access TiDB Dashboard

To access TiDB Dashboard, visit <http://127.0.0.1:2379/dashboard> via your browser. Replace `127.0.0.1:2379` with the actual PD instance address and port.

> **Note:**
>
> TiDB v6.5.0 (and later) and TiDB Operator v1.4.0 (and later) support deploying TiDB Dashboard as an independent Pod on Kubernetes. Using TiDB Operator, you can access the IP address of this Pod to start TiDB Dashboard. For details, see [Deploy TiDB Dashboard independently in TiDB Operator](https://docs.pingcap.com/tidb-in-kubernetes/v1.6/get-started#deploy-tidb-dashboard-independently).
## Access TiDB Dashboard when multiple PD instances are deployed

When multiple PD instances are deployed in your cluster and you can directly access **every** PD instance and port, you can simply replace `127.0.0.1:2379` in the <http://127.0.0.1:2379/dashboard/> address with **any** PD instance address and port.

> **Note:**
>
> If a firewall or reverse proxy is configured and you cannot directly access every PD instance, you might not be able to access TiDB Dashboard. Usually, this is because the firewall or reverse proxy is not correctly configured. See [Use TiDB Dashboard behind Reverse Proxy](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-ops-reverse-proxy) and [Secure TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-ops-security) to learn how to correctly configure the firewall or reverse proxy when multiple PD instances are deployed.
## Browser compatibility

You can use TiDB Dashboard in the following common desktop browsers of a relatively newer version:

- Chrome >= 77
- Firefox >= 68
- Edge >= 17

> **Note:**
>
> If you use the browsers above of earlier versions or other browsers to access TiDB Dashboard, some functions might not work properly.
## Sign in

After accessing TiDB Dashboard, you will be directed to the user login interface.

- You can sign in to TiDB Dashboard using the TiDB `root` account.
- You can also sign in to TiDB Dashboard via Single Sign-On (SSO). For more information, see [Configure SSO for TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-session-sso).
- If you have created a [User-defined SQL User](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-user), you can sign in using this account and the corresponding password.

If one of the following situations exists, the login might fail:

- TiDB `root` user does not exist.
- PD is not started or cannot be accessed.
- TiDB is not started or cannot be accessed.
- Wrong `root` password.

Once you have signed in, the session remains valid within the next 24 hours. To learn how to sign out, refer to the [Logout](#logout) section.
## Switch language

The following languages are supported in TiDB Dashboard:

- English
- Chinese (simplified)

In the **SQL User Sign In** page, you can click the **Switch Language** drop-down list to switch the interface language.

![Switch language](/media/dashboard/dashboard-access-switch-language.png)
## Logout

Once you have logged in, click the login user name in the left navigation bar to switch to the user page. Click the **Logout** button on the user page to log out the current user. After logging out, you need to re-enter your username and password.

![Logout](/media/dashboard/dashboard-access-logout.png)
