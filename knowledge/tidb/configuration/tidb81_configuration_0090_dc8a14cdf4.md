# Configure and create MySQL source connections in DM

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/quick-start-create-task.md`
- Source Title: `Create a Data Migration Task`
- Source Heading Path: `Create a Data Migration Task > Configure the MySQL data source | Create a Data Migration Task > Configure the MySQL data source > Encrypt the password | Create a Data Migration Task > Configure the MySQL data source > Edit the source configuration file | Create a Data Migration Task > Configure the MySQL data source > Create a source`
- Source Line Ranges: `86-147`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `source-configuration`, `password-encryption`, `dmctl`, `secret-key-path`, `gtid`, `source-id`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0090_dc8a14cdf4`
- Source ID: `tidb-docs-8.1:dm/quick-start-create-task.md#configure-the-mysql-data-source`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d3dd2a8fc2cb78b6eee291b05d6f974b64ab34628e5f0044447e48d361e2d70d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/quick-start-create-task#configure-the-mysql-data-source
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/quick-start-create-task.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented DM steps for encrypting a MySQL or TiDB password, defining source configuration files, and creating MySQL sources with dmctl.
- Retrieval Keywords: Configure the MySQL data source, Encrypt the password, dmctl encrypt, secret-key-path, conf/source1.yaml, conf/source2.yaml, source-id, mysql-replica-01, mysql-replica-02, enable-gtid: true, operate-source create, ./dmctl --master-addr=127.0.0.1:8261 operate-source create conf/source1.yaml, fCxfQ9XKCezSzuCD0Wf5dUD+LsKegSg=
- Follow-up Guidance: The chunk notes that starting from v8.0.0, DM-master must configure secret-key-path before using the dmctl encrypt command.
- Classification Note: This is classified as configuration because the content defines source YAML fields, password handling, and the dmctl command used to register source configurations in DM.

## Official Source Content

## Configure the MySQL data source

Before starting a data migration task, you need to configure the MySQL data source.
### Encrypt the password

> **Note:**
>
> + You can skip this step if the database does not have a password.
> + You can use the plaintext password to configure the source information in DM v1.0.6 and later versions.

For safety reasons, it is recommended to configure and use encrypted passwords. You can use dmctl to encrypt the MySQL/TiDB password. Suppose the password is "123456":

> **Note:**
>
> Starting from v8.0.0, you must configure [`secret-key-path`](https://docs.pingcap.com/tidb/stable/dm/dm-master-configuration-file) for DM-master before using the `dmctl encrypt` command.

```bash
./dmctl encrypt "123456"
```

```
fCxfQ9XKCezSzuCD0Wf5dUD+LsKegSg=
```

Save this encrypted value, and use it for creating a MySQL data source in the following steps.
### Edit the source configuration file

Write the following configurations to `conf/source1.yaml`.

```yaml
# MySQL1 Configuration.

source-id: "mysql-replica-01"

# Indicates whether GTID is enabled
enable-gtid: true

from:
  host: "127.0.0.1"
  user: "root"
  password: "fCxfQ9XKCezSzuCD0Wf5dUD+LsKegSg="
  port: 3306
```

In MySQL2 data source, copy the above configurations to `conf/source2.yaml`. You need to change `name` to `mysql-replica-02` and change `password` and `port` to appropriate values.
### Create a source

To load the data source configurations of MySQL1 into the DM cluster using dmctl, run the following command in the terminal:

```bash
./dmctl --master-addr=127.0.0.1:8261 operate-source create conf/source1.yaml
```

For MySQL2, replace the configuration file in the above command with that of MySQL2.
