# TiFlash tiflash.toml configuration reference

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tiflash-configuration.md`
- Source Title: `Configure TiFlash`
- Source Heading Path: `Configure TiFlash > TiFlash configuration parameters > Configure the `tiflash.toml` file`
- Source Line Ranges: `42-293`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `pd`, `tikv`, `tidb`, `tiup`, `operator`
- Topic Tags: `configuration-file`, `storage`, `multi-disk`, `io-rate-limit`, `ports`, `logging`, `memory`, `coprocessor`, `compression`, `security`, `tls`, `resource-control`, `mpp`, `scheduler`, `s3`, `disaggregated-mode`, `deprecated-settings`, `version-dependent-behavior`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0354_a76084d4a4`
- Source ID: `tidb-docs-8.1:tiflash/tiflash-configuration.md#configure-the-tiflash-toml-file`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2345b70de77fcf9577f1e953142e4c846e26c81d198a98d3c72306edb71aba98`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-the-tiflash-toml-file
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tiflash-configuration.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiFlash `tiflash.toml` configuration reference for storage paths, ports, memory, coprocessor limits, compression, logging, security, resource control, MinTSO scheduler, or version-specific TiFlash settings.
- Retrieval Keywords: tiflash.toml, listen_host, tcp_port, mark_cache_size, minmax_index_cache_size, delta_index_cache_size, path, path_realtime_mode, tmp_path, [storage], storage.main.dir, storage.latest.dir, storage.io_rate_limit, max_bytes_per_sec, max_read_bytes_per_sec, max_write_bytes_per_sec, foreground_write_weight, background_write_weight, foreground_read_weight, background_read_weight, auto_tune_sec, storage.s3, storage.remote.cache, service_addr, compact_log_min_gap, compact_log_min_rows, compact_log_min_bytes, disaggregated_mode, flash.proxy, advertise-addr, status-addr, engine-addr, data-dir, logger, level, errorlog, raft.pd_addr, status.metrics_port, profiles.default, dt_enable_logical_split, max_threads, tidb_max_tiflash_threads, max_memory_usage, max_memory_usage_for_all_queries, cop_pool_size, cop_pool_handle_limit, cop_pool_max_queued_seconds, batch_cop_pool_size, manual_compact_pool_size, enable_elastic_threadpool, dt_compression_method, dt_compression_level, dt_page_gc_threshold, max_bytes_before_external_group_by, max_bytes_before_external_sort, max_bytes_before_external_join, enable_resource_control, task_scheduler_thread_soft_limit, task_scheduler_thread_hard_limit, task_scheduler_active_set_soft_limit, security.redact_info_log, ca_path, cert_path, key_path, TiFlash Server is Busy, ALTER TABLE ... COMPACT, CompactLog, DTFile format_version
- Follow-up Guidance: The chunk also points to the TiFlash disaggregated and S3 documentation and the TiFlash MinTSO scheduler documentation for details on those specific settings.
- Classification Note: This chunk is classified as configuration because it is the official parameter reference for the TiFlash `tiflash.toml` file, including defaults, effects, deprecations, and version-dependent behavior.

## Official Source Content

```toml
## The listening host for supporting services such as TPC/HTTP. It is recommended to configure it as "0.0.0.0", which means to listen on all IP addresses of this machine.
listen_host = "0.0.0.0"
## The TiFlash TCP service port. This port is used for internal testing and is set to 9000 by default. Before TiFlash v7.1.0, this port is enabled by default with a security risk. To enhance security, it is recommended to apply access control on this port to only allow access from whitelisted IP addresses. Starting from TiFlash v7.1.0, you can avoid the security risk by commenting out the configuration of this port. When the TiFlash configuration file does not specify this port, it will be disabled. 
## It is **NOT** recommended to configure this port in any TiFlash deployment. (Note: Starting from TiFlash v7.1.0, TiFlash deployed by TiUP >= v1.12.5 or TiDB Operator >= v1.5.0 disables the port by default and is more secure.)
# tcp_port = 9000
## The cache size limit of the metadata of a data block. Generally, you do not need to change this value.
mark_cache_size = 1073741824
## The cache size limit of the min-max index of a data block. Generally, you do not need to change this value.
minmax_index_cache_size = 1073741824
## The cache size limit of the DeltaIndex. The default value is 0, which means no limit.
delta_index_cache_size = 0

## The storage path of TiFlash data. If there are multiple directories, separate each directory with a comma.
## path and path_realtime_mode are deprecated since v4.0.9. Use the configurations
## in the [storage] section to get better performance in the multi-disk deployment scenarios
## Since TiDB v5.2.0, if you need to use the storage.io_rate_limit configuration, you need to set the storage path of TiFlash data to storage.main.dir at the same time.
## When the [storage] configurations exist, both path and path_realtime_mode configurations are ignored.
# path = "/tidb-data/tiflash-9000"
## or
# path = "/ssd0/tidb-data/tiflash,/ssd1/tidb-data/tiflash,/ssd2/tidb-data/tiflash"
## The default value is false. If you set it to true and multiple directories
## are set in the path, the latest data is stored in the first directory and older
## data is stored in the rest directories.
# path_realtime_mode = false

## The path in which the TiFlash temporary files are stored. By default it is the first directory in path
## or in storage.latest.dir appended with "/tmp".
# tmp_path = "/tidb-data/tiflash-9000/tmp"

## Storage paths settings take effect starting from v4.0.9
[storage]

    ## DTFile format
    ## * format_version = 2, the default format for versions < v6.0.0.
    ## * format_version = 3, the default format for v6.0.0 and v6.1.x, which provides more data validation features.
    ## * format_version = 4, the default format for versions from v6.2.0 to v7.3.0, which reduces write amplification and background task resource consumption
    ## * format_version = 5, the default format for v7.4.0 and later versions (introduced in v7.3.0), which reduces the number of physical files by merging smaller files. 
    # format_version = 5

    [storage.main]
    ## The list of directories to store the main data. More than 90% of the total data is stored in
    ## the directory list.
    dir = [ "/tidb-data/tiflash-9000" ]
    ## or
    # dir = [ "/ssd0/tidb-data/tiflash", "/ssd1/tidb-data/tiflash" ]

    ## The maximum storage capacity of each directory in storage.main.dir.
    ## If it is not set, or is set to multiple 0, the actual disk (the disk where the directory is located) capacity is used.
    ## Note that human-readable numbers such as "10GB" are not supported yet.
    ## Numbers are specified in bytes.
    ## The size of the capacity list should be the same with the dir size.
    ## For example:
    # capacity = [ 10737418240, 10737418240 ]

    [storage.latest]
    ## The list of directories to store the latest data. About 10% of the total data is stored in
    ## the directory list. The directories (or directory) listed here require higher IOPS
    ## metrics than those in storage.main.dir.
    ## If it is not set (by default), the values of storage.main.dir are used.
    # dir = [ ]
    ## The maximum storage capacity of each directory in storage.latest.dir.
    ## If it is not set, or is set to multiple 0, the actual disk (the disk where the directory is located) capacity is used.
    # capacity = [ 10737418240, 10737418240 ]

    ## [storage.io_rate_limit] settings are new in v5.2.0.
    [storage.io_rate_limit]
    ## This configuration item determines whether to limit the I/O traffic, which is disabled by default. This traffic limit in TiFlash is suitable for cloud storage that has the disk bandwidth of a small and specific size.
    ## The total I/O bandwidth for disk reads and writes. The unit is bytes and the default value is 0, which means the I/O traffic is not limited by default.
    # max_bytes_per_sec = 0
    ## max_read_bytes_per_sec and max_write_bytes_per_sec have similar meanings to max_bytes_per_sec. max_read_bytes_per_sec means the total I/O bandwidth for disk reads, and max_write_bytes_per_sec means the total I/O bandwidth for disk writes.
    ## These configuration items limit I/O bandwidth for disk reads and writes separately. You can use them for cloud storage that calculates the limit of I/O bandwidth for disk reads and writes separately, such as the Persistent Disk provided by Google Cloud.
    ## When the value of max_bytes_per_sec is not 0, max_bytes_per_sec is prioritized.
    # max_read_bytes_per_sec = 0
    # max_write_bytes_per_sec = 0

    ## The following parameters control the bandwidth weights assigned to different I/O traffic types. Generally, you do not need to adjust these parameters.
    ## TiFlash internally divides I/O requests into four types: foreground writes, background writes, foreground reads, background reads.
    ## When the I/O traffic limit is initialized, TiFlash assigns the bandwidth according to the following weight ratio.
    ## The following  default configurations indicate that each type of traffic gets a weight of 25% (25 / (25 + 25 + 25 + 25) = 25%).
    ## If the weight is configured to 0, the corresponding I/O traffic is not limited.
    # foreground_write_weight = 25
    # background_write_weight = 25
    # foreground_read_weight = 25
    # background_read_weight = 25
    ## TiFlash supports automatically tuning the traffic limit for different I/O types according to the current I/O load. Sometimes, the tuned bandwidth might exceed the weight ratio set above.
    ## auto_tune_sec indicates the interval of automatic tuning. The unit is seconds. If the value of auto_tune_sec is 0, the automatic tuning is disabled.
    # auto_tune_sec = 5

    ## The following configuration items only take effect for the TiFlash disaggregated storage and compute architecture mode. For details, see documentation at https://docs.pingcap.com/tidb/dev/tiflash-disaggregated-and-s3.
    # [storage.s3]
    # endpoint: http://s3.{region}.amazonaws.com # S3 endpoint address
    # bucket: mybucket                           # TiFlash stores all data in this bucket
    # root: /cluster1_data                       # Root directory where data is stored in the S3 bucket
    # access_key_id: {ACCESS_KEY_ID}             # Access S3 with ACCESS_KEY_ID
    # secret_access_key: {SECRET_ACCESS_KEY}     # Access S3 with SECRET_ACCESS_KEY
    # [storage.remote.cache]
    # dir: /data1/tiflash/cache        # Local data cache directory of the Compute Node
    # capacity: 858993459200           # 800 GiB

[flash]
    ## The listening address of TiFlash coprocessor services.
    service_addr = "0.0.0.0:3930"

    ## Introduced in v7.4.0. When the gap between the `applied_index` advanced by the current Raft state machine and the `applied_index` at the last disk spilling exceeds `compact_log_min_gap`, TiFlash executes the `CompactLog` command from TiKV and spills data to disk. Increasing this gap might reduce the disk spilling frequency of TiFlash, thus reducing read latency in random write scenarios, but it might also increase memory overhead. Decreasing this gap might increase the disk spilling frequency of TiFlash, thus alleviating memory pressure in TiFlash. However, at this stage, the disk spilling frequency of TiFlash will not be higher than that of TiKV, even if this gap is set to 0.
    ## It is recommended to keep the default value.
    # compact_log_min_gap = 200
    ## Introduced in v5.0. When the number or the size of rows in the Regions cached by TiFlash exceeds either of the following thresholds, TiFlash executes the `CompactLog` command from TiKV and spills data to disk.
    ## It is recommended to keep the default value.
    # compact_log_min_rows = 40960 # 40k
    # compact_log_min_bytes = 33554432 # 32MB

    ## The following configuration item only takes effect for the TiFlash disaggregated storage and compute architecture mode. For details, see documentation at https://docs.pingcap.com/tidb/dev/tiflash-disaggregated-and-s3.
    # disaggregated_mode = tiflash_write # The supported mode is `tiflash_write` or `tiflash_compute.

[flash.proxy]
    ## The listening address of proxy. If it is left empty, 127.0.0.1:20170 is used by default.
    addr = "127.0.0.1:20170"
    ## The external access address of addr. If it is left empty, "addr" is used by default.
    ## Should guarantee that other nodes can access through `advertise-addr` when you deploy the cluster on multiple nodes.
    advertise-addr = ""
    ## The listening address from which the proxy pulls metrics or status information. If it is left empty, 127.0.0.1:20292 is used by default.
    status-addr = "127.0.0.1:20292"
    ## The external access address of status-addr. If it is left empty, the value of "status-addr" is used by default.
    ## Should guarantee that other nodes can access through `advertise-status-addr` when you deploy the cluster on multiple nodes.
    advertise-status-addr = ""
    ## The external access address of the TiFlash coprocessor service.
    engine-addr = "10.0.1.20:3930"
    ## The data storage path of proxy.
    data-dir = "/tidb-data/tiflash-9000/flash"
    ## The configuration file path of proxy.
    config = "/tidb-deploy/tiflash-9000/conf/tiflash-learner.toml"
    ## The log path of proxy.
    log-file = "/tidb-deploy/tiflash-9000/log/tiflash_tikv.log"

[logger]
    ## Note that the following parameters only take effect in tiflash.log and tiflash_error.log. If you need to configure log parameters of TiFlash Proxy, specify them in tiflash-learner.toml.
    ## log level (available options: "trace", "debug", "info", "warn", "error"). The default value is "info".
    level = "info"
    ## The log of TiFlash.
    log = "/tidb-deploy/tiflash-9000/log/tiflash.log"
    ## The error log of TiFlash. The "warn" and "error" level logs are also output to this log file.
    errorlog = "/tidb-deploy/tiflash-9000/log/tiflash_error.log"
    ## Size of a single log file. The default value is "100M".
    size = "100M"
    ## Maximum number of log files to save. The default value is 10. For TiFlash logs and TiFlash error logs, the maximum number of log files to save is `count` respectively.
    count = 10

[raft]
    ## PD service address. Multiple addresses are separated with commas.
    pd_addr = "10.0.1.11:2379,10.0.1.12:2379,10.0.1.13:2379"

[status]
    ## The port through which Prometheus pulls metrics information. The default value is 8234.
    metrics_port = 8234

[profiles]

[profiles.default]
    ## The default value is false. This parameter determines whether the segment
    ## of DeltaTree Storage Engine uses logical split.
    ## Using the logical split can reduce the write amplification.
    ## However, these are at the cost of disk space waste.
    ## It is strongly recommended to keep the default value `false` and
    ## not to change it to `true` in v6.2.0 and later versions. For details,
    ## see known issue [#5576](https://github.com/pingcap/tiflash/issues/5576).
    # dt_enable_logical_split = false

    ## `max_threads` indicates the internal thread concurrency when TiFlash executes an MPP task.
    ## The default value is 0. When it is set to 0,
    ## TiFlash uses the number of CPU cores as the execution concurrency.
    ## This parameter only takes effect
    ## when the system variable `tidb_max_tiflash_threads` is set to -1.
    max_threads = 0
    
    ## The memory usage limit for the generated intermediate data in a single query.
    ## When the value is an integer, the unit is byte. For example, 34359738368 means 32 GiB of memory limit, and 0 means no limit.
    ## When the value is a floating-point number in the range of [0.0, 1.0), it means the ratio of the allowed memory usage to the total memory of the node. For example, 0.8 means 80% of the total memory, and 0.0 means no limit.
    ## The default value is 0, which means no limit.
    ## When a query attempts to consume memory that exceeds this limit, the query is terminated and an error is reported.
    max_memory_usage = 0

    ## The memory usage limit for the generated intermediate data in all queries.
    ## When the value is an integer, the unit is byte. For example, 34359738368 means 32 GiB of memory limit, and 0 means no limit.
    ## When the value is a floating-point number in the range of [0.0, 1.0), it means the ratio of the allowed memory usage to the total memory of the node. For example, 0.8 means 80% of the total memory, and 0.0 means no limit.
    ## The default value is 0.8, which means 80% of the total memory.
    ## When the queries attempt to consume memory that exceeds this limit, the queries are terminated and an error is reported.
    max_memory_usage_for_all_queries = 0.8

    ## New in v5.0. This item specifies the maximum number of cop requests that TiFlash Coprocessor executes at the same time. If the number of requests exceeds the specified value, the exceeded requests will queue. If the configuration value is set to 0 or not set, the default value is used, which is twice the number of physical cores.
    cop_pool_size = 0

    ## New in v5.0. This item specifies the maximum number of cop requests that TiFlash Coprocessor handles at the same time, including the requests being executed and the requests waiting in the queue. If the number of requests exceeds the specified value, the error "TiFlash Server is Busy" is returned. -1 indicates no limit; 0 indicates using the default value, which is 10 * cop_pool_size.
    cop_pool_handle_limit = 0

    ## New in v5.0. This item specifies the maximum time that a cop request can queue in TiFlash. If a cop request waits in the queue for a time longer than the value specified by this configuration, the error "TiFlash Server is Busy" is returned. A value less than or equal to 0 indicates no limit.
    cop_pool_max_queued_seconds = 15

    ## New in v5.0. This item specifies the maximum number of batch requests that TiFlash Coprocessor executes at the same time. If the number of requests exceeds the specified value, the exceeded requests will queue. If the configuration value is set to 0 or not set, the default value is used, which is twice the number of physical cores.
    batch_cop_pool_size = 0
    ## New in v6.1.0. This item specifies the number of requests that TiFlash can concurrently process when it receives ALTER TABLE ... COMPACT from TiDB.
    ## If the value is set to 0, the default value 1 prevails.
    manual_compact_pool_size = 1
    ## New in v5.4.0. This item enables or disables the elastic thread pool feature, which significantly improves CPU utilization in high concurrency scenarios of TiFlash. The default value is true.
    enable_elastic_threadpool = true
    ## Compression algorithm of the TiFlash storage engine. The value can be LZ4, zstd, or LZ4HC, and is case-insensitive. By default, LZ4 is used.
    dt_compression_method = "LZ4"
    ## Compression level of the TiFlash storage engine. The default value is 1.
    ## It is recommended that you set this value to 1 if dt_compression_method is LZ4.
    ## It is recommended that you set this value to -1 (smaller compression rate, but better read performance) or 1 if dt_compression_method is zstd.
    ## It is recommended that you set this value to 9 if dt_compression_method is LZ4HC.
    dt_compression_level = 1

    ## New in v6.2.0. This item specifies the minimum ratio of valid data in a PageStorage data file. When the ratio of valid data in a PageStorage data file is less than the value of this configuration, GC is triggered to compact data in the file. The default value is 0.5.
    dt_page_gc_threshold = 0.5

    ## New in v7.0.0. This item specifies the maximum memory available for the HashAggregation operator with group by key before a disk spill is triggered. When the memory usage exceeds the threshold, HashAggregation reduces memory usage by spilling to disk. This item defaults to 0, which means that the memory usage is unlimited and spill to disk is never used for HashAggregation.
    max_bytes_before_external_group_by = 0

    ## New in v7.0.0. This item specifies the maximum memory available for the sort or topN operator before a disk spill is triggered. When the memory usage exceeds the threshold, the sort or topN operator reduces memory usage by spilling to disk. This item defaults to 0, which means that the memory usage is unlimited and spill to disk is never used for sort or topN.
    max_bytes_before_external_sort = 0

    ## New in v7.0.0. This item specifies the maximum memory available for the HashJoin operator with EquiJoin before a disk spill is triggered. When the memory usage exceeds the threshold, HashJoin reduces memory usage by spilling to disk. This item defaults to 0, which means that the memory usage is unlimited and spill to disk is never used for HashJoin with EquiJoin.
    max_bytes_before_external_join = 0

    ## New in v7.4.0. This item controls whether to enable the TiFlash resource control feature. When it is set to true, TiFlash uses the pipeline execution model.
    enable_resource_control = true

    ## New in v6.0.0. This item is used for the MinTSO scheduler. It specifies the maximum number of threads that one resource group can use. The default value is 5000. For details about the MinTSO scheduler, see https://docs.pingcap.com/tidb/v8.1/tiflash-mintso-scheduler.
    task_scheduler_thread_soft_limit = 5000

    ## New in v6.0.0. This item is used for the MinTSO scheduler. It specifies the maximum number of threads in the global scope. The default value is 10000. For details about the MinTSO scheduler, see https://docs.pingcap.com/tidb/v8.1/tiflash-mintso-scheduler.
    task_scheduler_thread_hard_limit = 10000

    ## New in v6.4.0. This item is used for the MinTSO scheduler. It specifies the maximum number of queries that can run simultaneously in a TiFlash instance. The default value is 0, which means twice the number of vCPUs. For details about the MinTSO scheduler, see https://docs.pingcap.com/tidb/v8.1/tiflash-mintso-scheduler.
    task_scheduler_active_set_soft_limit = 0

## Security settings take effect starting from v4.0.5.
[security]
    ## New in v5.0. This configuration item enables or disables log redaction. If the configuration value
    ## is set to true, all user data in the log will be replaced by ?.
    ## Note that you also need to set security.redact-info-log for tiflash-learner's logging in tiflash-learner.toml.
    # redact_info_log = false

    ## Path of the file that contains a list of trusted SSL CAs. If set, the following settings
    ## cert_path and key_path are also needed.
    # ca_path = "/path/to/ca.pem"
    ## Path of the file that contains X509 certificate in PEM format.
    # cert_path = "/path/to/tiflash-server.pem"
    ## Path of the file that contains X509 key in PEM format.
    # key_path = "/path/to/tiflash-server-key.pem"
```
