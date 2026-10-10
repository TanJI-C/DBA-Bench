# Hybrid deployment topology and key parameters

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/hybrid-deployment-topology.md`
- Source Title: `Hybrid Deployment Topology`
- Source Heading Path: `Hybrid Deployment Topology | Hybrid Deployment Topology > Topology information | Hybrid Deployment Topology > Topology information > Topology templates | Hybrid Deployment Topology > Topology information > Key parameters`
- Source Line Ranges: `5-105`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `tidb`, `tikv`, `tiup`
- Topic Tags: `hybrid-deployment`, `topology`, `multi-instance`, `numa`, `location-labels`, `readpool`, `block-cache`, `raftstore`, `capacity-planning`, `configuration-template`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0042_e44acb08be`
- Source ID: `tidb-docs-8.1:hybrid-deployment-topology.md#hybrid-deployment-topology`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3f259863087c53fab125a1b0c6a75d32b196760a54b7451e316b983095a813c2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/hybrid-deployment-topology#hybrid-deployment-topology
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/hybrid-deployment-topology.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving official guidance for TiDB and TiKV hybrid deployment on a single machine with multiple instances, including NUMA binding, label scheduling, and key topology parameters.
- Retrieval Keywords: Hybrid Deployment Topology, hybrid deployment, multiple instances on a single machine, NUMA node bindings, numa_node, numactl --membind, readpool.unified.max-thread-count, readpool.storage.use-unified-pool, readpool.coprocessor.use-unified-pool, storage.block-cache.capacity, raftstore.capacity, replication.location-labels, location_labels, server.labels.host, PD and Prometheus are deployed together, separate file systems, simple-multi-instance.yaml, complex-multi-instance.yaml, Topology Configuration File for Deploying TiDB Using TiUP
- Follow-up Guidance: The source also points to the simple and complex hybrid deployment templates and to the TiUP topology reference for detailed descriptions of configuration items.
- Classification Note: This chunk is classified as architecture because it defines the hybrid deployment topology, component placement, and configuration parameters for multi-instance TiDB and TiKV deployments on shared physical machines.

## Official Source Content

# Hybrid Deployment Topology

This document describes the topology and key parameters of the TiKV and TiDB hybrid deployment.

The hybrid deployment is usually used in the following scenario:

The deployment machine has multiple CPU processors with sufficient memory. To improve the utilization rate of the physical machine resources, multiple instances can be deployed on a single machine, that is, TiDB and TiKV's CPU resources are isolated through NUMA node bindings. PD and Prometheus are deployed together, but their data directories need to use separate file systems.
## Topology information

| Instance | Count | Physical machine configuration | IP | Configuration |
| :-- | :-- | :-- | :-- | :-- |
| TiDB | 6 | 32 VCore 64GB | 10.0.1.1<br/> 10.0.1.2<br/> 10.0.1.3 | Configure NUMA to bind CPU cores |
| PD | 3 | 16 VCore 32 GB | 10.0.1.4<br/> 10.0.1.5<br/> 10.0.1.6 | Configure the `location_labels` parameter |
| TiKV | 6 | 32 VCore 64GB | 10.0.1.7<br/> 10.0.1.8<br/> 10.0.1.9 | 1. Separate the instance-level port and status_port; <br/> 2. Configure the global parameters `readpool`, `storage` and `raftstore`; <br/> 3. Configure labels of the instance-level host; <br/> 4. Configure NUMA to bind CPU cores |
| Monitoring & Grafana | 1 | 4 VCore 8GB * 1 500GB (ssd)  | 10.0.1.10 | Default configuration |

> **Note:**
>
> The IP addresses of the instances are given as examples only. In your actual deployment, replace the IP addresses with your actual IP addresses.
### Topology templates

- [The simple template for the hybrid deployment](https://github.com/pingcap/docs/blob/master/config-templates/simple-multi-instance.yaml)
- [The complex template for the hybrid deployment](https://github.com/pingcap/docs/blob/master/config-templates/complex-multi-instance.yaml)

For detailed descriptions of the configuration items in the above TiDB cluster topology file, see [Topology Configuration File for Deploying TiDB Using TiUP](https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster-topology-reference).
### Key parameters

This section introduces the key parameters when you deploy multiple instances on a single machine, which is mainly used in scenarios when multiple instances of TiDB and TiKV are deployed on a single machine. You need to fill in the results into the configuration template according to the calculation methods provided below.

- Optimize the configuration of TiKV

    - To configure `readpool` to be self-adaptive to the thread pool. By configuring the `readpool.unified.max-thread-count` parameter, you can make `readpool.storage` and `readpool.coprocessor` share a unified thread pool, and set the self-adaptive switch respectively.

        - Enable `readpool.storage` and `readpool.coprocessor`:

            ```yaml
            readpool.storage.use-unified-pool: true
            readpool.coprocessor.use-unified-pool: true
            ```

        - The calculation method:

            ```
            readpool.unified.max-thread-count = cores * 0.8 / the number of TiKV instances
            ```

    - To configure the storage CF (all RocksDB column families) to be self-adaptive to memory. By configuring the `storage.block-cache.capacity` parameter, you can make CF automatically balance the memory usage.

        - The calculation method:

            ```
            storage.block-cache.capacity = (MEM_TOTAL * 0.5 / the number of TiKV instances)
            ```

    - If multiple TiKV instances are deployed on the same physical disk, add the `capacity` parameter in the TiKV configuration:

        ```
        raftstore.capacity = disk total capacity / the number of TiKV instances
        ```

- The label scheduling configuration

    Since multiple instances of TiKV are deployed on a single machine, if the physical machines go down, the Raft Group might lose two of the default three replicas, which causes the cluster unavailability. To address this issue, you can use the label to enable the smart scheduling of PD, which ensures that the Raft Group has more than two replicas in multiple TiKV instances on the same machine.

    - The TiKV configuration

        The same host-level label information is configured for the same physical machine:

        ```yml
        config:
          server.labels:
            host: tikv1
        ```

    - The PD configuration

        To enable PD to identify and scheduling Regions, configure the labels type for PD:

        ```yml
        pd:
          replication.location-labels: ["host"]
        ```

- `numa_node` core binding

    - In the instance parameter module, configure the corresponding `numa_node` parameter and add the number of CPU cores.
    
    - Before using NUMA to bind cores, make sure that the numactl tool is installed, and confirm the information of CPUs in the physical machines. After that, configure the parameters.

    - The `numa_node` parameter corresponds to the `numactl --membind` configuration.

> **Note:**
>
> - When editing the configuration file template, modify the required parameter, IP, port, and directory.
> - Each component uses the global `<deploy_dir>/<components_name>-<port>` as their `deploy_dir` by default. For example, if TiDB specifies the `4001` port, its `deploy_dir` is `/tidb-deploy/tidb-4001` by default. Therefore, in multi-instance scenarios, when specifying a non-default port, you do not need to specify the directory again.
> - You do not need to manually create the `tidb` user in the configuration file. The TiUP cluster component automatically creates the `tidb` user on the target machines. You can customize the user, or keep the user consistent with the control machine.
> - If you configure the deployment directory as a relative path, the cluster will be deployed in the home directory of the user.
