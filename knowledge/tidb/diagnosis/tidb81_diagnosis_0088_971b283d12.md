# Azure Private Link troubleshooting for endpoint service and canceled setup

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/set-up-private-endpoint-connections-on-azure.md`
- Source Title: `Connect to a TiDB Cloud Dedicated Cluster via Azure Private Link`
- Source Heading Path: `Connect to a TiDB Cloud Dedicated Cluster via Azure Private Link > Troubleshooting | Connect to a TiDB Cloud Dedicated Cluster via Azure Private Link > Troubleshooting > TiDB Cloud fails to create an endpoint service. What should I do? | Connect to a TiDB Cloud Dedicated Cluster via Azure Private Link > Troubleshooting > If I cancel the action during setup, what should I do before accepting the private endpoint?`
- Source Line Ranges: `113-123`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `troubleshooting`, `endpoint service`, `creating state`, `failed state`, `support ticket`, `canceled setup`, `endpoint detection`, `networking page`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0088_971b283d12`
- Source ID: `tidb-docs-8.1:tidb-cloud/set-up-private-endpoint-connections-on-azure.md#troubleshooting`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0360a966a3ec5557b7ccbb62e50e205a7ceead4b7f8998822a2edfa6416956ab`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections-on-azure#troubleshooting
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/set-up-private-endpoint-connections-on-azure.md

## Retrieval Guidance

- Use When: Use this when the user is troubleshooting Azure Private Link setup problems such as an endpoint service stuck in Creating or a canceled setup flow in the TiDB Cloud console.
- Retrieval Keywords: Troubleshooting, endpoint service, Creating state, failed, support ticket, Create Azure Private Endpoint, Cancel, Create Azure Private Endpoint Connection, Networking page, automatically detect your private endpoints, delete the endpoint directly
- Follow-up Guidance: If the Azure private endpoint was already created, the source says it can still be viewed on the Networking page and either configured to complete setup or deleted in the TiDB Cloud console.
- Classification Note: This is classified as diagnosis because the content addresses troubleshooting conditions and what the documented outcomes are for failed endpoint service creation or canceled setup.

## Official Source Content

## Troubleshooting
### TiDB Cloud fails to create an endpoint service. What should I do?

The endpoint service is created automatically after you open the **Create Azure Private Endpoint** page and choose the TiDB cluster. If it shows as failed or remains in the **Creating** state for a long time, submit a [support ticket](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) for assistance.
### If I cancel the action during setup, what should I do before accepting the private endpoint?

The Azure private endpoint connection feature can automatically detect your private endpoints. This means that after [creating an Azure private endpoint](#step-2-create-an-azure-private-endpoint) in the Azure portal, if you click **Cancel** in the **Create Azure Private Endpoint Connection** dialog in the TiDB Cloud console, you can still view the created endpoint on the **Networking** page. If the cancellation is unintentional, you can continue to configure the endpoint to complete the setup. If the cancellation is intentional, you can delete the endpoint directly in the TiDB Cloud console.

[^1]: The diagram of the Azure Private Link architecture is from the [What is Azure Private Link service](https://learn.microsoft.com/en-us/azure/private-link/private-link-service-overview) document ([source file on GitHub](https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/private-link/private-link-service-overview.md)) in Azure documentation, licensed under the Creative Commons Attribution 4.0 International.
