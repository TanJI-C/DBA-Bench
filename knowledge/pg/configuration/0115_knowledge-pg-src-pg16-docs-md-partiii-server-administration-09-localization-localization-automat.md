# Automatic Character Set Conversion Between Server and Client

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/09_localization.md`
- Source Title: `Localization`
- Source Heading Path: `Localization > Automatic Character Set Conversion Between Server and Client`
- Source Line Ranges: `496-570`
- Chunk ID: `pg16_configuration_0115_b341cda8af`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9c08e65c697d00833b805e52871e136bbb2125027e430bdd8e1ecbf97f56c825`

## Retrieval Guidance

- Use When: 客户端字符集乱码、转换错误或需要设置连接编码。
- Retrieval Keywords: client_encoding, \encoding, SET CLIENT_ENCODING, SET NAMES, SHOW client_encoding, PGCLIENTENCODING, SQL_ASCII, encoding conversion error
- Follow-up Guidance: 避免 SQL_ASCII，确认 server encoding 与 client encoding 可转换。
- Classification Note: 说明 client_encoding 设置方式、PGCLIENTENCODING、SET NAMES、\encoding、SQL_ASCII 风险和转换失败错误。

## Official Source Content

### Automatic Character Set Conversion Between Server and Client

PostgreSQL supports automatic character
set conversion between server and client for many combinations of
character sets ([multibyte-conversions-supported](#multibyte-conversions-supported)
shows which ones).

To enable automatic character set conversion, you have to
tell PostgreSQL the character set
(encoding) you would like to use in the client. There are several
ways to accomplish this:

- Using the `\encoding` command in
psql.
`\encoding` allows you to change client
encoding on the fly. For
example, to change the encoding to `SJIS`, type:

```
\encoding SJIS
```
- libpq ([libpq-control](#libpq-control)) has functions to control the client encoding.
- Using `SET client_encoding TO`.

Setting the client encoding can be done with this SQL command:

```
SET CLIENT_ENCODING TO '`value`';
```

Also you can use the standard SQL syntax `SET NAMES`
for this purpose:

```
SET NAMES '`value`';
```

To query the current client encoding:

```
SHOW client_encoding;
```

To return to the default encoding:

```
RESET client_encoding;
```
- Using `PGCLIENTENCODING`. If the environment variable
`PGCLIENTENCODING` is defined in the client's
environment, that client encoding is automatically selected
when a connection to the server is made.  (This can
subsequently be overridden using any of the other methods
mentioned above.)
- Using the configuration variable [guc-client-encoding](#guc-client-encoding). If the
`client_encoding` variable is set, that client
encoding is automatically selected when a connection to the
server is made.  (This can subsequently be overridden using any
of the other methods mentioned above.)

If the conversion of a particular character is not possible
— suppose you chose `EUC_JP` for the
server and `LATIN1` for the client, and some
Japanese characters are returned that do not have a representation in
`LATIN1` — an error is reported.

If the client character set is defined as `SQL_ASCII`,
encoding conversion is disabled, regardless of the server's character
set.  (However, if the server's character set is
not `SQL_ASCII`, the server will still check that
incoming data is valid for that encoding; so the net effect is as
though the client character set were the same as the server's.)
Just as for the server, use of `SQL_ASCII` is unwise
unless you are working with all-ASCII data.
