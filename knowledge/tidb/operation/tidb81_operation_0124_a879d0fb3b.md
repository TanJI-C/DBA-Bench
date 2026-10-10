# Create and verify a DM data source

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/quick-start-create-source.md`
- Source Title: `Create a Data Source for TiDB Data Migration`
- Source Heading Path: `Create a Data Source for TiDB Data Migration | Create a Data Source for TiDB Data Migration > Step 1: Configure the data source | Create a Data Source for TiDB Data Migration > Step 2: Create a data source | Create a Data Source for TiDB Data Migration > Step 3: Query the data source you created`
- Source Line Ranges: `5-137`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`
- Topic Tags: `data-source`, `source-configuration`, `password-encryption`, `dmctl`, `source-creation`, `source-query`, `verification`, `tls`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0124_a879d0fb3b`
- Source ID: `tidb-docs-8.1:dm/quick-start-create-source.md#create-a-data-source-for-tidb-data-migration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `50b9be548a061e914648c1f4aa184d97a9542c62bfc08c00b19b0d455deb4b61`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/quick-start-create-source#create-a-data-source-for-tidb-data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/quick-start-create-source.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the DM commands and source configuration example to create a data source, optionally encrypt the upstream password, and verify the created source by source-id or source list.
- Retrieval Keywords: Create a Data Source for TiDB Data Migration, tiup dmctl encrypt, secret-key-path, operate-source create, config source, operate-source show, source-id, source-mysql-01.yaml, mysql-01, dm-worker-1, ssl-ca, ssl-cert, ssl-key, source is added but there is no free worker to bound
- Follow-up Guidance: The source also points to Manage Data Source Configurations, Upstream Database Configuration File, and Deploy a DM Cluster Using TiUP for related commands and prerequisites.
- Classification Note: This is classified as an operation chunk because the official content provides a step-by-step procedure to configure, create, and query a DM data source using dmctl and a YAML source configuration file.

## Official Source Content

# Create a Data Source for TiDB Data Migration

> **Note:**
>
> Before creating a data source, you need to [Deploy a DM Cluster Using TiUP](https://docs.pingcap.com/tidb/stable/dm/deploy-a-dm-cluster-using-tiup).

The document describes how to create a data source for the data migration task of TiDB Data Migration (DM).

A data source contains the information for accessing the upstream migration task. Because a data migration task requires referring its corresponding data source to obtain the configuration information of access, you need to create the data source of a task before creating a data migration task. For specific data source management commands, refer to [Manage Data Source Configurations](https://docs.pingcap.com/tidb/stable/dm/dm-manage-source).
## Step 1: Configure the data source

1. (optional) Encrypt the data source password

    In DM configuration files, it is recommended to use the password encrypted with dmctl. You can follow the example below to obtain the encrypted password of the data source, which can be used to write the configuration file later.

    Starting from v8.0.0, you must configure [`secret-key-path`](https://docs.pingcap.com/tidb/stable/dm/dm-master-configuration-file) for DM-master before using the `tiup dmctl encrypt` command.

    ```bash
    tiup dmctl encrypt 'abc!@#123'
    ```

    ```
    MKxn0Qo3m3XOyjCnhEMtsUCm83EhGQDZ/T4=
    ```

2. Write the configuration file of the data source

    For each data source, you need an individual configuration file to create it. You can follow the example below to create a data source whose ID is "mysql-01". First create the configuration file `./source-mysql-01.yaml`:

    ```yaml
    source-id: "mysql-01"    # The ID of the data source, you can refer this source-id in the task configuration and dmctl command to associate the corresponding data source.

    from:
      host: "127.0.0.1"
      port: 3306
      user: "root"
      password: "MKxn0Qo3m3XOyjCnhEMtsUCm83EhGQDZ/T4=" # The user password of the upstream data source. It is recommended to use the password encrypted with dmctl.
      security:                                        # The TLS configuration of the upstream data source. If not necessary, it can be deleted.
        ssl-ca: "/path/to/ca.pem"
        ssl-cert: "/path/to/cert.pem"
        ssl-key: "/path/to/key.pem"
    ```
## Step 2: Create a data source

You can use the following command to create a data source:

```bash
tiup dmctl --master-addr <master-addr> operate-source create ./source-mysql-01.yaml
```

For other configuration parameters, refer to [Upstream Database Configuration File](https://docs.pingcap.com/tidb/stable/dm/dm-source-configuration-file).

The returned results are as follows:

```
{
    "result": true,
    "msg": "",
    "sources": [
        {
            "result": true,
            "msg": "",
            "source": "mysql-01",
            "worker": "dm-worker-1"
        }
    ]
}
```
## Step 3: Query the data source you created

After creating a data source, you can use the following command to query the data source:

- If you know the `source-id` of the data source, you can use the `dmctl config source <source-id>` command to directly check the configuration of the data source:

    ```bash
    tiup dmctl --master-addr <master-addr> config source mysql-01
    ```

    ```
    {
      "result": true,
      "msg": "",
      "cfg": "enable-gtid: false
        flavor: mysql
        source-id: mysql-01
        from:
          host: 127.0.0.1
          port: 3306
          user: root
          password: '******'
    }
    ```

- If you do not know the `source-id`, you can use the `dmctl operate-source show` command to check the source database list, from which you can find the corresponding data source.

    ```bash
    tiup dmctl --master-addr <master-addr> operate-source show
    ```

    ```
    {
        "result": true,
        "msg": "",
        "sources": [
            {
                "result": true,
                "msg": "source is added but there is no free worker to bound",
                "source": "mysql-02",
                "worker": ""
            },
            {
                "result": true,
                "msg": "",
                "source": "mysql-01",
                "worker": "dm-worker-1"
            }
        ]
    }
    ```
