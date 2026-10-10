# High reliability security and authentication FAQs

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/high-reliability-faq.md`
- Source Title: `High Reliability FAQs`
- Source Heading Path: `High Reliability FAQs | High Reliability FAQs > Does TiDB support data encryption? | High Reliability FAQs > Does TiDB support modifying the MySQL version string of the server to a specific one that is required by the security vulnerability scanning tool? | High Reliability FAQs > What authentication protocols does TiDB support? What's the process? | High Reliability FAQs > How to modify the user password and privilege?`
- Source Line Ranges: `5-43`
- Source Scope: `shared`
- Primary Component: `shared`
- Related Components: `tidb`, `tiup`
- Topic Tags: `data-encryption`, `tls`, `transparent-data-encryption`, `server-version`, `security-scanning`, `authentication`, `sasl`, `challenge-response`, `user-password`, `privileges`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0282_8fb672e7ae`
- Source ID: `tidb-docs-8.1:faq/high-reliability-faq.md#high-reliability-faqs`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `25bedabf2dfa19e41e0de7b10af812589fd11cdeb93dd679f199b65642872e9b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/high-reliability-faq#high-reliability-faqs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/high-reliability-faq.md

## Retrieval Guidance

- Use When: Use this chunk when answering questions about TiDB security and authentication FAQs covering TLS, transparent data encryption, changing the server version string for security vulnerability scanning tools, SASL challenge-response authentication, and modifying user passwords or privileges.
- Retrieval Keywords: enable TLS between TiDB clients and servers, transparent data encryption, TDE, server-version, security vulnerability scanning tool, tiup cluster edit-config <cluster-name>, tiup cluster reload <cluster-name> -R tidb, SASL protocol, challenge-response authentication, ALTER USER, UPDATE mysql.user, TiDB user account management
- Follow-up Guidance: The source points to related documentation for enabling TLS between TiDB clients and servers, encryption at rest, the server-version configuration item, and TiDB user account management.
- Classification Note: This is a reference chunk because it summarizes multiple official FAQ answers about security, authentication, encryption, configuration, and user account management in TiDB.

## Official Source Content

# High Reliability FAQs

This document summarizes the FAQs related to high reliability of TiDB.
## Does TiDB support data encryption?

Yes. To encrypt data in the network traffic, you can [enable TLS between TiDB clients and servers](https://docs.pingcap.com/tidb/stable/enable-tls-between-clients-and-servers). To encrypt data in the storage engine, you can enable [transparent data encryption (TDE)](https://docs.pingcap.com/tidb/stable/encryption-at-rest).
## Does TiDB support modifying the MySQL version string of the server to a specific one that is required by the security vulnerability scanning tool?

- Since v3.0.8, TiDB supports modifying the version string of the server by modifying [`server-version`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#server-version) in the configuration file.

- Since v4.0, if you deploy TiDB using TiUP, you can also specify the proper version string by executing `tiup cluster edit-config <cluster-name>` to edit the following section:

    ```
    server_configs:
      tidb:
        server-version: 'YOUR_VERSION_STRING'
    ```

    Then, use the `tiup cluster reload <cluster-name> -R tidb` command to make the preceding modification effective to avoid the failure of security vulnerability scan.
## What authentication protocols does TiDB support? What's the process?

Like MySQL, TiDB supports the SASL protocol for user login authentication and password processing.

When the client connects to TiDB, the challenge-response authentication mode starts. The process is as follows:

1. The client connects to the server.
2. The server sends a random string challenge to the client.
3. The client sends the username and response to the server.
4. The server verifies the response.
## How to modify the user password and privilege?

To modify the user password in TiDB, it is recommended to use `ALTER USER` (for example, `ALTER USER 'test'@'localhost' IDENTIFIED BY 'mypass';`), not `UPDATE mysql.user` which might lead to the condition that the password in other nodes is not refreshed timely.

It is recommended to use the official standard statements when modifying the user password and privilege. For details, see [TiDB user account management](https://docs.pingcap.com/tidb/stable/user-account-management).
