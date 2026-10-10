# mysql2 connection and CRUD code snippets

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-ruby-mysql2.md`
- Source Title: `Connect to TiDB with mysql2`
- Source Heading Path: `Connect to TiDB with mysql2 > Sample code snippets | Connect to TiDB with mysql2 > Sample code snippets > Connect to TiDB with connection options | Connect to TiDB with mysql2 > Sample code snippets > Insert data | Connect to TiDB with mysql2 > Sample code snippets > Query data | Connect to TiDB with mysql2 > Sample code snippets > Update data | Connect to TiDB with mysql2 > Sample code snippets > Delete data | Connect to TiDB with mysql2 > Best practices`
- Source Line Ranges: `205-306`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `shared`, `cloud`
- Topic Tags: `ruby`, `mysql2`, `code-snippets`, `connection-options`, `dotenv`, `environment-variables`, `tls`, `sslca`, `insert`, `query`, `update`, `delete`, `crud`, `best-practices`, `ca-certificates`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0177_436a6c461c`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-ruby-mysql2.md#sample-code-snippets`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7bcbeddb5d79684236591384ce99b6db80e719be67f52c941534bc5b6d24d62a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-ruby-mysql2#sample-code-snippets
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-ruby-mysql2.md

## Retrieval Guidance

- Use When: Use this chunk when you need Ruby mysql2 code examples for connecting to TiDB with environment variables and TLS options, or basic CRUD functions for the players table.
- Retrieval Keywords: Sample code snippets, Mysql2::Client.new(options), Dotenv.load, require 'mysql2', DATABASE_ENABLE_SSL, DATABASE_SSL_CA, ssl_mode: :verify_identity, sslca, create_player, get_player_by_id, update_player, delete_player_by_id, INSERT INTO players (coins, goods) VALUES, SELECT id, coins, goods FROM players WHERE id, UPDATE players SET coins = coins +, DELETE FROM players WHERE id, client.last_id, client.affected_rows, Best practices, CA certificates
- Follow-up Guidance: The best practices section explains the default CA certificate search paths and notes that setting `sslca` to `nil` is recommended for flexibility across different environments.
- Classification Note: This is classified as reference because the content mainly provides reusable code snippets, exact connection options, SQL statements, and related notes for development lookup.

## Official Source Content

## Sample code snippets

You can refer to the following sample code snippets to complete your own application development.

For complete sample code and how to run it, check out the [tidb-samples/tidb-ruby-mysql2-quickstart](https://github.com/tidb-samples/tidb-ruby-mysql2-quickstart) repository.
### Connect to TiDB with connection options

The following code establishes a connection to TiDB with options defined in the environment variables:

```ruby
require 'dotenv/load'
require 'mysql2'
Dotenv.load # Load the environment variables from the .env file

options = {
  host: ENV['DATABASE_HOST'] || '127.0.0.1',
  port: ENV['DATABASE_PORT'] || 4000,
  username: ENV['DATABASE_USER'] || 'root',
  password: ENV['DATABASE_PASSWORD'] || '',
  database: ENV['DATABASE_NAME'] || 'test'
}
options.merge(ssl_mode: :verify_identity) unless ENV['DATABASE_ENABLE_SSL'] == 'false'
options.merge(sslca: ENV['DATABASE_SSL_CA']) if ENV['DATABASE_SSL_CA']
client = Mysql2::Client.new(options)
```

> **Note**
>
> For [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential), TLS connection **MUST** be enabled via `DATABASE_ENABLE_SSL` when using public endpoint, but you **don't** have to specify an SSL CA certificate via `DATABASE_SSL_CA`, because mysql2 gem will search for existing CA certificates in a particular order until a file is discovered.
### Insert data

The following query creates a single player with two fields and returns the `last_insert_id`:

```ruby
def create_player(client, coins, goods)
  result = client.query(
    "INSERT INTO players (coins, goods) VALUES (#{coins}, #{goods});"
  )
  client.last_id
end
```

For more information, refer to [Insert data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data).
### Query data

The following query returns the record of a specific player by ID:

```ruby
def get_player_by_id(client, id)
  result = client.query(
    "SELECT id, coins, goods FROM players WHERE id = #{id};"
  )
  result.first
end
```

For more information, refer to [Query data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table).
### Update data

The following query updated the record of a specific player by ID:

```ruby
def update_player(client, player_id, inc_coins, inc_goods)
  result = client.query(
    "UPDATE players SET coins = coins + #{inc_coins}, goods = goods + #{inc_goods} WHERE id = #{player_id};"
  )
  client.affected_rows
end
```

For more information, refer to [Update data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data).
### Delete data

The following query deletes the record of a specific player:

```ruby
def delete_player_by_id(client, id)
  result = client.query(
    "DELETE FROM players WHERE id = #{id};"
  )
  client.affected_rows
end
```

For more information, refer to [Delete data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data).
## Best practices

By default, the mysql2 gem can search for existing CA certificates in a particular order until a file is discovered.

1. `/etc/ssl/certs/ca-certificates.crt` for Debian, Ubuntu, Gentoo, Arch, or Slackware
2. `/etc/pki/tls/certs/ca-bundle.crt` for RedHat, Fedora, CentOS, Mageia, Vercel, or Netlify
3. `/etc/ssl/ca-bundle.pem` for OpenSUSE
4. `/etc/ssl/cert.pem` for macOS or Alpine (docker container)

While it is possible to specify the CA certificate path manually, doing so might cause significant inconvenience in multi-environment deployment scenarios, because different machines and environments might store the CA certificate in different locations. Therefore, setting `sslca` to `nil` is recommended for flexibility and ease of deployment across different environments.
