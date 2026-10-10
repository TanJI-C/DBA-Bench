# Connected Care support plan details and service matrix

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/connected-care-detail.md`
- Source Title: `Connected Care Details`
- Source Heading Path: `Connected Care Details`
- Source Line Ranges: `5-144`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `support-plans`, `response-times`, `service-matrix`, `billing-support`, `technical-support`, `monitoring-services`, `im-integration`, `customer-resources`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0790_f750fb0d17`
- Source ID: `tidb-docs-8.1:tidb-cloud/connected-care-detail.md#connected-care-details`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `782b51cc8dd24dbbec4881134bd7615a303033eef88e781c4c05e5b2acd30f25`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/connected-care-detail#connected-care-details
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/connected-care-detail.md

## Retrieval Guidance

- Use When: Use this chunk when comparing Connected Care support plans in TiDB Cloud, including response times, service availability, and customer resources across Basic, Developer, Enterprise, and Premium.
- Retrieval Keywords: Connected Care Details, Connected Care support services, support plan Basic Developer Enterprise Premium, Initial Response Time S1 S2 S3 S4, business hours 9 AM - 6 PM local time Monday to Friday, Billing and account support, Ticket-based technical support, End-to-end database guidance, Connected: Clinic service for advanced monitoring, Connected: AI chat in IM, Connected: IM subscription for TiDB Cloud alerts, Connected: IM ticket creation and update subscription, Connected: IM interaction for support tickets, Technical Account Manager, Knowledge Base, TiDB.AI, Community Workspace, FAQ, Documentations, Slack, Lark, Zoom
- Follow-up Guidance: The source also defines business hours, explains that IM means Instant Message with Slack and Lark currently supported, and describes Clinic as a monitoring service with advanced monitoring and diagnostic capabilities for TiDB Cloud clusters.
- Classification Note: This is reference content because it presents a service matrix for Connected Care plans, listing support features, response times, and customer resources without procedural steps.

## Official Source Content

# Connected Care Details

This document provides detailed information about the [Connected Care](https://docs.pingcap.com/tidb/stable/tidb-cloud/connected-care-overview) support services.

<table>
<thead>
  <tr>
    <th>Support plan</th>
    <th>Basic</th>
    <th>Developer</th>
    <th>Enterprise</th>
    <th>Premium</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td>Features and Services</td>
    <td>Great for personal starter projects, connecting you with an active community and AI-powered assistance for essential support needs.</td>
    <td>Ideal for development and testing phases, offering direct connections and unlimited access to tech support, to kickstart your cloud journey.</td>
    <td>Designed for production workloads, connecting your operations with advanced monitoring, prompt alerts, and fast 7x24 response times for a seamless experience.</td>
    <td>Built for enterprises with mission-critical workloads, offering the fastest response times, proactive support, and dedicated connections through named Technical Account Managers.</td>
  </tr>
  <tr>
    <td rowspan="4">Initial Response Time</td>
    <td>-</td>
    <td>S1: 4 business hours</td>
    <td>S1: 1 hour</td>
    <td>S1: 30 minutes</td>
  </tr>
  <tr>
    <td>-</td>
    <td>S2: 8 business hours</td>
    <td>S2: 2 hours</td>
    <td>S2: 1 hour</td>
  </tr>
  <tr>
    <td>-</td>
    <td>S3: 12 business hours</td>
    <td>S3: 8 business hours</td>
    <td>S3: 4 business hours</td>
  </tr>
  <tr>
    <td>-</td>
    <td>S4: 24 business hours</td>
    <td>S4: 24 business hours</td>
    <td>S4: 24 business hours</td>
  </tr>
  <tr>
    <td rowspan="9">Services</td>
    <td>Billing and account support</td>
    <td>Billing and account support</td>
    <td>Billing and account support</td>
    <td>Billing and account support</td>
  </tr>
  <tr>
    <td>-</td>
    <td>Ticket-based technical support</td>
    <td>Ticket-based technical support</td>
    <td>Ticket-based technical support</td>
  </tr>
  <tr>
    <td>-</td>
    <td>End-to-end database guidance</td>
    <td>End-to-end database guidance</td>
    <td>End-to-end database guidance</td>
  </tr>
  <tr>
    <td>-</td>
    <td>-</td>
    <td><a href="/tidbcloud/tidb-cloud-clinic">Connected: Clinic service for advanced monitoring</a></td>
    <td><a href="/tidbcloud/tidb-cloud-clinic">Connected: Clinic service for advanced monitoring</a></td>
  </tr>
  <tr>
    <td>-</td>
    <td>-</td>
    <td><a href="/tidbcloud/connected-ai-chat-in-im">Connected: AI chat in IM</a></td>
    <td><a href="/tidbcloud/connected-ai-chat-in-im">Connected: AI chat in IM</a></td>
  </tr>
  <tr>
    <td>-</td>
    <td>-</td>
    <td>Connected: IM subscription for TiDB Cloud alerts (via <a href="/tidbcloud/monitor-alert-slack">Slack</a> or <a href="/tidbcloud/monitor-alert-zoom">Zoom</a>)</td>
    <td>Connected: IM subscription for TiDB Cloud alerts (via <a href="/tidbcloud/monitor-alert-slack">Slack</a> or <a href="/tidbcloud/monitor-alert-zoom">Zoom</a>)</td>
  </tr>
  <tr>
    <td>-</td>
    <td>-</td>
    <td>Connected: IM ticket creation and update subscription (via <a href="/tidbcloud/connected-slack-ticket-creation">Slack</a> or <a href="/tidbcloud/connected-lark-ticket-creation">Lark</a>)</td>
    <td>Connected: IM ticket creation and update subscription (via <a href="/tidbcloud/connected-slack-ticket-creation">Slack</a> or <a href="/tidbcloud/connected-lark-ticket-creation">Lark</a>)</td>
  </tr>
  <tr>
    <td>-</td>
    <td>-</td>
    <td>-</td>
    <td>Connected: IM interaction for support tickets (via <a href="/tidbcloud/connected-slack-ticket-interaction">Slack</a> or <a href="/tidbcloud/connected-lark-ticket-interaction">Lark</a>)</td>
  </tr>
  <tr>
    <td>-</td>
    <td>-</td>
    <td>-</td>
    <td>Technical Account Manager</td>
  </tr>
  <tr>
    <td rowspan="5">Customer Resources</td>
    <td>Documentations</td>
    <td>Documentations</td>
    <td>Documentations</td>
    <td>Documentations</td>
  </tr>
  <tr>
    <td>FAQ</td>
    <td>FAQ</td>
    <td>FAQ</td>
    <td>FAQ</td>
  </tr>
  <tr>
    <td>Community Workspace</td>
    <td>Community Workspace</td>
    <td>Community Workspace</td>
    <td>Community Workspace</td>
  </tr>
  <tr>
    <td><a href="https://tidb.ai/">TiDB.AI</a></td>
    <td><a href="https://tidb.ai/">TiDB.AI</a></td>
    <td><a href="https://tidb.ai/">TiDB.AI</a></td>
    <td><a href="https://tidb.ai/">TiDB.AI</a></td>
  </tr>
  <tr>
    <td>-</td>
    <td>Knowledge Base</td>
    <td>Knowledge Base</td>
    <td>Knowledge Base</td>
  </tr>
</tbody>
</table>

- Business hours: 9 AM - 6 PM local time, Monday to Friday
- IM: Instant Message. Currently, [Slack](https://slack.com/) and [Lark](https://www.larksuite.com/) are supported. We are planning to support [Microsoft Teams](https://www.microsoft.com/en-us/microsoft-teams/group-chat-software) in the future.
- [Clinic](https://clinic.pingcap.com/): a modern monitoring service that provides advanced monitoring and diagnostic capabilities for your TiDB Cloud clusters.
