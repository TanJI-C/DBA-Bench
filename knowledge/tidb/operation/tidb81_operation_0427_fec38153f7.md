# TiDB Cloud support access, ticket management, and support plan changes

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-support.md`
- Source Title: `TiDB Cloud Support`
- Source Heading Path: `TiDB Cloud Support | TiDB Cloud Support > Access PingCAP Help Center | TiDB Cloud Support > Create an account or billing support ticket | TiDB Cloud Support > Create a technical support ticket | TiDB Cloud Support > View support tickets | TiDB Cloud Support > Check or upgrade your support plan | TiDB Cloud Support > Downgrade your support plan`
- Source Line Ranges: `5-121`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`, `tidb`, `tikv`, `pd`, `tiflash`
- Topic Tags: `support`, `help-center`, `tickets`, `billing`, `technical-support`, `severity`, `support-plans`, `upgrade`, `downgrade`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0427_fec38153f7`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-support.md#tidb-cloud-support`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `69825a38bbe6c36dbde33727e7bc2fc1c835c09b57d2ef5bc1feb50954ecb90a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support#tidb-cloud-support
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-support.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about accessing PingCAP Help Center from TiDB Cloud, creating or viewing support tickets, understanding ticket fields and severity, or checking, upgrading, or downgrading a TiDB Cloud support plan.
- Retrieval Keywords: TiDB Cloud Support, PingCAP Help Center, Request Support, Create Ticket, Get Support, TiDB Cloud Account/Billing Support, TiDB Cloud Technical Support, Submit a request, Severity, S1, S2, S3, S4, Components, TiDB, TiKV, PD, TiFlash, Affects versions, Requests, Check or upgrade your support plan, Downgrade your support plan, Developer, Enterprise, Premium, Basic, Contact Sales, Add Credit Card and Upgrade
- Follow-up Guidance: The content also states how to access the Help Center from the TiDB Cloud console, how to view historical tickets through Requests, and that Technical Support is only available for customers subscribed to Developer, Enterprise, or Premium support plans.
- Classification Note: This is classified as a cloud operation topic because the content describes TiDB Cloud support access paths, ticket management workflows, severity and component fields, and support plan changes in the TiDB Cloud console.

## Official Source Content

# TiDB Cloud Support

TiDB Cloud offers tiered support plan offerings tailored to meet customers' needs. For more information, see [Connected Care Details](https://docs.pingcap.com/tidb/stable/tidb-cloud/connected-care-detail).

> **Note:**
>
> To request a [Proof of Concept (PoC)](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-poc), a demo, or free trial credits, click **?** in the lower-right corner of the [TiDB Cloud console](https://tidbcloud.com/), and click **Contact Sales**.
## Access PingCAP Help Center

The [PingCAP Help Center](https://tidb.support.pingcap.com/servicedesk/customer/portals) is the central hub for TiDB Cloud users to access support services and manage support tickets.

You can access the PingCAP Help Center via <https://tidb.support.pingcap.com/servicedesk/customer/portals> directly, or through the [TiDB Cloud console](https://tidbcloud.com/) in the following ways:

- Click **?** in the lower-right corner of the [TiDB Cloud console](https://tidbcloud.com/), and then click **Request Support**.
- Click **Support** in the lower-left corner of [TiDB Cloud console](https://tidbcloud.com/), and then click **Create Ticket**.
- On the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, click **...** in the row of your cluster, and then select **Get Support**.
- On your cluster overview page, click **...** in the upper-right corner, and then select **Get Support**.
## Create an account or billing support ticket

To create a support ticket about account or billing issues, take the following steps:

1. Log in to the [PingCAP Help Center](https://tidb.support.pingcap.com/servicedesk/customer/portals), and then click [TiDB Cloud Account/Billing Support](https://tidb.support.pingcap.com/servicedesk/customer/portal/16).
2. Click **Submit a request**.
3. Fill in the following fields:

    - **Summary**: provide a brief summary of your question.
    - **TiDB Cloud Org**: select the relevant TiDB Cloud organization, if applicable.
    - **TiDB Cloud Cluster**: select the relevant TiDB Cloud cluster, if applicable.
    - **Description**: provide the details about the issue.
    - **Severity**: estimate the business impact of the issue and choose the proper severity for it. (S1 is not applicable to billing or account issues.)

4. Click **Submit**.
## Create a technical support ticket

To create a support ticket about technical issues, take the following steps:

1. Log in to the [PingCAP Help Center](https://tidb.support.pingcap.com/servicedesk/customer/portals), and then click [TiDB Cloud Technical Support](https://tidb.support.pingcap.com/servicedesk/customer/portal/6).

    > **Note:**
    >
    > The [TiDB Cloud Technical Support](https://tidb.support.pingcap.com/servicedesk/customer/portal/6) entry is only available for customers subscribed to **Developer**, **Enterprise**, or **Premium** [support plans](https://docs.pingcap.com/tidb/stable/tidb-cloud/connected-care-detail).

2. Click **Submit a request**.

3. Fill in the following fields:

    - **Summary**: provide a brief summary of your question.
    - **TiDB Cloud Org**: select the relevant TiDB Cloud organization for the issue.
    - **TiDB Cloud Cluster**: select the relevant TiDB Cloud cluster, if applicable.
    - **Environment**: select the corresponding environment in which you use the TiDB Cloud cluster.
    - **Description**: describe the issue you encountered as detailed as possible. For example, share the exact timestamp when you encountered the issue, attach the detailed error messages and call stack of the issue, and add your troubleshooting or analysis of the issue.
    - **Severity**: estimate the business impact of the issue and choose the proper severity for it.

        | Severity | Description |
        | --- | --- |
        | S1 | Complete loss of production environmental functionality |
        | S2 | High impact on operations in production environments |
        | S3 | Non-critical database usage issues in production or non-production environments |
        | S4 | General question on how a particular feature or function performs or should be configured. An issue that has minimal impact on business and can be tolerated for a reasonable period. |

    - **Components**: select the relevant TiDB Cloud component to report the issue for, such as TiDB, TiKV, PD, or TiFlash.
    - **Affects versions**: specify the TiDB Cloud cluster version related to the issue.

4. Click **Submit**.
## View support tickets

To view all the historical support tickets, log in to the [PingCAP Help Center](https://tidb.support.pingcap.com/servicedesk/customer/portals), click your avatar in the upper-right corner, and then click **Requests**.
## Check or upgrade your support plan

TiDB Cloud offers a free basic support plan by default. For extended services, you can upgrade to a paid plan.

To check or upgrade your support plan, perform the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com/), click **Support** in the lower-left corner.

    On this page, you can find your current plan. By default, the **Basic** free plan is selected.

2. Choose your desired support plan.

    <div label="Upgrade to Developer or Enterprise">

    To upgrade to **Developer** or **Enterprise**:

    1. Click **Upgrade** in the **Developer** or **Enterprise** pane. An **Upgrade to Developer Plan** or **Upgrade to Enterprise Plan** page is displayed.
    2. Check the corresponding support service information on the page. For a complete version of each support plan, see [Connected Care Details](https://docs.pingcap.com/tidb/stable/tidb-cloud/connected-care-detail).
    3. Click **Add Credit Card and Upgrade**, and then fill in the **Credit Card** details.

        For more information about billing, see [TiDB Cloud Payment Method](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing#payment-method).

    4. Click **Save Card** in the lower-right corner of the page.

    After the payment is finished, you have upgraded your plan to **Standard** or **Enterprise**.

    </div>
    <div label="Upgrade to Premium">

    To upgrade your plan to **Premium**:

    1. Click **Contact Sales** in the **Premium** pane. A **Contact Us** page is displayed.
    2. Fill in and submit your contact information on the page. Then, the support team will contact you and help you with your subscription.

    </div>
## Downgrade your support plan

To downgrade your support plan, perform the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com/), click **Support** in the lower-left corner.
2. Choose the support plan you want to switch to, and then click **Downgrade**.
