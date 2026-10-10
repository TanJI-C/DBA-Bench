# Slack support ticket interaction and support contact

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/connected-slack-ticket-interaction.md`
- Source Title: `Interact with Support Tickets via Slack`
- Source Heading Path: `Interact with Support Tickets via Slack | Interact with Support Tickets via Slack > Interact with support tickets | Interact with Support Tickets via Slack > FAQs | Interact with Support Tickets via Slack > Contact support`
- Source Line Ranges: `5-52`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `slack`, `support-tickets`, `ticket-creation`, `ticket-replies`, `two-way-sync`, `help-center`, `premium-support`, `contact-support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0300_95de4ab6d5`
- Source ID: `tidb-docs-8.1:tidb-cloud/connected-slack-ticket-interaction.md#interact-with-support-tickets-via-slack`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7bf8ea9982a1fc69f66ef3eebd4f423e9ea76ea9232a53dd83405a9e6ea6bd44`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/connected-slack-ticket-interaction#interact-with-support-tickets-via-slack
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/connected-slack-ticket-interaction.md

## Retrieval Guidance

- Use When: Use this chunk when answering how TiDB Cloud Premium support customers interact with support tickets in Slack using PingCAP Support Bot, including ticket creation, thread replies, two-way synchronization, ticket status lookup, and support contact details.
- Retrieval Keywords: PingCAP Support Bot, Interact with Support Tickets via Slack, Premium support plan, Slack support channel, Raise request, Create, two-way information synchronization, support engineer's comments, message thread, ticket link, PingCAP Help Center, support@pingcap.com, Technical Account Manager, TAM, check the status of my ticket
- Follow-up Guidance: It also states that the Slack ticket support feature is available upon request and that users can check ticket status in the PingCAP Help Center with the email address used to create the ticket.
- Classification Note: The content is classified as a cloud operation topic because it describes operational interaction with TiDB Cloud support tickets through Slack and support contact channels.

## Official Source Content

# Interact with Support Tickets via Slack

For customers subscribed to the **Premium** [support plan](https://docs.pingcap.com/tidb/stable/tidb-cloud/connected-care-detail), TiDB Cloud provides a ticket bot called **PingCAP Support Bot** in [Slack](https://slack.com/), to support more comprehensive interaction and management of support tickets.

> **Note:**
>
> The ticket support feature for Slack is available upon request. If you are interested in trying this feature, contact TiDB Cloud support at <a href="mailto:support@pingcap.com">support@pingcap.com</a> or reach out to your Technical Account Manager (TAM).

You can use **PingCAP Support Bot** to create a support ticket in Slack:

![Create a support ticket in Slack](/media/tidb-cloud/connected-slack-ticket-interaction-creation.gif)

You can also reply to the support ticket directly in Slack:

![Reply to a support ticket in Slack](/media/tidb-cloud/connected-slack-ticket-interaction-reply.gif)
## Interact with support tickets

In the Slack support channel, you only need to mention **PingCAP Support Bot** and describe the problem in a message. Then, the bot will send you a message with a **Raise request** button.

![slack-ticket-interaction-1](/media/tidb-cloud/connected-slack-ticket-interaction-1.png)

Click **Raise request** to open a form, fill it out according to the problem, and then click **Create** to submit the ticket.

![slack-ticket-interaction-2](/media/tidb-cloud/connected-slack-ticket-interaction-2.png)

After submission, the bot will send a confirmation message in the thread, which includes the ticket link.

![slack-ticket-interaction-3](/media/tidb-cloud/connected-slack-ticket-interaction-3.png)

For customers subscribed to the **Premium** [support plan](https://docs.pingcap.com/tidb/stable/tidb-cloud/connected-care-detail), two-way information synchronization is supported between Slack and the ticket system.

The support engineer's comments on the ticket will be synchronized to the Slack message thread, and users do not need to jump to the support portal to view them. Users can reply directly in this message thread, and these replies will be synchronized to the ticket system.

In this way, customers subscribed to the **Premium** support plan can quickly create, respond, and manage tickets without leaving Slack.

![slack-ticket-interaction-4](/media/tidb-cloud/connected-slack-ticket-interaction-4.png)
## FAQs

- How can I check the status of my ticket?

    Log in to the [PingCAP Help Center](https://tidb.support.pingcap.com/servicedesk/customer/user/requests) with the email address used to create the ticket. You can view all historical tickets and their status for the current account.
## Contact support

For help or questions, please contact our support team at <a href="mailto:support@pingcap.com">support@pingcap.com</a>.
