# Rails ActiveRecord connection and CRUD snippets

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-ruby-rails.md`
- Source Title: `Connect to TiDB with Rails framework and ActiveRecord ORM`
- Source Heading Path: `Connect to TiDB with Rails Framework and ActiveRecord ORM > Sample code snippets | Connect to TiDB with Rails Framework and ActiveRecord ORM > Sample code snippets > Connect to TiDB with connection options | Connect to TiDB with Rails Framework and ActiveRecord ORM > Sample code snippets > Insert data | Connect to TiDB with Rails Framework and ActiveRecord ORM > Sample code snippets > Query data | Connect to TiDB with Rails Framework and ActiveRecord ORM > Sample code snippets > Update data | Connect to TiDB with Rails Framework and ActiveRecord ORM > Sample code snippets > Delete data | Connect to TiDB with Rails Framework and ActiveRecord ORM > Best practices`
- Source Line Ranges: `198-280`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `cloud`, `shared`, `sql`
- Topic Tags: `rails`, `activerecord`, `ruby`, `database-yml`, `database-url`, `tls`, `mysql2`, `crud`, `insert`, `query`, `update`, `delete`, `ca-certificates`, `best-practices`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0179_007eb4828e`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-ruby-rails.md#sample-code-snippets`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0fdcd01328aed3a69cd5cbfefe59e6f9f29e1c5556b11a394e465eee86f336ed`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-ruby-rails#sample-code-snippets
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-ruby-rails.md

## Retrieval Guidance

- Use When: Use this chunk when you need reference snippets for Rails ActiveRecord connection settings in config/database.yml, CRUD examples for the Player model, or notes about mysql2 CA certificate handling.
- Retrieval Keywords: config/database.yml, adapter: mysql2, encoding: utf8mb4, url: <%= ENV["DATABASE_URL"] %>, quickstart_test, ssl_mode, verify_identity, sslca, mysql2 gem, Player.create!(coins: 100, goods: 100), Player.find_by(id: new_player.id), player.update(coins: 50, goods: 50), player.destroy, Insert data, Query data, Update data, Delete data, CA certificates, /etc/ssl/certs/ca-certificates.crt, /etc/pki/tls/certs/ca-bundle.crt, /etc/ssl/ca-bundle.pem, /etc/ssl/cert.pem, setting sslca to nil
- Follow-up Guidance: The source points to the tidb-samples/tidb-ruby-rails-quickstart repository for the complete sample code and links to separate TiDB docs for insert, query, update, and delete data.
- Classification Note: This chunk is classified as reference because the official content provides reusable connection configuration, CRUD code snippets, and CA certificate behavior details rather than a full setup procedure.

## Official Source Content

## Sample code snippets

You can refer to the following sample code snippets to complete your own application development.

For complete sample code and how to run it, check out the [tidb-samples/tidb-ruby-rails-quickstart](https://github.com/tidb-samples/tidb-ruby-rails-quickstart) repository.
### Connect to TiDB with connection options

The following code in `config/database.yml` establishes a connection to TiDB with options defined in the environment variables:

```yml
default: &default
  adapter: mysql2
  encoding: utf8mb4
  pool: <%= ENV.fetch("RAILS_MAX_THREADS") { 5 } %>
  url: <%= ENV["DATABASE_URL"] %>

development:
  <<: *default

test:
  <<: *default
  database: quickstart_test

production:
  <<: *default
```

> **Note**
>
> For [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential), TLS connection **MUST** be enabled via setting the `ssl_mode` query parameter to `verify_identity` in `DATABASE_URL` when using public endpoint, but you **don't** have to specify an SSL CA certificate via `DATABASE_URL`, because mysql2 gem will search for existing CA certificates in a particular order until a file is discovered.
### Insert data

The following query creates a single Player with two fields and returns the created `Player` object:

```ruby
new_player = Player.create!(coins: 100, goods: 100)
```

For more information, refer to [Insert data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data).
### Query data

The following query returns the record of a specific player by ID:

```ruby
player = Player.find_by(id: new_player.id)
```

For more information, refer to [Query data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table).
### Update data

The following query updates a `Player` object:

```ruby
player.update(coins: 50, goods: 50)
```

For more information, refer to [Update data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data).
### Delete data

The following query deletes a `Player` object:

```ruby
player.destroy
```

For more information, refer to [Delete data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data).
## Best practices

By default, the mysql2 gem (used by ActiveRecord ORM to connect TiDB) will search for existing CA certificates in a particular order until a file is discovered.

1. /etc/ssl/certs/ca-certificates.crt # Debian / Ubuntu / Gentoo / Arch / Slackware
2. /etc/pki/tls/certs/ca-bundle.crt # RedHat / Fedora / CentOS / Mageia / Vercel / Netlify
3. /etc/ssl/ca-bundle.pem # OpenSUSE
4. /etc/ssl/cert.pem # MacOS / Alpine (docker container)

While it is possible to specify the CA certificate path manually, this approach may cause significant inconvenience in multi-environment deployment scenarios, as different machines and environments may store the CA certificate in varying locations. Therefore, setting `sslca` to `nil` is recommended for flexibility and ease of deployment across different environments.
