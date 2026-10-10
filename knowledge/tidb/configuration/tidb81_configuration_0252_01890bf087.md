# Serverless TLS connection setup and root certificate management

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/secure-connections-to-serverless-clusters.md`
- Source Title: `TLS Connections to TiDB Cloud Serverless`
- Source Heading Path: `TLS Connections to TiDB Cloud Serverless | TLS Connections to TiDB Cloud Serverless > Prerequisites | TLS Connections to TiDB Cloud Serverless > TLS connection to a TiDB Cloud Serverless cluster | TLS Connections to TiDB Cloud Serverless > Root certificate management | TLS Connections to TiDB Cloud Serverless > Root certificate management > Root certificate issuance and validity | TLS Connections to TiDB Cloud Serverless > Root certificate management > Root certificate default path`
- Source Line Ranges: `6-90`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `tls`, `serverless`, `connection`, `password`, `certificate`, `ca`, `root-certificate`, `lets-encrypt`, `client-configuration`, `operating-systems`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0252_01890bf087`
- Source ID: `tidb-docs-8.1:tidb-cloud/secure-connections-to-serverless-clusters.md#tls-connections-to-tidb-cloud-serverless`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5ed5d85871a8c0f726777e5a85244ec866d16d9faa686609c2ea32aec406fd86`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/secure-connections-to-serverless-clusters#tls-connections-to-tidb-cloud-serverless
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/secure-connections-to-serverless-clusters.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how to connect to a TiDB Cloud Serverless cluster with TLS, handle generated passwords, use the required user name prefix, or locate and configure the CA root certificate path for different operating systems and clients.
- Retrieval Keywords: TiDB Cloud Serverless TLS connection, Connect dialog Public connection type, Generate Password, Reset Password, user name prefix, Let's Encrypt, ISRG Root X1, system root CA stores, mysqlclient, ssl argument, ca: /etc/ssl/cert.pem, DBeaver, MacOS /etc/ssl/cert.pem, Debian Ubuntu Arch /etc/ssl/certs/ca-certificates.crt, RedHat Fedora CentOS Mageia /etc/pki/tls/certs/ca-bundle.crt, Alpine /etc/ssl/cert.pem, OpenSUSE /etc/ssl/ca-bundle.pem, Windows registry certificate stores
- Follow-up Guidance: If a client or GUI tool does not use the system root CA stores or does not accept a certificate file with multiple certificates inside, the content points to configuring the CA root path or downloading the ISRG Root X1 certificate.
- Classification Note: This is classified as configuration because the content describes connection setup in the TiDB Cloud console, password handling, user name formatting, and CA root certificate path configuration for TLS clients.

## Official Source Content

# TLS Connections to TiDB Cloud Serverless

Establishing a secure TLS connection between your client and your TiDB Cloud Serverless cluster is one of the basic security practices for connecting to your databases. The server certificate for TiDB Cloud Serverless is issued by an independent third-party certificate provider. You can easily connect to your TiDB Cloud Serverless cluster without downloading a server-side digital certificate.
## Prerequisites

- Log in to TiDB Cloud via [Password Authentication](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-password-authentication) or [SSO Authentication](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-sso-authentication).
- [Create a TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-quickstart).
## TLS connection to a TiDB Cloud Serverless cluster

In the [TiDB Cloud console](https://tidbcloud.com/), you can get examples of different connection methods and connect to your TiDB Cloud Serverless cluster as follows:

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, and then click the name of your cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A dialog is displayed.

3. In the dialog, keep the default setting of the connection type as `Public`, and select your preferred connection method and operating system.

4. If you have not set a password yet, click **Generate Password** to generate a random password for your TiDB Cloud Serverless cluster. The password will be automatically embedded in the sample connection string for connecting to your cluster easily.

    > **Note:**
    >
    > - The random password consists of 16 characters, including uppercase and lowercase letters, numbers, and special characters.
    > - After you close this dialog, the generated password will not show again, so you need to save the password in a secure location. If you forget it, you can click **Reset Password** in this dialog to reset it.
    > - The TiDB Cloud Serverless cluster can be accessed through the internet. If you need to use the password elsewhere, it is recommended that you reset it to ensure database security.

5. Connect to your cluster with the connection string.

    > **Note:**
    >
    > When you connect to a TiDB Cloud Serverless cluster, you must include the prefix for your cluster in the user name and wrap the name with quotation marks. For more information, see [User name prefix](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#user-name-prefix).
## Root certificate management
### Root certificate issuance and validity

TiDB Cloud Serverless uses certificates from [Let's Encrypt](https://letsencrypt.org/) as a Certificate Authority (CA) for TLS connection between clients and TiDB Cloud Serverless clusters. Once the TiDB Cloud Serverless certificate expires, it will be automatically rotated without affecting the normal operations of your cluster and the established TLS secure connection.

If the client uses the system's root CA stores by default, such as Java and Go, you can easily connect securely to TiDB Cloud Serverless clusters without specifying the path of CA roots. However, some drivers and ORMs do not use the system root CA stores. In those cases, you need to configure the CA root path of the drivers or ORMs to your system root CA stores. For example, when you use [mysqlclient](https://github.com/PyMySQL/mysqlclient) to connect a TiDB Cloud Serverless cluster in Python on macOS, you need to set `ca: /etc/ssl/cert.pem` in the `ssl` argument.

If you are using a GUI client, such as DBeaver, which does not accept a certificate file with multiple certificates inside, you must download the [ISRG Root X1](https://letsencrypt.org/certs/isrgrootx1.pem) certificate.
### Root certificate default path

In different operating systems, the default storage paths of the root certificate are as follows：

**MacOS**

```
/etc/ssl/cert.pem
```

**Debian / Ubuntu / Arch**

```
/etc/ssl/certs/ca-certificates.crt
```

**RedHat / Fedora / CentOS / Mageia**

```
/etc/pki/tls/certs/ca-bundle.crt
```

**Alpine**

```
/etc/ssl/cert.pem
```

**OpenSUSE**

```
/etc/ssl/ca-bundle.pem
```

**Windows**

Windows does not offer a specific path to the CA root. Instead, it uses the [registry](https://learn.microsoft.com/en-us/windows-hardware/drivers/install/local-machine-and-current-user-certificate-stores) to store certificates. For this reason, to specify the CA root path on Windows, take the following steps:

1. Download the [ISRG Root X1 certificate](https://letsencrypt.org/certs/isrgrootx1.pem) and then save it in a path you prefer, such as `<path_to_ca>`.
2. Use the path (`<path_to_ca>`) as your CA root path when you connect to a TiDB Cloud Serverless cluster.
