# Run local quick checks and review Clinic upload FAQ

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/clinic/clinic-user-guide-for-tiup.md`
- Source Title: `Troubleshoot Clusters Using PingCAP Clinic`
- Source Heading Path: `Troubleshoot Clusters Using PingCAP Clinic > Perform a quick check on the cluster status locally | Troubleshoot Clusters Using PingCAP Clinic > FAQ`
- Source Line Ranges: `278-360`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`, `cloud`
- Topic Tags: `quick-check`, `config-check`, `collect`, `diagnostic-result`, `knowledge-base`, `breakpoint-upload`, `data-retention`, `permissions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0012_a463353f44`
- Source ID: `tidb-docs-8.1:clinic/clinic-user-guide-for-tiup.md#perform-a-quick-check-on-the-cluster-status-locally`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `10044560aa8d5d34dc6800d2fad9c52466346407721d5077126ce2ab30238b43`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/clinic/clinic-user-guide-for-tiup#perform-a-quick-check-on-the-cluster-status-locally
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/clinic/clinic-user-guide-for-tiup.md

## Retrieval Guidance

- Use When: Use this content when you need the local quick check workflow for configuration data or the FAQ details about re-uploading, Clinic Server access permissions, and uploaded data retention.
- Retrieval Keywords: tiup diag collect ${cluster-name} --include="config", tiup diag check ${subdir-in-output-data}, local quick check, meta.yaml, Diagnostic result, RuleID, Variation, knowledge base link, PingCAP Clinic, Health Report, breakpoint upload, Clinic Server, data access link, permission, 180 days
- Follow-up Guidance: If a returned Clinic Server link cannot be opened, the content says to log in first, then check access permissions, and contact the data owner for permission if needed.
- Classification Note: This is classified as diagnosis because the content explains how to collect configuration data, run `tiup diag check`, interpret diagnostic results, and review related FAQ items for upload and access.

## Official Source Content

## Perform a quick check on the cluster status locally

You can have a quick check on the cluster status locally using Diag. Even if your cluster is running stably for now, it is necessary to periodically check the cluster to detect potential stability risks. You can identify potential health risks of a cluster using the local quick check feature provided by PingCAP Clinic. The local check only checks configuration. To check more items, such as metrics and logs, it is recommended to upload the diagnostic data to the Clinic Server and use the Health Report feature.

1. Collect configuration data:

    ```bash
    tiup diag collect ${cluster-name} --include="config"
    ```

    The data of configuration files are relatively small. After the collection, the collected data is stored in the current path by default. In the test environment, for a cluster with 18 nodes, the data size of configuration files is less than 10 KB.

2. Diagnose configuration data:

    ```bash
    tiup diag check ${subdir-in-output-data}
    ```

    `${subdir-in-output-data}` in the above command is the path that stores the collected data, and this path has the `meta.yaml` file.

3. View the diagnostic result:

    The diagnostic result is returned on the command line. For example:

    ```bash
    Starting component `diag`: /root/.tiup/components/diag/v0.7.0/diag check diag-fNTnz5MGhr6

    # Diagnostic result
    lili 2022-01-24T09:33:57+08:00

    ## 1. Cluster basic information
    - Cluster ID: 7047403704292855808
    - Cluster Name: lili
    - Cluster Version: v5.3.0

    ## 2. Sampling information
    - Sample ID: fNTnz5MGhr6
    - Sampling Date: 2022-01-24T09:33:57+08:00
    - Sample Content:: [system monitor log config]

    ## 3. Diagnostic result, including potential configuration problems
    In this inspection, 22 rules were executed.

    The results of **1** rules were abnormal and needed to be further discussed with support team.

    The following is the details of the abnormalities.

    ### Diagnostic result summary
    The configuration rules are all derived from PingCAP's OnCall Service.

    If the results of the configuration rules are found to be abnormal, they may cause the cluster to fail.

    There were **1** abnormal results.

    #### Path to save the diagnostic result file

    Rule Name: tidb-max-days
    - RuleID: 100
    - Variation: TidbConfig.log.file.max-days
    - For more information, please visit: https://s.tidb.io/msmo6awg
    - Check Result:
      TidbConfig_172.16.7.87:4000   TidbConfig.log.file.max-days:0   warning
      TidbConfig_172.16.7.86:4000   TidbConfig.log.file.max-days:0   warning
      TidbConfig_172.16.7.179:4000   TidbConfig.log.file.max-days:0   warning

    Result report and record are saved at diag-fNTnz5MGhr6/report-220125153215
    ```

    In the last section of the diagnostic result (under `#### Path to save the diagnostic result file` in the above example output), for each configuration potential risk found, Diag provides a corresponding knowledge base link with detailed configuration suggestions. In the example above, the relevant link is `https://s.tidb.io/msmo6awg`.
## FAQ

1. If the data upload fails, can I re-upload it?

    Yes. Data upload supports breakpoint upload. If the upload fails, you can upload it again directly.

2. After uploading data, I cannot open the returned data access link. What should I do?

    Log in to Clinic Server first. If you still cannot open the link after login success, check whether you have access to data. If not, contact the data owner for permission. After getting the permission, log in to Clinic Server and open the link again.

3. How long will the uploaded data be kept on the Clinic Server?

    The longest time is 180 days. You can delete the data you uploaded on the Clinic Server page at any time.
