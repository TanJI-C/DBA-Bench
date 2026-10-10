# Billing overview, invoices, bills, and cost explorer

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-billing.md`
- Source Title: `TiDB Cloud Billing`
- Source Heading Path: `TiDB Cloud Billing | TiDB Cloud Billing > Invoices | TiDB Cloud Billing > Billing details | TiDB Cloud Billing > Cost explorer`
- Source Line Ranges: `5-89`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dashboard`
- Topic Tags: `billing`, `pricing`, `invoices`, `billing-details`, `cost-explorer`, `cost-analysis`, `csv-export`, `organization-roles`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0408_80fd8a96c8`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-billing.md#tidb-cloud-billing`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9c4f82ed7c9fea31ee6156c13624fdefa69ececeb0cfb765805d0d8041bac7ea`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing#tidb-cloud-billing
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-billing.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs TiDB Cloud billing information about invoices, bills, billing details, CSV export, or the Cost Explorer in the Billing page.
- Retrieval Keywords: TiDB Cloud Billing, Invoices, Billing details, Bills tab, Cost Explorer, Billing page, Organization Owner, Organization Billing Manager, invoice quota $500, monthly invoice, Stripe, AWS Marketplace, Azure Marketplace, Google Cloud Marketplace, download invoices, billing summary by project and by service, usage details, CSV format, daily usage details, rounded off to the 2nd decimal place, accurate to the 6th decimal place, group by service project cluster region product type charge type, Cost Graph, Cost Breakdown
- Follow-up Guidance: The content also gives the TiDB Cloud console navigation to the Billing page and describes what the Invoices, Bills, and Cost Explorer tabs display.
- Classification Note: This is classified as cloud operation content because it explains billing console usage, invoice handling, billing details, and cost analysis for a TiDB Cloud organization.

## Official Source Content

# TiDB Cloud Billing

> **Note:**
>
> [TiDB Cloud Serverless clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) are free until May 31, 2023, with a 100% discount off. After that, usage beyond the [free quota](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#usage-quota) will be charged.

TiDB Cloud charges according to the resources that you consume. You can visit the following pages to get more information about the pricing.

- [TiDB Cloud Serverless Pricing Details](https://www.pingcap.com/tidb-serverless-pricing-details/)
- [TiDB Cloud Dedicated Pricing Details](https://www.pingcap.com/tidb-dedicated-pricing-details/)
## Invoices

If you are in the `Organization Owner` or `Organization Billing Manager` role of your organization, you can manage the invoice information of TiDB Cloud. Otherwise, skip this section.

After you set up the payment method, TiDB Cloud will generate an invoice once your cost reaches a quota, which is $500 by default. If you want to raise the quota or receive one invoice per month, you can [contact our sales](https://www.pingcap.com/contact-us/).

> **Note:**
>
> If you sign up for TiDB Cloud through [AWS Marketplace](https://aws.amazon.com/marketplace), [Azure Marketplace](https://azuremarketplace.microsoft.com/), or [Google Cloud Marketplace](https://console.cloud.google.com/marketplace), you can pay through your AWS account, Azure account, or Google Cloud account directly but cannot add payment methods or download invoices in the TiDB Cloud console.

After you contact our sales for receiving an invoice on a monthly basis, TiDB Cloud will generate the invoice for the previous month at the beginning of each month.

Invoice costs include TiDB cluster usage consumption, discounts, backup storage costs, support service cost, credit consumption, and data transmission costs in your organization.

For each monthly invoice:

- TiDB Cloud provides the invoice to you on the ninth of each month. From the first to the ninth day, you cannot view the last month's cost details, but can obtain the cluster usage information of this month via the billing console.
- The default method for paying invoices is credit card deduction. If you want to use other payment methods, please send a ticket request to let us know.
- You can view the summary and details of charges for the current month and the previous month.

> **Note:**
>
> All billing deductions will be completed through the third-party platform Stripe.

To view the list of invoices, perform the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target organization using the combo box in the upper-left corner.

2. In the left navigation pane, click **Billing**.

3. On the **Billing** page, click the **Invoices** tab.
## Billing details

If you are in the `Organization Owner` or `Organization Billing Manager` role of your organization, you can view and export the billing details of TiDB Cloud. Otherwise, skip this section.

After setting the payment method, TiDB Cloud will generate the invoice and billing details of the historical months, and generate the bill details of the current month at the beginning of each month. The billing details include your organization's TiDB cluster usage consumption, discounts, backup storage costs, data transmission costs, support service cost, credit consumption, and project splitting information.

> **Note:**
>
> Due to delays and other reasons, the billing details of the current month are for reference only, not guaranteed to be accurate. TiDB Cloud ensures the accuracy of historical bills so that you can perform cost accounting and meet other needs.

To view the billing details, perform the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target organization using the combo box in the upper-left corner.

2. In the left navigation pane, click **Billing**.

On the **Billing** page, the **Bills** tab is displayed by default.

The **Bills** tab shows the billing summary by project and by service. You can also see the usage details and download the data in CSV format.

> **Note:**
>
> The total amount in the monthly bill might differ from that in the daily usage details due to differences in precision:
>
> - The total amount in the monthly bill is rounded off to the 2nd decimal place.
> - The total amount in the daily usage details is accurate to the 6th decimal place.
## Cost explorer

If you are in the `Organization Owner` or `Organization Billing Manager` role of your organization, you can view and analyze the usage costs of TiDB Cloud. Otherwise, skip this section.

To analyze and customize your cost reports of your organization, perform the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target organization using the combo box in the upper-left corner.
2. In the left navigation pane, click **Billing**.
3. On the **Billing** page, click the **Cost Explorer** tab.
4. On the **Cost Explorer** tab, expand the **Filter** section in the upper-right corner to customize your report. You can set the time range, select a grouping option (such as by service, project, cluster, region, product type, and charge type), and apply filters by selecting specific services, projects, clusters, or regions. The cost explorer will display you with the following information:

    - **Cost Graph**: visualizes the cost trends over the selected time range. You can switch between **Monthly**, **Daily**, and **Total** views.
    - **Cost Breakdown**: displays a detailed breakdown of your costs according to the selected grouping option. For further analysis, you can download the data in CSV format.
