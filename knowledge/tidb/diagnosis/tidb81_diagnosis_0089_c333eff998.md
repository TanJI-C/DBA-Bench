# Troubleshooting Google Cloud private endpoint setup for TiDB Cloud

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/set-up-private-endpoint-connections-on-google-cloud.md`
- Source Title: `Connect to a TiDB Cloud Dedicated Cluster via Google Cloud Private Service Connect`
- Source Heading Path: `Connect to a TiDB Cloud Dedicated Cluster via Google Cloud Private Service Connect > Troubleshooting | Connect to a TiDB Cloud Dedicated Cluster via Google Cloud Private Service Connect > Troubleshooting > TiDB Cloud fails to create an endpoint service. What should I do? | Connect to a TiDB Cloud Dedicated Cluster via Google Cloud Private Service Connect > Troubleshooting > Fail to create an endpoint in Google Cloud. What should I do? | Connect to a TiDB Cloud Dedicated Cluster via Google Cloud Private Service Connect > Troubleshooting > I cancelled some actions. What should I do to handle cancellation before accepting endpoint access?`
- Source Line Ranges: `132-147`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `troubleshooting`, `endpoint-service`, `permission-errors`, `cancellation`, `manual-deletion`, `support-ticket`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0089_c333eff998`
- Source ID: `tidb-docs-8.1:tidb-cloud/set-up-private-endpoint-connections-on-google-cloud.md#troubleshooting`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d08d05ce6b83a10deb90a18cb5b2a49dc0ea3cb2f03502008c70d74d31b9accc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections-on-google-cloud#troubleshooting
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/set-up-private-endpoint-connections-on-google-cloud.md

## Retrieval Guidance

- Use When: Use this chunk when the user is troubleshooting Google Cloud private endpoint setup failures, long-running endpoint service creation, permission errors, or cancelled setup actions.
- Retrieval Keywords: Troubleshooting, endpoint service, Creating state for a long time, failed, support ticket, Google Cloud Shell, permission-related error, necessary permissions, retrying, cancelled actions, Unsaved drafts, manually delete the corresponding endpoint, delete endpoint
- Follow-up Guidance: This content explains that long-running or failed endpoint service creation should be handled with a support ticket, permission-related endpoint creation errors require reviewing the Google Cloud Shell error message, and cancelled actions might require manual endpoint deletion in the Google Cloud console.
- Classification Note: This is classified as diagnosis because the content is organized as troubleshooting guidance for setup failures, permission issues, and cancellation handling.

## Official Source Content

## Troubleshooting
### TiDB Cloud fails to create an endpoint service. What should I do?

The endpoint service is created automatically after you open the **Create Google Cloud Private Endpoint Connection** page and choose the TiDB cluster. If it shows as failed or remains in the **Creating** state for a long time, submit a [support ticket](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) for assistance.
### Fail to create an endpoint in Google Cloud. What should I do?

To troubleshoot the issue, you need to review the error message returned by Google Cloud Shell after you execute the private endpoint creation command. If it is a permission-related error, you must grant the necessary permissions before retrying.
### I cancelled some actions. What should I do to handle cancellation before accepting endpoint access?

Unsaved drafts of cancelled actions will not be retained or displayed. You need to repeat each step when creating a new private endpoint in the TiDB Cloud console next time.

If you have already executed the command to create a private endpoint in Google Cloud Shell, you need to manually [delete the corresponding endpoint](https://cloud.google.com/vpc/docs/configure-private-service-connect-services#delete-endpoint) in the Google Cloud console.
