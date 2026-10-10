# TiDB Cloud Dedicated TLS prerequisites and connection methods

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-tls-connect-to-dedicated.md`
- Source Title: `TLS Connections to TiDB Cloud Dedicated`
- Source Heading Path: `TLS Connections to TiDB Cloud Dedicated | TLS Connections to TiDB Cloud Dedicated > Prerequisites | TLS Connections to TiDB Cloud Dedicated > Secure connection to a TiDB Cloud Dedicated cluster`
- Source Line Ranges: `6-176`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `sql`
- Topic Tags: `tls`, `secure-connection`, `ca-certificate`, `client-configuration`, `ip-access-list`, `jdbc`, `mysql-cli`, `python`, `go`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0309_685b8ddedc`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-tls-connect-to-dedicated.md#tls-connections-to-tidb-cloud-dedicated`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `404f29636e184c8f77e62b758dd27d21653b08108ec7f15b7cc7acdbb1117a9e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-tls-connect-to-dedicated#tls-connections-to-tidb-cloud-dedicated
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-tls-connect-to-dedicated.md

## Retrieval Guidance

- Use When: Use this when you need the prerequisites and example TLS connection settings for connecting to a TiDB Cloud Dedicated cluster from clients such as MySQL CLI, MyCLI, JDBC, Python, or Go.
- Retrieval Keywords: TLS Connections to TiDB Cloud Dedicated, TiDB Cloud Dedicated, Prerequisites, Connect, Connection Type Public, Configure IP Access List, CA cert, TLS 1.2, TLS 1.3, require_secure_transport, mysql --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca.pem --tls-version="TLSv1.2", mycli --ssl-ca=ca.pem --ssl-verify-server-cert, jdbc:mysql://, sslMode=VERIFY_IDENTITY, trustCertificateKeyStoreUrl, trustCertificateKeyStorePassword, keytool -importcert -alias TiDBCACert -file ca.pem, mysqlclient, ssl_mode="VERIFY_IDENTITY", ssl={"ca": "ca.pem"}, Go-MySQL-Driver, mysql.RegisterTLSConfig, MinVersion: tls.VersionTLS12
- Follow-up Guidance: The source also states that you can download the cluster CA certificate in the TiDB Cloud console and then use the connection string or sample code shown in the Connect dialog for your preferred method.
- Classification Note: This chunk is classified as configuration because it provides prerequisites, console settings, CA certificate handling, and client connection parameters for TLS access to a TiDB Cloud Dedicated cluster.

## Official Source Content

# TLS Connections to TiDB Cloud Dedicated

On TiDB Cloud, establishing TLS connections is one of the basic security practices for connecting to TiDB Cloud Dedicated clusters. You can configure multiple TLS connections from your client, application, and development tools to your TiDB Cloud Dedicated cluster to protect data transmission security. For security reasons, TiDB Cloud Dedicated only supports TLS 1.2 and TLS 1.3, and does not support TLS 1.0 and TLS 1.1 versions.

To ensure data security, TiDB cluster CA for your TiDB Cloud Dedicated cluster is hosted on [AWS Certificate Manager (ACM)](https://aws.amazon.com/certificate-manager/), and TiDB cluster private keys are stored in AWS-managed hardware security modules (HSMs) that meet [FIPS 140-2 Level 3](https://csrc.nist.gov/projects/cryptographic-module-validation-program/Certificate/3139) security standards.
## Prerequisites

- Log in to TiDB Cloud via [Password Authentication](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-password-authentication) or [SSO Authentication](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-sso-authentication), and then [Create a TiDB Cloud Dedicated cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster).

- Set a password to access your cluster in secure settings.

    To do so, you can navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, click **...** in the row of your TiDB Cloud Dedicated cluster, and then select **Password Settings**. In password settings, you can click **Auto-generate Password** to automatically generate a root password with a length of 16 characters, including numbers, uppercase and lowercase characters, and special characters.
## Secure connection to a TiDB Cloud Dedicated cluster

In the [TiDB Cloud console](https://tidbcloud.com/), you can get examples of different connection methods and connect to your TiDB Cloud Dedicated cluster as follows:

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, and then click the name of your TiDB Cloud Dedicated cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A dialog is displayed.

3. In the connection dialog, select **Public** from the **Connection Type** drop-down list.

    If you have not configured the IP access list, click **Configure IP Access List** to configure it before your first connection. For more information, see [Configure an IP access list](https://docs.pingcap.com/tidb/stable/tidb-cloud/configure-ip-access-list).

4. Click **CA cert** to download CA cert for TLS connection to TiDB clusters. The CA cert supports TLS 1.2 version by default.

    > **Note:**
    >
    > - You can store the downloaded CA cert in the default storage path of your operating system, or specify another storage path. You need to replace the CA cert path in the code example with your own CA cert path in the subsequent steps.
    > - TiDB Cloud Dedicated does not force clients to use TLS connections, and user-defined configuration of the [`require_secure_transport`](https://docs.pingcap.com/tidb/stable/system-variables#require_secure_transport-new-in-v610) variable is currently not supported on TiDB Cloud Dedicated.

5. Choose your preferred connection method, and then refer to the connection string and sample code on the tab to connect to your cluster.

The following examples show the connection strings in MySQL, MyCLI, JDBC, Python, Go, and Node.js:

<div label="MySQL CLI">

MySQL CLI client attempts to establish a TLS connection by default. When you connect to TiDB Cloud Dedicated clusters, you need to set `ssl-mode` and `ssl-ca`.

```shell
mysql --connect-timeout 15 --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca.pem --tls-version="TLSv1.2" -u root -h tidb.eqlfbdgthh8.clusters.staging.tidb-cloud.com -P 4000 -D test -p
```

Parameter description：

- With `--ssl-mode=VERIFY_IDENTITY`, MySQL CLI client forces to enable TLS and validate TiDB Cloud Dedicated clusters.
- Use `--ssl-ca=<CA_path>` to specify your local path of the downloaded TiDB cluster `ca.pem`.
- Use `--tls-version=TLSv1.2` to restrict the versions of the TLS protocol. If you want to use TLS 1.3, you can set the version to `TLSv1.3`.

</div>

<div label="MyCLI">

[MyCLI](https://www.mycli.net/) automatically enables TLS when using TLS related parameters. When you connect to TiDB Cloud Dedicated clusters, you need to set `ssl-ca` and `ssl-verify-server-cert`.

```shell
mycli --ssl-ca=ca.pem --ssl-verify-server-cert -u root -h tidb.eqlfbdgthh8.clusters.staging.tidb-cloud.com -P 4000 -D test
```

Parameter descriptions：

- Use `--ssl-ca=<CA_path>` to specify your local path of the downloaded TiDB cluster `ca.pem`.
- With `--ssl-verify-server-cert` to validate TiDB Cloud Dedicated clusters.

</div>

<div label="JDBC">

[MySQL Connector/J](https://dev.mysql.com/doc/connector-j/en/)'s TLS connection configurations are used here as an example.

After downloading TiDB cluster CA, if you want to import it into your operating system, you can use the `keytool -importcert -alias TiDBCACert -file ca.pem -keystore <your_custom_truststore_path> -storepass <your_truststore_password>` command.

```shell
/* Be sure to replace the parameters in the following connection string. */
/* version >= 8.0.28 */
jdbc:mysql://tidb.srgnqxji5bc.clusters.staging.tidb-cloud.com:4000/test?user=root&password=<your_password>&sslMode=VERIFY_IDENTITY&tlsVersions=TLSv1.2&trustCertificateKeyStoreUrl=file:<your_custom_truststore_path>&trustCertificateKeyStorePassword=<your_truststore_password>
```

You can click **show example usage** to view detailed code examples.

```
import com.mysql.jdbc.Driver;
import java.sql.*;

class Main {
  public static void main(String args[]) throws SQLException, ClassNotFoundException {
    Class.forName("com.mysql.cj.jdbc.Driver");
    try {
      Connection conn = DriverManager.getConnection("jdbc:mysql://tidb.srgnqxji5bc.clusters.staging.tidb-cloud.com:4000/test?user=root&password=<your_password>&sslMode=VERIFY_IDENTITY&tlsVersions=TLSv1.2&trustCertificateKeyStoreUrl=file:<your_custom_truststore_path>&trustCertificateKeyStorePassword=<your_truststore_password>");
      Statement stmt = conn.createStatement();
      try {
        ResultSet rs = stmt.executeQuery("SELECT DATABASE();");
        if (rs.next()) {
          System.out.println("using db:" + rs.getString(1));
        }
      } catch (Exception e) {
        System.out.println("exec error:" + e);
      }
    } catch (Exception e) {
      System.out.println("connect error:" + e);
    }
  }
}
```

Parameter description：

- Set `sslMode=VERIFY_IDENTITY` to enable TLS and validate TiDB Cloud Dedicated clusters.
- Set `enabledTLSProtocols=TLSv1.2` to restrict the versions of the TLS protocol. If you want to use TLS 1.3, you can set the version to `TLSv1.3`.
- Set `trustCertificateKeyStoreUrl` to your custom truststore path.
- Set `trustCertificateKeyStorePassword` to your truststore password.

</div>

<div label="Python">

[mysqlclient](https://pypi.org/project/mysqlclient/)'s TLS connection configurations are used here as an example.

```
host="tidb.srgnqxji5bc.clusters.staging.tidb-cloud.com", user="root", password="<your_password>", port=4000, database="test", ssl_mode="VERIFY_IDENTITY", ssl={"ca": "ca.pem"}
```

You can click **show example usage** to view detailed code examples.

```
import MySQLdb

connection = MySQLdb.connect(host="tidb.srgnqxji5bc.clusters.staging.tidb-cloud.com", port=4000, user="root", password="<your_password>", database="test", ssl_mode="VERIFY_IDENTITY", ssl={"ca": "ca.pem"})

with connection:
    with connection.cursor() as cursor:
        cursor.execute("SELECT DATABASE();")
        m = cursor.fetchone()
        print(m[0])
```

Parameter descriptions：

- Set `ssl_mode="VERIFY_IDENTITY"` to enable TLS and validate TiDB Cloud Dedicated clusters.
- Use `ssl={"ca": "<CA_path>"}` to specify your local path of the downloaded TiDB cluster `ca.pem`.

</div>

<div label="Go">

[Go-MySQL-Driver](https://github.com/go-sql-driver/mysql)'s TLS connection configurations are used here as an example.

```
rootCertPool := x509.NewCertPool()
pem, err := ioutil.ReadFile("ca.pem")
if err != nil {
    log.Fatal(err)
}
if ok := rootCertPool.AppendCertsFromPEM(pem); !ok {
    log.Fatal("Failed to append PEM.")
}
mysql.RegisterTLSConfig("tidb", &tls.Config{
    RootCAs:    rootCertPool,
    MinVersion: tls.VersionTLS12,
    ServerName: "tidb.srgnqxji5bc.clusters.staging.tidb-cloud.com",
})

db, err := sql.Open("mysql", "root:<your_password>@tcp(tidb.srgnqxji5bc.clusters.staging.tidb-cloud.com:4000)/test?tls=tidb")
```

You can click **show example usage** to view detailed code examples.
