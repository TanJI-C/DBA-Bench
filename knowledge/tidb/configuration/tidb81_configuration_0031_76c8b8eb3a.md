# Configure TiDB Dashboard behind a reverse proxy

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-ops-reverse-proxy.md`
- Source Title: `Use TiDB Dashboard behind a Reverse Proxy`
- Source Heading Path: `Use TiDB Dashboard behind a Reverse Proxy | Use TiDB Dashboard behind a Reverse Proxy > Procedures | Use TiDB Dashboard behind a Reverse Proxy > Procedures > Step 1: Get the actual TiDB Dashboard address | Use TiDB Dashboard behind a Reverse Proxy > Procedures > Step 2: Configure the reverse proxy`
- Source Line Ranges: `5-112`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `pd`, `tiup`, `shared`
- Topic Tags: `reverse-proxy`, `haproxy`, `nginx`, `address-discovery`, `proxy-upstream`, `security-warning`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0031_76c8b8eb3a`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-ops-reverse-proxy.md#use-tidb-dashboard-behind-a-reverse-proxy`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `214827ba5e2a4669d6014d858bad2ee99203fd961e82e8369ef15ca7bdb11870`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-ops-reverse-proxy#use-tidb-dashboard-behind-a-reverse-proxy
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-ops-reverse-proxy.md

## Retrieval Guidance

- Use When: Use this content when you need the official steps to expose TiDB Dashboard through a reverse proxy and must find the actual TiDB Dashboard address before configuring HAProxy or NGINX.
- Retrieval Keywords: TiDB Dashboard behind a Reverse Proxy, tiup cluster display CLUSTER_NAME --dashboard, actual TiDB Dashboard address, Deployment with multiple PD instances, HAProxy, NGINX, frontend tidb_dashboard_front, backend tidb_dashboard_back, use_backend tidb_dashboard_back if { path /dashboard } or { path_beg /dashboard/ }, proxy_pass http://192.168.0.123:2379/dashboard/, /dashboard/, 8033, sudo nginx -s reload, security risks
- Follow-up Guidance: The content also points to Secure TiDB Dashboard for security details and notes that `tiup cluster display CLUSTER_NAME --dashboard` is available only in `tiup cluster` v1.0.3 or later.
- Classification Note: This is classified as configuration because it gives reverse proxy setup procedures, upstream discovery commands, and exact HAProxy and NGINX configuration snippets for TiDB Dashboard.

## Official Source Content

# Use TiDB Dashboard behind a Reverse Proxy

You can use a reverse proxy to safely expose the TiDB Dashboard service from the internal network to the external.
## Procedures
### Step 1: Get the actual TiDB Dashboard address

When multiple PD instances are deployed in the cluster, only one of the PD instances actually runs TiDB Dashboard. Therefore, you need to ensure that the upstream of the reverse proxy points to the correct address. For details of this mechanism, see [Deployment with multiple PD instances](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-ops-deploy#deployment-with-multiple-pd-instances).

When you use the TiUP tool for deployment, execute the following command to get the actual TiDB Dashboard address (replace `CLUSTER_NAME` with your cluster name):

```shell
tiup cluster display CLUSTER_NAME --dashboard
```

The output is the actual TiDB Dashboard address. A sample is as follows:

```bash
http://192.168.0.123:2379/dashboard/
```

> **Note:**
>
> This feature is available only in the later version of the `tiup cluster` deployment tool (v1.0.3 or later).
>
> <details>
> <summary>Upgrade TiUP Cluster</summary>
>
> ```bash
> tiup update --self
> tiup update cluster --force
> ```
>
> </details>
### Step 2: Configure the reverse proxy

<details>
<summary> <strong>Use HAProxy</strong> </summary>

When you use [HAProxy](https://www.haproxy.org/) as the reverse proxy, take the following steps:

1. Use reverse proxy for TiDB Dashboard on the `8033` port (for example). In the HAProxy configuration file, add the following configuration:

    ```haproxy
    frontend tidb_dashboard_front
      bind *:8033
      use_backend tidb_dashboard_back if { path /dashboard } or { path_beg /dashboard/ }

    backend tidb_dashboard_back
      mode http
      server tidb_dashboard 192.168.0.123:2379
    ```

    Replace `192.168.0.123:2379` with IP and port of the actual address of the TiDB Dashboard obtained in [Step 1](#step-1-get-the-actual-tidb-dashboard-address).

    > **Warning:**
    >
    > You must retain the `if` part in the `use_backend` directive to ensure that services **only in this path** are behind reverse proxy; otherwise, security risks might be introduced. See [Secure TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-ops-security).

2. Restart HAProxy for the configuration to take effect.

3. Test whether the reverse proxy is effective: access the `/dashboard/` address on the `8033` port of the machine where HAProxy is located (such as `http://example.com:8033/dashboard/`) to access TiDB Dashboard.

</details>

<details>
<summary> <strong>Use NGINX</strong> </summary>

When you use [NGINX](https://nginx.org/) as the reverse proxy, take the following steps:

1. Use reverse proxy for TiDB Dashboard on the `8033` port (for example). In the NGINX configuration file, add the following configuration:

    ```nginx
    server {
        listen 8033;
        location /dashboard/ {
        proxy_pass http://192.168.0.123:2379/dashboard/;
        }
    }
    ```

    Replace `http://192.168.0.123:2379/dashboard/` with the actual address of the TiDB Dashboard obtained in [Step 1](#step-1-get-the-actual-tidb-dashboard-address).

    > **Warning:**
    >
    > You must keep the `/dashboard/` path in the `proxy_pass` directive to ensure that only the services under this path are reverse proxied. Otherwise, security risks will be introduced. See [Secure TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-ops-security).

2. Reload NGINX for the configuration to take effect.

    ```shell
    sudo nginx -s reload
    ```

3. Test whether the reverse proxy is effective: access the `/dashboard/` address on the `8033` port of the machine where NGINX is located (such as `http://example.com:8033/dashboard/`) to access TiDB Dashboard.

</details>
