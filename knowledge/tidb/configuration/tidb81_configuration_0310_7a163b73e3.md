# TLS connection examples for TiDB Cloud Dedicated clients

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-tls-connect-to-dedicated.md`
- Source Title: `TLS Connections to TiDB Cloud Dedicated`
- Source Heading Path: `TLS Connections to TiDB Cloud Dedicated > Secure connection to a TiDB Cloud Dedicated cluster`
- Source Line Ranges: `177-284`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`
- Topic Tags: `tls`, `client-connection`, `ca-certificate`, `hostname-verification`, `tls-versions`, `go`, `nodejs`, `mysql-driver`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0310_7a163b73e3`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-tls-connect-to-dedicated.md#secure-connection-to-a-tidb-cloud-dedicated-cluster`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8680b05bd2bcf0f63a3e227817d4989c36a59254824b493d22663e794c16e9f0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-tls-connect-to-dedicated#secure-connection-to-a-tidb-cloud-dedicated-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-tls-connect-to-dedicated.md

## Retrieval Guidance

- Use When: Use this chunk when looking for client-side TLS connection examples to a TiDB Cloud Dedicated cluster in Go or Node.js, including CA certificate loading, hostname verification, and TLS version settings.
- Retrieval Keywords: TiDB Cloud Dedicated TLS connection, go-sql-driver/mysql, mysql.RegisterTLSConfig, tls.Config, RootCAs, MinVersion: tls.VersionTLS12, ServerName, tls=true, mysql2, ssl.ca, fs.readFileSync('ca.pem'), rejectUnauthorized: true, SELECT DATABASE();, hostname verification, ca.pem
- Follow-up Guidance: The examples show querying `SELECT DATABASE();` after connecting and note that Node.js `ssl: { minVersion: 'TLSv1.2' }` can be changed to `TLSv1.3` if desired.
- Classification Note: This is classified as configuration because the content provides concrete client TLS connection settings and code examples for TiDB Cloud Dedicated.

## Official Source Content

```
package main
import (
  "crypto/tls"
  "crypto/x509"
  "database/sql"
  "fmt"
  "io/ioutil"
  "log"

  "github.com/go-sql-driver/mysql"
)
func main() {
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
  if err != nil {
    log.Fatal("failed to connect database", err)
  }
  defer db.Close()

  var dbName string
  err = db.QueryRow("SELECT DATABASE();").Scan(&dbName)
  if err != nil {
    log.Fatal("failed to execute query", err)
  }
  fmt.Println(dbName)
}
```

Parameter descriptions：

- Register `tls.Config` in the TLS connection configuration to enable TLS and validate TiDB Cloud Dedicated clusters.
- Set `MinVersion: tls.VersionTLS12` to restrict the versions of TLS protocol.
- Set `ServerName: "<host>"` to verify TiDB Cloud Dedicated's hostname.
- If you do not want to register a new TLS configuration, you can just set `tls=true` in the connection string.

</div>

<div label="Node.js">

[Mysql2](https://www.npmjs.com/package/mysql2)'s TLS connection configurations are used here as an example.

```
var connection = mysql.createConnection({
  host: 'tidb.srgnqxji5bc.clusters.staging.tidb-cloud.com',
  port: 4000,
  user: 'root',
  password: '<your_password>',
  database: 'test',
  ssl: {
    ca: fs.readFileSync('ca.pem'),
    minVersion: 'TLSv1.2',
    rejectUnauthorized: true
  }
});
```

You can click **show example usage** to view detailed code examples.

```
var mysql = require('mysql2');
var fs = require('fs');
var connection = mysql.createConnection({
  host: 'tidb.srgnqxji5bc.clusters.staging.tidb-cloud.com',
  port: 4000,
  user: 'root',
  password: '<your_password>',
  database: 'test',
  ssl: {
    ca: fs.readFileSync('ca.pem'),
    minVersion: 'TLSv1.2',
    rejectUnauthorized: true
  }
});
connection.connect(function(err) {
  if (err) {
    throw err
  }
  connection.query('SELECT DATABASE();', function(err, rows) {
    if (err) {
      throw err
    }
    console.log(rows[0]['DATABASE()']);
    connection.end()
  });
});
```

Parameter descriptions：

- Set `ssl: {minVersion: 'TLSv1.2'}` to restrict the versions of the TLS protocol. If you want to use TLS 1.3, you can set the version to `TLSv1.3`.
- Set `ssl: {ca: fs.readFileSync('<CA_path>')}` to read your local CA path of the downloaded TiDB cluster `ca.pem`.

</div>
