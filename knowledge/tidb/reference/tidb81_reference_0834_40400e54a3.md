# FAQ for sharing Kafka PSC across TiDB Cloud projects

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/setup-self-hosted-kafka-private-service-connect.md`
- Source Title: `Set Up Self-Hosted Kafka Private Service Connect in Google Cloud`
- Source Heading Path: `Set Up Self-Hosted Kafka Private Service Connect in Google Cloud > FAQ | Set Up Self-Hosted Kafka Private Service Connect in Google Cloud > FAQ > How to connect to the same Kafka Private Service Connect service from two different TiDB Cloud projects?`
- Source Line Ranges: `686-704`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`, `ecosystem`
- Topic Tags: `faq`, `private-service-connect`, `kafka`, `multi-project`, `changefeed`, `advertised-listeners`, `bootstrap-ports`, `kafka-proxy`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0834_40400e54a3`
- Source ID: `tidb-docs-8.1:tidb-cloud/setup-self-hosted-kafka-private-service-connect.md#faq`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `023c6bedd67581f0c782080f9e767006997f295a703420656eb5be31defbdf65`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/setup-self-hosted-kafka-private-service-connect#faq
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/setup-self-hosted-kafka-private-service-connect.md

## Retrieval Guidance

- Use When: Use this chunk when you need the FAQ guidance for connecting the same Kafka Private Service Connect service from two different TiDB Cloud projects.
- Retrieval Keywords: FAQ, two different TiDB Cloud projects, same Kafka Private Service Connect service, PSC port mapping, Reconfigure a running Kafka cluster, EXTERNAL2, Network endpoint group, new Bootstrap ports, new Kafka Advertised Listener Pattern, same Service Attachment, set up self-hosted Kafka Private Service Connect by Kafka-proxy, new Kafka-proxy PSC
- Follow-up Guidance: For PSC port mapping, the source says to create another group of EXTERNAL listeners and advertised listeners, add another group of Network endpoints, and use new Bootstrap ports and a new Kafka Advertised Listener Pattern with the same Service Attachment; for Kafka-proxy, it says to create a new Kafka-proxy PSC from the beginning with a new Kafka Advertised Listener Pattern.
- Classification Note: This is classified as reference because it is an FAQ entry describing supported connection patterns for sharing Kafka PSC access across two TiDB Cloud projects.

## Official Source Content

## FAQ
### How to connect to the same Kafka Private Service Connect service from two different TiDB Cloud projects?

If you have already followed the steps in this document and successfully set up the connection from the first project, and you want to set up a second connection from the second project, you can connect to the same Kafka Private Service Connect service from two different TiDB Cloud projects as follows:

- If you set up Kafka PSC by PSC port mapping, do the following:

    1. Follow instructions from the beginning of this document. When you proceed to [Step 1. Set up Kafka Cluster](#step-1-set-up-the-kafka-cluster), follow the [Reconfigure a running Kafka cluster](#reconfigure-a-running-kafka-cluster) section to create another group of EXTERNAL listeners and advertised listeners. You can name it as `EXTERNAL2`. Note that the port range of `EXTERNAL2` cannot overlap with the EXTERNAL.

    2. After reconfiguring the brokers, add another group of Network endpoints to the Network endpoint group, which maps the ports range to the `EXTERNAL2` listener.

    3. Configure the TiDB Cloud connection with the following input to create the new changefeed:

        - New Bootstrap ports
        - New Kafka Advertised Listener Pattern
        - The same Service Attachment

- If you [set up self-hosted Kafka Private Service Connect by Kafka-proxy](#set-up-self-hosted-kafka-private-service-connect-by-kafka-proxy), create a new Kafka-proxy PSC from the beginning with a new Kafka Advertised Listener Pattern.
