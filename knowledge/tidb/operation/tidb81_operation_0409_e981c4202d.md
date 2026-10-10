# Billing profile, credits, and discounts

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-billing.md`
- Source Title: `TiDB Cloud Billing`
- Source Heading Path: `TiDB Cloud Billing > Billing profile | TiDB Cloud Billing > Billing profile > Company name (optional) | TiDB Cloud Billing > Billing profile > Billing email (optional) | TiDB Cloud Billing > Billing profile > Primary business address | TiDB Cloud Billing > Billing profile > Business tax ID (optional) | TiDB Cloud Billing > Credits | TiDB Cloud Billing > Discounts`
- Source Line Ranges: `90-157`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dashboard`
- Topic Tags: `billing-profile`, `tax`, `vat`, `gst`, `billing-email`, `company-name`, `business-address`, `credits`, `discounts`, `payment-method`, `poc`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0409_e981c4202d`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-billing.md#billing-profile`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4a457a90c1b2a47b1be841c49052bb297aca0baafcfa5dfd8ebda59533a08716`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing#billing-profile
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-billing.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about the TiDB Cloud billing profile fields, credits usage and expiration behavior, or viewing discounts in the Billing page.
- Retrieval Keywords: Billing profile, Billing Profile tab, Company name, Billing email, Primary business address, Business tax ID, VAT/GST, tax calculation, invoices and other billing-related notifications, Credits, PoC, Proof of Concept, one credit is equivalent to one U.S. dollar, available credits, current usage, unused credits, support plan fees, credits expired, cannot create a new cluster, existing clusters will be recycled, backups will be recycled, payment method, Discounts, discount percentage, discount start and end date, Organization Owner, Organization Billing Manager
- Follow-up Guidance: The content also includes the TiDB Cloud console steps to open the Billing Profile, Credits, and Discounts tabs for the target organization.
- Classification Note: This is classified as cloud operation content because it covers billing profile management, credit and payment behavior, and discount visibility in the TiDB Cloud billing console.

## Official Source Content

## Billing profile

Paid organizations can create a billing profile. Information in this profile will be used to determine the tax calculation.

To view or update the billing profile of your organization, perform the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target organization using the combo box in the upper-left corner.
2. In the left navigation pane, click **Billing**.
3. On the **Billing** page, click the **Billing Profile** tab.

There are four fields in the billing profile.
### Company name (optional)

If this field is specified, this name will appear on invoices instead of your organization name.
### Billing email (optional)

If this field is specified, invoices and other billing-related notifications will be sent to this email address.
### Primary business address

This is the address of the company that purchases TiDB Cloud services. It is used to calculate any applicable taxes.
### Business tax ID (optional)

If your business is registered for VAT/GST, fill in a valid VAT/GST ID. By providing this information, we will exempt you from charging VAT/GST if applicable. This is important for businesses operating in regions where VAT/GST registration allows for certain tax exemptions or refunds.
## Credits

TiDB Cloud offers a certain number of credits for Proof of Concept (PoC) users. One credit is equivalent to one U.S. dollar. You can use credits to pay TiDB cluster fees before the credits become expired.

> **Tip:**
>
> To apply for a PoC, see [Perform a Proof of Concept (PoC) with TiDB Cloud](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-poc).

The detailed information of your credits is available on the **Credits** tab, including your total credits, available credits, current usage, and the status.

To view the credit information, perform the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target organization using the combo box in the upper-left corner.
2. In the left navigation pane, click **Billing**.
3. On the **Billing** page, click the **Credits** tab.

> **Note:**
>
> - After you set up your payment method, the cluster fees are first deducted from your unused credits, then from your payment method.
> - Credits cannot be used to pay the support plan fees.

> **Warning:**
>
> During a PoC process:
>
> - If all your credits become expired before you add a payment method, you cannot create a new cluster. After 3 days, all your existing clusters will be recycled. After 7 days, all your backups will be recycled. To resume the process, you can add a payment method.
> - If all your credits become expired after you add a payment method, your PoC process goes on, and fees are deducted from your payment method.
## Discounts

If you are in the `Organization Owner` or `Organization Billing Manager` role of your organization, you can view the discount information of TiDB Cloud on the **Discounts** tab. Otherwise, skip this section.

The discount information includes all discounts that you have received, the status, the discount percentage, and the discount start and end date.

To view the discount information, perform the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target organization using the combo box in the upper-left corner.
2. In the left navigation pane, click **Billing**.
3. On the **Billing** page, click the **Discounts** tab.
