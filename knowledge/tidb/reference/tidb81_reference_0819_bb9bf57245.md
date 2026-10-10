# TiDB Cloud console notifications overview, types, list, and viewing

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/notifications.md`
- Source Title: `Notifications in the TiDB Cloud Console`
- Source Heading Path: `Notifications in the TiDB Cloud Console | Notifications in the TiDB Cloud Console > Notification types | Notifications in the TiDB Cloud Console > Notifications list | Notifications in the TiDB Cloud Console > View notifications`
- Source Line Ranges: `5-56`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `notifications`, `notification-types`, `billing`, `alerts`, `recipients`, `console`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0819_bb9bf57245`
- Source ID: `tidb-docs-8.1:tidb-cloud/notifications.md#notifications-in-the-tidb-cloud-console`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e6c74f2e1501373d33fbb4621f4bbcdd760cb86694c9b868dfb2b89eb33f8b37`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/notifications#notifications-in-the-tidb-cloud-console
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/notifications.md

## Retrieval Guidance

- Use When: Use this chunk when asking what notification types exist in the TiDB Cloud console, which events trigger listed notifications, who receives them, or where to view unread notifications.
- Retrieval Keywords: TiDB Cloud console notifications, Notification types, Informational notifications, Actionable notifications, Alert notifications, Billing notifications, Feedback notifications, Notifications list, View notifications, TiDB Cloud Serverless cluster creation, TiDB Cloud Serverless cluster deletion, TiDB Cloud Dedicated cluster creation, TiDB Cloud Dedicated cluster deletion, Organization Budget threshold alert, Project Budget threshold alert, Serverless cluster spending limit threshold alert, Credits update, Discount update, Marketplace update, Support plan update, All project members, Organization Owner, Organization Billing Manager, Organization Billing Viewer, Project Owner, Notification in the lower-left corner, unread notifications
- Follow-up Guidance: It states that you can view notifications by clicking Notification in the lower-left corner of the TiDB Cloud console, and a number next to Notification shows how many are unread.
- Classification Note: This is reference content because it enumerates notification categories, the available notification list with trigger events and recipients, and the console location for viewing notifications.

## Official Source Content

# Notifications in the TiDB Cloud Console

The [TiDB Cloud console](https://tidbcloud.com/) provides notifications to keep you informed about important updates, system messages, product changes, billing reminders, and other relevant information. These notifications help you stay up-to-date and take necessary actions without leaving the console.
## Notification types

You might receive different types of notifications in the TiDB Cloud console, such as:

- **Informational notifications**

    Provide helpful updates, such as feature usage tips, application changes, or reminders for upcoming events.

- **Actionable notifications**

   Prompt you to perform specific actions, such as adding a credit card.

- **Alert notifications**

    Notify you of critical issues or urgent events requiring immediate attention, such as system errors, security warnings, or important updates.

- **Billing notifications**

    Deliver updates about billing-related activities, such as credit and discount updates.

- **Feedback notifications**

    Request feedback on your experience with a feature, such as rating a recent interaction or completing a survey.
## Notifications list

The following table lists the notifications available in TiDB Cloud, along with their trigger events and recipients:

| Notification | Trigger event | Notification recipient |
| --- | --- | --- |
| TiDB Cloud Serverless cluster creation | A [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) cluster is created. | All project members |
| TiDB Cloud Serverless cluster deletion | A TiDB Cloud Serverless cluster is deleted. | All project members |
| TiDB Cloud Dedicated cluster creation | A [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) cluster is created. | All project members |
| TiDB Cloud Dedicated cluster deletion | A TiDB Cloud Dedicated cluster is deleted. | All project members |
| Organization Budget threshold alert | The organization [budget threshold](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-budget) is reached. | `Organization Owner`, `Organization Billing Manager`, and `Organization Billing Viewer` |
| Project Budget threshold alert | The project [budget threshold](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-budget) is reached. | `Organization Owner`, `Organization Billing Manager`, `Organization Billing Viewer`, and `Project Owner` |
| Serverless cluster spending limit threshold alert | The [spending limit threshold](https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-serverless-spend-limit) for TiDB Cloud Serverless clusters in the organization is reached. | `Organization Owner`, `Organization Billing Manager`, `Organization Billing Viewer`, and `Project Owner` |
| Credits update | [Credits](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing#credits) for the organization are applied, fully used, reclaimed, or expired. | `Organization Owner`, `Organization Billing Manager`, and `Organization Billing Viewer` |
| Discount update | [Discounts](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing#discounts) for the organization are applied, reclaimed, or expired. | `Organization Owner`, `Organization Billing Manager`, and `Organization Billing Viewer` |
| Marketplace update | The organization has a subscription or unsubscription through a cloud provider marketplace. | All organization members |
| Support plan update | The support plan subscription for the organization is changed. | All organization members |
## View notifications

To view notifications, click **Notification** in the lower-left corner of the [TiDB Cloud console](https://tidbcloud.com/).

When new notifications are available, a number is displayed next to **Notification** indicating how many notifications are unread.
