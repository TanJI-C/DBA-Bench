# Oracle to TiDB function mappings

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/oracle-functions-to-tidb.md`
- Source Title: `Comparisons between Functions and Syntax of Oracle and TiDB`
- Source Heading Path: `Comparisons between Functions and Syntax of Oracle and TiDB | Comparisons between Functions and Syntax of Oracle and TiDB > Comparisons of functions`
- Source Line Ranges: `5-46`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `oracle-compatibility`, `function-mapping`, `type-conversion`, `date-functions`, `string-functions`, `null-handling`, `joins`, `sequences`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0461_427a5122ee`
- Source ID: `tidb-docs-8.1:oracle-functions-to-tidb.md#comparisons-between-functions-and-syntax-of-oracle-and-tidb`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bd995537c471e899b8e4d94a18ba90e21ed2f1bed4892ac6f0ac4dd827e790e3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/oracle-functions-to-tidb#comparisons-between-functions-and-syntax-of-oracle-and-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/oracle-functions-to-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when mapping Oracle functions or join syntax to TiDB equivalents for type conversion, date and time formatting, sequences, NULL handling, string operations, and Oracle-specific expressions such as `DECODE()` or `(+)` joins.
- Retrieval Keywords: Oracle to TiDB function mappings, TO_NUMBER, TO_CHAR, CONVERT(key,dataType), DATE_FORMAT(NOW(),'%Y-%m-%d %H:%i:%s'), STR_TO_DATE, SYSDATE, NOW(), SYSTIMESTAMP, CURRENT_TIMESTAMP(6), DATEDIFF, MONTHS_BETWEEN, TIMESTAMPDIFF(MONTH,SYSDATE,ENDDATE), DATE_ADD, ADD_MONTHS, TRUNC, TRUNCATE, NEXTVAL(sequence_name), UUID(), NVL, IFNULL, NVL2, IF(key is NOT NULL, val1, val2), DECODE, CASE WHEN, CONCAT('a','b'), CHAR_LENGTH, SUBSTRING, INSTR, LOCATE, GROUP_CONCAT, CHR(n), CHAR(n), LEFT JOIN, RIGHT JOIN, a.id = b.id(+)
- Follow-up Guidance: The source notes that these comparisons are based on Oracle 12.2.0.1.0 and TiDB v5.4.0, and that results or syntax might differ in other versions.
- Classification Note: This chunk is reference content because it is a comparison table of Oracle syntax and functions with corresponding TiDB syntax and notes.

## Official Source Content

# Comparisons between Functions and Syntax of Oracle and TiDB

This document describes the comparisons between functions and syntax of Oracle and TiDB. It helps you find the corresponding TiDB functions based on the Oracle functions, and understand the syntax differences between Oracle and TiDB.

> **Note:**
>
> The functions and syntax in this document are based on Oracle 12.2.0.1.0 and TiDB v5.4.0. They might be different in other versions.
## Comparisons of functions

The following table shows the comparisons between some Oracle and TiDB functions.

| Function | Oracle syntax | TiDB syntax | Note |
|---|---|---|---|
| Cast a value as a certain type | <li>`TO_NUMBER(key)`</li><li>`TO_CHAR(key)`</li> | `CONVERT(key,dataType)` | TiDB supports casting a value as one of the following types: `BINARY`, `CHAR`, `DATE`, `DATETIME`, `TIME`, `SIGNED INTEGER`, `UNSIGNED INTEGER` and `DECIMAL`. |
| Convert a date to a string | <li>`TO_CHAR(SYSDATE,'yyyy-MM-dd hh24:mi:ss')`</li> <li>`TO_CHAR(SYSDATE,'yyyy-MM-dd')`</li> | <li>`DATE_FORMAT(NOW(),'%Y-%m-%d %H:%i:%s')`</li><li>`DATE_FORMAT(NOW(),'%Y-%m-%d')`</li> | The format string of TiDB is case-sensitive. |
| Convert a string to a date | <li>`TO_DATE('2021-05-28 17:31:37','yyyy-MM-dd hh24:mi:ss')`</li><li>`TO_DATE('2021-05-28','yyyy-MM-dd hh24:mi:ss')`</li> | <li>`STR_TO_DATE('2021-05-28 17:31:37','%Y-%m-%d %H:%i:%s')`</li><li>`STR_TO_DATE('2021-05-28','%Y-%m-%d%T')` </li> | The format string of TiDB is case-sensitive. |
| Get the current system time in second precision | `SYSDATE` | `NOW()` | |
| Get the current system time in microsecond precision | `SYSTIMESTAMP` | `CURRENT_TIMESTAMP(6)` | |
| Get the number of days between two dates | `date1 - date2` | `DATEDIFF(date1, date2)` | |
| Get the number of months between two dates | `MONTHS_BETWEEN(ENDDATE,SYSDATE)` | `TIMESTAMPDIFF(MONTH,SYSDATE,ENDDATE)` | The results of `MONTHS_BETWEEN()` in Oracle and `TIMESTAMPDIFF()` in TiDB are different. `TIMESTAMPDIFF()` returns an integer. Note that the parameters in the two functions are swapped. |
| Add `n` days to a date | `DATEVAL + n` | `DATE_ADD(dateVal,INTERVAL n DAY)` | `n` can be a negative value.|
| Add `n` months to a date | `ADD_MONTHS(dateVal,n)`| `DATE_ADD(dateVal,INTERVAL n MONTH)` | `n` can be a negative value. |
| Get the day of a date | `TRUNC(SYSDATE)` | <li>`CAST(NOW() AS DATE)`</li><li>`DATE_FORMAT(NOW(),'%Y-%m-%d')`</li> | In TiDB, `CAST` and `DATE_FORMAT` return the same result. |
| Get the month of a date | `TRUNC(SYSDATE,'mm')` | `DATE_ADD(CURDATE(),interval - day(CURDATE()) + 1 day)`  | |
| Truncate a value | `TRUNC(2.136) = 2`<br/> `TRUNC(2.136,2) = 2.13` | `TRUNCATE(2.136,0) = 2`<br/> `TRUNCATE(2.136,2) = 2.13` | Data precision is preserved. Truncate the corresponding decimal places without rounding. |
| Get the next value in a sequence | `sequence_name.NEXTVAL` | `NEXTVAL(sequence_name)` | |
| Get a random sequence value | `SYS_GUID()` | `UUID()` | TiDB returns a Universal Unique Identifier (UUID). |
| Left join or right join | `SELECT * FROM a, b WHERE a.id = b.id(+);`<br/>`SELECT * FROM a, b WHERE a.id(+) = b.id;` | `SELECT * FROM a LEFT JOIN b ON a.id = b.id;`<br/>`SELECT * FROM a RIGHT JOIN b ON a.id = b.id;` | In a correlated query, TiDB does not support using (+) to left join or right join. You can use `LEFT JOIN` or `RIGHT JOIN` instead. |
| `NVL()` | `NVL(key,val)` | `IFNULL(key,val)` | If the value of the field is `NULL`, it returns `val`; otherwise, it returns the value of the field.  |
| `NVL2()` | `NVL2(key, val1, val2)` | `IF(key is NOT NULL, val1, val2)` | If the value of the field is not `NULL`, it returns `val1`; otherwise, it returns `val2`. |
| `DECODE()` | <li>`DECODE(key,val1,val2,val3)`</li><li>`DECODE(value,if1,val1,if2,val2,...,ifn,valn,val)`</li> | <li>`IF(key=val1,val2,val3)`</li><li>`CASE WHEN value=if1 THEN val1 WHEN value=if2 THEN val2,...,WHEN value=ifn THEN valn ELSE val END`</li> | <li>If the value of the field is `val1`, then it returns `val2`; otherwise it returns `val3`. </li><li>When the value of the field satisfies condition 1 (`if1`), it returns `val1`. When it satisfies condition 2 (`if2`), it returns `val2`. When it satisfies condition 3 (`if3`), it returns `val3`.</li> |
| Concatenate the string `a` and `b` | <code>'a' \|\| 'b'</code> | `CONCAT('a','b')` | |
| Get the length of a string | `LENGTH(str)` | `CHAR_LENGTH(str)` | |
| Get the substring as specified | `SUBSTR('abcdefg',0,2) = 'ab'`<br/> `SUBSTR('abcdefg',1,2) = 'ab'` | `SUBSTRING('abcdefg',0,2) = ''`<br/>`SUBSTRING('abcdefg',1,2) = 'ab'` | <li>In Oracle, the starting position 0 has the same effect as 1. </li><li>In TiDB, the starting position 0 returns an empty string. If you want to get a substring from the beginning, the starting position should be 1.</li> |
| Get the position of a substring | `INSTR('abcdefg','b',1,1)` | `INSTR('abcdefg','b')` | Search from the first character of `'abcdefg'` and return the position of the first occurrence of `'b'`. |
| Get the position of a substring | `INSTR('stst','s',1,2)` | `LENGTH(SUBSTRING_INDEX('stst','s',2)) + 1` | Search from the first character of `'stst'` and return the position of the second occurrence of `'s'`. |
| Get the position of a substring | `INSTR('abcabc','b',2,1)` | `LOCATE('b','abcabc',2)` | Search from the second character of `abcabc` and return the position of the first occurrence of `b`. |
| Concatenate values of a column | `LISTAGG(CONCAT(E.dimensionid,'---',E.DIMENSIONNAME),'***') within GROUP(ORDER BY DIMENSIONNAME)` | `GROUP_CONCAT(CONCAT(E.dimensionid,'---',E.DIMENSIONNAME) ORDER BY DIMENSIONNAME SEPARATOR '***')` | Concatenate values of a specified column to one row with the `***` delimiter. |
| Convert an ASCII code to a character | `CHR(n)` | `CHAR(n)` | The Tab (`CHR(9)`), LF (`CHR(10)`), and CR (`CHR(13)`) characters in Oracle correspond to `CHAR(9)`, `CHAR(10)`, and `CHAR(13)` in TiDB. |
