# Predefined Collations

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/09_localization.md`
- Source Title: `Localization`
- Source Heading Path: `Localization > Locale Support > ICU Locales > Predefined Collations`
- Source Line Ranges: `18-772`
- Chunk ID: `pg16_fact_0023_79459af00f`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b55ca28d786195bd51025679326bc6d11b847534374cc86824ed7970dd4e7ace`

## Retrieval Guidance

- Use When: 需要查看数据库当前可用 collations 或理解预定义 collation 来源。
- Retrieval Keywords: predefined collations, pg_collation, \dOS+, unicode, ucs_basic, initdb collations
- Follow-up Guidance: 可用 pg_import_system_collations 导入新增 OS locale。
- Classification Note: 说明 initdb 填充 pg_collation、SELECT * FROM pg_collation、\dOS+、unicode/ucs_basic 等预定义 collations。

## Official Source Content

## Locale Support

*Locale* support refers to an application respecting
cultural preferences regarding alphabets, sorting, number
formatting, etc.  PostgreSQL uses the standard ISO
C and POSIX locale facilities provided by the server operating
system.  For additional information refer to the documentation of your
system.

### Overview

Locale support is automatically initialized when a database
cluster is created using `initdb`.
`initdb` will initialize the database cluster
with the locale setting of its execution environment by default,
so if your system is already set to use the locale that you want
in your database cluster then there is nothing else you need to
do.  If you want to use a different locale (or you are not sure
which locale your system is set to), you can instruct
`initdb` exactly which locale to use by
specifying the `--locale` option. For example:

```
initdb --locale=sv_SE
```

This example for Unix systems sets the locale to Swedish
(`sv`) as spoken
in Sweden (`SE`).  Other possibilities might include
`en_US` (U.S. English) and `fr_CA` (French
Canadian).  If more than one character set can be used for a
locale then the specifications can take the form
`language_territory.codeset`.  For example,
`fr_BE.UTF-8` represents the French language (fr) as
spoken in Belgium (BE), with a UTF-8 character set
encoding.

What locales are available on your
system under what names depends on what was provided by the operating
system vendor and what was installed.  On most Unix systems, the command
`locale -a` will provide a list of available locales.
Windows uses more verbose locale names, such as `German_Germany`
or `Swedish_Sweden.1252`, but the principles are the same.

Occasionally it is useful to mix rules from several locales, e.g.,
use English collation rules but Spanish messages.  To support that, a
set of locale subcategories exist that control only certain
aspects of the localization rules:

| `LC_COLLATE` | String sort order |
| --- | --- |
| `LC_CTYPE` | Character classification (What is a letter? Its upper-case equivalent?) |
| `LC_MESSAGES` | Language of messages |
| `LC_MONETARY` | Formatting of currency amounts |
| `LC_NUMERIC` | Formatting of numbers |
| `LC_TIME` | Formatting of dates and times |

The category names translate into names of
`initdb` options to override the locale choice
for a specific category.  For instance, to set the locale to
French Canadian, but use U.S. rules for formatting currency, use
`initdb --locale=fr_CA --lc-monetary=en_US`.

If you want the system to behave as if it had no locale support,
use the special locale name `C`, or equivalently
`POSIX`.

Some locale categories must have their values
fixed when the database is created.  You can use different settings
for different databases, but once a database is created, you cannot
change them for that database anymore. `LC_COLLATE`
and `LC_CTYPE` are these categories.  They affect
the sort order of indexes, so they must be kept fixed, or indexes on
text columns would become corrupt.
(But you can alleviate this restriction using collations, as discussed
in [collation](#collation).)
The default values for these
categories are determined when `initdb` is run, and
those values are used when new databases are created, unless
specified otherwise in the `CREATE DATABASE` command.

The other locale categories can be changed whenever desired
by setting the server configuration parameters
that have the same name as the locale categories (see [runtime-config-client-format](#runtime-config-client-format) for details).  The values
that are chosen by `initdb` are actually only written
into the configuration file `postgresql.conf` to
serve as defaults when the server is started.  If you remove these
assignments from `postgresql.conf` then the
server will inherit the settings from its execution environment.

Note that the locale behavior of the server is determined by the
environment variables seen by the server, not by the environment
of any client.  Therefore, be careful to configure the correct locale settings
before starting the server.  A consequence of this is that if
client and server are set up in different locales, messages might
appear in different languages depending on where they originated.

> **Note:**

> When we speak of inheriting the locale from the execution
> environment, this means the following on most operating systems:
> For a given locale category, say the collation, the following
> environment variables are consulted in this order until one is
> found to be set: `LC_ALL`, `LC_COLLATE`
> (or the variable corresponding to the respective category),
> `LANG`.  If none of these environment variables are
> set then the locale defaults to `C`.
>

>

> Some message localization libraries also look at the environment
> variable `LANGUAGE` which overrides all other locale
> settings for the purpose of setting the language of messages.  If
> in doubt, please refer to the documentation of your operating
> system, in particular the documentation about
> gettext.
>

To enable messages to be translated to the user's preferred language,
NLS must have been selected at build time
(`configure --enable-nls`).  All other locale support is
built in automatically.

### Behavior

The locale settings influence the following SQL features:

- Sort order in queries using `ORDER BY` or the standard
comparison operators on textual data
- The `upper`, `lower`, and `initcap`
functions
- Pattern matching operators (`LIKE`, `SIMILAR TO`,
and POSIX-style regular expressions); locales affect both case
insensitive matching and the classification of characters by
character-class regular expressions
- The `to_char` family of functions
- The ability to use indexes with `LIKE` clauses

The drawback of using locales other than `C` or
`POSIX` in PostgreSQL is its performance
impact. It slows character handling and prevents ordinary indexes
from being used by `LIKE`. For this reason use locales
only if you actually need them.

As a workaround to allow PostgreSQL to use indexes
with `LIKE` clauses under a non-C locale, several custom
operator classes exist. These allow the creation of an index that
performs a strict character-by-character comparison, ignoring
locale comparison rules. Refer to [indexes-opclass](#indexes-opclass)
for more information.  Another approach is to create indexes using
the `C` collation, as discussed in
[collation](#collation).

### Selecting Locales

Locales can be selected in different scopes depending on requirements.
The above overview showed how locales are specified using
`initdb` to set the defaults for the entire cluster.  The
following list shows where locales can be selected.  Each item provides
the defaults for the subsequent items, and each lower item allows
overriding the defaults on a finer granularity.

1. As explained above, the environment of the operating system provides the
defaults for the locales of a newly initialized database cluster.  In
many cases, this is enough: If the operating system is configured for
the desired language/territory, then
PostgreSQL will by default also behave
according to that locale.
2. As shown above, command-line options for `initdb`
specify the locale settings for a newly initialized database cluster.
Use this if the operating system does not have the locale configuration
you want for your database system.
3. A locale can be selected separately for each database.  The SQL command
`CREATE DATABASE` and its command-line equivalent
`createdb` have options for that.  Use this for example
if a database cluster houses databases for multiple tenants with
different requirements.
4. Locale settings can be made for individual table columns.  This uses an
SQL object called *collation* and is explained in
[collation](#collation).  Use this for example to sort data in
different languages or customize the sort order of a particular table.
5. Finally, locales can be selected for an individual query.  Again, this
uses SQL collation objects.  This could be used to change the sort order
based on run-time choices or for ad-hoc experimentation.

### Locale Providers

PostgreSQL supports multiple *locale
providers*.  This specifies which library supplies the locale
data.  One standard provider name is `libc`, which uses
the locales provided by the operating system C library.  These are the
locales used by most tools provided by the operating system.  Another
provider is `icu`, which uses the external
ICU library.  ICU locales can
only be used if support for ICU was configured when PostgreSQL was built.

The commands and tools that select the locale settings, as described
above, each have an option to select the locale provider.  The examples
shown earlier all use the `libc` provider, which is the
default.  Here is an example to initialize a database cluster using the
ICU provider:

```
initdb --locale-provider=icu --icu-locale=en
```

See the description of the respective commands and programs for
details.  Note that you can mix locale providers at different
granularities, for example use `libc` by default for the
cluster but have one database that uses the `icu`
provider, and then have collation objects using either provider within
those databases.

Which locale provider to use depends on individual requirements.  For most
basic uses, either provider will give adequate results.  For the libc
provider, it depends on what the operating system offers; some operating
systems are better than others.  For advanced uses, ICU offers more locale
variants and customization options.

### ICU Locales

#### ICU Locale Names

The ICU format for the locale name is a [Language Tag](#icu-language-tag).

```
CREATE COLLATION mycollation1 (provider = icu, locale = 'ja-JP');
CREATE COLLATION mycollation2 (provider = icu, locale = 'fr');
```

#### Locale Canonicalization and Validation

When defining a new ICU collation object or database with ICU as the
provider, the given locale name is transformed ("canonicalized") into a
language tag if not already in that form. For instance,

```
CREATE COLLATION mycollation3 (provider = icu, locale = 'en-US-u-kn-true');
NOTICE:  using standard form "en-US-u-kn" for locale "en-US-u-kn-true"
CREATE COLLATION mycollation4 (provider = icu, locale = 'de_DE.utf8');
NOTICE:  using standard form "de-DE" for locale "de_DE.utf8"
```

If you see this notice, ensure that the `provider` and
`locale` are the expected result. For consistent results
when using the ICU provider, specify the canonical [language tag](#icu-language-tag) instead of relying on the
transformation.

A locale with no language name, or the special language name
`root`, is transformed to have the language
`und` ("undefined").

ICU can transform most libc locale names, as well as some other formats,
into language tags for easier transition to ICU. If a libc locale name is
used in ICU, it may not have precisely the same behavior as in libc.

If there is a problem interpreting the locale name, or if the locale name
represents a language or region that ICU does not recognize, you will see
the following warning:

```
CREATE COLLATION nonsense (provider = icu, locale = 'nonsense');
WARNING:  ICU locale "nonsense" has unknown language "nonsense"
HINT:  To disable ICU locale validation, set parameter icu_validation_level to DISABLED.
CREATE COLLATION
```

[guc-icu-validation-level](#guc-icu-validation-level) controls how the message is
reported. Unless set to `ERROR`, the collation will
still be created, but the behavior may not be what the user intended.

#### Language Tag

A language tag, defined in BCP 47, is a standardized identifier used to
identify languages, regions, and other information about a locale.

Basic language tags are simply
`language``-``region`;
or even just `language`. The
`language` is a language code
(e.g. `fr` for French), and
`region` is a region code
(e.g. `CA` for Canada). Examples:
`ja-JP`, `de`, or
`fr-CA`.

Collation settings may be included in the language tag to customize
collation behavior. ICU allows extensive customization, such as
sensitivity (or insensitivity) to accents, case, and punctuation;
treatment of digits within text; and many other options to satisfy a
variety of uses.

To include this additional collation information in a language tag,
append `-u`, which indicates there are additional
collation settings, followed by one or more
`-``key``-``value`
pairs. The `key` is the key for a [collation setting](#icu-collation-settings) and
`value` is a valid value for that setting. For
boolean settings, the `-``key`
may be specified without a corresponding
`-``value`, which implies a
value of `true`.

For example, the language tag `en-US-u-kn-ks-level2`
means the locale with the English language in the US region, with
collation settings `kn` set to `true`
and `ks` set to `level2`. Those
settings mean the collation will be case-insensitive and treat a sequence
of digits as a single number:

```
CREATE COLLATION mycollation5 (provider = icu, deterministic = false, locale = 'en-US-u-kn-ks-level2');
SELECT 'aB' = 'Ab' COLLATE mycollation5 as result;
result
--------
t
(1 row)

SELECT 'N-45'  **Note:**

> The `C` and `POSIX` locales may behave
> differently depending on the database encoding.
>

Additionally, two SQL standard collation names are available:

**`unicode`**
: This collation sorts using the Unicode Collation Algorithm with the
Default Unicode Collation Element Table.  It is available in all
encodings.  ICU support is required to use this collation.  (This
collation has the same behavior as the ICU root locale; see [collation-managing-predefined-icu-und-x-icu](#collation-managing-predefined-icu-und-x-icu).)

**`ucs_basic`**
: This collation sorts by Unicode code point.  It is only available for
encoding `UTF8`.  (This collation has the same
behavior as the libc locale specification `C` in
`UTF8` encoding.)

#### Predefined Collations

If the operating system provides support for using multiple locales
within a single program (`newlocale` and related functions),
or if support for ICU is configured,
then when a database cluster is initialized, `initdb`
populates the system catalog `pg_collation` with
collations based on all the locales it finds in the operating
system at the time.

To inspect the currently available locales, use the query `SELECT
* FROM pg_collation`, or the command `\dOS+`
in psql.

##### libc Collations

For example, the operating system might
provide a locale named `de_DE.utf8`.
`initdb` would then create a collation named
`de_DE.utf8` for encoding `UTF8`
that has both `LC_COLLATE` and
`LC_CTYPE` set to `de_DE.utf8`.
It will also create a collation with the `.utf8`
tag stripped off the name.  So you could also use the collation
under the name `de_DE`, which is less cumbersome
to write and makes the name less encoding-dependent.  Note that,
nevertheless, the initial set of collation names is
platform-dependent.

The default set of collations provided by `libc` map
directly to the locales installed in the operating system, which can be
listed using the command `locale -a`.  In case
a `libc` collation is needed that has different values
for `LC_COLLATE` and `LC_CTYPE`, or if new
locales are installed in the operating system after the database system
was initialized, then a new collation may be created using
the [sql-createcollation](#sql-createcollation) command.
New operating system locales can also be imported en masse using
the [`pg_import_system_collations()`](#functions-admin-collation) function.

Within any particular database, only collations that use that
database's encoding are of interest.  Other entries in
`pg_collation` are ignored.  Thus, a stripped collation
name such as `de_DE` can be considered unique
within a given database even though it would not be unique globally.
Use of the stripped collation names is recommended, since it will
make one fewer thing you need to change if you decide to change to
another database encoding.  Note however that the `default`,
`C`, and `POSIX` collations can be used regardless of
the database encoding.

PostgreSQL considers distinct collation
objects to be incompatible even when they have identical properties.
Thus for example,

```
SELECT a COLLATE "C"  **Tip:**

> To deal with text in different Unicode normalization forms, it is also
> an option to use the functions/expressions
> `normalize` and `is normalized` to
> preprocess or check the strings, instead of using nondeterministic
> collations.  There are different trade-offs for each approach.
>

### ICU Custom Collations

ICU allows extensive control over collation behavior by defining new
collations with collation settings as a part of the language tag. These
settings can modify the collation order to suit a variety of needs. For
instance:

```
-- ignore differences in accents and case
CREATE COLLATION ignore_accent_case (provider = icu, deterministic = false, locale = 'und-u-ks-level1');
SELECT 'Å' = 'A' COLLATE ignore_accent_case; -- true
SELECT 'z' = 'Z' COLLATE ignore_accent_case; -- true

-- upper case letters sort before lower case.
CREATE COLLATION upper_first (provider = icu, locale = 'und-u-kf-upper');
SELECT 'B'  **Note:**

> For many collation settings, you must create the collation with
> `deterministic` set to `false` for the
> setting to have the desired effect (see  linkend="collation-nondeterministic"/>). Additionally, some settings
> only take effect when the key `ka` is set to
> `shifted` (see  linkend="icu-collation-settings-table"/>).
>

#### Collation Settings Examples

**`CREATE COLLATION "de-u-co-phonebk-x-icu" (provider = icu, locale = 'de-u-co-phonebk');`**
: German collation with phone book collation type

**`CREATE COLLATION "und-u-co-emoji-x-icu" (provider = icu, locale = 'und-u-co-emoji');`**
: Root collation with Emoji collation type, per Unicode Technical Standard #51

**`CREATE COLLATION latinlast (provider = icu, locale = 'en-u-kr-grek-latn');`**
: Sort Greek letters before Latin ones.  (The default is Latin before Greek.)

**`CREATE COLLATION upperfirst (provider = icu, locale = 'en-u-kf-upper');`**
: Sort upper-case letters before lower-case letters.  (The default is
lower-case letters first.)

**`CREATE COLLATION special (provider = icu, locale = 'en-u-kf-upper-kr-grek-latn');`**
: Combines both of the above options.

#### ICU Tailoring Rules

If the options provided by the collation settings shown above are not
sufficient, the order of collation elements can be changed with tailoring
rules, whose syntax is detailed at [](https://unicode-org.github.io/icu/userguide/collation/customization/).

This small example creates a collation based on the root locale with a
tailoring rule:

```
CREATE COLLATION custom (provider = icu, locale = 'und', rules = '&V '  **Important:**

> On most modern operating systems, PostgreSQL
> can determine which character set is implied by the `LC_CTYPE`
> setting, and it will enforce that only the matching database encoding is
> used.  On older systems it is your responsibility to ensure that you use
> the encoding expected by the locale you have selected.  A mistake in
> this area is likely to lead to strange behavior of locale-dependent
> operations such as sorting.
>

>

> PostgreSQL will allow superusers to create
> databases with `SQL_ASCII` encoding even when
> `LC_CTYPE` is not `C` or `POSIX`.  As noted
> above, `SQL_ASCII` does not enforce that the data stored in
> the database has any particular encoding, and so this choice poses risks
> of locale-dependent misbehavior.  Using this combination of settings is
> deprecated and may someday be forbidden altogether.
>

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

### Available Character Set Conversions

PostgreSQL allows conversion between any
two character sets for which a conversion function is listed in the
[`pg_conversion`](#catalog-pg-conversion)
system catalog.  PostgreSQL comes with
some predefined conversions, as summarized in
[multibyte-translation-table](#multibyte-translation-table) and shown in more
detail in [builtin-conversions-table](#builtin-conversions-table).  You can
create a new conversion using the SQL command
[sql-createconversion](#sql-createconversion).  (To be used for automatic
client/server conversions, a conversion must be marked
as "default" for its character set pair.)

| Server Character Set | Available Client Character Sets |
| --- | --- |
| `BIG5` | *not supported as a server encoding* |
| `EUC_CN` | *EUC_CN*,         `MULE_INTERNAL`,         `UTF8` |
| `EUC_JP` | *EUC_JP*,         `MULE_INTERNAL`,         `SJIS`,         `UTF8` |
| `EUC_JIS_2004` | *EUC_JIS_2004*,         `SHIFT_JIS_2004`,         `UTF8` |
| `EUC_KR` | *EUC_KR*,         `MULE_INTERNAL`,         `UTF8` |
| `EUC_TW` | *EUC_TW*,         `BIG5`,         `MULE_INTERNAL`,         `UTF8` |
| `GB18030` | *not supported as a server encoding* |
| `GBK` | *not supported as a server encoding* |
| `ISO_8859_5` | *ISO_8859_5*,         `KOI8R`,         `MULE_INTERNAL`,         `UTF8`,         `WIN866`,         `WIN1251` |
| `ISO_8859_6` | *ISO_8859_6*,         `UTF8` |
| `ISO_8859_7` | *ISO_8859_7*,         `UTF8` |
| `ISO_8859_8` | *ISO_8859_8*,         `UTF8` |
| `JOHAB` | *not supported as a server encoding* |
| `KOI8R` | *KOI8R*,         `ISO_8859_5`,         `MULE_INTERNAL`,         `UTF8`,         `WIN866`,         `WIN1251` |
| `KOI8U` | *KOI8U*,         `UTF8` |
| `LATIN1` | *LATIN1*,         `MULE_INTERNAL`,         `UTF8` |
| `LATIN2` | *LATIN2*,         `MULE_INTERNAL`,         `UTF8`,         `WIN1250` |
| `LATIN3` | *LATIN3*,         `MULE_INTERNAL`,         `UTF8` |
| `LATIN4` | *LATIN4*,         `MULE_INTERNAL`,         `UTF8` |
| `LATIN5` | *LATIN5*,         `UTF8` |
| `LATIN6` | *LATIN6*,         `UTF8` |
| `LATIN7` | *LATIN7*,         `UTF8` |
| `LATIN8` | *LATIN8*,         `UTF8` |
| `LATIN9` | *LATIN9*,         `UTF8` |
| `LATIN10` | *LATIN10*,         `UTF8` |
| `MULE_INTERNAL` | *MULE_INTERNAL*,          `BIG5`,          `EUC_CN`,          `EUC_JP`,          `EUC_KR`,          `EUC_TW`,          `ISO_8859_5`,          `KOI8R`,          `LATIN1` to `LATIN4`,          `SJIS`,          `WIN866`,          `WIN1250`,          `WIN1251` |
| `SJIS` | *not supported as a server encoding* |
| `SHIFT_JIS_2004` | *not supported as a server encoding* |
| `SQL_ASCII` | *any (no conversion will be performed)* |
| `UHC` | *not supported as a server encoding* |
| `UTF8` | *all supported encodings* |
| `WIN866` | *WIN866*,          `ISO_8859_5`,          `KOI8R`,          `MULE_INTERNAL`,          `UTF8`,          `WIN1251` |
| `WIN874` | *WIN874*,         `UTF8` |
| `WIN1250` | *WIN1250*,          `LATIN2`,          `MULE_INTERNAL`,          `UTF8` |
| `WIN1251` | *WIN1251*,          `ISO_8859_5`,          `KOI8R`,          `MULE_INTERNAL`,          `UTF8`,          `WIN866` |
| `WIN1252` | *WIN1252*,          `UTF8` |
| `WIN1253` | *WIN1253*,          `UTF8` |
| `WIN1254` | *WIN1254*,          `UTF8` |
| `WIN1255` | *WIN1255*,          `UTF8` |
| `WIN1256` | *WIN1256*,         `UTF8` |
| `WIN1257` | *WIN1257*,          `UTF8` |
| `WIN1258` | *WIN1258*,         `UTF8` |

| Conversion Name           (Note: The conversion names follow a standard naming scheme: The            official name of the source encoding with all            non-alphanumeric characters replaced by underscores, followed            by `_to_`, followed by the similarly processed            destination encoding name.  Therefore, these names sometimes            deviate from the customary encoding names shown in            .) | Source Encoding | Destination Encoding |
| --- | --- | --- |
| `big5_to_euc_tw` | `BIG5` | `EUC_TW` |
| `big5_to_mic` | `BIG5` | `MULE_INTERNAL` |
| `big5_to_utf8` | `BIG5` | `UTF8` |
| `euc_cn_to_mic` | `EUC_CN` | `MULE_INTERNAL` |
| `euc_cn_to_utf8` | `EUC_CN` | `UTF8` |
| `euc_jp_to_mic` | `EUC_JP` | `MULE_INTERNAL` |
| `euc_jp_to_sjis` | `EUC_JP` | `SJIS` |
| `euc_jp_to_utf8` | `EUC_JP` | `UTF8` |
| `euc_kr_to_mic` | `EUC_KR` | `MULE_INTERNAL` |
| `euc_kr_to_utf8` | `EUC_KR` | `UTF8` |
| `euc_tw_to_big5` | `EUC_TW` | `BIG5` |
| `euc_tw_to_mic` | `EUC_TW` | `MULE_INTERNAL` |
| `euc_tw_to_utf8` | `EUC_TW` | `UTF8` |
| `gb18030_to_utf8` | `GB18030` | `UTF8` |
| `gbk_to_utf8` | `GBK` | `UTF8` |
| `iso_8859_10_to_utf8` | `LATIN6` | `UTF8` |
| `iso_8859_13_to_utf8` | `LATIN7` | `UTF8` |
| `iso_8859_14_to_utf8` | `LATIN8` | `UTF8` |
| `iso_8859_15_to_utf8` | `LATIN9` | `UTF8` |
| `iso_8859_16_to_utf8` | `LATIN10` | `UTF8` |
| `iso_8859_1_to_mic` | `LATIN1` | `MULE_INTERNAL` |
| `iso_8859_1_to_utf8` | `LATIN1` | `UTF8` |
| `iso_8859_2_to_mic` | `LATIN2` | `MULE_INTERNAL` |
| `iso_8859_2_to_utf8` | `LATIN2` | `UTF8` |
| `iso_8859_2_to_windows_1250` | `LATIN2` | `WIN1250` |
| `iso_8859_3_to_mic` | `LATIN3` | `MULE_INTERNAL` |
| `iso_8859_3_to_utf8` | `LATIN3` | `UTF8` |
| `iso_8859_4_to_mic` | `LATIN4` | `MULE_INTERNAL` |
| `iso_8859_4_to_utf8` | `LATIN4` | `UTF8` |
| `iso_8859_5_to_koi8_r` | `ISO_8859_5` | `KOI8R` |
| `iso_8859_5_to_mic` | `ISO_8859_5` | `MULE_INTERNAL` |
| `iso_8859_5_to_utf8` | `ISO_8859_5` | `UTF8` |
| `iso_8859_5_to_windows_1251` | `ISO_8859_5` | `WIN1251` |
| `iso_8859_5_to_windows_866` | `ISO_8859_5` | `WIN866` |
| `iso_8859_6_to_utf8` | `ISO_8859_6` | `UTF8` |
| `iso_8859_7_to_utf8` | `ISO_8859_7` | `UTF8` |
| `iso_8859_8_to_utf8` | `ISO_8859_8` | `UTF8` |
| `iso_8859_9_to_utf8` | `LATIN5` | `UTF8` |
| `johab_to_utf8` | `JOHAB` | `UTF8` |
| `koi8_r_to_iso_8859_5` | `KOI8R` | `ISO_8859_5` |
| `koi8_r_to_mic` | `KOI8R` | `MULE_INTERNAL` |
| `koi8_r_to_utf8` | `KOI8R` | `UTF8` |
| `koi8_r_to_windows_1251` | `KOI8R` | `WIN1251` |
| `koi8_r_to_windows_866` | `KOI8R` | `WIN866` |
| `koi8_u_to_utf8` | `KOI8U` | `UTF8` |
| `mic_to_big5` | `MULE_INTERNAL` | `BIG5` |
| `mic_to_euc_cn` | `MULE_INTERNAL` | `EUC_CN` |
| `mic_to_euc_jp` | `MULE_INTERNAL` | `EUC_JP` |
| `mic_to_euc_kr` | `MULE_INTERNAL` | `EUC_KR` |
| `mic_to_euc_tw` | `MULE_INTERNAL` | `EUC_TW` |
| `mic_to_iso_8859_1` | `MULE_INTERNAL` | `LATIN1` |
| `mic_to_iso_8859_2` | `MULE_INTERNAL` | `LATIN2` |
| `mic_to_iso_8859_3` | `MULE_INTERNAL` | `LATIN3` |
| `mic_to_iso_8859_4` | `MULE_INTERNAL` | `LATIN4` |
| `mic_to_iso_8859_5` | `MULE_INTERNAL` | `ISO_8859_5` |
| `mic_to_koi8_r` | `MULE_INTERNAL` | `KOI8R` |
| `mic_to_sjis` | `MULE_INTERNAL` | `SJIS` |
| `mic_to_windows_1250` | `MULE_INTERNAL` | `WIN1250` |
| `mic_to_windows_1251` | `MULE_INTERNAL` | `WIN1251` |
| `mic_to_windows_866` | `MULE_INTERNAL` | `WIN866` |
| `sjis_to_euc_jp` | `SJIS` | `EUC_JP` |
| `sjis_to_mic` | `SJIS` | `MULE_INTERNAL` |
| `sjis_to_utf8` | `SJIS` | `UTF8` |
| `windows_1258_to_utf8` | `WIN1258` | `UTF8` |
| `uhc_to_utf8` | `UHC` | `UTF8` |
| `utf8_to_big5` | `UTF8` | `BIG5` |
| `utf8_to_euc_cn` | `UTF8` | `EUC_CN` |
| `utf8_to_euc_jp` | `UTF8` | `EUC_JP` |
| `utf8_to_euc_kr` | `UTF8` | `EUC_KR` |
| `utf8_to_euc_tw` | `UTF8` | `EUC_TW` |
| `utf8_to_gb18030` | `UTF8` | `GB18030` |
| `utf8_to_gbk` | `UTF8` | `GBK` |
| `utf8_to_iso_8859_1` | `UTF8` | `LATIN1` |
| `utf8_to_iso_8859_10` | `UTF8` | `LATIN6` |
| `utf8_to_iso_8859_13` | `UTF8` | `LATIN7` |
| `utf8_to_iso_8859_14` | `UTF8` | `LATIN8` |
| `utf8_to_iso_8859_15` | `UTF8` | `LATIN9` |
| `utf8_to_iso_8859_16` | `UTF8` | `LATIN10` |
| `utf8_to_iso_8859_2` | `UTF8` | `LATIN2` |
| `utf8_to_iso_8859_3` | `UTF8` | `LATIN3` |
| `utf8_to_iso_8859_4` | `UTF8` | `LATIN4` |
| `utf8_to_iso_8859_5` | `UTF8` | `ISO_8859_5` |
| `utf8_to_iso_8859_6` | `UTF8` | `ISO_8859_6` |
| `utf8_to_iso_8859_7` | `UTF8` | `ISO_8859_7` |
| `utf8_to_iso_8859_8` | `UTF8` | `ISO_8859_8` |
| `utf8_to_iso_8859_9` | `UTF8` | `LATIN5` |
| `utf8_to_johab` | `UTF8` | `JOHAB` |
| `utf8_to_koi8_r` | `UTF8` | `KOI8R` |
| `utf8_to_koi8_u` | `UTF8` | `KOI8U` |
| `utf8_to_sjis` | `UTF8` | `SJIS` |
| `utf8_to_windows_1258` | `UTF8` | `WIN1258` |
| `utf8_to_uhc` | `UTF8` | `UHC` |
| `utf8_to_windows_1250` | `UTF8` | `WIN1250` |
| `utf8_to_windows_1251` | `UTF8` | `WIN1251` |
| `utf8_to_windows_1252` | `UTF8` | `WIN1252` |
| `utf8_to_windows_1253` | `UTF8` | `WIN1253` |
| `utf8_to_windows_1254` | `UTF8` | `WIN1254` |
| `utf8_to_windows_1255` | `UTF8` | `WIN1255` |
| `utf8_to_windows_1256` | `UTF8` | `WIN1256` |
| `utf8_to_windows_1257` | `UTF8` | `WIN1257` |
| `utf8_to_windows_866` | `UTF8` | `WIN866` |
| `utf8_to_windows_874` | `UTF8` | `WIN874` |
| `windows_1250_to_iso_8859_2` | `WIN1250` | `LATIN2` |
| `windows_1250_to_mic` | `WIN1250` | `MULE_INTERNAL` |
| `windows_1250_to_utf8` | `WIN1250` | `UTF8` |
| `windows_1251_to_iso_8859_5` | `WIN1251` | `ISO_8859_5` |
| `windows_1251_to_koi8_r` | `WIN1251` | `KOI8R` |
| `windows_1251_to_mic` | `WIN1251` | `MULE_INTERNAL` |
| `windows_1251_to_utf8` | `WIN1251` | `UTF8` |
| `windows_1251_to_windows_866` | `WIN1251` | `WIN866` |
| `windows_1252_to_utf8` | `WIN1252` | `UTF8` |
| `windows_1256_to_utf8` | `WIN1256` | `UTF8` |
| `windows_866_to_iso_8859_5` | `WIN866` | `ISO_8859_5` |
| `windows_866_to_koi8_r` | `WIN866` | `KOI8R` |
| `windows_866_to_mic` | `WIN866` | `MULE_INTERNAL` |
| `windows_866_to_utf8` | `WIN866` | `UTF8` |
| `windows_866_to_windows_1251` | `WIN866` | `WIN` |
| `windows_874_to_utf8` | `WIN874` | `UTF8` |
| `euc_jis_2004_to_utf8` | `EUC_JIS_2004` | `UTF8` |
| `utf8_to_euc_jis_2004` | `UTF8` | `EUC_JIS_2004` |
| `shift_jis_2004_to_utf8` | `SHIFT_JIS_2004` | `UTF8` |
| `utf8_to_shift_jis_2004` | `UTF8` | `SHIFT_JIS_2004` |
| `euc_jis_2004_to_shift_jis_2004` | `EUC_JIS_2004` | `SHIFT_JIS_2004` |
| `shift_jis_2004_to_euc_jis_2004` | `SHIFT_JIS_2004` | `EUC_JIS_2004` |

### Further Reading

These are good sources to start learning about various kinds of encoding
systems.

**CJKV Information Processing: Chinese, Japanese, Korean & Vietnamese Computing**
: Contains detailed explanations of `EUC_JP`,
`EUC_CN`, `EUC_KR`,
`EUC_TW`.

**[](https://www.unicode.org/)**
: The web site of the Unicode Consortium.

**[RFC 3629](https://datatracker.ietf.org/doc/html/rfc3629)**
: UTF-8 (8-bit UCS/Unicode Transformation
Format) is defined here.
