# Lark support ticket creation and update subscription

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/connected-lark-ticket-creation.md`
- Source Title: `Create Tickets and Subscribe to Ticket Updates via Lark`
- Source Heading Path: `Create Tickets and Subscribe to Ticket Updates via Lark | Create Tickets and Subscribe to Ticket Updates via Lark > Create a support ticket | Create Tickets and Subscribe to Ticket Updates via Lark > Subscribe to ticket updates | Create Tickets and Subscribe to Ticket Updates via Lark > FAQs | Create Tickets and Subscribe to Ticket Updates via Lark > Contact support`
- Source Line Ranges: `5-44`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `support`, `lark`, `ticket-creation`, `ticket-updates`, `help-center`, `enterprise-plan`, `contact`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0297_68fc0a2d63`
- Source ID: `tidb-docs-8.1:tidb-cloud/connected-lark-ticket-creation.md#create-tickets-and-subscribe-to-ticket-updates-via-lark`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `08e1a7c2856e37a78f280aabd61b37a4ad1dd0ca1acd612e6ae20611f47b11fa`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/connected-lark-ticket-creation#create-tickets-and-subscribe-to-ticket-updates-via-lark
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/connected-lark-ticket-creation.md

## Retrieval Guidance

- Use When: Use this when the user asks how to create a TiDB Cloud support ticket in Lark, receive ticket updates in Lark, check ticket status in the PingCAP Help Center, or asks about availability of the PingCAP Support Bot for Enterprise support plan customers.
- Retrieval Keywords: PingCAP Support Bot, Lark, PingCAP Support Group, Create a support ticket, Subscribe to ticket updates, PingCAP Help Center, Enterprise support plan, Reporter field, support@pingcap.com, Technical Account Manager, TAM, ticket link, ticket status, historical tickets
- Follow-up Guidance: The content also states that the Lark ticket support feature is available upon request and provides support@pingcap.com and a Technical Account Manager as contacts.
- Classification Note: This is classified as a cloud operation topic because it describes operational support workflows in TiDB Cloud using Lark, the PingCAP Help Center, and support contact channels.

## Official Source Content

# Create Tickets and Subscribe to Ticket Updates via Lark

For customers subscribed to the **Enterprise** [support plan](https://docs.pingcap.com/tidb/stable/tidb-cloud/connected-care-detail), TiDB Cloud provides a ticket bot called **PingCAP Support Bot** in [Lark](https://www.larksuite.com/). This bot helps you create support tickets and receive updates directly from the support ticket system.

> **Note:**
>
> The ticket support feature for Lark is available upon request. If you are interested in trying this feature, contact TiDB Cloud support at <a href="mailto:support@pingcap.com">support@pingcap.com</a> or reach out to your Technical Account Manager (TAM).
## Create a support ticket

1. In the **PingCAP Support Group** on Lark, mention `@PingCAP Support Bot` and describe the problem in a message. Then, the bot will send you an ephemeral card message that is visible only to you.

    ![lark-ticket-creation-1](/media/tidb-cloud/connected-lark-ticket-creation-1.png)

2. In the card, enter the email address you use for the [TiDB Cloud console](https://tidbcloud.com/) in the **Reporter** field, fill in the other fields as needed, and then click **Submit** to create the ticket.

    ![lark-ticket-creation-2](/media/tidb-cloud/connected-lark-ticket-creation-2.png)

After the ticket is created, the bot replies with the ticket link in the thread. You can click the link to view ticket details in the [PingCAP Help Center](https://tidb.support.pingcap.com/servicedesk/customer/portals).

![lark-ticket-creation-3](/media/tidb-cloud/connected-lark-ticket-creation-3.png)

![lark-ticket-creation-4](/media/tidb-cloud/connected-lark-ticket-creation-4.png)
## Subscribe to ticket updates

After you [create a support ticket](#create-a-support-ticket), you can receive ticket updates directly in the Lark **PingCAP Support Group**. When a support engineer responds to your ticket, the bot posts an update message in the group. The message includes the ticket title, a link to the ticket, and the latest comment.

![lark-ticket-creation-5](/media/tidb-cloud/connected-lark-ticket-creation-5.png)
## FAQs

- How can I check the status of my ticket?

    Log in to the [PingCAP Help Center](https://tidb.support.pingcap.com/servicedesk/customer/user/requests) with the email address used to create the ticket. You can view all historical tickets and their status for the current account.
## Contact support

For help or questions, please contact our support team at <a href="mailto:support@pingcap.com">support@pingcap.com</a>.
