# Collect, upload, and view Clinic diagnostic data

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/clinic/quick-start-with-clinic.md`
- Source Title: `Quick Start Guide for PingCAP Clinic`
- Source Heading Path: `Quick Start Guide for PingCAP Clinic > Steps`
- Source Line Ranges: `108-153`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `cloud`, `shared`
- Topic Tags: `data-collection`, `upload`, `download-url`, `health-report`, `internet-access`, `package-upload`, `size-limit`, `version-dependency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0031_401ad851b3`
- Source ID: `tidb-docs-8.1:clinic/quick-start-with-clinic.md#steps`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `79fcd46f50cd9e929d5bd6457a1bbfb465e9e09cad56a9402269eb19d738c1c3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/clinic/quick-start-with-clinic#steps
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/clinic/quick-start-with-clinic.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants the basic workflow and commands to collect diagnostic data with Diag, upload it to Clinic Server, obtain the Download URL, or know when Health Report becomes available.
- Retrieval Keywords: tiup diag collect ${cluster-name} -f="-4h" -t="-2h", estimated data size, target data storage path, enter Y, tiup diag upload ${filepath}, Download URL, compressed file no larger than 3 GB, Diag v0.9.0 or a later version, tiup update diag, pack and upload data, Health Report, 5 to 15 minutes
- Follow-up Guidance: The source says that if the cluster network cannot access the internet, you need to pack the collected data and upload the package, and it links to Method 2. Pack and upload data.
- Classification Note: This is classified as operation because the content gives the step-by-step collection, upload, and report-viewing procedure with command examples and runtime conditions.

## Official Source Content

## Steps

1. Run Diag to collect diagnostic data.

    For example, to collect the diagnostic data from 4 hours ago to 2 hours ago based on the current time, run the following command:

    ```bash
    tiup diag collect ${cluster-name} -f="-4h" -t="-2h"
    ```

    After you run the command, Diag does not start collecting data immediately. Instead, Diag provides the estimated data size and the target data storage path in the output for you to confirm whether to continue. To confirm that you want to start collecting data, enter `Y`.

    After the collection is complete, Diag provides the folder path where the collected data is located.

2. Upload the collected data to Clinic Server.

    > **Note:**
    >
    > The size of data (the compressed file with collected data) to be uploaded should be **no larger than** 3 GB. Otherwise, the data upload fails.

    - If the network where your cluster is located can access the internet, you can directly upload the folder with collected data using the following command:

        ```bash
        tiup diag upload ${filepath}
        ```

        After the upload is completed, the `Download URL` is displayed in the output.

        > **Note:**
        >
        > When uploading data using this method, you need to use Diag v0.9.0 or a later version. You can get the Diag version when you run it. If the Diag version is earlier than 0.9.0, you can use the `tiup update diag` command to upgrade Diag to the latest version.

    - If the network where your cluster is located cannot access the internet, you need to pack the collected data and upload the package. For details, see [Method 2. Pack and upload data](https://docs.pingcap.com/tidb/stable/clinic/clinic-user-guide-for-tiup#method-2-pack-and-upload-data).

3. After the upload is complete, get the data access link from `Download URL` in the command output.

    By default, the diagnostic data includes the cluster name, cluster topology information, log content in the collected diagnostic data, and Grafana Dashboard information reorganized based on the metrics in the collected data.

    You can use the data to troubleshoot cluster problems by yourself, or you can provide the data access link to PingCAP technical support staff to facilitate the remote troubleshooting.

4. View the results of Health Report

    After data is uploaded, Clinic Server processes the data automatically in the background. The Health Report is generated in approximately 5 to 15 minutes. You can view the report by opening the diagnostic data link and click the "Health Report".
