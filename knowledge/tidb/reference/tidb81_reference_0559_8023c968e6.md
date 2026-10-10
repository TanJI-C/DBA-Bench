# CREATE SEQUENCE syntax, parameters, functions, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-create-sequence.md`
- Source Title: `CREATE SEQUENCE`
- Source Heading Path: `CREATE SEQUENCE | CREATE SEQUENCE > Synopsis | CREATE SEQUENCE > Syntax | CREATE SEQUENCE > Parameters | CREATE SEQUENCE > `SEQUENCE` function | CREATE SEQUENCE > Examples | CREATE SEQUENCE > MySQL compatibility | CREATE SEQUENCE > See also`
- Source Line Ranges: `5-320`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `create sequence`, `sequence syntax`, `sequence parameters`, `nextval`, `lastval`, `setval`, `cache`, `cycle`, `mysql compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0559_8023c968e6`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-create-sequence.md#create-sequence`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2bc12606a74c77bf9004d2f0ecaa337140f266a0be03ac7cb9d1d2cb6dfdefef`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-sequence#create-sequence
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-create-sequence.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks for CREATE SEQUENCE syntax, sequence options, sequence functions such as NEXTVAL or LASTVAL or SETVAL, examples, or TiDB and MariaDB compatibility behavior for sequences.
- Retrieval Keywords: CREATE SEQUENCE, TEMPORARY SEQUENCE, IF NOT EXISTS, INCREMENT, MINVALUE, MAXVALUE, START WITH, CACHE, NOCACHE, CYCLE, NOCYCLE, NEXTVAL, NEXT VALUE FOR, LASTVAL, SETVAL, Sequence 'test.seq2' has run out, SHOW CREATE SEQUENCE, ALTER SEQUENCE, DROP SEQUENCE, Sequence Functions, MariaDB progression
- Follow-up Guidance: The source also points to related topics: ALTER SEQUENCE, DROP SEQUENCE, SHOW CREATE SEQUENCE, and Sequence Functions.
- Classification Note: This is a reference chunk because it provides formal CREATE SEQUENCE syntax, parameter defaults, function semantics, examples, and compatibility notes from the official SQL statement documentation.

## Official Source Content

# CREATE SEQUENCE

The `CREATE SEQUENCE` statement creates sequence objects in TiDB. The sequence is a database object that is on a par with the table and the `View` object. The sequence is used to generate serialized IDs in a customized way.
## Synopsis

```ebnf+diagram
CreateSequenceStmt ::=
    'CREATE' 'SEQUENCE' IfNotExists TableName CreateSequenceOptionListOpt

IfNotExists ::=
    ('IF' 'NOT' 'EXISTS')?

TableName ::=
    Identifier ('.' Identifier)?

CreateSequenceOptionListOpt ::=
    SequenceOption*

SequenceOptionList ::=
    SequenceOption

SequenceOption ::=
    ( 'INCREMENT' ( '='? | 'BY' ) | 'START' ( '='? | 'WITH' ) | ( 'MINVALUE' | 'MAXVALUE' | 'CACHE' ) '='? ) SignedNum
|   'COMMENT' '='? stringLit
|   'NOMINVALUE'
|   'NO' ( 'MINVALUE' | 'MAXVALUE' | 'CACHE' | 'CYCLE' )
|   'NOMAXVALUE'
|   'NOCACHE'
|   'CYCLE'
|   'NOCYCLE'
```
## Syntax

```sql
CREATE [TEMPORARY] SEQUENCE [IF NOT EXISTS] sequence_name
    [ INCREMENT [ BY | = ] increment ]
    [ MINVALUE [=] minvalue | NO MINVALUE | NOMINVALUE ]
    [ MAXVALUE [=] maxvalue | NO MAXVALUE | NOMAXVALUE ]
    [ START [ WITH | = ] start ]
    [ CACHE [=] cache | NOCACHE | NO CACHE]
    [ CYCLE | NOCYCLE | NO CYCLE]
    [table_options]
```
## Parameters

|Parameters | Default value | Description |
| :-- | :-- | :--|
| `TEMPORARY` | `false` | TiDB currently does not support the `TEMPORARY` option and provides only syntax compatibility for it. |
| `INCREMENT` | `1` | Specifies the increment of a sequence. Its positive or negative values can control the growth direction of the sequence. |
| `MINVALUE` | `1` or `-9223372036854775807` | Specifies the minimum value of a sequence. When `INCREMENT` > `0`, the default value is `1`. When `INCREMENT` < `0`, the default value is `-9223372036854775807`. |
| `MAXVALUE` | `9223372036854775806` or `-1` | Specifies the maximum value of a sequence. When `INCREMENT` > `0`, the default value is `9223372036854775806`. When `INCREMENT` < `0`, the default value is `-1`. |
| `START` | `MINVALUE` or `MAXVALUE`| Specifies the initial value of a sequence. When `INCREMENT` > `0`, the default value is `MINVALUE`. When `INCREMENT` < `0`, the default value is `MAXVALUE`. |
| `CACHE` | `1000` | Specifies the local cache size of a sequence in TiDB. |
| `CYCLE` | `NO CYCLE` | Specifies whether a sequence restarts from the minimum value (or maximum for the descending sequence). When `INCREMENT` > `0`, the default value is `MINVALUE`. When `INCREMENT` < `0`, the default value is `MAXVALUE`. |
## `SEQUENCE` function

You can control a sequence through the following expression functions:

+ `NEXTVAL` or `NEXT VALUE FOR`

    Essentially, both are the `NEXTVAL()` function that gets the next valid value of a sequence object. The parameter of the `NEXTVAL()` function is the `identifier` of the sequence.

+ `LASTVAL`

    This function gets the last used value of this session. If the value does not exist, `NULL` is used. The parameter of this function is the `identifier` of the sequence.

+ `SETVAL`

    This function sets the progression of the current value for a sequence. The first parameter of this function is the `identifier` of the sequence; the second parameter is `num`.

> **Note:**
>
> In the implementation of a sequence in TiDB, the `SETVAL` function cannot change the initial progression or cycle progression of this sequence. This function only returns the next valid value based on this progression.
## Examples

+ Create a sequence object with the default parameter:

    ```sql
    CREATE SEQUENCE seq;
    ```

    ```
    Query OK, 0 rows affected (0.06 sec)
    ```

+ Use the `NEXTVAL()` function to get the next value of the sequence object:

    ```sql
    SELECT NEXTVAL(seq);
    ```

    ```
    +--------------+
    | NEXTVAL(seq) |
    +--------------+
    |            1 |
    +--------------+
    1 row in set (0.02 sec)
    ```

+ Use the `LASTVAL()` function to get the value generated by the last call to a sequence object in this session:

    ```sql
    SELECT LASTVAL(seq);
    ```

    ```
    +--------------+
    | LASTVAL(seq) |
    +--------------+
    |            1 |
    +--------------+
    1 row in set (0.02 sec)
    ```

+ Use the `SETVAL()` function to set the current value (or the current position) of the sequence object:

    ```sql
    SELECT SETVAL(seq, 10);
    ```

    ```
    +-----------------+
    | SETVAL(seq, 10) |
    +-----------------+
    |              10 |
    +-----------------+
    1 row in set (0.01 sec)
    ```

+ You can also use the `next value for` syntax to get the next value of the sequence:

    ```sql
    SELECT next value for seq;
    ```

    ```
    +--------------------+
    | next value for seq |
    +--------------------+
    |                 11 |
    +--------------------+
    1 row in set (0.00 sec)
    ```

+ Create a sequence object with default custom parameters:

    ```sql
    CREATE SEQUENCE seq2 start 3 increment 2 minvalue 1 maxvalue 10 cache 3;
    ```

    ```
    Query OK, 0 rows affected (0.01 sec)
    ```

+ When the sequence object has not been used in this session, the `LASTVAL()` function returns a `NULL` value.

    ```sql
    SELECT LASTVAL(seq2);
    ```

    ```
    +---------------+
    | LASTVAL(seq2) |
    +---------------+
    |          NULL |
    +---------------+
    1 row in set (0.01 sec)
    ```

+ The first valid value of the `NEXTVAL()` function for the sequence object is the value of `START` parameter.

    ```sql
    SELECT NEXTVAL(seq2);
    ```

    ```
    +---------------+
    | NEXTVAL(seq2) |
    +---------------+
    |             3 |
    +---------------+
    1 row in set (0.00 sec)
    ```

+ Although the `SETVAL()` function can change the current value of the sequence object, it cannot change the arithmetic progression rule for the next value.

    ```sql
    SELECT SETVAL(seq2, 6);
    ```

    ```
    +-----------------+
    | SETVAL(seq2, 6) |
    +-----------------+
    |               6 |
    +-----------------+
    1 row in set (0.00 sec)
    ```

+ When you use `NEXTVAL()` to get the next value, the next value will follow the arithmetic progression rule defined by the sequence.

    ```sql
    SELECT next value for seq2;
    ```

    ```
    +---------------------+
    | next value for seq2 |
    +---------------------+
    |                   7 |
    +---------------------+
    1 row in set (0.00 sec)
    ```

+ You can use the next value of the sequence as the default value for the column, as in the following example.

    ```sql
    CREATE table t(a int default next value for seq2);
    ```

    ```
    Query OK, 0 rows affected (0.02 sec)
    ```

+ In the following example, the value is not specified, so the default value of `seq2` is used.

    ```sql
    INSERT into t values();
    ```

    ```
    Query OK, 1 row affected (0.00 sec)
    ```

    ```sql
    SELECT * from t;
    ```

    ```
    +------+
    | a    |
    +------+
    |    9 |
    +------+
    1 row in set (0.00 sec)
    ```

+ In the following example, the value is not specified, so the default value of `seq2` is used. But the next value of `seq2` is not within the range defined in the above example (`CREATE SEQUENCE seq2 start 3 increment 2 minvalue 1 maxvalue 10 cache 3;`), so an error is returned.

    ```sql
    INSERT into t values();
    ```

    ```
    ERROR 4135 (HY000): Sequence 'test.seq2' has run out
    ```
## MySQL compatibility

This statement is a TiDB extension. The implementation is modeled on sequences available in MariaDB.

Except for the `SETVAL` function, all other functions have the same _progressions_ as MariaDB. Here "progression" means that the numbers in a sequence follow a certain arithmetic progression rule defined by the sequence. Although you can use `SETVAL` to set the current value of a sequence, the subsequent values of the sequence still follow the original progression rule.

For example:

```
1, 3, 5, ...            // The sequence starts from 1 and increments by 2.
select SETVAL(seq, 6)   // Sets the current value of a sequence to 6.
7, 9, 11, ...           // Subsequent values still follow the progression rule.
```

In the `CYCLE` mode, the initial value of a sequence in the first round is the value of the `START` parameter, and the initial value in the subsequent rounds is the value of `MinValue` (`INCREMENT` > 0) or `MaxValue` (`INCREMENT` < 0).
## See also

* [ALTER SEQUENCE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-sequence)
* [DROP SEQUENCE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-sequence)
* [SHOW CREATE SEQUENCE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-sequence)
* [Sequence Functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/sequence-functions)
