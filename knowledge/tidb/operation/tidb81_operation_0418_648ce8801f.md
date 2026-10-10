# TiDB Cloud partner programs and daily management tasks

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-partners.md`
- Source Title: `TiDB Cloud Partner Web Console`
- Source Heading Path: `TiDB Cloud Partner Web Console | TiDB Cloud Partner Web Console > Reseller through AWS Channel Partner Private Offer (CPPO) | TiDB Cloud Partner Web Console > Reseller through AWS Channel Partner Private Offer (CPPO) > Become a reseller of PingCAP | TiDB Cloud Partner Web Console > Reseller through AWS Channel Partner Private Offer (CPPO) > Manage daily tasks for a reseller | TiDB Cloud Partner Web Console > Managed Service Provider (MSP) | TiDB Cloud Partner Web Console > Managed Service Provider (MSP) > Become an MSP of PingCAP | TiDB Cloud Partner Web Console > Managed Service Provider (MSP) > Manage daily tasks for an MSP`
- Source Line Ranges: `6-72`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `partner-console`, `reseller`, `aws-marketplace`, `cppo`, `managed-service-provider`, `registration`, `account-activation`, `api`, `billing`, `customer-management`, `deprecated`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0418_648ce8801f`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-partners.md#tidb-cloud-partner-web-console`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `628dc745bc6d90c191b6969ed0eebe29c4f92c0dbe4cdb4614e4a59623e496d7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-partners#tidb-cloud-partner-web-console
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-partners.md

## Retrieval Guidance

- Use When: Use this chunk when someone asks about TiDB Cloud partner program types, how to enroll as a reseller or MSP, or which console and APIs are available for partner daily management tasks in TiDB Cloud.
- Retrieval Keywords: TiDB Cloud Partner Web Console, partner-console.tidbcloud.com, Reseller through AWS Channel Partner Private Offer, AWS Marketplace Channel Partner Private Offer, AWS CPPO, Managed Service Provider, MSP, Partner Management API, Support page, MSP Management API, deprecated, contact sales, become a partner, account activation email, API key, monthly bill, credits, discounts, sign-up URL, customer organization ID
- Follow-up Guidance: The source also states that after partner registration, an MSP receives an email notification to activate the account in the TiDB Cloud Partner console and an API key for the MSP Management API.
- Classification Note: This is classified as a cloud operation topic because the content describes TiDB Cloud partner program enrollment and daily management through the partner console and partner management APIs.

## Official Source Content

# TiDB Cloud Partner Web Console

TiDB Cloud Partner Web Console is designed for partners focused on SaaS solutions, with the goal of building and nurturing a strong partnership between PingCAP and our partners to better serve our customers.

There are two types of TiDB Cloud partners:

- Reseller: resells TiDB Cloud through AWS Marketplace Channel Partner Private Offer (CPPO)
- Managed Service Provider (MSP): resells TiDB Cloud and provides value-added services
## Reseller through AWS Channel Partner Private Offer (CPPO)

The reseller through [AWS CPPO](https://aws.amazon.com/marketplace/features/cpprivateoffers) allows customers to purchase TiDB Cloud through the AWS Marketplace directly from a reseller. This enables customers to benefit from the partner's business knowledge, localized support, and expertise, while still enjoying the fast and seamless purchasing experience they expect from AWS Marketplace.
### Become a reseller of PingCAP

If you are interested in the reseller program and would like to join as a partner, [contact sales](https://www.pingcap.com/partners/become-a-partner/) to enroll.
### Manage daily tasks for a reseller

As a reseller, you have two ways to manage your daily management tasks:

- [TiDB Cloud Partner console](https://partner-console.tidbcloud.com)
- Partner Management API. You can find the open API documentation on the **Support** page of the TiDB Cloud Partner console.
## Managed Service Provider (MSP)

An MSP is a partner who resells TiDB Cloud and provides value-added services, including but not limited to TiDB Cloud organization management, billing services, and technical support.

Benefits of becoming a managed service provider include:

- Discounts and incentive programs
- Enablement training
- Increased visibility through certification
- Joint marketing opportunities
### Become an MSP of PingCAP

If you are interested in the MSP program and would like to join as a partner, [contact sales](https://www.pingcap.com/partners/become-a-partner/) to enroll. Please provide the following information:

- Company name
- Company contact email
- Company official website URL
- Company logo (One SVG file for light mode and one SVG file for dark mode; a horizontal logo with 256 x 48 pixels is preferred)

The preceding information is used to generate an exclusive sign-up URL and page with your company logo for your customers.

We will carefully evaluate your request and get back to you soon.
### Manage daily tasks for an MSP

As a TiDB Cloud MSP partner, there are two methods for you to manage your daily management tasks:

- [TiDB Cloud Partner console](https://partner-console.tidbcloud.com)
- [MSP Management API (deprecated)](https://docs.pingcap.com/tidbcloud/api/v1beta1/msp)

After your complete the registration as a TiDB Cloud partner, you will receive an email notification to activate the account in the TiDB Cloud Partner console, and receive an API key for the MSP Management API.

You can use the MSP management API to manage the following daily tasks:

- Query the MSP monthly bill for a specific month
- Query credits applied to an MSP
- Query discounts applied to an MSP
- Query the monthly bill for a specific MSP customer
- Create a new sign-up URL for an MSP customer
- List all MSP customers
- Retrieve MSP customer information by the customer organization ID
