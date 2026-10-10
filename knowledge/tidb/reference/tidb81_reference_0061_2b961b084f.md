# TiKV command-line configuration flags

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/command-line-flags-for-tikv-configuration.md`
- Source Title: `TiKV Configuration Flags`
- Source Heading Path: `TiKV Configuration Flags | TiKV Configuration Flags > `-A, --addr` | TiKV Configuration Flags > `--advertise-addr` | TiKV Configuration Flags > `--status-addr` | TiKV Configuration Flags > `--advertise-status-addr` | TiKV Configuration Flags > `-C, --config` | TiKV Configuration Flags > `--capacity` | TiKV Configuration Flags > `--config-info <FORMAT>` | TiKV Configuration Flags > `--data-dir` | TiKV Configuration Flags > `-L` | TiKV Configuration Flags > `--log-file` | TiKV Configuration Flags > `--pd``
- Source Line Ranges: `5-98`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `pd`, `shared`
- Topic Tags: `command-line-flags`, `network-addresses`, `status-endpoint`, `configuration-file`, `capacity`, `config-inspection`, `data-directory`, `log-level`, `log-file`, `pd-endpoints`, `nat`, `docker`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0061_2b961b084f`
- Source ID: `tidb-docs-8.1:command-line-flags-for-tikv-configuration.md#tikv-configuration-flags`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f9ae66199fc51671020b0cb9d667a45f74935b0436b8d325a866cbdd3e93eb29`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/command-line-flags-for-tikv-configuration#tikv-configuration-flags
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/command-line-flags-for-tikv-configuration.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiKV command-line flags for server addresses, status endpoints, config file precedence, capacity, config inspection output, data directory, logging, or PD endpoint configuration.
- Retrieval Keywords: TiKV Configuration Flags, -A, --addr, --advertise-addr, --status-addr, --advertise-status-addr, -C, --config, --capacity, --config-info <FORMAT>, json, --data-dir, -L, --log-file, --pd, 127.0.0.1:20160, 20180, http://host:status_port/metrics, http://host:status_port/debug/pprof/profile, Docker, NAT, PD servers, log-level, log-file, TiKV Server
- Follow-up Guidance: The source also states readable unit conversions for command line parameters: file sizes use KB, MB, GB, TB, PB and time uses ms, s, m, h.
- Classification Note: This is reference content because it enumerates TiKV command-line configuration flags, their defaults, accepted values, and exact meanings.

## Official Source Content

# TiKV Configuration Flags

TiKV supports some readable unit conversions for command line parameters.

- File size (based on byte): KB, MB, GB, TB, PB (or lowercase)
- Time (based on ms): ms, s, m, h
## `-A, --addr`

- The address that the TiKV server monitors
- Default: `"127.0.0.1:20160"`
- To deploy a cluster, you must use `--addr` to specify the IP address of the current host, such as `"192.168.100.113:20160"`. If the cluster is run on Docker, specify the IP address of Docker as `"0.0.0.0:20160"`.
## `--advertise-addr`

- The server advertise address for client traffic from outside
- Default: `${addr}`
- If the client cannot connect to TiKV through the `--addr` address because of Docker or NAT network, you must manually set the `--advertise-addr` address.
- For example, the internal IP address of Docker is 172.17.0.1, while the IP address of the host is 192.168.100.113 and the port mapping is set to `-p 20160:20160`. In this case, you can set `--advertise-addr` to "192.168.100.113:20160". The client can find this service through 192.168.100.113:20160.
## `--status-addr`

+ The port through which the TiKV service status is listened
+ Default: `"20180"`
+ The Prometheus can access this status information via `http://host:status_port/metrics`.
+ The Profile can access this status information via `http://host:status_port/debug/pprof/profile`.
## `--advertise-status-addr`

- The address through which TiKV accesses service status from outside.
- Default: The value of `--status-addr` is used.
- If the client cannot connect to TiKV through the `--status-addr` address because of Docker or NAT network, you must manually set the `--advertise-status-addr` address.
- For example, the internal IP address of Docker is `172.17.0.1`, while the IP address of the host is `192.168.100.113` and the port mapping is set to `-p 20180:20180`. In this case, set `--advertise-status-addr="192.168.100.113:20180"`. The client can find this service through `192.168.100.113:20180`.
## `-C, --config`

- The config file
- Default: `""`
- If you set the configuration using the command line, the same setting in the config file will be overwritten.
## `--capacity`

- The store capacity
- Default: `0` (unlimited)
- PD uses this flag to determine how to balance the TiKV servers. (Tip: you can use 10GB instead of 1073741824)
## `--config-info <FORMAT>`

- When this flag is used, available configuration values are listed according to `FORMAT` and then exit.
- Value option for `FORMAT`: `json`. Currently, only JSON format is supported.
- Only the configuration name (Name), default value (DefaultValue) and current value (ValueInFile) are listed in the output JSON. If the `-C` or `--config` is specified, the current value and the default value of configuration items in the file are listed together, and other items without `-C` or `--config` specified only have default values. The following is an example:

    ```json
    {
    "Component": "TiKV Server",
    "Version": "6.2.0",
    "Parameters": [
        {
        "Name": "log-level",
        "DefaultValue": "info",
        "ValueInFile": "warn"
        },
        {
        "Name": "log-file",
        "DefaultValue": ""
        },
        ...
    ]
    }
    ```
## `--data-dir`

- The path to the data directory
- Default: `"/tmp/tikv/store"`
## `-L`

- The log level
- Default: `"info"`
- Optional values: `"debug"`, `"info"`, `"warn"`, `"error"`, `"fatal"`
## `--log-file`

- The log file
- Default: `""`
- If this flag is not set, logs will be written to "stderr". If this flag is set, logs are output to the corresponding file.
## `--pd`

- The address list of PD servers
- Default: `""`
- To make TiKV work, you must use the value of `--pd` to connect the TiKV server to the PD server. Separate multiple PD addresses using comma, for example "192.168.100.113:2379, 192.168.100.114:2379, 192.168.100.115:2379".
