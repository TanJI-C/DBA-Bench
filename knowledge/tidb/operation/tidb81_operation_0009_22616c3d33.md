# Deploy and install HAProxy with command reference

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/haproxy-best-practices.md`
- Source Title: `Best Practices for Using HAProxy in TiDB`
- Source Heading Path: `Best Practices for Using HAProxy in TiDB > Deploy HAProxy | Best Practices for Using HAProxy in TiDB > Deploy HAProxy > Install HAProxy | Best Practices for Using HAProxy in TiDB > Deploy HAProxy > Install HAProxy > HAProxy commands`
- Source Line Ranges: `77-167`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`
- Topic Tags: `haproxy`, `deployment`, `installation`, `source-build`, `compilation`, `environment-setup`, `binary-path`, `verification`, `command-line-options`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0009_22616c3d33`
- Source ID: `tidb-docs-8.1:best-practices/haproxy-best-practices.md#deploy-haproxy`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9b22f5f299bf771c211292de75af47d5612b9832fd314153c96761732cdb430c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/haproxy-best-practices#deploy-haproxy
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/haproxy-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented HAProxy deployment and installation commands from source, PATH setup, installation verification, or the HAProxy command-line option reference.
- Retrieval Keywords: Deploy HAProxy, Install HAProxy, wget https://www.haproxy.org/download/2.6/src/haproxy-2.6.2.tar.gz, tar zxf haproxy-2.6.2.tar.gz, make -j 8 TARGET=linux-glibc USE_THREAD=1, make PREFIX=${/app/haproxy} SBINDIR=${/app/haproxy/bin} install, export PATH=/app/haproxy/bin:$PATH, which haproxy, haproxy --help, HAProxy commands, -v, -vv, -d, -db, -dM, -V, -D, -C <dir>, -W, -q, -c, -n <limit>, -m <limit>, -N <limit>, -L <name>, -p <file>, -de, -dp, -dS, -dR, -dr, -dV, -sf <pidlist>, -st <pidlist>, -x <unix_socket>, -S <bind>[,<bind_options>...], Management Guide of HAProxy, General Commands Manual of HAProxy
- Follow-up Guidance: The source also points to the HAProxy configuration file documentation and to the Management Guide of HAProxy and General Commands Manual of HAProxy for more command-line details.
- Classification Note: This chunk is operational because it contains concrete deployment, compilation, environment setup, verification steps, and executable command references.

## Official Source Content

## Deploy HAProxy

You can easily use HAProxy to configure and set up a load-balanced database environment. This section shows general deployment operations. You can customize the [configuration file](http://cbonte.github.io/haproxy-dconv/2.6/configuration.html) based on your actual scenario.
### Install HAProxy

1. Download the package of the HAProxy 2.6.2 source code:

    ```bash
    wget https://www.haproxy.org/download/2.6/src/haproxy-2.6.2.tar.gz
    ```

2. Extract the package:

    ```bash
    tar zxf haproxy-2.6.2.tar.gz
    ```

3. Compile the application from the source code:

    ```bash
    cd haproxy-2.6.2
    make clean
    make -j 8 TARGET=linux-glibc USE_THREAD=1
    make PREFIX=${/app/haproxy} SBINDIR=${/app/haproxy/bin} install  # Replace `${/app/haproxy}` and `${/app/haproxy/bin}` with your custom directories.
    ```

4. Reconfigure the profile:

    ```bash
    echo 'export PATH=/app/haproxy/bin:$PATH' >> /etc/profile
    . /etc/profile
    ```

5. Check whether the installation is successful:

    ```bash
    which haproxy
    ```
#### HAProxy commands

Execute the following command to print a list of keywords and their basic usage:

```bash
haproxy --help
```

| Option | Description |
| :-------| :---------|
| `-v` | Reports the version and build date. |
| `-vv` | Displays the version, build options, libraries versions and usable pollers. |
| `-d` | Enables debug mode. |
| `-db` | Disables background mode and multi-process mode. |
| `-dM [<byte>]` | Forces memory poisoning, which means that each and every memory region allocated with malloc() or pool_alloc2() will be filled with `<byte>` before being passed to the caller. |
| `-V` | Enables verbose mode (disables quiet mode). |
| `-D` | Starts as a daemon.|
| `-C <dir>` | Changes to directory `<dir>` before loading configuration files. |
| `-W` | Master-worker mode. |
| `-q` | Sets "quiet" mode: This disables some messages during the configuration parsing and during startup. |
| `-c` | Only performs a check of the configuration files and exits before trying to bind. |
| `-n <limit>` | Limits the per-process connection limit to `<limit>`. |
| `-m <limit>` | Limits the total allocatable memory to `<limit>` megabytes across all processes. |
| `-N <limit>` | Sets the default per-proxy maxconn to `<limit>` instead of the builtin default value (usually 2000). |
| `-L <name>` | Changes the local peer name to `<name>`, which defaults to the local hostname. |
| `-p <file>` | Writes all processes' PIDs into `<file>` during startup. |
| `-de` | Disables the use of epoll(7). epoll(7) is available only on Linux 2.6 and some custom Linux 2.4 systems. |
| `-dp` | Disables the use of poll(2). select(2) might be used instead. |
| `-dS` | Disables the use of splice(2), which is broken on older kernels. |
| `-dR` | Disables SO_REUSEPORT usage. |
| `-dr` | Ignores server address resolution failures. |
| `-dV` | Disables SSL verify on the server side. |
| `-sf <pidlist>` | Sends the "finish" signal to the PIDs in pidlist after startup. The processes which receive this signal wait for all sessions to finish before exiting. This option must be specified last, followed by any number of PIDs. Technically speaking, SIGTTOU and SIGUSR1 are sent. |
| `-st <pidlist>` | Sends the "terminate" signal to the PIDs in pidlist after startup. The processes which receive this signal terminate immediately, closing all active sessions. This option must be specified last, followed by any number of PIDs. Technically speaking, SIGTTOU and SIGTERM are sent. |
| `-x <unix_socket>` | Connects to the specified socket and retrieves all the listening sockets from the old process. Then, these sockets are used instead of binding new ones. |
| `-S <bind>[,<bind_options>...]` | In master-worker mode, creates a master CLI. This CLI enables access to the CLI of every worker. Useful for debugging, it's a convenient way of accessing a leaving process. |

For more details on HAProxy command line options, refer to [Management Guide of HAProxy](http://cbonte.github.io/haproxy-dconv/2.6/management.html) and [General Commands Manual of HAProxy](https://manpages.debian.org/buster-backports/haproxy/haproxy.1.en.html).
