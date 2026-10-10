# Manage payment methods and contracts

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-billing.md`
- Source Title: `TiDB Cloud Billing`
- Source Heading Path: `TiDB Cloud Billing > Payment method | TiDB Cloud Billing > Contract`
- Source Line Ranges: `158-208`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dashboard`
- Topic Tags: `billing`, `payment-methods`, `credit-cards`, `contracts`, `organization-roles`, `stripe`, `marketplace`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0410_3a9b957556`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-billing.md#payment-method`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0896a6c00ee90d0e9d8e6d377be9bbe437f5fd7e4d6338cfe1241c89d44223e4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing#payment-method
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-billing.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs TiDB Cloud billing details about managing payment methods, adding or setting a default credit card, marketplace payment limitations, or reviewing a contract in the Billing console.
- Retrieval Keywords: Organization Owner, Organization Billing Manager, Payment Method, Add Credit Card, Add a New Card, Save Card, default credit card, Billing profile, primary business address, tax calculation, Stripe, AWS Marketplace, Azure Marketplace, Google Cloud Marketplace, cannot add payment methods, cannot download invoices, Contract, Billing page, TiDB Cloud console
- Follow-up Guidance: It also states that marketplace sign-up users can pay through their AWS, Azure, or Google Cloud account directly but cannot add payment methods or download invoices in the TiDB Cloud console.
- Classification Note: This is classified as an operation chunk because the content describes role-based billing console tasks for payment methods and contract management in TiDB Cloud.

## Official Source Content

## Payment method

If you are in the `Organization Owner` or `Organization Billing Manager` role of your organization, you can manage the payment information of TiDB Cloud. Otherwise, skip this section.

> **Note:**
>
> If you sign up for TiDB Cloud through [AWS Marketplace](https://aws.amazon.com/marketplace), [Azure Marketplace](https://azuremarketplace.microsoft.com/), or [Google Cloud Marketplace](https://console.cloud.google.com/marketplace), you can pay through your AWS account, Azure account, or Google Cloud account directly but cannot add payment methods or download invoices in the TiDB Cloud console.

The fee is deducted from a bound credit card according to your cluster usage. To add a valid credit card, you can use either of the following methods:

- When you are creating a TiDB Cloud Dedicated cluster:

    1. On the **Create Cluster** page, click **Add Credit Card**.
    2. In the **Add a Card** dialog, fill in the card information and billing address.
    3. Click **Save Card**.

- Anytime in the billing console:

    1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target organization using the combo box in the upper-left corner.
    2. In the left navigation pane, click **Billing**.
    3. On the **Billing** page, click the **Payment Method** tab, and then click **Add a New Card**.
    4. Fill in the credit card information and credit card address, and then click **Save Card**.

        If you do not specify a primary business address in [**Billing profile**](#billing-profile), the credit card address will be used as your primary business address for tax calculation. You can update your primary business address in **Billing profile** anytime.

> **Note:**
>
> To ensure the security of credit card sensitive data, TiDB Cloud does not save any customer credit card information and saves them in the third-party payment platform Stripe. All billing deductions are completed through Stripe.

You can bind multiple credit cards, and set one of them as the default credit card in the payment method of the billing console. After setting, subsequent billings will be automatically deducted from the default credit card.

To set the default credit card, perform the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target organization using the combo box in the upper-left corner.
2. In the left navigation pane, click **Billing**.
3. On the **Billing** page, click the **Payment Method** tab.
4. Select a credit card in the credit card list, and then click **Yes** when you are prompted to set it as the default credit card.
## Contract

If you are in the `Organization Owner` or `Organization Billing Manager` role of your organization, you can manage your customized TiDB Cloud subscriptions in the TiDB Cloud console to meet compliance requirements. Otherwise, skip this section.

If you have agreed with our sales on a contract and received an email to review and accept the contract online, you can do the following:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target organization using the combo box in the upper-left corner.
2. In the left navigation pane, click **Billing**.
3. On the **Billing** page, click the **Contract** tab.
4. On the **Contract** tab, locate the contract you want to review, and then click **...** in the row of the contract.

To learn more about contracts, feel free to [contact our sales](https://www.pingcap.com/contact-us/).
