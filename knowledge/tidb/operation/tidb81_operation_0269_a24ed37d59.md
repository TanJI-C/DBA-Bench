# Binary package usage example for Pump deployment

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/deploy-tidb-binlog.md`
- Source Title: `TiDB Binlog Cluster Deployment`
- Source Heading Path: `TiDB Binlog Cluster Deployment > Deploy TiDB Binlog using a binary package > The usage example`
- Source Line Ranges: `31-152`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`
- Topic Tags: `deployment`, `binary-package`, `pump`, `configuration`, `command-line`, `pd-urls`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0269_a24ed37d59`
- Source ID: `tidb-docs-8.1:tidb-binlog/deploy-tidb-binlog.md#the-usage-example`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9ddcc93affee415a700475e08323d3e8e490ca079707d19c55cf66474576611f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/deploy-tidb-binlog#the-usage-example
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/deploy-tidb-binlog.md

## Retrieval Guidance

- Use When: Use this chunk when looking for a binary deployment example for Pump, including Pump command-line parameters, a sample pump.toml configuration, PD node addresses, and how command-line parameters interact with configuration file values.
- Retrieval Keywords: The usage example, Deploy Pump using the binary, ./pump -help, Usage of Pump, -addr, -advertise-addr, -config, -data-dir, -gc, -heartbeat-interval, -log-file, -log-rotate, -metrics-addr, -metrics-interval, -node-id, -pd-urls, -fake-binlog-interval, pump.toml, addr = "192.168.0.11:8250", advertise-addr = "192.168.0.11:8250", gc = 7, data-dir = "data.pump", heartbeat-interval = 2, pd-urls = "http://192.168.0.16:2379,http://192.168.0.15:2379,http://192.168.0.14:2379", [security], ssl-ca, ssl-cert, ssl-key, [storage], sync-log, stop-write-at-available-space, ./pump -config pump.toml, If the command line parameters is the same with the configuration file parameters, the values of command line parameters are used
- Follow-up Guidance: The chunk continues to the next step with "Deploy Drainer using binary" and begins by showing how to view Drainer command line parameters using `./drainer -help`.
- Classification Note: This is classified as an operation chunk because the content gives a concrete binary-package deployment example and runtime configuration details for Pump in a self-managed environment.

## Official Source Content

### The usage example

Assuming that you have three PD nodes, one TiDB node, two Pump nodes, and one Drainer node, the information of each node is as follows:

| Node     | IP           |
| :---------|:------------ |
| TiDB     | 192.168.0.10 |
| PD1      | 192.168.0.16 |
| PD2      | 192.168.0.15 |
| PD3      | 192.168.0.14 |
| Pump     | 192.168.0.11 |
| Pump     | 192.168.0.12 |
| Drainer  | 192.168.0.13 |

The following part shows how to use Pump and Drainer based on the nodes above.

1. Deploy Pump using the binary.

    - To view the command line parameters of Pump, execute `./pump -help`:

        ```bash
        Usage of Pump:
        -L string
            the output information level of logs: debug, info, warn, error, fatal ("info" by default)
        -V
            the print version information
        -addr string
            the RPC address through which Pump provides the service (-addr="192.168.0.11:8250")
        -advertise-addr string
            the RPC address through which Pump provides the external service (-advertise-addr="192.168.0.11:8250")
        -config string
            the path of the configuration file. If you specify the configuration file, Pump reads the configuration in the configuration file first. If the corresponding configuration also exits in the command line parameters, Pump uses the configuration of the command line parameters to cover that of the configuration file.
        -data-dir string
            the path where the Pump data is stored
        -gc int
            the number of days to retain the data in Pump ("7" by default)
        -heartbeat-interval int
            the interval of the heartbeats Pump sends to PD (in seconds)
        -log-file string
            the file path of logs
        -log-rotate string
            the switch frequency of logs (hour/day)
        -metrics-addr string
            the Prometheus Pushgateway address. If not set, it is forbidden to report the monitoring metrics.
        -metrics-interval int
            the report frequency of the monitoring metrics ("15" by default, in seconds)
        -node-id string
            the unique ID of a Pump node. If you do not specify this ID, the system automatically generates an ID based on the host name and listening port.
        -pd-urls string
            the address of the PD cluster nodes (-pd-urls="http://192.168.0.16:2379,http://192.168.0.15:2379,http://192.168.0.14:2379")
        -fake-binlog-interval int
            the frequency at which a Pump node generates fake binlog ("3" by default, in seconds)
        ```

    - Taking deploying Pump on "192.168.0.11" as an example, the Pump configuration file is as follows:

        ```toml
        # Pump Configuration

        # the bound address of Pump
        addr = "192.168.0.11:8250"

        # the address through which Pump provides the service
        advertise-addr = "192.168.0.11:8250"

        # the number of days to retain the data in Pump ("7" by default)
        gc = 7

        # the directory where the Pump data is stored
        data-dir = "data.pump"

        # the interval of the heartbeats Pump sends to PD (in seconds)
        heartbeat-interval = 2

        # the address of the PD cluster nodes (each separated by a comma with no whitespace)
        pd-urls = "http://192.168.0.16:2379,http://192.168.0.15:2379,http://192.168.0.14:2379"

        # [security]
        # This section is generally commented out if no special security settings are required.
        # The file path containing a list of trusted SSL CAs connected to the cluster.
        # ssl-ca = "/path/to/ca.pem"
        # The path to the X509 certificate in PEM format that is connected to the cluster.
        # ssl-cert = "/path/to/drainer.pem"
        # The path to the X509 key in PEM format that is connected to the cluster.
        # ssl-key = "/path/to/drainer-key.pem"

        # [storage]
        # Set to true (by default) to guarantee reliability by ensuring binlog data is flushed to the disk
        # sync-log = true

        # When the available disk capacity is less than the set value, Pump stops writing data.
        # 42 MB -> 42000000, 42 mib -> 44040192
        # default: 10 gib
        # stop-write-at-available-space = "10 gib"
        # The LSM DB settings embedded in Pump. Unless you know this part well, it is usually commented out.
        # [storage.kv]
        # block-cache-capacity = 8388608
        # block-restart-interval = 16
        # block-size = 4096
        # compaction-L0-trigger = 8
        # compaction-table-size = 67108864
        # compaction-total-size = 536870912
        # compaction-total-size-multiplier = 8.0
        # write-buffer = 67108864
        # write-L0-pause-trigger = 24
        # write-L0-slowdown-trigger = 17
        ```

    - The example of starting Pump:

        ```bash
        ./pump -config pump.toml
        ```

        If the command line parameters is the same with the configuration file parameters, the values of command line parameters are used.

2. Deploy Drainer using binary.

    - To view the command line parameters of Drainer, execute `./drainer -help`:
