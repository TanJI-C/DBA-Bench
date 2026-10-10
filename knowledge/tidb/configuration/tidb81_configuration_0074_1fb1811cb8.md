# Enable TLS between DM and upstream or downstream databases

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-enable-tls.md`
- Source Title: `Enable TLS for DM Connections`
- Source Heading Path: `Enable TLS for DM Connections > Enable encrypted data transmission between DM components and the upstream or downstream database | Enable TLS for DM Connections > Enable encrypted data transmission between DM components and the upstream or downstream database > Enable encrypted data transmission for upstream database | Enable TLS for DM Connections > Enable encrypted data transmission between DM components and the upstream or downstream database > Enable encrypted data transmission for downstream TiDB`
- Source Line Ranges: `88-126`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `tls`, `certificates`, `encrypted-connections`, `upstream-database`, `downstream-tidb`, `source-configuration`, `task-configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0074_1fb1811cb8`
- Source ID: `tidb-docs-8.1:dm/dm-enable-tls.md#enable-encrypted-data-transmission-between-dm-components-and-the-upstream-or-downstream-database`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7b793c9e13354b2179e3be61394f8dfd01538c9caed7643f0295f3616702935e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-enable-tls#enable-encrypted-data-transmission-between-dm-components-and-the-upstream-or-downstream-database
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-enable-tls.md

## Retrieval Guidance

- Use When: Use this content when enabling encrypted connections between DM components and an upstream database or downstream TiDB by setting client certificate paths in source or task configuration.
- Retrieval Keywords: Enable encrypted data transmission between DM components and the upstream or downstream database, upstream database, downstream TiDB, source configuration file, task configuration file, from.security.ssl-ca, from.security.ssl-cert, from.security.ssl-key, target-database.security.ssl-ca, target-database.security.ssl-cert, target-database.security.ssl-key, MySQL client certificate, TiDB client certificate, encrypted connections
- Follow-up Guidance: The content notes that all DM-master and DM-worker components must be able to read the certificates and key files through the specified paths.
- Classification Note: This is classified as configuration because the official content shows the YAML security settings for TLS between DM and upstream or downstream databases in source and task configuration files.

## Official Source Content

## Enable encrypted data transmission between DM components and the upstream or downstream database

This section introduces how to enable encrypted data transmission between DM components and the upstream or downstream database.
### Enable encrypted data transmission for upstream database

1. Configure the upstream database, enable the encryption support, and set the server certificate. For detailed operations, see [Using encrypted connections](https://dev.mysql.com/doc/refman/8.0/en/using-encrypted-connections.html).

2. Set the MySQL client certificate in the source configuration file:

    > **Note:**
    >
    > Make sure that all DM-master and DM-worker components can read the certificates and the key files via specified paths.

    ```yaml
    from:
        security:
            ssl-ca: "/path/to/mysql-ca.pem"
            ssl-cert: "/path/to/mysql-cert.pem"
            ssl-key: "/path/to/mysql-key.pem"
    ```
### Enable encrypted data transmission for downstream TiDB

1. Configure the downstream TiDB to use encrypted connections. For detailed operations, refer to [Configure TiDB server to use secure connections](https://docs.pingcap.com/tidb/stable/enable-tls-between-clients-and-servers#configure-tidb-server-to-use-secure-connections).

2. Set the TiDB client certificate in the task configuration file:

    > **Note:**
    >
    > Make sure that all DM-master and DM-worker components can read the certificates and the key files via specified paths.

    ```yaml
    target-database:
        security:
            ssl-ca: "/path/to/tidb-ca.pem"
            ssl-cert: "/path/to/tidb-client-cert.pem"
            ssl-key: "/path/to/tidb-client-key.pem"
    ```
