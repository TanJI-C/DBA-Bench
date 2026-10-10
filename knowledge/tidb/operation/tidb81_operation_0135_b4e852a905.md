# Deployment and operation tools overview

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ecosystem-tool-user-guide.md`
- Source Title: `TiDB Tools Overview`
- Source Heading Path: `TiDB Tools Overview | TiDB Tools Overview > Deployment and operation Tools | TiDB Tools Overview > Deployment and operation Tools > Deploy and operate TiDB on physical or virtual machines - TiUP | TiDB Tools Overview > Deployment and operation Tools > Deploy and operate TiDB on Kubernetes - TiDB Operator`
- Source Line Ranges: `5-36`
- Source Scope: `all`
- Primary Component: `ecosystem`
- Related Components: `tiup`, `operator`, `tidb`, `pd`, `tikv`
- Topic Tags: `tools-overview`, `deployment`, `operations`, `physical-machines`, `virtual-machines`, `kubernetes`, `cluster-management`, `lifecycle-management`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0135_b4e852a905`
- Source ID: `tidb-docs-8.1:ecosystem-tool-user-guide.md#tidb-tools-overview`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5171088adcc7adc14b971eb40de00ab88594e56a4a7edb3b165583fe9707d656`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ecosystem-tool-user-guide#tidb-tools-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ecosystem-tool-user-guide.md

## Retrieval Guidance

- Use When: Use this chunk when identifying which TiDB deployment and operation tool fits physical or virtual machines versus Kubernetes and what life-cycle management each tool covers.
- Retrieval Keywords: TiUP, TiUP cluster, TiDB Operator, physical or virtual machines, Kubernetes, deploy and operate TiDB, package manager, cluster management, deployment and operation tools, deploying starting stopping destroying scaling upgrading, manage TiDB cluster parameters, full life-cycle management
- Follow-up Guidance: The chunk points to TiUP basics such as Terminology and Concepts, Deploy a TiDB Cluster Using TiUP, and Manage TiUP Components with TiUP Commands, and to TiDB Operator Architecture and Get Started with TiDB Operator on Kubernetes.
- Classification Note: This is classified as operation because the content compares TiUP and TiDB Operator for deploying, operating, and managing the TiDB cluster life cycle in different environments.

## Official Source Content

# TiDB Tools Overview

TiDB provides a rich set of tools to help you deploy and maintain TiDB, manage data (such as data migration, backup & restore, and data comparison), and run Spark SQL on TiKV. You can select the applicable tools according to your needs.
## Deployment and operation Tools

TiDB provides TiUP and TiDB Operator to meet your deployment and operation needs in different system environments.
### Deploy and operate TiDB on physical or virtual machines - TiUP

[TiUP](https://docs.pingcap.com/tidb/stable/tiup/tiup-overview) is a TiDB package manager on physical or virtual machines. TiUP can manage multiple TiDB components such as TiDB, PD, and TiKV. To start any component in the TiDB ecosystem, you just need to execute a single line of TiUP command.

TiUP provides [TiUP cluster](https://github.com/pingcap/tiup/tree/master/components/cluster), a cluster management component written in Golang. By using TiUP cluster, you can easily perform daily database operations, including deploying, starting, stopping, destroying, scaling, and upgrading a TiDB cluster, and manage TiDB cluster parameters.

The following are the basics of TiUP:

- [Terminology and Concepts](https://docs.pingcap.com/tidb/stable/tiup/tiup-terminology-and-concepts)
- [Deploy a TiDB Cluster Using TiUP](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup)
- [Manage TiUP Components with TiUP Commands](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-management)
- Applicable TiDB versions: v4.0 and later versions
### Deploy and operate TiDB on Kubernetes - TiDB Operator

[TiDB Operator](https://github.com/pingcap/tidb-operator) is an automatic operation system for managing TiDB clusters on Kubernetes. It provides full life-cycle management for TiDB including deployment, upgrades, scaling, backup, and configuration changes. With TiDB Operator, TiDB can run seamlessly in the Kubernetes clusters deployed on a public or private cloud.

The following are the basics of TiDB Operator:

- [TiDB Operator Architecture](https://docs.pingcap.com/tidb-in-kubernetes/stable/architecture)
- [Get Started with TiDB Operator on Kubernetes](https://docs.pingcap.com/tidb-in-kubernetes/stable/get-started/)
- Applicable TiDB versions: v2.1 and later versions
