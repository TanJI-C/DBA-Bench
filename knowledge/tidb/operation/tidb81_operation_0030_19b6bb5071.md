# View collected diagnostic data and upload it to Clinic Server

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/clinic/clinic-user-guide-for-tiup.md`
- Source Title: `Troubleshoot Clusters Using PingCAP Clinic`
- Source Heading Path: `Troubleshoot Clusters Using PingCAP Clinic > Troubleshoot cluster problems remotely > Step 3. View data locally (optional) | Troubleshoot Clusters Using PingCAP Clinic > Troubleshoot cluster problems remotely > Step 4. Upload data | Troubleshoot Clusters Using PingCAP Clinic > Troubleshoot cluster problems remotely > Step 4. Upload data > Method 1. Upload directly | Troubleshoot Clusters Using PingCAP Clinic > Troubleshoot cluster problems remotely > Step 4. Upload data > Method 2. Pack and upload data`
- Source Line Ranges: `203-277`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `cloud`, `shared`
- Topic Tags: `diagnostic-data`, `local-view`, `upload`, `packaging`, `internet-access`, `token`, `region`, `clinic-server`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0030_19b6bb5071`
- Source ID: `tidb-docs-8.1:clinic/clinic-user-guide-for-tiup.md#step-3-view-data-locally-optional`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e41fd38d14edf0d7c079ecdff74909a0552c30668bf3e6d8033319fb8d8c7b00`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/clinic/clinic-user-guide-for-tiup#step-3-view-data-locally-optional
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/clinic/clinic-user-guide-for-tiup.md

## Retrieval Guidance

- Use When: Use this content when you need to locate where TiUP Diag stores collected diagnostic files, understand direct versus packaged upload to Clinic Server, or find the exact upload and package commands.
- Retrieval Keywords: tiup diag upload, tiup diag package ${filepath}, Download URL, Clinic Server, --compress-metrics=false, insight.json, limits.conf, sysctl.conf, dmesg.log, ss.txt, config.json, meta.yaml, /monitor, token, region, .diag, pack and upload data, upload directly
- Follow-up Guidance: If upload fails because token or region was not set in Diag, the content states that Diag reports the failure and reminds you to set a token or `region`.
- Classification Note: This is classified as an operation topic because the content describes viewing collected data, choosing an upload method based on internet access, and running `tiup diag upload` or `tiup diag package`.

## Official Source Content

### Step 3. View data locally (optional)

The collected data is stored in separate subdirectories based on its data source. These subdirectories are named after machine names and port numbers. The storage locations of the configuration, logs, and other files of each node are the same as their relative storage paths in the real server of your TiDB cluster:

- Basic information of the system and hardware: in `insight.json`
- Contents in the system `/etc/security/limits.conf`: in `limits.conf`
- List of kernel parameters: in `sysctl.conf`
- Kernel logs: in `dmesg.log`
- Network connection during data collection: in `ss.txt`
- Configuration data: in the `config.json` directory of each node
- Meta-information for the cluster itself: in `meta.yaml` (this file is located at the top level of the directory that stores collected data)
- Monitoring data: in the `/monitor` file directory. The monitoring data is compressed by default and cannot be viewed directly. To directly view the JSON files with monitoring data, disable compression with the `--compress-metrics=false` parameter when collecting data.
### Step 4. Upload data

To provide cluster diagnostic data to PingCAP technical support staff, you need to upload the data to the Clinic Server first, and then send the obtained data access link to the staff. The Clinic Server is a cloud service that stores and shares diagnostic data securely.

Depending on the network connection of the cluster, you can choose one of the following methods to upload data:

- Methods 1: if the network where the cluster is located can access the internet, you can [directly upload data using the upload command](#method-1-upload-directly).
- Methods 2: if the network where the cluster is located cannot access the internet, you need to [pack the data and then upload it](#method-2-pack-and-upload-data).

> **Note:**
>
> If you did not set a token or `region` in Diag before uploading data, Diag reports the upload failure and reminds you to set a token or `region`. To set a token, see [the second step in Prerequisites](#prerequisites).
#### Method 1. Upload directly

If the network where the cluster is located can access the internet, you can directly upload the folder with collected data obtained in [Step 2: Collect data](#step-2-collect-data) using the following command:

```bash
tiup diag upload
```

After the upload is completed, the `Download URL` is displayed in the output. You can open the link of `Download URL` to see the uploaded data or send the link to the PingCAP technical support staff you contacted before.
#### Method 2. Pack and upload data

If the network where your cluster is located cannot access the internet, you need to pack the data on your intranet and upload the data package to the Clinic Server using a device with internet access. The detailed operations are as follows:

1. Pack the collected data obtained in [Step 2. Collect data](#step-2-collect-data) by running the following command:

    ```bash
    tiup diag package ${filepath}
    ```

    During packaging, Diag encrypts and compresses the data at the same time. In the test environment, 800 MB of data was compressed to 57 MB. The following is an example output:

    ```bash
    Starting component `diag`: /root/.tiup/components/diag/v0.7.0/diag package diag-fNTnz5MGhr6
    packaged data set saved to /home/user/diag-fNTnz5MGhr6.diag
    ```

    After the packaging is complete, the data is packaged to the `.diag` format. The `.diag` file can only be decrypted and viewed after being uploaded to the Clinic Server. If you want to directly forward the collected data instead of uploading it to the Clinic Server, you can compress the data by your own method and forward it.

2. From a machine with internet access, upload the compressed data package:

    ```bash
    tiup diag upload ${filepath}
    ```

    The following is an example output:

    ```bash
    [root@Copy-of-VM-EE-CentOS76-v1 user]# tiup diag upload /home/user/diag-fNTnz5MGhr6
    Starting component `diag`: /root/.tiup/components/diag/v0.7.0/diag upload /home/user/diag-fNTnz5MGhr6
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>><>>>>>>>>>
    Completed!
    Download URL: "https://clinic.pingcap.com.cn/portal/#/orgs/4/clusters/XXXX"
    ```

3. After the upload is complete, you can open the link of `Download URL` to see the uploaded data or send the link to the PingCAP technical support staff you contacted before.
