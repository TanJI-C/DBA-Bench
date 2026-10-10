# PingCAP Clinic overview, scenarios, and diagnostic data collection principles

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/clinic/clinic-introduction.md`
- Source Title: `PingCAP Clinic Overview`
- Source Heading Path: `PingCAP Clinic Overview | PingCAP Clinic Overview > User scenarios | PingCAP Clinic Overview > Implementation principles`
- Source Line Ranges: `5-59`
- Source Scope: `shared`
- Primary Component: `shared`
- Related Components: `operator`, `tiup`, `tidb`, `tikv`, `pd`
- Topic Tags: `overview`, `diagnostic-service`, `diag`, `clinic-server`, `user-scenarios`, `remote-troubleshooting`, `health-check`, `data-collection`, `topology`, `scp`, `ssh`, `http`, `sql`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0012_2be84dba76`
- Source ID: `tidb-docs-8.1:clinic/clinic-introduction.md#pingcap-clinic-overview`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dcc4529c86687bbc91e230c617e3b2d0e4c931050446ac3427dbacacf64b61e4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/clinic/clinic-introduction#pingcap-clinic-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/clinic/clinic-introduction.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks what PingCAP Clinic is, which components it includes, what troubleshooting or health-check scenarios it supports, or how Diag collects diagnostic data from TiUP or TiDB Operator clusters.
- Retrieval Keywords: PingCAP Clinic, Diag client, Clinic Server, PingCAP Clinic Overview, TiUP, TiDB Operator, remote troubleshooting, quick health check, diagnostic data collection, cluster topology, SCP, SSH, HTTP interface, Prometheus, SQL statements, system variables, TiDB v4.0 and later, does not support TiDB Ansible
- Follow-up Guidance: The source also points to detailed pages for Quick Start, troubleshooting guides, and PingCAP Clinic Diagnostic Data.
- Classification Note: This is classified as architecture because the content describes the PingCAP Clinic service, its Diag client and Clinic Server components, supported user scenarios, and the data collection methods across TiUP, TiDB Operator, TiDB, TiKV, PD, and Prometheus.

## Official Source Content

# PingCAP Clinic Overview

PingCAP Clinic Diagnostic Service (PingCAP Clinic) is a diagnostic service provided by PingCAP for TiDB clusters that are deployed using either TiUP or TiDB Operator. This service helps to troubleshoot cluster problems remotely and provides a quick check of cluster status locally. With PingCAP Clinic, you can ensure the stable operation of your TiDB cluster for its full life-cycle, predict potential problems, reduce the probability of problems, troubleshoot cluster problems quickly, and fix cluster problems.

PingCAP Clinic provides the following two components to diagnose cluster problems:

- [Diag client](https://github.com/pingcap/diag):

    Diag client (Diag) is an open-source diagnostic tool deployed on the cluster side. Diag is used to collect cluster diagnostic data, upload diagnostic data to the Clinic Server, and perform a quick health check locally on your cluster. For a full list of diagnostic data that can be collected by Diag, see [PingCAP Clinic Diagnostic Data](https://docs.pingcap.com/tidb/stable/clinic/clinic-data-instruction-for-tiup).

    > **Note:**
    >
    > Diag supports TiDB v4.0 and later versions, but **does not support** collecting data from clusters deployed using TiDB Ansible.

- Clinic Server:

    Clinic Server is a cloud service deployed in the cloud. By providing diagnostic services in the SaaS model, the Clinic Server can not only receive uploaded diagnostic data but also work as an online diagnostic environment to store data, view data, and provide cluster diagnostic reports. Clinic Server provides two independent services depending on the storage location:

    - [Clinic Server for international users](https://clinic.pingcap.com): Data is stored in AWS in US.
    - [Clinic Server for users in the Chinese mainland](https://clinic.pingcap.com.cn): Data is stored in AWS in China (Beijing) regions.
## User scenarios

- Troubleshoot cluster problems remotely

    When your cluster has some problems that cannot be fixed quickly, you can [get support](https://docs.pingcap.com/tidb/stable/support) from PingCAP or the community. When contacting technical support for remote assistance, you need to save various diagnostic data from the cluster and forward the data to the support staff. In this case, you can use Diag to collect diagnostic data with one click. Diag helps you to collect complete diagnostic data quickly, which can avoid complex manual data collection operations. After collecting data, you can upload the data to the Clinic Server for PingCAP technical support staff to troubleshoot cluster problems. The Clinic Server provides secure storage for uploaded diagnostic data and supports the online diagnosis, which greatly improves the troubleshooting efficiency.

- Quickly check cluster status

    Even if your cluster is running stably for now, it is necessary to periodically check the cluster to detect potential stability risks. You can identify potential health risks of a cluster using the local and server-side quick check feature provided by PingCAP Clinic.
## Implementation principles

This section introduces the implementation principles about how Diag collects diagnostic data from a cluster.

First, Diag gets cluster topology information from the deployment tool TiUP (tiup-cluster) or TiDB Operator (tidb-operator). Then, Diag collects different types of diagnostic data through various data collection methods as follows:

- Transfer server files through SCP

    For clusters deployed using TiUP, Diag can collect log files and configuration files directly from the nodes of the target component through the Secure copy protocol (SCP).

- Collect data by running commands remotely through SSH

    For clusters deployed using TiUP, Diag can connect to the target component system through SSH (Secure Shell) and run commands (such as Insight) to obtain system information, including kernel logs, kernel parameters, and basic information of the system and hardware.

- Collect data through HTTP call

    - By calling the HTTP interface of TiDB components, Diag can get the real-time configuration sampling information and the real-time performance sampling information of TiDB, TiKV, PD, and other components.
    - By calling the HTTP interface of Prometheus, Diag can get alert information and monitoring metrics data.

- Query database parameters through SQL statements

    Using SQL statements, Diag can query system variables and other information of TiDB. To use this method, you need to **additionally provide** the username and password to access TiDB when collecting data.
