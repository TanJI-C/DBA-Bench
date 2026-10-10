# Customize TiDB Dashboard path prefix with reverse proxy

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-ops-reverse-proxy.md`
- Source Title: `Use TiDB Dashboard behind a Reverse Proxy`
- Source Heading Path: `Use TiDB Dashboard behind a Reverse Proxy > Customize path prefix | Use TiDB Dashboard behind a Reverse Proxy > Customize path prefix > Step 1: Modify PD configuration to specify the path prefix of TiDB Dashboard service | Use TiDB Dashboard behind a Reverse Proxy > Customize path prefix > Step 2: Modify the reverse proxy configuration | Use TiDB Dashboard behind a Reverse Proxy > What's next`
- Source Line Ranges: `113-309`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `pd`, `tiup`, `shared`
- Topic Tags: `path-prefix`, `pd-configuration`, `public-path-prefix`, `reverse-proxy`, `haproxy`, `nginx`, `rolling-restart`, `firewall`, `security-warning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0032_c94ee98ff8`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-ops-reverse-proxy.md#customize-path-prefix`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `095ac4cbdf53d97d8745a4bf5ea88e276f9350b345423ed1eaf2dd486714443b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-ops-reverse-proxy#customize-path-prefix
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-ops-reverse-proxy.md

## Retrieval Guidance

- Use When: Use this content when you need to customize the TiDB Dashboard path prefix behind a reverse proxy, including PD `dashboard.public-path-prefix` settings and matching HAProxy or NGINX path mapping.
- Retrieval Keywords: Customize path prefix, public-path-prefix, dashboard.public-path-prefix, [dashboard], PD configuration, server_configs, tiup cluster edit-config CLUSTER_NAME, tiup cluster reload CLUSTER_NAME -R pd, /foo, /, http-request set-path %[path,regsub(^/foo/?,/dashboard/)], http-request set-path /dashboard%[path], location /foo/, location /, proxy_pass http://192.168.0.123:2379/dashboard/, rolling restart, reverse proxy, Secure TiDB Dashboard, firewall
- Follow-up Guidance: The content further notes that after a customized path prefix takes effect, TiDB Dashboard can only be accessed through a reverse proxy that matches the path prefix, and it links to Secure TiDB Dashboard for firewall and security information.
- Classification Note: This is classified as configuration because it defines PD `dashboard.public-path-prefix` changes, TiUP configuration edit and reload commands, and the exact reverse proxy rules needed for custom or root path prefixes.

## Official Source Content

## Customize path prefix

TiDB Dashboard provides services by default in the `/dashboard/` path, such as `http://example.com:8033/dashboard/`, which is the case even for reverse proxies. To configure the reverse proxy to provide the TiDB Dashboard service with a non-default path, such as `http://example.com:8033/foo/` or `http://example.com:8033/`, take the following steps.
### Step 1: Modify PD configuration to specify the path prefix of TiDB Dashboard service

Modify the `public-path-prefix` configuration item in the `[dashboard]` category of the PD configuration to specify the path prefix of the TiDB Dashboard service. After this item is modified, restart the PD instance for the modification to take effect.

For example, if the cluster is deployed using TiUP and you want the service to run on `http://example.com:8033/foo/`, you can specify the following configuration:

```yaml
server_configs:
  pd:
    dashboard.public-path-prefix: /foo
```

<details>
<summary> <strong>Modify configuration when deploying a new cluster using TiUP</strong> </summary>

If you are deploying a new cluster, you can add the configuration above to the `topology.yaml` TiUP topology file and deploy the cluster. For specific instruction, see [TiUP deployment document](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup#step-3-initialize-cluster-topology-file).

</details>

<details>

<summary> <strong>Modify configuration of a deployed cluster using TiUP</strong> </summary>

For a deployed cluster:

1. Open the configuration file of the cluster in the edit mode (replace `CLUSTER_NAME` with the cluster name).

    ```shell
    tiup cluster edit-config CLUSTER_NAME
    ```

2. Modify or add configuration items under the `pd` configuration of `server_configs`. If no `server_configs` exists, add it at the top level:

    ```yaml
    monitored:
      ...
    server_configs:
      tidb: ...
      tikv: ...
      pd:
        dashboard.public-path-prefix: /foo
      ...
    ```

    The configuration file after the modification is similar to the following file:

    ```yaml
    server_configs:
      pd:
        dashboard.public-path-prefix: /foo
      global:
        user: tidb
        ...
    ```

    Or

    ```yaml
    monitored:
      ...
    server_configs:
      tidb: ...
      tikv: ...
      pd:
        dashboard.public-path-prefix: /foo
    ```

3. Perform a rolling restart to all PD instances for the modified configuration to take effect (replace `CLUSTER_NAME` with your cluster name):

    ```shell
    tiup cluster reload CLUSTER_NAME -R pd
    ```

See [Common TiUP Operations - Modify the configuration](https://docs.pingcap.com/tidb/stable/maintain-tidb-using-tiup#modify-the-configuration) for details.

</details>

If you want that the TiDB Dashboard service is run in the root path (such as `http://example.com:8033/`), use the following configuration:

```yaml
server_configs:
  pd:
    dashboard.public-path-prefix: /
```

> **Warning:**
>
> After the modified and customized path prefix takes effect, you cannot directly access TiDB Dashboard. You can only access TiDB Dashboard through a reverse proxy that matches the path prefix.
### Step 2: Modify the reverse proxy configuration

<details>
<summary> <strong>Use HAProxy</strong> </summary>

Taking `http://example.com:8033/foo/` as an example, the corresponding HAProxy configuration is as follows:

```haproxy
frontend tidb_dashboard_front
  bind *:8033
  use_backend tidb_dashboard_back if { path /foo } or { path_beg /foo/ }

backend tidb_dashboard_back
  mode http
  http-request set-path %[path,regsub(^/foo/?,/dashboard/)]
  server tidb_dashboard 192.168.0.123:2379
```

Replace `192.168.0.123:2379` with IP and port of the actual address of the TiDB Dashboard obtained in [Step 1](#step-1-get-the-actual-tidb-dashboard-address).

> **Warning:**
>
> You must retain the `if` part in the `use_backend` directive to ensure that services **only in this path** are behind reverse proxy; otherwise, security risks might be introduced. See [Secure TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-ops-security).

If you want that the TiDB Dashboard service is run in the root path (such as `http://example.com:8033/`), use the following configuration:

```haproxy
frontend tidb_dashboard_front
  bind *:8033
  use_backend tidb_dashboard_back
backend tidb_dashboard_back
  mode http
  http-request set-path /dashboard%[path]
  server tidb_dashboard 192.168.0.123:2379
```

Modify the configuration and restart HAProxy for the modified configuration to take effect.

</details>

<details>
<summary> <strong>Use NGINX</strong> </summary>

Taking `http://example.com:8033/foo/` as an example, the corresponding NGINX configuration is as follows:

```nginx
server {
  listen 8033;
  location /foo/ {
    proxy_pass http://192.168.0.123:2379/dashboard/;
  }
}
```

Replace `http://192.168.0.123:2379/dashboard/` with the actual address of the TiDB Dashboard obtained in [Step 1](#step-1-get-the-actual-tidb-dashboard-address).

> **Warning:**
>
> You must retain the `/dashboard/` path in the `proxy_pass` directive to ensure that services **only in this path** are behind reverse proxy; otherwise, security risks might be introduced. See [Secure TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-ops-security).

If you want that the TiDB Dashboard service is run in the root path (such as `http://example.com:8033/`), use the following configuration:

```nginx
server {
  listen 8033;
  location / {
    proxy_pass http://192.168.0.123:2379/dashboard/;
  }
}
```

Modify the configuration and restart NGINX for the modified configuration to take effect.

```shell
sudo nginx -s reload
```

</details>
## What's next

To learn how to enhance the security of TiDB Dashboard, such as configuring a firewall, see [Secure TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-ops-security).
