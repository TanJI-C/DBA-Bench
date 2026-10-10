# HAProxy configuration and lifecycle commands

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/haproxy-best-practices.md`
- Source Title: `Best Practices for Using HAProxy in TiDB`
- Source Heading Path: `Best Practices for Using HAProxy in TiDB > Deploy HAProxy > Configure HAProxy | Best Practices for Using HAProxy in TiDB > Deploy HAProxy > Start HAProxy | Best Practices for Using HAProxy in TiDB > Deploy HAProxy > Stop HAProxy`
- Source Line Ranges: `168-252`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`
- Topic Tags: `haproxy`, `load-balancing`, `configuration`, `proxy-protocol`, `startup`, `shutdown`, `health-checks`, `stats`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0003_188886682d`
- Source ID: `tidb-docs-8.1:best-practices/haproxy-best-practices.md#configure-haproxy`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `89d895f0dde5b491446e9fb72522b473ad6b33b09ef274d13c7230625856aa71`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/haproxy-best-practices#configure-haproxy
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/haproxy-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when looking for HAProxy configuration items, PROXY protocol settings for TiDB, or the commands to start and stop HAProxy in a TiDB deployment.
- Retrieval Keywords: /etc/haproxy/haproxy.cfg, global, defaults, listen admin_stats, listen tidb-cluster, bind 0.0.0.0:3390, mode tcp, balance leastconn, server tidb-1 10.9.18.229:4000 check inter 2000 rise 2 fall 3, send-proxy, SHOW PROCESSLIST, PROXY protocol, proxy-protocol.networks, stats socket /var/lib/haproxy/stats, stats uri /haproxy, stats auth admin:pingcap123, haproxy -f /etc/haproxy/haproxy.cfg, ps -ef | grep haproxy, kill -9 ${haproxy.pid}
- Follow-up Guidance: The source also notes that before using the PROXY protocol, you need to configure proxy-protocol.networks in the TiDB server configuration file.
- Classification Note: This chunk is classified as configuration because it provides HAProxy configuration examples, listener and health-check settings, PROXY protocol options, and lifecycle commands for starting and stopping HAProxy.

## Official Source Content

### Configure HAProxy

A configuration template is generated when you use yum to install HAProxy. You can also customize the following configuration items according to your scenario.

```yaml
global                                     # Global configuration.
   log         127.0.0.1 local2            # Global syslog servers (up to two).
   chroot      /var/lib/haproxy            # Changes the current directory and sets superuser privileges for the startup process to improve security.
   pidfile     /var/run/haproxy.pid        # Writes the PIDs of HAProxy processes into this file.
   maxconn     4096                        # The maximum number of concurrent connections for a single HAProxy process. It is equivalent to the command-line argument "-n".
   nbthread    48                          # The maximum number of threads. (The upper limit is equal to the number of CPUs)
   user        haproxy                     # Same with the UID parameter.
   group       haproxy                     # Same with the GID parameter. A dedicated user group is recommended.
   daemon                                  # Makes the process fork into background. It is equivalent to the command line "-D" argument. It can be disabled by the command line "-db" argument.
   stats socket /var/lib/haproxy/stats     # The directory where statistics output is saved.

defaults                                   # Default configuration.
   log global                              # Inherits the settings of the global configuration.
   retries 2                               # The maximum number of retries to connect to an upstream server. If the number of connection attempts exceeds the value, the backend server is considered unavailable.
   timeout connect  2s                     # The maximum time to wait for a connection attempt to a backend server to succeed. It should be set to a shorter time if the server is located on the same LAN as HAProxy.
   timeout client 30000s                   # The maximum inactivity time on the client side.
   timeout server 30000s                   # The maximum inactivity time on the server side.

listen admin_stats                         # The name of the Stats page reporting information from frontend and backend. You can customize the name according to your needs.
   bind 0.0.0.0:8080                       # The listening port.
   mode http                               # The monitoring mode.
   option httplog                          # Enables HTTP logging.
   maxconn 10                              # The maximum number of concurrent connections.
   stats refresh 30s                       # Automatically refreshes the Stats page every 30 seconds.
   stats uri /haproxy                      # The URL of the Stats page.
   stats realm HAProxy                     # The authentication realm of the Stats page.
   stats auth admin:pingcap123             # User name and password in the Stats page. You can have multiple user names.
   stats hide-version                      # Hides the version information of HAProxy on the Stats page.
   stats admin if TRUE                     # Manually enables or disables the backend server (supported in HAProxy 1.4.9 or later versions).

listen tidb-cluster                        # Database load balancing.
   bind 0.0.0.0:3390                       # The Floating IP address and listening port.
   mode tcp                                # HAProxy uses layer 4, the transport layer.
   balance leastconn                       # The server with the smallest number of connections receives the connection. "leastconn" is recommended where long sessions are expected, such as LDAP, SQL and TSE, rather than protocols using short sessions, such as HTTP. The algorithm is dynamic, which means that server weights might be adjusted on the fly for slow starts for instance.
   server tidb-1 10.9.18.229:4000 check inter 2000 rise 2 fall 3       # Detects port 4000 at a frequency of once every 2000 milliseconds. If it is detected as successful twice, the server is considered available; if it is detected as failed three times, the server is considered unavailable.
   server tidb-2 10.9.39.208:4000 check inter 2000 rise 2 fall 3
   server tidb-3 10.9.64.166:4000 check inter 2000 rise 2 fall 3
```

To check the source IP address using `SHOW PROCESSLIST`, you need to configure the [PROXY protocol](https://www.haproxy.org/download/1.8/doc/proxy-protocol.txt) to connect to TiDB.

```yaml
   server tidb-1 10.9.18.229:4000 send-proxy check inter 2000 rise 2 fall 3       
   server tidb-2 10.9.39.208:4000 send-proxy check inter 2000 rise 2 fall 3
   server tidb-3 10.9.64.166:4000 send-proxy check inter 2000 rise 2 fall 3
```

> **Note:**
>
> Before using the PROXY protocol, you need to configure [`proxy-protocol.networks`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#networks) in the configuration file of the TiDB server.
### Start HAProxy

To start HAProxy, run `haproxy`. `/etc/haproxy/haproxy.cfg` is read by default (recommended).

```bash
haproxy -f /etc/haproxy/haproxy.cfg
```
### Stop HAProxy

To stop HAProxy, use the `kill -9` command.

1. Run the following command:

    ```bash
    ps -ef | grep haproxy
    ```

2. Terminate the process of HAProxy:

    ```bash
    kill -9 ${haproxy.pid}
    ```
