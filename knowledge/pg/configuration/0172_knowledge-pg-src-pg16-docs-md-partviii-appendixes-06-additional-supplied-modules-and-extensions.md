# Configuration; Security Limitations

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVIII_appendixes/06_additional_supplied_modules_and_extensions.md`
- Source Title: `postgresql.conf`
- Source Heading Path: `Additional Supplied Modules and Extensions > pgcrypto > PGP Options; Raw Encryption; Random Data; Notes > Configuration; Security Limitations`
- Source Line Ranges: `574-583, 617-742, 801-821, 838-850, 857-865, 866-869, 1475-1482, 1563-1583, 1801-1817, 2016-2029, 2088-2096, 2180-2185, 2258-2267, 2436-2453, 2644-2654, 2710-2720, 2789-2799, 2823-2841, 2881-2913, 5394-6101, 6240-6254, 6574-6632, 8484-8542, 10362-10411, 10909-10914, 11135-11145`
- Chunk ID: `pg16_configuration_0172_2f02c0ee44`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e4de527587002c16329a8ec41db7cac1538f8ee256c0e50a26fafca48d4ea196`

## Retrieval Guidance

- Use When: Configure pgcrypto encryption function options or interpret security limitations.
- Retrieval Keywords: pgcrypto, pgp_sym_encrypt, pgp_pub_encrypt, cipher-algo, s2k-mode, compress-algo, OpenSSL, FIPS
- Follow-up Guidance: Human security review is recommended for cryptographic choices and key handling.
- Classification Note: The section defines cryptographic function options and build/runtime caveats that configure encryption, compression, S2K, cipher, and random-data behavior.

## Official Source Content

### Configuration Parameters

**`auth_delay.milliseconds` (`integer`)**
: The number of milliseconds to wait before reporting an authentication
failure.  The default is 0.

These parameters must be set in `postgresql.conf`.
Typical usage might be:

```

### Configuration Parameters

There are several configuration parameters that control the behavior of
`auto_explain`.  Note that the default behavior is
to do nothing, so you must set at least
`auto_explain.log_min_duration` if you want any results.

**`auto_explain.log_min_duration` (`integer`)**
: `auto_explain.log_min_duration` is the minimum statement
execution time, in milliseconds, that will cause the statement's plan to
be logged. Setting this to `0` logs all plans.
`-1` (the default) disables logging of plans. For
example, if you set it to `250ms` then all statements
that run 250ms or longer will be logged. Only superusers can change this
setting.

**`auto_explain.log_parameter_max_length` (`integer`)**
: `auto_explain.log_parameter_max_length` controls the
logging of query parameter values. A value of `-1` (the
default) logs the parameter values in full. `0` disables
logging of parameter values. A value greater than zero truncates each
parameter value to that many bytes. Only superusers can change this
setting.

**`auto_explain.log_analyze` (`boolean`)**
: `auto_explain.log_analyze` causes `EXPLAIN ANALYZE`
output, rather than just `EXPLAIN` output, to be printed
when an execution plan is logged. This parameter is off by default.
Only superusers can change this setting.

> **Note:**
> When this parameter is on, per-plan-node timing occurs for all
> statements executed, whether or not they run long enough to actually
> get logged.  This can have an extremely negative impact on performance.
> Turning off `auto_explain.log_timing` ameliorates the
> performance cost, at the price of obtaining less information.
>

**`auto_explain.log_buffers` (`boolean`)**
: `auto_explain.log_buffers` controls whether buffer
usage statistics are printed when an execution plan is logged; it's
equivalent to the `BUFFERS` option of `EXPLAIN`.
This parameter has no effect
unless `auto_explain.log_analyze` is enabled.
This parameter is off by default.
Only superusers can change this setting.

**`auto_explain.log_wal` (`boolean`)**
: `auto_explain.log_wal` controls whether WAL
usage statistics are printed when an execution plan is logged; it's
equivalent to the `WAL` option of `EXPLAIN`.
This parameter has no effect
unless `auto_explain.log_analyze` is enabled.
This parameter is off by default.
Only superusers can change this setting.

**`auto_explain.log_timing` (`boolean`)**
: `auto_explain.log_timing` controls whether per-node
timing information is printed when an execution plan is logged; it's
equivalent to the `TIMING` option of `EXPLAIN`.
The overhead of repeatedly reading the system clock can slow down
queries significantly on some systems, so it may be useful to set this
parameter to off when only actual row counts, and not exact times, are
needed.
This parameter has no effect
unless `auto_explain.log_analyze` is enabled.
This parameter is on by default.
Only superusers can change this setting.

**`auto_explain.log_triggers` (`boolean`)**
: `auto_explain.log_triggers` causes trigger
execution statistics to be included when an execution plan is logged.
This parameter has no effect
unless `auto_explain.log_analyze` is enabled.
This parameter is off by default.
Only superusers can change this setting.

**`auto_explain.log_verbose` (`boolean`)**
: `auto_explain.log_verbose` controls whether verbose
details are printed when an execution plan is logged; it's
equivalent to the `VERBOSE` option of `EXPLAIN`.
This parameter is off by default.
Only superusers can change this setting.

**`auto_explain.log_settings` (`boolean`)**
: `auto_explain.log_settings` controls whether information
about modified configuration options is printed when an execution plan is logged.
Only options affecting query planning with value different from the built-in
default value are included in the output.  This parameter is off by default.
Only superusers can change this setting.

**`auto_explain.log_format` (`enum`)**
: `auto_explain.log_format` selects the
`EXPLAIN` output format to be used.
The allowed values are `text`, `xml`,
`json`, and `yaml`.  The default is text.
Only superusers can change this setting.

**`auto_explain.log_level` (`enum`)**
: `auto_explain.log_level` selects the log level at which
auto_explain will log the query plan.
Valid values are `DEBUG5`, `DEBUG4`,
`DEBUG3`, `DEBUG2`,
`DEBUG1`, `INFO`,
`NOTICE`, `WARNING`,
and `LOG`. The default is `LOG`.
Only superusers can change this setting.

**`auto_explain.log_nested_statements` (`boolean`)**
: `auto_explain.log_nested_statements` causes nested
statements (statements executed inside a function) to be considered
for logging.  When it is off, only top-level query plans are logged. This
parameter is off by default. Only superusers can change this setting.

**`auto_explain.sample_rate` (`real`)**
: `auto_explain.sample_rate` causes auto_explain to only
explain a fraction of the statements in each session.  The default is 1,
meaning explain all the queries.  In case of nested statements, either all
will be explained or none. Only superusers can change this setting.

In ordinary usage, these parameters are set
in `postgresql.conf`, although superusers can alter them
on-the-fly within their own sessions.
Typical usage might be:

```

### Configuration Parameters

**`basebackup_to_shell.command` (`string`)**
: The command which the server should execute for each archive generated
by the backup process. If `%f` occurs in the command
string, it will be replaced by the name of the archive (e.g.
`base.tar`). If `%d` occurs in the
command string, it will be replaced by the target detail provided by
the user. A target detail is required if `%d` is
used in the command string, and prohibited otherwise. For security
reasons, it may contain only alphanumeric characters. If
`%%` occurs in the command string, it will be replaced
by a single `%`. If `%` occurs in
the command string followed by any other character or at the end of the
string, an error occurs.

**`basebackup_to_shell.required_role` (`string`)**
: The role required in order to make use of the `shell`
backup target. If this is not set, any replication user may make use of
the `shell` backup target.

### Configuration Parameters

**`basic_archive.archive_directory` (`string`)**
: The directory where the server should copy WAL segment files.  This
directory must already exist.  The default is an empty string, which
effectively halts WAL archiving, but if [guc-archive-mode](#guc-archive-mode)
is enabled, the server will accumulate WAL segment files in the
expectation that a value will soon be provided.

These parameters must be set in `postgresql.conf`.
Typical usage might be:

```

### Notes

Server crashes may leave temporary files with the prefix
`archtemp` in the archive directory.  It is recommended to
delete such files before restarting the server after a crash.  It is safe to
remove such files while the server is running as long as they are unrelated
to any archiving still in progress, but users should use extra caution when
doing so.

### Author

Nathan Bossart

### Notes

For examples of usage, see the regression test `sql/cube.sql`.

To make it harder for people to break things, there
is a limit of 100 on the number of dimensions of cubes. This is set
in `cubedata.h` if you need something bigger.

## Notes

If untrusted users have access to a database that has not adopted a
[secure schema usage pattern](#ddl-schemas-patterns),
begin each session by removing publicly-writable schemas from
`search_path`.  One could, for example,
add `options=-csearch_path=` to

connstr.  This consideration is not specific
to `dblink`; it applies to every interface for
executing arbitrary SQL commands.

Only superusers may use `dblink_connect` to create
non-password-authenticated and non-GSSAPI-authenticated connections.
If non-superusers need this capability, use
`dblink_connect_u` instead.

It is unwise to choose connection names that contain equal signs,
as this opens a risk of confusion with connection info strings
in other `dblink` functions.

## Notes

A convenient way to use `dblink` with predetermined
queries is to create a view.
This allows the column type information to be buried in the view,
instead of having to spell it out in every query.  For example,

```
CREATE VIEW myremote_pg_proc AS
SELECT *
FROM dblink('dbname=postgres options=-csearch_path=',
'select proname, prosrc from pg_proc')
AS t1(proname name, prosrc text);

SELECT * FROM myremote_pg_proc WHERE proname LIKE 'bytea%';
```

## Notes

Since a cursor can only persist within a transaction,
`dblink_open` starts an explicit transaction block
(`BEGIN`) on the remote side, if the remote side was
not already within a transaction.  This transaction will be
closed again when the matching `dblink_close` is
executed.  Note that if
you use `dblink_exec` to change data between
`dblink_open` and `dblink_close`,
and then an error occurs or you use `dblink_disconnect` before
`dblink_close`, your change *will be
lost* because the transaction will be aborted.

## Notes

On a mismatch between the number of return columns specified in the
`FROM` clause, and the actual number of columns returned by the
remote cursor, an error will be thrown. In this event, the remote cursor
is still advanced by as many rows as it would have been if the error had
not occurred.  The same is true for any other error occurring in the local
query after the remote `FETCH` has been done.

## Notes

If `dblink_open` started an explicit transaction block,
and this is the last remaining open cursor in this connection,
`dblink_close` will issue the matching `COMMIT`.

## Notes

When asynchronous queries are initiated by
`dblink_send_query`, the error message associated with
the connection might not get updated until the server's response message
is consumed. This typically means that `dblink_is_busy`
or `dblink_get_result` should be called prior to
`dblink_error_message`, so that any error generated by
the asynchronous query will be visible.

## Notes

This function *must* be called if
`dblink_send_query` returned 1.
It must be called once for each query
sent, and one additional time to obtain an empty set result,
before the connection can be used again.

When using `dblink_send_query` and
`dblink_get_result`, dblink fetches the entire
remote query result before returning any of it to the local query
processor.  If the query returns a large number of rows, this can result
in transient memory bloat in the local session.  It may be better to open
such a query as a cursor with `dblink_open` and then fetch a
manageable number of rows at a time.  Alternatively, use plain
`dblink()`, which avoids memory bloat by spooling large result
sets to disk.

## Notes

As of PostgreSQL 9.0, the attribute numbers in

primary_key_attnums are interpreted as logical
column numbers, corresponding to the column's position in
`SELECT * FROM relname`.  Previous versions interpreted the
numbers as physical column positions.  There is a difference if any
column(s) to the left of the indicated column have been dropped during
the lifetime of the table.

## Notes

As of PostgreSQL 9.0, the attribute numbers in

primary_key_attnums are interpreted as logical
column numbers, corresponding to the column's position in
`SELECT * FROM relname`.  Previous versions interpreted the
numbers as physical column positions.  There is a difference if any
column(s) to the left of the indicated column have been dropped during
the lifetime of the table.

## Notes

As of PostgreSQL 9.0, the attribute numbers in

primary_key_attnums are interpreted as logical
column numbers, corresponding to the column's position in
`SELECT * FROM relname`.  Previous versions interpreted the
numbers as physical column positions.  There is a difference if any
column(s) to the left of the indicated column have been dropped during
the lifetime of the table.

### Configuration

The dictionary accepts three options:

- The `maxlen` parameter specifies the maximum number of
digits allowed in an integer word.  The default value is 6.
- The `rejectlong` parameter specifies whether an overlength
integer should be truncated or ignored.  If `rejectlong` is
`false` (the default), the dictionary returns the first
`maxlen` digits of the integer. If `rejectlong` is
`true`, the dictionary treats an overlength integer as a stop
word, so that it will not be indexed.  Note that this also means that
such an integer cannot be searched for.
- The `absval` parameter specifies whether leading
"`+`" or "`-`"
signs should be removed from integer words.  The default
is `false`.  When `true`, the sign is
removed before `maxlen` is applied.

### Configuration

A `dict_xsyn` dictionary accepts the following options:

- `matchorig` controls whether the original word is accepted by
the dictionary. Default is `true`.
- `matchsynonyms` controls whether the synonyms are
accepted by the dictionary. Default is `false`.
- `keeporig` controls whether the original word is included in
the dictionary's output. Default is `true`.
- `keepsynonyms` controls whether the synonyms are included in
the dictionary's output. Default is `true`.
- `rules` is the base name of the file containing the list of
synonyms.  This file must be stored in
`$SHAREDIR/tsearch_data/` (where `$SHAREDIR` means
the PostgreSQL installation's shared-data directory).
Its name must end in `.rules` (which is not to be included in
the `rules` parameter).

The rules file has the following format:

- Each line represents a group of synonyms for a single word, which is
given first on the line. Synonyms are separated by whitespace, thus:

```
word syn1 syn2 syn3
```
- The sharp (`#`) sign is a comment delimiter. It may appear at
any position in a line.  The rest of the line will be skipped.

Look at `xsyn_sample.rules`, which is installed in
`$SHAREDIR/tsearch_data/`, for an example.

## pgcrypto — cryptographic functions

The `pgcrypto` module provides cryptographic functions for
PostgreSQL.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

`pgcrypto` requires OpenSSL and won't be installed if
OpenSSL support was not selected when PostgreSQL was built.

### General Hashing Functions

#### `digest()`

```
digest(data text, type text) returns bytea
digest(data bytea, type text) returns bytea
```

Computes a binary hash of the given
data.

type is the algorithm to use.
Standard algorithms are `md5`, `sha1`,
`sha224`, `sha256`,
`sha384` and `sha512`.
Moreover, any digest algorithm OpenSSL supports
is automatically picked up.

If you want the digest as a hexadecimal string, use
`encode()` on the result.  For example:

```
CREATE OR REPLACE FUNCTION sha1(bytea) returns text AS $$
SELECT encode(digest($1, 'sha1'), 'hex')
$$ LANGUAGE SQL STRICT IMMUTABLE;
```

#### `hmac()`

```
hmac(data text, key text, type text) returns bytea
hmac(data bytea, key bytea, type text) returns bytea
```

Calculates hashed MAC for
data with key
key.

type is the same as in `digest()`.

This is similar to `digest()` but the hash can only be
recalculated knowing the key.  This prevents the scenario of someone
altering data and also changing the hash to match.

If the key is larger than the hash block size it will first be hashed and
the result will be used as key.

### Password Hashing Functions

The functions `crypt()` and `gen_salt()`
are specifically designed for hashing passwords.
`crypt()` does the hashing and `gen_salt()`
prepares algorithm parameters for it.

The algorithms in `crypt()` differ from the usual
MD5 or SHA1 hashing algorithms in the following respects:

1. They are slow.  As the amount of data is so small, this is the only
way to make brute-forcing passwords hard.
2. They use a random value, called the *salt*, so that users
having the same password will have different encrypted passwords.
This is also an additional defense against reversing the algorithm.
3. They include the algorithm type in the result, so passwords hashed with
different algorithms can co-exist.
4. Some of them are adaptive — that means when computers get
faster, you can tune the algorithm to be slower, without
introducing incompatibility with existing passwords.

[pgcrypto-crypt-algorithms](#pgcrypto-crypt-algorithms) lists the algorithms
supported by the `crypt()` function.

| Algorithm | Max Password Length | Adaptive? | Salt Bits | Output Length | Description |
| --- | --- | --- | --- | --- | --- |
| `bf` | 72 | yes | 128 | 60 | Blowfish-based, variant 2a |
| `md5` | unlimited | no | 48 | 34 | MD5-based crypt |
| `xdes` | 8 | yes | 24 | 20 | Extended DES |
| `des` | 8 | no | 12 | 13 | Original UNIX crypt |

#### `crypt()`

```
crypt(password text, salt text) returns text
```

Calculates a crypt(3)-style hash of
password.
When storing a new password, you need to use
`gen_salt()` to generate a new
salt value.
To check a password, pass the stored hash value as
salt,
and test whether the result matches the stored value.

Example of setting a new password:

```
UPDATE ... SET pswhash = crypt('new password', gen_salt('md5'));
```

Example of authentication:

```
SELECT (pswhash = crypt('entered password', pswhash)) AS pswmatch FROM ... ;
```

This returns `true` if the entered password is correct.

#### `gen_salt()`

```
gen_salt(type text [, iter_count integer ]) returns text
```

Generates a new random salt string for use in `crypt()`.
The salt string also tells `crypt()` which algorithm to use.

The
type parameter specifies the hashing algorithm.
The accepted types are: `des`, `xdes`,
`md5` and `bf`.

The
iter_count parameter lets the user specify the iteration
count, for algorithms that have one.
The higher the count, the more time it takes to hash
the password and therefore the more time to break it.  Although with
too high a count the time to calculate a hash may be several years
— which is somewhat impractical.  If the
iter_count
parameter is omitted, the default iteration count is used.
Allowed values for
iter_count depend on the algorithm and
are shown in [pgcrypto-icfc-table](#pgcrypto-icfc-table).

| Algorithm | Default | Min | Max |
| --- | --- | --- | --- |
| `xdes` | 725 | 1 | 16777215 |
| `bf` | 6 | 4 | 31 |

For `xdes` there is an additional limitation that the
iteration count must be an odd number.

To pick an appropriate iteration count, consider that
the original DES crypt was designed to have the speed of 4 hashes per
second on the hardware of that time.
Slower than 4 hashes per second would probably dampen usability.
Faster than 100 hashes per second is probably too fast.

[pgcrypto-hash-speed-table](#pgcrypto-hash-speed-table) gives an overview of the relative slowness
of different hashing algorithms.
The table shows how much time it would take to try all
combinations of characters in an 8-character password, assuming
that the password contains either only lower case letters, or
upper- and lower-case letters and numbers.
In the `crypt-bf` entries, the number after a slash is
the
iter_count parameter of
`gen_salt`.

| Algorithm | Hashes/sec | For `[a-z]` | For `[A-Za-z0-9]` | Duration relative to `md5 hash` |
| --- | --- | --- | --- | --- |
| `crypt-bf/8` | 1792 | 4 years | 3927 years | 100k |
| `crypt-bf/7` | 3648 | 2 years | 1929 years | 50k |
| `crypt-bf/6` | 7168 | 1 year | 982 years | 25k |
| `crypt-bf/5` | 13504 | 188 days | 521 years | 12.5k |
| `crypt-md5` | 171584 | 15 days | 41 years | 1k |
| `crypt-des` | 23221568 | 157.5 minutes | 108 days | 7 |
| `sha1` | 37774272 | 90 minutes | 68 days | 4 |
| `md5` (hash) | 150085504 | 22.5 minutes | 17 days | 1 |

Notes:

- The machine used is an Intel Mobile Core i3.
- `crypt-des` and `crypt-md5` algorithm numbers are
taken from John the Ripper v1.6.38 `-test` output.
- `md5 hash` numbers are from mdcrack 1.2.
- `sha1` numbers are from lcrack-20031130-beta.
- `crypt-bf` numbers are taken using a simple program that
loops over 1000 8-character passwords.  That way the speed
with different numbers of iterations can be shown.  For reference: `john
-test` shows 13506 loops/sec for `crypt-bf/5`.
(The very small
difference in results is in accordance with the fact that the
`crypt-bf` implementation in `pgcrypto`
is the same one used in John the Ripper.)

Note that "try all combinations" is not a realistic exercise.
Usually password cracking is done with the help of dictionaries, which
contain both regular words and various mutations of them.  So, even
somewhat word-like passwords could be cracked much faster than the above
numbers suggest, while a 6-character non-word-like password may escape
cracking.  Or not.

### PGP Encryption Functions

The functions here implement the encryption part of the OpenPGP
([RFC 4880](https://datatracker.ietf.org/doc/html/rfc4880))
standard.  Supported are both symmetric-key and public-key encryption.

An encrypted PGP message consists of 2 parts, or *packets*:

- Packet containing a session key — either symmetric-key or public-key
encrypted.
- Packet containing data encrypted with the session key.

When encrypting with a symmetric key (i.e., a password):

1. The given password is hashed using a String2Key (S2K) algorithm.  This is
rather similar to `crypt()` algorithms — purposefully
slow and with random salt — but it produces a full-length binary
key.
2. If a separate session key is requested, a new random key will be
generated.  Otherwise the S2K key will be used directly as the session
key.
3. If the S2K key is to be used directly, then only S2K settings will be put
into the session key packet.  Otherwise the session key will be encrypted
with the S2K key and put into the session key packet.

When encrypting with a public key:

1. A new random session key is generated.
2. It is encrypted using the public key and put into the session key packet.

In either case the data to be encrypted is processed as follows:

1. Optional data-manipulation: compression, conversion to UTF-8,
and/or conversion of line-endings.
2. The data is prefixed with a block of random bytes.  This is equivalent
to using a random IV.
3. A SHA1 hash of the random prefix and data is appended.
4. All this is encrypted with the session key and placed in the data packet.

#### `pgp_sym_encrypt()`

```
pgp_sym_encrypt(data text, psw text [, options text ]) returns bytea
pgp_sym_encrypt_bytea(data bytea, psw text [, options text ]) returns bytea
```

Encrypt
data with a symmetric PGP key
psw.
The
options parameter can contain option settings,
as described below.

#### `pgp_sym_decrypt()`

```
pgp_sym_decrypt(msg bytea, psw text [, options text ]) returns text
pgp_sym_decrypt_bytea(msg bytea, psw text [, options text ]) returns bytea
```

Decrypt a symmetric-key-encrypted PGP message.

Decrypting `bytea` data with `pgp_sym_decrypt` is disallowed.
This is to avoid outputting invalid character data.  Decrypting
originally textual data with `pgp_sym_decrypt_bytea` is fine.

The
options parameter can contain option settings,
as described below.

#### `pgp_pub_encrypt()`

```
pgp_pub_encrypt(data text, key bytea [, options text ]) returns bytea
pgp_pub_encrypt_bytea(data bytea, key bytea [, options text ]) returns bytea
```

Encrypt
data with a public PGP key
key.
Giving this function a secret key will produce an error.

The
options parameter can contain option settings,
as described below.

#### `pgp_pub_decrypt()`

```
pgp_pub_decrypt(msg bytea, key bytea [, psw text [, options text ]]) returns text
pgp_pub_decrypt_bytea(msg bytea, key bytea [, psw text [, options text ]]) returns bytea
```

Decrypt a public-key-encrypted message.
key must be the
secret key corresponding to the public key that was used to encrypt.
If the secret key is password-protected, you must give the password in

psw.  If there is no password, but you want to specify
options, you need to give an empty password.

Decrypting `bytea` data with `pgp_pub_decrypt` is disallowed.
This is to avoid outputting invalid character data.  Decrypting
originally textual data with `pgp_pub_decrypt_bytea` is fine.

The
options parameter can contain option settings,
as described below.

#### `pgp_key_id()`

```
pgp_key_id(bytea) returns text
```

`pgp_key_id` extracts the key ID of a PGP public or secret key.
Or it gives the key ID that was used for encrypting the data, if given
an encrypted message.

It can return 2 special key IDs:

- `SYMKEY`

The message is encrypted with a symmetric key.
- `ANYKEY`

The message is public-key encrypted, but the key ID has been removed.
That means you will need to try all your secret keys on it to see
which one decrypts it.  `pgcrypto` itself does not produce
such messages.

Note that different keys may have the same ID.   This is rare but a normal
event. The client application should then try to decrypt with each one,
to see which fits — like handling `ANYKEY`.

#### `armor()`, `dearmor()`

```
armor(data bytea [ , keys text[], values text[] ]) returns text
dearmor(data text) returns bytea
```

These functions wrap/unwrap binary data into PGP ASCII-armor format,
which is basically Base64 with CRC and additional formatting.

If the
keys and
values arrays are specified,
an *armor header* is added to the armored format for each
key/value pair. Both arrays must be single-dimensional, and they must
be of the same length.  The keys and values cannot contain any non-ASCII
characters.

#### `pgp_armor_headers`

```
pgp_armor_headers(data text, key out text, value out text) returns setof record
```

`pgp_armor_headers()` extracts the armor headers from

data.  The return value is a set of rows with two columns,
key and value.  If the keys or values contain any non-ASCII characters,
they are treated as UTF-8.

#### Options for PGP Functions

Options are named to be similar to GnuPG.  An option's value should be
given after an equal sign; separate options from each other with commas.
For example:

```
pgp_sym_encrypt(data, psw, 'compress-algo=1, cipher-algo=aes256')
```

All of the options except `convert-crlf` apply only to
encrypt functions.  Decrypt functions get the parameters from the PGP
data.

The most interesting options are probably
`compress-algo` and `unicode-mode`.
The rest should have reasonable defaults.

##### cipher-algo

Which cipher algorithm to use.

```
Values: bf, aes128, aes192, aes256, 3des, cast5
Default: aes128
Applies to: pgp_sym_encrypt, pgp_pub_encrypt
```

##### compress-algo

Which compression algorithm to use.  Only available if
PostgreSQL was built with zlib.

```
Values:
0 - no compression
1 - ZIP compression
2 - ZLIB compression (= ZIP plus meta-data and block CRCs)
Default: 0
Applies to: pgp_sym_encrypt, pgp_pub_encrypt
```

##### compress-level

How much to compress.  Higher levels compress smaller but are slower.
0 disables compression.

```
Values: 0, 1-9
Default: 6
Applies to: pgp_sym_encrypt, pgp_pub_encrypt
```

##### convert-crlf

Whether to convert `\n` into `\r\n` when
encrypting and `\r\n` to `\n` when
decrypting.  RFC 4880 specifies that text data should be stored using
`\r\n` line-feeds.  Use this to get fully RFC-compliant
behavior.

```
Values: 0, 1
Default: 0
Applies to: pgp_sym_encrypt, pgp_pub_encrypt, pgp_sym_decrypt, pgp_pub_decrypt
```

##### disable-mdc

Do not protect data with SHA-1.  The only good reason to use this
option is to achieve compatibility with ancient PGP products, predating
the addition of SHA-1 protected packets to RFC 4880.
Recent gnupg.org and pgp.com software supports it fine.

```
Values: 0, 1
Default: 0
Applies to: pgp_sym_encrypt, pgp_pub_encrypt
```

##### sess-key

Use separate session key.  Public-key encryption always uses a separate
session key; this option is for symmetric-key encryption, which by default
uses the S2K key directly.

```
Values: 0, 1
Default: 0
Applies to: pgp_sym_encrypt
```

##### s2k-mode

Which S2K algorithm to use.

```
Values:
0 - Without salt.  Dangerous!
1 - With salt but with fixed iteration count.
3 - Variable iteration count.
Default: 3
Applies to: pgp_sym_encrypt
```

##### s2k-count

The number of iterations of the S2K algorithm to use.  It must
be a value between 1024 and 65011712, inclusive.

```
Default: A random value between 65536 and 253952
Applies to: pgp_sym_encrypt, only with s2k-mode=3
```

##### s2k-digest-algo

Which digest algorithm to use in S2K calculation.

```
Values: md5, sha1
Default: sha1
Applies to: pgp_sym_encrypt
```

##### s2k-cipher-algo

Which cipher to use for encrypting separate session key.

```
Values: bf, aes, aes128, aes192, aes256
Default: use cipher-algo
Applies to: pgp_sym_encrypt
```

##### unicode-mode

Whether to convert textual data from database internal encoding to
UTF-8 and back.  If your database already is UTF-8, no conversion will
be done, but the message will be tagged as UTF-8.  Without this option
it will not be.

```
Values: 0, 1
Default: 0
Applies to: pgp_sym_encrypt, pgp_pub_encrypt
```

#### Generating PGP Keys with GnuPG

To generate a new key:

```
gpg --gen-key
```

The preferred key type is "DSA and Elgamal".

For RSA encryption you must create either DSA or RSA sign-only key
as master and then add an RSA encryption subkey with
`gpg --edit-key`.

To list keys:

```
gpg --list-secret-keys
```

To export a public key in ASCII-armor format:

```
gpg -a --export KEYID > public.key
```

To export a secret key in ASCII-armor format:

```
gpg -a --export-secret-keys KEYID > secret.key
```

You need to use `dearmor()` on these keys before giving them to
the PGP functions.  Or if you can handle binary data, you can drop
`-a` from the command.

For more details see `man gpg`,
[The GNU
Privacy Handbook](https://www.gnupg.org/gph/en/manual.html) and other documentation on
[](https://www.gnupg.org/).

#### Limitations of PGP Code

- No support for signing.  That also means that it is not checked
whether the encryption subkey belongs to the master key.
- No support for encryption key as master key.  As such practice
is generally discouraged, this should not be a problem.
- No support for several subkeys.  This may seem like a problem, as this
is common practice.  On the other hand, you should not use your regular
GPG/PGP keys with `pgcrypto`, but create new ones,
as the usage scenario is rather different.

### Raw Encryption Functions

These functions only run a cipher over data; they don't have any advanced
features of PGP encryption.  Therefore they have some major problems:

1. They use user key directly as cipher key.
2. They don't provide any integrity checking, to see
if the encrypted data was modified.
3. They expect that users manage all encryption parameters
themselves, even IV.
4. They don't handle text.

So, with the introduction of PGP encryption, usage of raw
encryption functions is discouraged.

```
encrypt(data bytea, key bytea, type text) returns bytea
decrypt(data bytea, key bytea, type text) returns bytea

encrypt_iv(data bytea, key bytea, iv bytea, type text) returns bytea
decrypt_iv(data bytea, key bytea, iv bytea, type text) returns bytea
```

Encrypt/decrypt data using the cipher method specified by

type.  The syntax of the

type string is:

```
`algorithm` ` `-` `mode`   `/pad:` `padding`
```

where `algorithm` is one of:

- `bf` — Blowfish
- `aes` — AES (Rijndael-128, -192 or -256)

and `mode` is one of:

- `cbc` — next block depends on previous (default)
- `ecb` — each block is encrypted separately (for
testing only)

and `padding` is one of:

- `pkcs` — data may be any length (default)
- `none` — data must be multiple of cipher block size

So, for example, these are equivalent:

```
encrypt(data, 'fooz', 'bf')
encrypt(data, 'fooz', 'bf-cbc/pad:pkcs')
```

In `encrypt_iv` and `decrypt_iv`, the

iv parameter is the initial value for the CBC mode;
it is ignored for ECB.
It is clipped or padded with zeroes if not exactly block size.
It defaults to all zeroes in the functions without this parameter.

### Random-Data Functions

```
gen_random_bytes(count integer) returns bytea
```

Returns
count cryptographically strong random bytes.
At most 1024 bytes can be extracted at a time.  This is to avoid
draining the randomness generator pool.

```
gen_random_uuid() returns uuid
```

Returns a version 4 (random) UUID. (Obsolete, this function
internally calls the [core
function](#functions-uuid) of the same name.)

### Notes

#### Configuration

`pgcrypto` configures itself according to the findings of the
main PostgreSQL `configure` script.  The options that
affect it are `--with-zlib` and
`--with-ssl=openssl`.

When compiled with zlib, PGP encryption functions are able to
compress data before encrypting.

`pgcrypto` requires OpenSSL.
Otherwise, it will not be built or installed.

When compiled against OpenSSL 3.0.0 and later
versions, the legacy provider must be activated in the
`openssl.cnf` configuration file in order to use older
ciphers like DES or Blowfish.

#### NULL Handling

As is standard in SQL, all functions return NULL, if any of the arguments
are NULL.  This may create security risks on careless usage.

#### Security Limitations

All `pgcrypto` functions run inside the database server.
That means that all
the data and passwords move between `pgcrypto` and client
applications in clear text.  Thus you must:

1. Connect locally or use SSL connections.
2. Trust both system and database administrator.

If you cannot, then better do crypto inside client application.

The implementation does not resist
[side-channel
attacks](https://en.wikipedia.org/wiki/Side-channel_attack).  For example, the time required for
a `pgcrypto` decryption function to complete varies among
ciphertexts of a given size.

### Author

Marko Kreen markokr@gmail.com

`pgcrypto` uses code from the following sources:

| Algorithm | Author | Source origin |
| --- | --- | --- |
| DES crypt | David Burren and others | FreeBSD libcrypt |
| MD5 crypt | Poul-Henning Kamp | FreeBSD libcrypt |
| Blowfish crypt | Solar Designer | www.openwall.com |

### Configuration Parameters

**`pg_prewarm.autoprewarm` (`boolean`)**
: Controls whether the server should run the autoprewarm worker. This is
on by default. This parameter can only be set at server start.

**`pg_prewarm.autoprewarm_interval` (`integer`)**
: This is the interval between updates to `autoprewarm.blocks`.
The default is 300 seconds. If set to 0, the file will not be
dumped at regular intervals, but only when the server is shut down.

These parameters must be set in `postgresql.conf`.
Typical usage might be:

```

### Configuration Parameters

**`pg_stat_statements.max` (`integer`)**
: `pg_stat_statements.max` is the maximum number of
statements tracked by the module (i.e., the maximum number of rows
in the `pg_stat_statements` view).  If more distinct
statements than that are observed, information about the least-executed
statements is discarded.  The number of times such information was
discarded can be seen in the
`pg_stat_statements_info` view.
The default value is 5000.
This parameter can only be set at server start.

**`pg_stat_statements.track` (`enum`)**
: `pg_stat_statements.track` controls which statements
are counted by the module.
Specify `top` to track top-level statements (those issued
directly by clients), `all` to also track nested statements
(such as statements invoked within functions), or `none` to
disable statement statistics collection.
The default value is `top`.
Only superusers can change this setting.

**`pg_stat_statements.track_utility` (`boolean`)**
: `pg_stat_statements.track_utility` controls whether
utility commands are tracked by the module.  Utility commands are
all those other than `SELECT`, `INSERT`,
`UPDATE`, `DELETE`, and `MERGE`.
The default value is `on`.
Only superusers can change this setting.

**`pg_stat_statements.track_planning` (`boolean`)**
: `pg_stat_statements.track_planning` controls whether
planning operations and duration are tracked by the module.
Enabling this parameter may incur a noticeable performance penalty,
especially when statements with identical query structure are executed
by many concurrent connections which compete to update a small number of
`pg_stat_statements` entries.
The default value is `off`.
Only superusers can change this setting.

**`pg_stat_statements.save` (`boolean`)**
: `pg_stat_statements.save` specifies whether to
save statement statistics across server shutdowns.
If it is `off` then statistics are not saved at
shutdown nor reloaded at server start.
The default value is `on`.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

The module requires additional shared memory proportional to
`pg_stat_statements.max`.  Note that this
memory is consumed whenever the module is loaded, even if
`pg_stat_statements.track` is set to `none`.

These parameters must be set in `postgresql.conf`.
Typical usage might be:

```

### Configuration Parameters

**`postgres_fdw.application_name` (`string`)**
: Specifies a value for [guc-application-name](#guc-application-name)
configuration parameter used when `postgres_fdw`
establishes a connection to a foreign server.  This overrides
`application_name` option of the server object.
Note that change of this parameter doesn't affect any existing
connections until they are re-established.

`postgres_fdw.application_name` can be any string
of any length and contain even non-ASCII characters.  However when
it's passed to and used as `application_name`
in a foreign server, note that it will be truncated to less than
`NAMEDATALEN` characters.
Anything other than printable ASCII characters are replaced with [C-style hexadecimal escapes](#sql-syntax-strings-escape).
See [guc-application-name](#guc-application-name) for details.

`%` characters begin "escape sequences"
that are replaced with status information as outlined below.
Unrecognized escapes are ignored. Other characters are copied straight
to the application name. Note that it's not allowed to specify a
plus/minus sign or a numeric literal after the `%`
and before the option, for alignment and padding.

Escape
Effect

`%a`
Application name on local server

`%c`

Session ID on local server
(see [guc-log-line-prefix](#guc-log-line-prefix) for details)

`%C`

Cluster name on local server
(see [guc-cluster-name](#guc-cluster-name) for details)

`%u`
User name on local server

`%d`
Database name on local server

`%p`
Process ID of backend on local server

`%%`
Literal %

For example, suppose user `local_user` establishes
a connection from database `local_db` to
`foreign_db` as user `foreign_user`,
the setting `'db=%d, user=%u'` is replaced with
`'db=local_db, user=local_user'`.

### Configuration

An `unaccent` dictionary accepts the following options:

- `RULES` is the base name of the file containing the list of
translation rules.  This file must be stored in
`$SHAREDIR/tsearch_data/` (where `$SHAREDIR` means
the PostgreSQL installation's shared-data directory).
Its name must end in `.rules` (which is not to be included in
the `RULES` parameter).

The rules file has the following format:

- Each line represents one translation rule, consisting of a character with
accent followed by a character without accent.  The first is translated
into the second.  For example,

```
A
A
A
A
A
A
AE
```

The two characters must be separated by whitespace, and any leading or
trailing whitespace on a line is ignored.
- Alternatively, if only one character is given on a line, instances of
that character are deleted; this is useful in languages where accents
are represented by separate characters.
- Actually, each "character" can be any string not containing
whitespace, so `unaccent` dictionaries could be used for
other sorts of substring substitutions besides diacritic removal.
- As with other PostgreSQL text search configuration files,
the rules file must be stored in UTF-8 encoding.  The data is
automatically translated into the current database's encoding when
loaded.  Any lines containing untranslatable characters are silently
ignored, so that rules files can contain rules that are not applicable in
the current encoding.

A more complete example, which is directly useful for most European
languages, can be found in `unaccent.rules`, which is installed
in `$SHAREDIR/tsearch_data/` when the `unaccent`
module is installed.  This rules file translates characters with accents
to the same characters without accents, and it also expands ligatures
into the equivalent series of simple characters (for example,  to
AE).

## Notes

oid2name requires a running database server with
non-corrupt system catalogs.  It is therefore of only limited use
for recovering from catastrophic database corruption situations.

## Notes

vacuumlo works by the following method:
First, vacuumlo builds a temporary table which contains all
of the OIDs of the large objects in the selected database.  It then scans
through all columns in the database that are of type
`oid` or `lo`, and removes matching entries from the temporary
table.  (Note: Only types with these names are considered; in particular,
domains over them are not considered.)  The remaining entries in the
temporary table identify orphaned LOs.  These are removed.
