# Available Character Set Conversions

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/09_localization.md`
- Source Title: `Localization`
- Source Heading Path: `Localization > Available Character Set Conversions`
- Source Line Ranges: `571-756`
- Chunk ID: `pg16_fact_0025_1008a7efbe`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `27da1b16d84c0b8febac30a9886742d641787cb6747bba0fec2c383e140d6d1e`

## Retrieval Guidance

- Use When: 需要确认某两个编码之间是否支持自动转换。
- Retrieval Keywords: character set conversions, pg_conversion, UTF8, LATIN1, EUC_JP, SJIS, SQL_ASCII, conversion function
- Follow-up Guidance: 自定义转换需 CREATE CONVERSION 且标记 default 才可用于自动 client/server 转换。
- Classification Note: 列出 server/client encoding 可转换组合和 pg_conversion 内置转换函数。

## Official Source Content

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
