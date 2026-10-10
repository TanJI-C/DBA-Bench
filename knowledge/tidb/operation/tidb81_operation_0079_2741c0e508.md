# DM-worker setup with command-line and configuration file

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/deploy-a-dm-cluster-using-binary.md`
- Source Title: `Deploy Data Migration Using DM Binary`
- Source Heading Path: `Deploy Data Migration Using DM Binary > Sample scenario > Deploy DM-worker | Deploy Data Migration Using DM Binary > Sample scenario > Deploy DM-worker > DM-worker command-line parameters | Deploy Data Migration Using DM Binary > Sample scenario > Deploy DM-worker > DM-worker configuration file`
- Source Line Ranges: `132-204`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `dm-worker`, `command-line-parameters`, `configuration-file`, `join`, `startup`, `logging`, `cluster-deployment`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0079_2741c0e508`
- Source ID: `tidb-docs-8.1:dm/deploy-a-dm-cluster-using-binary.md#deploy-dm-worker`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e94212f2cb3aa6359c35cbe2e2c63a03c281cdca2f53f0a1f6e3e80baf5cdb36`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/deploy-a-dm-cluster-using-binary#deploy-dm-worker
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/deploy-a-dm-cluster-using-binary.md

## Retrieval Guidance

- Use When: Use this chunk when you need the exact DM-worker command-line parameters, the recommended DM-worker configuration file, or the startup command for joining DM-worker to existing DM-master nodes.
- Retrieval Keywords: Deploy DM-worker, dm-worker --help, DM-worker command-line parameters, DM-worker configuration file, worker-addr, join, keepalive-ttl, log-file, name, conf/dm-worker1.toml, ./dm-worker -config conf/dm-worker1.toml, 192.168.0.4:8261,192.168.0.5:8261,192.168.0.6:8261, worker1, worker2, Now, a DM cluster is successfully deployed
- Follow-up Guidance: The source adds that for `DM-worker2`, you change `name` to `worker2`, repeat the startup step, and then the DM cluster is successfully deployed.
- Classification Note: This is classified as an operation chunk because the content provides self-managed deployment instructions, startup commands, and DM-worker configuration fields for joining the cluster.

## Official Source Content

### Deploy DM-worker

You can configure DM-worker by using [command-line parameters](#dm-worker-command-line-parameters) or [the configuration file](#dm-worker-configuration-file).
#### DM-worker command-line parameters

The following is the description of the DM-worker command-line parameters:

```bash
./dm-worker --help
```

```
Usage of worker:
  -L string
        log level: debug, info, warn, error, fatal (default "info")
  -V    prints version and exit
  -advertise-addr string
        advertise address for client traffic (default "${worker-addr}")
  -config string
        path to config file
  -join string
        join to an existing cluster (usage: dm-master cluster's "${master-addr}")
  -keepalive-ttl int
        dm-worker's TTL for keepalive with etcd (in seconds) (default 10)
  -log-file string
        log file path
  -name string
        human-readable name for DM-worker member
  -print-sample-config
        print sample config file of dm-worker
  -worker-addr string
        listen address for client traffic
```

> **Note:**
>
> In some situations, you cannot use the above method to configure DM-worker because some configurations are not exposed to the command line. In such cases, use the configuration file instead.
#### DM-worker configuration file

The following is the DM-worker configuration file. It is recommended that you configure DM-worker by using this method.

1. Write the following configuration to `conf/dm-worker1.toml`:

      ```toml
      # Worker Configuration.
      name = "worker1"

      # Log configuration.
      log-level = "info"
      log-file = "dm-worker.log"

      # DM-worker address.
      worker-addr = ":8262"

      # The master-addr configuration of the DM-master nodes in the cluster.
      join = "192.168.0.4:8261,192.168.0.5:8261,192.168.0.6:8261"
      ```

2. Execute the following command in the terminal to run DM-worker:

      ```bash
      ./dm-worker -config conf/dm-worker1.toml
      ```

3. For DM-worker2, change `name` in the configuration file to `worker2`. Then repeat Step 2.

Now, a DM cluster is successfully deployed.
