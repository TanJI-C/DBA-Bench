# Network exposure controls for TiDB Dashboard and PD port

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-ops-security.md`
- Source Title: `Secure TiDB Dashboard`
- Source Heading Path: `Secure TiDB Dashboard > Use a firewall to block untrusted access | Secure TiDB Dashboard > Use a firewall to block untrusted access > How to open access to TiDB Dashboard port when deploying multiple PD instances | Secure TiDB Dashboard > Reverse proxy only for TiDB Dashboard | Secure TiDB Dashboard > Enable TLS for reverse proxy | Secure TiDB Dashboard > Other recommended safety measures`
- Source Line Ranges: `24-99`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `pd`, `tiup`, `operator`, `tidb`, `tikv`, `shared`
- Topic Tags: `firewall`, `network-security`, `pd-client-port`, `reverse-proxy`, `tls`, `mtls`, `kubernetes`, `external-access`, `warnings`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0040_4c2089c11e`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-ops-security.md#use-a-firewall-to-block-untrusted-access`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f566e2896693b6b622911df5a9059d35ad232a6845d1f8793489498943b7e99f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-ops-security#use-a-firewall-to-block-untrusted-access
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-ops-security.md

## Retrieval Guidance

- Use When: Use this chunk when controlling external network exposure of TiDB Dashboard on the PD client port, including firewall, reverse proxy, TLS, and multiple-PD access considerations.
- Retrieval Keywords: Use a firewall to block untrusted access, PD client port, http://IP:2379/dashboard/, http://IP:2379/pd/api/v1/members, Reverse proxy only for TiDB Dashboard, only with the /dashboard prefix, do not expose the PD client port directly to the external network, How to open access to TiDB Dashboard port when deploying multiple PD instances, tiup cluster display CLUSTER_NAME --dashboard, TiDB Dashboard independently in TiDB Operator, independent Pod on Kubernetes, Enable TLS for reverse proxy, mTLS, Use TiDB Dashboard behind a Reverse Proxy
- Follow-up Guidance: For multiple PD instances, the source says the actual TiDB Dashboard address can be viewed with `tiup cluster display CLUSTER_NAME --dashboard`, and it also points to reverse proxy and TLS documentation for safer exposure.
- Classification Note: This is classified as an operation topic for the dashboard component because it covers network-access controls and exposure boundaries around TiDB Dashboard services carried on the PD client port.

## Official Source Content

## Use a firewall to block untrusted access

> **Note:**
>
> TiDB v6.5.0 (and later) and TiDB Operator v1.4.0 (and later) support deploying TiDB Dashboard as an independent Pod on Kubernetes. Using TiDB Operator, you can access the IP address of this Pod to start TiDB Dashboard. This port does not communicate with other privileged interfaces of PD and no extra firewall is required if provided externally. For details, see [Deploy TiDB Dashboard independently in TiDB Operator](https://docs.pingcap.com/tidb-in-kubernetes/v1.6/get-started#deploy-tidb-dashboard-independently).

TiDB Dashboard provides services through the PD client port, which defaults to <http://IP:2379/dashboard/>. Although TiDB Dashboard requires identity authentication, other privileged interfaces (such as <http://IP:2379/pd/api/v1/members>) in PD carried on the PD client port do not require identity authentication and can perform privileged operations. Therefore, exposing the PD client port directly to the external network is extremely risky.

It is recommended that you take the following measures:

+ Use a firewall to prohibit a component from accessing **any** client port of the PD component via the external network or untrusted network.

    > **Note:**
    >
    > TiDB, TiKV, and other components need to communicate with the PD component through the PD client port, so do not block access to the internal network between components. Otherwise, the cluster will become unavailable.

+ See [Use TiDB Dashboard behind a Reverse Proxy](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-ops-reverse-proxy) to learn how to configure the reverse proxy to safely provide the TiDB Dashboard service on another port to the external network.
### How to open access to TiDB Dashboard port when deploying multiple PD instances

> **Warning:**
>
> This section describes an unsafe access solution, which is for the test environment only. **DO NOT** use this solution in the production environment.

In the test environment, you might need to configure the firewall to open the TiDB Dashboard port for external access.

When multiple PD instances are deployed, only one of the PD instances actually runs TiDB Dashboard, and browser redirection occurs when you access other PD instances. Therefore, you need to ensure that the firewall is configured with the correct IP address. For details of this mechanism, see [Deployment with multiple PD instances](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-ops-deploy#deployment-with-multiple-pd-instances).

When using the TiUP deployment tool, you can view the address of the PD instance that actually runs TiDB Dashboard by running the following command (replace `CLUSTER_NAME` with the cluster name):

```bash
tiup cluster display CLUSTER_NAME --dashboard
```

The output is the actual TiDB Dashboard address.

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

The following is a sample output:

```bash
http://192.168.0.123:2379/dashboard/
```

In this example, the firewall needs to be configured with inbound access for the `2379` port of the `192.168.0.123` open IP, and the TiDB Dashboard is accessed via <http://192.168.0.123:2379/dashboard/>.
## Reverse proxy only for TiDB Dashboard

As mentioned in [Use a firewall to block untrusted access](#use-a-firewall-to-block-untrusted access), the services provided under the PD client port include not only TiDB Dashboard (located at <http://IP:2379/dashboard/>), but also other privileged interfaces in PD (such as <http://IP:2379/pd/api/v1/members>). Therefore, when using a reverse proxy to provide TiDB Dashboard to the external network, ensure that the services **ONLY** with the `/dashboard` prefix are provided (**NOT** all services under the port) to avoid that the external network can access the privileged interface in PD through the reverse proxy.

It is recommended that you see [Use TiDB Dashboard behind a Reverse Proxy](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-ops-reverse-proxy) to learn a safe and recommended reverse proxy configuration.
## Enable TLS for reverse proxy

To further enhance the security of the transport layer, you can enable TLS for reverse proxy, and even introduce mTLS to authenticate user certificates.

See [Configuring HTTPS servers](http://nginx.org/en/docs/http/configuring_https_servers.html) and [HAProxy SSL Termination](https://www.haproxy.com/blog/haproxy-ssl-termination/) for more details.
## Other recommended safety measures

- [Enable TLS Authentication and Encrypt the Stored Data](https://docs.pingcap.com/tidb/stable/enable-tls-between-components)
- [Enable TLS Between TiDB Clients and Servers](https://docs.pingcap.com/tidb/stable/enable-tls-between-clients-and-servers)
