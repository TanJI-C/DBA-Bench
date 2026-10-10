# Configure and enable TiFlash disaggregated storage and compute with S3

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tiflash-disaggregated-and-s3.md`
- Source Title: `TiFlash Disaggregated Storage and Compute Architecture and S3 Support`
- Source Heading Path: `TiFlash Disaggregated Storage and Compute Architecture and S3 Support > Usage`
- Source Line Ranges: `72-171`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tiup`, `tidb`, `sql`
- Topic Tags: `topology`, `s3-endpoint`, `access-key`, `secret-key`, `environment-variables`, `write-node`, `compute-node`, `remote-cache`, `scale-out`, `replica-configuration`, `edit-config`, `reload`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0357_c369d442d2`
- Source ID: `tidb-docs-8.1:tiflash/tiflash-disaggregated-and-s3.md#usage`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `044015bc8fe560cb8434c99e18bae6eec438e5b5135519809749d514563e01ee`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tiflash-disaggregated-and-s3#usage
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tiflash-disaggregated-and-s3.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how to configure, deploy, or enable TiFlash disaggregated storage and compute with S3 in a TiUP topology and TiDB configuration.
- Retrieval Keywords: scale-out.topo.yaml, tiflash_servers, flash.disaggregated_mode, tiflash_write, tiflash_compute, storage.s3.endpoint, storage.s3.bucket, storage.s3.root, storage.s3.access_key_id, storage.s3.secret_access_key, storage.main.dir, storage.remote.cache.dir, storage.remote.cache.capacity, S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY, tiup cluster scale-out, ALTER TABLE table_name SET TIFLASH REPLICA 1, tiup cluster edit-config, disaggregated-tiflash: true, tiup cluster reload mycluster -R tidb
- Follow-up Guidance: The source also states that environment variables have higher priority than access keys written directly in the configuration file and shows the TiDB setting needed to query TiFlash using the disaggregated architecture.
- Classification Note: This chunk is classified as configuration because it provides the topology YAML, S3-related settings, environment variable options, replica configuration, and the TiDB configuration flag for disaggregated TiFlash queries.

## Official Source Content

## Usage

By default, TiUP deploys TiFlash in the coupled storage and computation architecture. If you need to deploy TiFlash in the disaggregated storage and compute architecture, take the following steps for manual configuration:

1. Prepare a TiFlash topology configuration file, such as `scale-out.topo.yaml`, with the following configuration:

    ```yaml
    tiflash_servers:
      # In the TiFlash topology configuration file, the `storage.s3` configuration indicates that the disaggregated storage and compute architecture is used for deployment.
      # If `flash.disaggregated_mode: tiflash_compute` is configured for a node, it is a Compute Node.
      # If `flash.disaggregated_mode: tiflash_write` is configured for a node, it is a Write Node.

      # 172.31.8.1~2 are TiFlash Write Nodes
      - host: 172.31.8.1
        config:
          flash.disaggregated_mode: tiflash_write               # This is a Write Node
          storage.s3.endpoint: http://s3.{region}.amazonaws.com # S3 endpoint address
          storage.s3.bucket: mybucket                           # TiFlash stores all data in this bucket
          storage.s3.root: /cluster1_data                       # Root directory where data is stored in the S3 bucket
          storage.s3.access_key_id: {ACCESS_KEY_ID}             # Access S3 with ACCESS_KEY_ID
          storage.s3.secret_access_key: {SECRET_ACCESS_KEY}     # Access S3 with SECRET_ACCESS_KEY
          storage.main.dir: ["/data1/tiflash/data"]             # Local data directory of the Write Node. Configure it in the same way as the directory configuration of the coupled storage and compute architecture
      - host: 172.31.8.2
        config:
          flash.disaggregated_mode: tiflash_write               # This is a Write Node
          storage.s3.endpoint: http://s3.{region}.amazonaws.com # S3 endpoint address
          storage.s3.bucket: mybucket                           # TiFlash stores all data in this bucket
          storage.s3.root: /cluster1_data                       # Root directory where data is stored in the S3 bucket
          storage.s3.access_key_id: {ACCESS_KEY_ID}             # Access S3 with ACCESS_KEY_ID
          storage.s3.secret_access_key: {SECRET_ACCESS_KEY}     # Access S3 with SECRET_ACCESS_KEY
          storage.main.dir: ["/data1/tiflash/data"]             # Local data directory of the Write Node. Configure it in the same way as the directory configuration of the coupled storage and compute architecture

      # 172.31.9.1~2 are TiFlash Compute Nodes
      - host: 172.31.9.1
        config:
          flash.disaggregated_mode: tiflash_compute             # This is a Compute Node
          storage.s3.endpoint: http://s3.{region}.amazonaws.com # S3 endpoint address
          storage.s3.bucket: mybucket                           # TiFlash stores all data in this bucket
          storage.s3.root: /cluster1_data                       # Root directory where data is stored in the S3 bucket
          storage.s3.access_key_id: {ACCESS_KEY_ID}             # Access S3 with ACCESS_KEY_ID
          storage.s3.secret_access_key: {SECRET_ACCESS_KEY}     # Access S3 with SECRET_ACCESS_KEY
          storage.main.dir: ["/data1/tiflash/data"]             # Local data directory of the Compute Node. Configure it in the same way as the directory configuration of the coupled storage and compute architecture
          storage.remote.cache.dir: /data1/tiflash/cache        # Local data cache directory of the Compute Node
          storage.remote.cache.capacity: 858993459200           # 800 GiB
      - host: 172.31.9.2
        config:
          flash.disaggregated_mode: tiflash_compute             # This is a Compute Node
          storage.s3.endpoint: http://s3.{region}.amazonaws.com # S3 endpoint address
          storage.s3.bucket: mybucket                           # TiFlash stores all data in this bucket
          storage.s3.root: /cluster1_data                       # Root directory where data is stored in the S3 bucket
          storage.s3.access_key_id: {ACCESS_KEY_ID}             # Access S3 with ACCESS_KEY_ID
          storage.s3.secret_access_key: {SECRET_ACCESS_KEY}     # Access S3 with SECRET_ACCESS_KEY
          storage.main.dir: ["/data1/tiflash/data"]             # Local data directory of the Compute Node. Configure it in the same way as the directory configuration of the coupled storage and compute architecture
          storage.remote.cache.dir: /data1/tiflash/cache        # Local data cache directory of the Compute Node
          storage.remote.cache.capacity: 858993459200           # 800 GiB
    ```

    * Note that the above `ACCESS_KEY_ID` and `SECRET_ACCESS_KEY` are directly written in the configuration file. You can also choose to configure them separately using environment variables. If both ways are configured, the environment variables have higher priority.

        To configure `ACCESS_KEY_ID` and `SECRET_ACCESS_KEY` through environment variables, switch to the user environment that starts the TiFlash process (usually `tidb`) on all machines where TiFlash processes are deployed, and then modify `~/.bash_profile` to add the following configurations:

        ```shell
        export S3_ACCESS_KEY_ID={ACCESS_KEY_ID}
        export S3_SECRET_ACCESS_KEY={SECRET_ACCESS_KEY}
        ```

    * `storage.s3.endpoint` supports connecting to S3 using the `http` or `https` mode, and you can set the mode by directly modifying the URL. For example, `https://s3.{region}.amazonaws.com`.

2. Add TiFlash nodes and reset the number of TiFlash replicas:

    ```shell
    tiup cluster scale-out mycluster ./scale-out.topo.yaml
    ```

    ```sql
    ALTER TABLE table_name SET TIFLASH REPLICA 1;
    ```

3. Modify the TiDB configuration to query TiFlash using the disaggregated storage and compute architecture.

    1. Open the TiDB configuration file in edit mode:

          ```shell
          tiup cluster edit-config mycluster
          ```

    2. Add the following configuration items to the TiDB configuration file:

        ```shell
        server_configs:
        tidb:
        disaggregated-tiflash: true   # Query TiFlash using the disaggregated storage and compute architecture
        ```

    3. Restart TiDB:

        ```shell
        tiup cluster reload mycluster -R tidb
        ```
