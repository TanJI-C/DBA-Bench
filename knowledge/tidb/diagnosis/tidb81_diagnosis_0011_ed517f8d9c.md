# Remote troubleshooting data collection with Diag

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/clinic/clinic-user-guide-for-tiup.md`
- Source Title: `Troubleshoot Clusters Using PingCAP Clinic`
- Source Heading Path: `Troubleshoot Clusters Using PingCAP Clinic > Troubleshoot cluster problems remotely | Troubleshoot Clusters Using PingCAP Clinic > Troubleshoot cluster problems remotely > Step 1. Check the data to be collected | Troubleshoot Clusters Using PingCAP Clinic > Troubleshoot cluster problems remotely > Step 2. Collect data`
- Source Line Ranges: `123-202`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`, `dm`, `shared`
- Topic Tags: `clinic`, `diag`, `data-collection`, `remote-troubleshooting`, `monitoring-data`, `configuration-data`, `time-range`, `include-exclude`, `cluster-diagnostics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0011_ed517f8d9c`
- Source ID: `tidb-docs-8.1:clinic/clinic-user-guide-for-tiup.md#troubleshoot-cluster-problems-remotely`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `368193102acad9fa5b20b7f5f57fceaa5f2718d6f8b8952966a81e5072db4df0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/clinic/clinic-user-guide-for-tiup#troubleshoot-cluster-problems-remotely
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/clinic/clinic-user-guide-for-tiup.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the Diag commands and parameters to collect remote troubleshooting data from a TiUP-deployed TiDB or DM cluster within a specified time range.
- Retrieval Keywords: tiup diag collect, tiup diag collectdm, -f, --from, -t, --to, UTC by default, 12:30 +0800, tiup diag collect -h, tiup diag collectdm -h, --include, --exclude, -N, --node, -l, db_vars, perf, debug, system, monitor, log, config, tiup diag collect <cluster-name> --include="system,monitor,log,config,db_vars,perf,debug", Estimated size of data to collect, Do you want to continue? [y/N], Collected data are stored in
- Follow-up Guidance: The source says Diag first shows the estimated data size and target storage path for confirmation, and after completion it prints the folder path of the collected data.
- Classification Note: This is classified as diagnosis because the content focuses on collecting diagnostic data, including monitoring data and configuration information, for later troubleshooting.

## Official Source Content

## Troubleshoot cluster problems remotely

You can use Diag to quickly collect diagnostic data from TiDB clusters and DM clusters, including monitoring data and configuration information.
### Step 1. Check the data to be collected

For a full list of data that can be collected by Diag, see [PingCAP Clinic Diagnostic Data](https://docs.pingcap.com/tidb/stable/clinic/clinic-data-instruction-for-tiup).

To improve the efficiency of the later diagnosis, you are recommended to collect full diagnostic data including monitoring data and configuration information. For details, see [Collect data from clusters](#step-2-collect-data).
### Step 2. Collect data

With Diag, you can collect data from the TiDB clusters and the DM clusters deployed using TiUP.

1. Run the data collection command of Diag.

    For example, to collect the diagnostic data from 4 hours ago to 2 hours ago based on the current time, run the following command:

    <div label="TiDB Cluster">

    ```bash
    tiup diag collect ${cluster-name} -f="-4h" -t="-2h"
    ```

    </div>
    <div label="DM Cluster">

    ```bash
    tiup diag collectdm ${dm-cluster-name} -f="-4h" -t="-2h"
    ```

    </div>

    Descriptions of the parameters for data collection:

    - `-f/--from`: specifies the start time of the data collection. If you do not specify this parameter, the default start time is 2 hours before the current time. To modify the time zone, use the `-f="12:30 +0800"` syntax. If you do not specify the time zone information in this parameter, such as `+0800`, the time zone is UTC by default.
    - `-t/--to`: specifies the end time of the data collection. If you do not specify this parameter, the default end time is the current moment. To modify the time zone, use the `-f="12:30 +0800"` syntax. If you do not specify the time zone information in this parameter, such as `+0800`, the time zone is UTC by default.

    Parameter usage tips:

    In addition to specifying the data collection time, you can use Diag to specify more parameters. To get all parameters, run the `tiup diag collect -h` or `tiup diag collectdm -h` command.

    > **Note:**
    >
    > - Diag does not collect system variables data (db_vars) by default. To collect this data, you need to additionally provide a username and password that can access the database. Note that the reading access to system variables should be enabled in this database.
    > - Diag does not collect performance data (`perf`) and debug data (`debug`) by default.
    > - To collect full diagnostic data including system variables, use the command `tiup diag collect <cluster-name> --include="system,monitor,log,config,db_vars,perf,debug"`.

    - `-l`: the bandwidth limit for transferring files, the unit is Kbit/s, and the default value is `100000` (the `-l` parameter of scp).
    - `-N/--node`: only collects data from a specified node. The format is `ip:port`.
    - `--include`: only collects specific types of data. The optional values are `system`, `monitor`, `log`, `config`, and `db_vars`. To include two or more types, you can use `,` as a separator between the types.
    - `--exclude`: does not collect specific types of data. The optional values are `system`, `monitor`, `log`, `config`, and `db_vars`. To exclude two or more types, you can use `,` as a separator between the types.

    After you run the command, Diag does not start collecting data immediately. Instead, Diag provides the estimated data size and the target data storage path in the output for you to confirm whether to continue. For example:

    ```bash
    Estimated size of data to collect:
    Host               Size       Target
    ----               ----       ------
    172.16.7.129:9090  43.57 MB   1775 metrics, compressed
    172.16.7.87        0 B        /tidb-deploy/tidb-4000/log/tidb_stderr.log
    ... ...
    172.16.7.179       325 B      /tidb-deploy/tikv-20160/conf/tikv.toml
    Total              2.01 GB    (inaccurate)
    These data will be stored in /home/user/diag-fNTnz5MGhr6
    Do you want to continue? [y/N]: (default=N)
    ```

2. Enter `Y` to confirm that you want to start collecting data.

    Collecting data takes a certain amount of time. The time varies according to the volume of data to be collected. For example, in a test environment, collecting 1 GB of data takes about 10 minutes.

    After the collection is complete, Diag provides the folder path where the collected data is located. For example:

    ```bash
    Collected data are stored in /home/user/diag-fNTnz5MGhr6
    ```
