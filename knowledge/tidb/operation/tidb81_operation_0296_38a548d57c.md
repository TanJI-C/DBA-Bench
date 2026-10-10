# Connected Care feature differences, transition schedule, and support plan changes

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/connected-care-overview.md`
- Source Title: `Connected Care Overview`
- Source Heading Path: `Connected Care Overview > Differences between legacy support services and Connected Care support services | Connected Care Overview > Transition to Connected Care | Connected Care Overview > FAQs | Connected Care Overview > FAQs > How do I check or make changes to my current support plan?`
- Source Line Ranges: `44-95`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `legacy-support`, `feature-differences`, `transition`, `shutdown-dates`, `automatic-transition`, `support-page`, `plan-upgrade`, `premium-plan`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0296_38a548d57c`
- Source ID: `tidb-docs-8.1:tidb-cloud/connected-care-overview.md#differences-between-legacy-support-services-and-connected-care-support-services`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6e3c7c6e5b1a912461300d8ecd3248db1a1be2352f4186cdbc14a226a5de8545`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/connected-care-overview#differences-between-legacy-support-services-and-connected-care-support-services
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/connected-care-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about differences between legacy support services and Connected Care, shutdown dates for legacy plans, automatic transition behavior, or how to view or change the current support plan in TiDB Cloud.
- Retrieval Keywords: Differences between legacy support services and Connected Care support services, Transition to Connected Care, legacy support plans, shutdown date, Legacy Basic plan, Legacy Standard plan, Legacy Enterprise, Legacy Premium, Feb 17, 2025, Jan 15, 2026, automatically transitioned to the Basic support plan, Connected: Clinic service, Connected: AI chat in IM, IM subscription for TiDB Cloud alerts, IM ticket creation and update subscription, IM interaction for support tickets, How do I check or make changes to my current support plan?, TiDB Cloud console, Support page, CURRENT tag, Premium support plan, contact sales
- Follow-up Guidance: The source says to click Support in the lower-left corner of the TiDB Cloud console to see the Support page with the current plan marked by a CURRENT tag, and it states that upgrading to the Premium plan requires contacting sales.
- Classification Note: This is operation content because it explains transition behavior, legacy plan shutdown schedules, and the console path for checking or changing a support plan.

## Official Source Content

## Differences between legacy support services and Connected Care support services

The support plans in the Connected Care services introduce a completely new set of features as follows:

- Connected: Clinic service

    This feature offers an advanced monitoring and diagnostic service, Clinic, designed to help you quickly identify performance issues, optimize your database, and enhance overall performance with detailed analysis and actionable insights. For more information, see [Connected: Clinic Service](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-clinic).

- Connected: AI chat in IM

    This feature enables you to chat with an AI assistant through an instant message (IM) tool to receive immediate answers to your questions. For more information, see [Connected: AI chat in IM](https://docs.pingcap.com/tidb/stable/tidb-cloud/connected-ai-chat-in-im).

- Connected: IM subscription for TiDB Cloud alerts

    This feature provides you with an easy way to subscribe to alert notifications via an IM tool, keeping you informed about critical updates. For more information, see [Subscribe via Slack](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-alert-slack) and [Subscribe via Zoom](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-alert-zoom).

- Connected: IM ticket creation and update subscription

    This feature enables you to create a support ticket and subscribe to your support ticket updates through an IM tool. For more information, see [Create Tickets and Subscribe to Ticket Updates via Slack](https://docs.pingcap.com/tidb/stable/tidb-cloud/connected-slack-ticket-creation) and [Create Tickets and Subscribe to Ticket Updates via Lark](https://docs.pingcap.com/tidb/stable/tidb-cloud/connected-lark-ticket-creation).

- Connected: IM interaction for support tickets

    This feature enables you to quickly create and interact with support tickets through an IM tool for streamlined communication. For more information, see [Interact with Support Tickets via Slack](https://docs.pingcap.com/tidb/stable/tidb-cloud/connected-slack-ticket-interaction) and [Interact with Support Tickets via Lark](https://docs.pingcap.com/tidb/stable/tidb-cloud/connected-lark-ticket-interaction).

With these new features, the Connected Care services offer you better connectivity, more personalized support, and cost-effective solutions for different customer needs.

- New **Enterprise** and **Premium** plans: connect customers with modern communication tools and advanced AI capabilities through advanced monitoring service in Clinic, IM subscription for TiDB Cloud alerts, IM subscription for ticket updates, AI chat in IM, and IM interaction for support tickets.

- New **Developer** plan: customers benefit from access to the same community and [TiDB.AI](https://tidb.ai/) assistance as the **Basic** plan, while also enjoying direct connections with unlimited access to technical support.

- New **Basic** plan: customers will be guided to join the active community channels, where they can engage with other community members and interact with [TiDB.AI](https://tidb.ai/) for technical assistance.
## Transition to Connected Care

The following table lists the shutdown schedules for the legacy support plans:

| Support plans                        | Shutdown date |
|:----------------------------------------|:--------------|
| Legacy **Basic** plan                     | Feb 17, 2025  |
| Legacy **Standard** plan                           | Feb 17, 2025  |
| Legacy **Enterprise** and **Premium** plans | Jan 15, 2026  |

Once a legacy support plan shuts down, TiDB Cloud will no longer support it. If you do not transition to any support plan in Connected Care by the relevant shutdown date, you will be automatically transitioned to the **Basic** support plan in Connected Care.
## FAQs
### How do I check or make changes to my current support plan?

In the [TiDB Cloud console](https://tidbcloud.com/), click **Support** in the lower-left corner. The **Support** page is displayed, with your current support plan highlighted with a **CURRENT** tag.

You can transition to a new support plan on the **Support** page, except for the **Premium** support plan. To upgrade to the **Premium** plan, please [contact sales](https://www.pingcap.com/contact-us).
