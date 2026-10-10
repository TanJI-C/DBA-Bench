# Control and target machine software recommendations

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/hardware-and-software-requirements.md`
- Source Title: `Software and Hardware Recommendations`
- Source Heading Path: `Software and Hardware Recommendations > Software recommendations | Software and Hardware Recommendations > Software recommendations > Control machine | Software and Hardware Recommendations > Software recommendations > Target machines`
- Source Line Ranges: `145-165`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `control-machine`, `target-machines`, `software-prerequisites`, `tiup`, `sshpass`, `numa`, `tar`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0366_cfc1cb9669`
- Source ID: `tidb-docs-8.1:hardware-and-software-requirements.md#software-recommendations`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d57ea61c85fdde29e0b3f3ab2663f3b9ad9783837c729b391bba9df9eb3ac7de`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/hardware-and-software-requirements#software-recommendations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/hardware-and-software-requirements.md

## Retrieval Guidance

- Use When: Use this chunk when identifying software prerequisites and minimum versions for the control machine and target machines in a TiUP-based TiDB deployment.
- Retrieval Keywords: Software recommendations, Control machine, Target machines, sshpass 1.06 or later, TiUP 1.5.0 or later, numa 2.0.12 or later, tar any, deploy TiUP on the control machine, operate and manage TiDB clusters
- Follow-up Guidance: The source states that deploying TiUP on the control machine is required to operate and manage TiDB clusters.
- Classification Note: This is reference content because it lists exact prerequisite software and versions for control and target machines.

## Official Source Content

## Software recommendations
### Control machine

| Software | Version |
| :--- | :--- |
| sshpass | 1.06 or later |
| TiUP | 1.5.0 or later |

> **Note:**
>
> It is required that you [deploy TiUP on the control machine](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup#step-2-deploy-tiup-on-the-control-machine) to operate and manage TiDB clusters.
### Target machines

| Software | Version |
| :--- | :--- |
| sshpass | 1.06 or later |
| numa | 2.0.12 or later |
| tar | any |
