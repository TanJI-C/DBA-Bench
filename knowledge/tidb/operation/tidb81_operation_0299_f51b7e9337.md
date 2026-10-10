# Slack support ticket creation and ticket update subscription

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/connected-slack-ticket-creation.md`
- Source Title: `Create Tickets and Subscribe to Ticket Updates in Slack`
- Source Heading Path: `Create Tickets and Subscribe to Ticket Updates in Slack | Create Tickets and Subscribe to Ticket Updates in Slack > Create a support ticket | Create Tickets and Subscribe to Ticket Updates in Slack > Subscribe to ticket updates | Create Tickets and Subscribe to Ticket Updates in Slack > FAQs | Create Tickets and Subscribe to Ticket Updates in Slack > Contact support`
- Source Line Ranges: `5-44`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `slack`, `support`, `ticketing`, `subscription`, `help-center`, `enterprise-plan`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0299_f51b7e9337`
- Source ID: `tidb-docs-8.1:tidb-cloud/connected-slack-ticket-creation.md#create-tickets-and-subscribe-to-ticket-updates-in-slack`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `88df7183218597419e872846850c6360292fa1149c8e5a5056ff7322b76833e6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/connected-slack-ticket-creation#create-tickets-and-subscribe-to-ticket-updates-in-slack
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/connected-slack-ticket-creation.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about creating a TiDB Cloud support ticket in Slack, subscribing to ticket updates in Slack, checking ticket status, or contacting support for the Slack ticket bot.
- Retrieval Keywords: PingCAP Support Bot, Slack support channel, Raise request, Create a support ticket, Subscribe to ticket updates, Enterprise support plan, PingCAP Help Center, ticket link, support@pingcap.com, Technical Account Manager, TAM, ticket update message
- Follow-up Guidance: It also states that the Slack ticket support feature is available upon request and that ticket status can be viewed by logging in to the PingCAP Help Center with the email address used to create the ticket.
- Classification Note: The classification is operation for the cloud component because the content describes how Enterprise plan customers use Slack and the PingCAP Help Center to create support tickets and receive ticket update subscriptions.

## Official Source Content

# Create Tickets and Subscribe to Ticket Updates in Slack

For customers subscribed to the **Enterprise** [support plan](https://docs.pingcap.com/tidb/stable/tidb-cloud/connected-care-detail), TiDB Cloud provides a ticket bot called **PingCAP Support Bot** in [Slack](https://slack.com/), to support quick ticket creation.

> **Note:**
>
> The ticket support feature for Slack is available upon request. If you are interested in trying this feature, contact TiDB Cloud support at <a href="mailto:support@pingcap.com">support@pingcap.com</a> or reach out to your Technical Account Manager (TAM).
## Create a support ticket

In the Slack support channel, you only need to mention **PingCAP Support Bot** and describe the problem in a message. Then, the ticket bot will send you a message with a **Raise request** button.

![slack-ticket-creation-1](/media/tidb-cloud/connected-slack-ticket-creation-1.png)

Click **Raise request** to open a form, fill it out according to the problem, and then click **Create** to submit the ticket.

![slack-ticket-creation-2](/media/tidb-cloud/connected-slack-ticket-creation-2.png)

After successfully creating the ticket, the bot will reply with the ticket link. You can click the link to view the ticket details in the [PingCAP Help Center](https://tidb.support.pingcap.com/servicedesk/customer/portals).

![slack-ticket-creation-3](/media/tidb-cloud/connected-slack-ticket-creation-3.png)

![slack-ticket-creation-4](/media/tidb-cloud/connected-slack-ticket-creation-4.png)
## Subscribe to ticket updates

The **Enterprise** support plan supports subscriptions to ticket updates in Slack. When a support engineer responds to a ticket, a ticket update message will appear in the Slack channel. The message includes information such as the ticket title, ticket link, and last comment content.

![slack-ticket-creation-5](/media/tidb-cloud/connected-slack-ticket-creation-5.png)
## FAQs

- How can I check the status of my ticket?

    Log in to the [PingCAP Help Center](https://tidb.support.pingcap.com/servicedesk/customer/user/requests) with the email address used to create the ticket. You can view all historical tickets and their status for the current account.
## Contact support

For help or questions, please contact our support team at <a href="mailto:support@pingcap.com">support@pingcap.com</a>.
