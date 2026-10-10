# CREATE OPERATOR

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/create_operator.md`
- Source Title: `create operator`
- Source Heading Path: `Part VI Reference > SQL Commands > CREATE OPERATOR`
- Source Line Ranges: `1-168`
- Chunk ID: `pg16_fact_0231_48e94c8544`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `ba66bc55f1b66ea985e3a6a93722fb644766a2a379c67201cfdd8737f7aeb003`

## Retrieval Guidance

- Use When: Use for operator definition syntax.
- Retrieval Keywords: CREATE OPERATOR, operator function, commutator, negator
- Follow-up Guidance: No section split needed.
- Classification Note: Operator creation reference.

## Official Source Content

CREATE OPERATOR
7
SQL - Language Statements

CREATE OPERATOR
define a new operator

```
CREATE OPERATOR `name` (
{FUNCTION|PROCEDURE} = `function_name`
[, LEFTARG = `left_type` ] [, RIGHTARG = `right_type` ]
[, COMMUTATOR = `com_op` ] [, NEGATOR = `neg_op` ]
[, RESTRICT = `res_proc` ] [, JOIN = `join_proc` ]
[, HASHES ] [, MERGES ]
)
```

## Description

`CREATE OPERATOR` defines a new operator,
`name`.  The user who
defines an operator becomes its owner.  If a schema name is given
then the operator is created in the specified schema.  Otherwise it
is created in the current schema.

The operator name is a sequence of up to `NAMEDATALEN`-1
(63 by default) characters from the following list:

```
+ - * /  = ~ ! @ # % ^ & | ` ?
```

There are a few restrictions on your choice of name:

- `--` and `/*` cannot appear anywhere in an operator name,
since they will be taken as the start of a comment.
- A multicharacter operator name cannot end in `+` or
`-`,
unless the name also contains at least one of these characters:

```
~ ! @ # % ^ & | ` ?
```

For example, `@-` is an allowed operator name,
but `*-` is not.
This restriction allows PostgreSQL to
parse SQL-compliant commands without requiring spaces between tokens.
- The symbol `=>` is reserved by the SQL grammar,
so it cannot be used as an operator name.

The operator `!=` is mapped to
`<>` on input, so these two names are always
equivalent.

For binary operators, both `LEFTARG` and
`RIGHTARG` must be defined.  For prefix operators only
`RIGHTARG` should be defined.
The `function_name`
function must have been previously defined using `CREATE
FUNCTION` and must be defined to accept the correct number
of arguments (either one or two) of the indicated types.

In the syntax of `CREATE OPERATOR`, the keywords
`FUNCTION` and `PROCEDURE` are
equivalent, but the referenced function must in any case be a function, not
a procedure.  The use of the keyword `PROCEDURE` here is
historical and deprecated.

The other clauses specify optional operator optimization clauses.
Their meaning is detailed in [xoper-optimization](#xoper-optimization).

To be able to create an operator, you must have `USAGE`
privilege on the argument types and the return type, as well
as `EXECUTE` privilege on the underlying function.  If a
commutator or negator operator is specified, you must own these operators.

## Parameters

**`name`**
: The name of the operator to be defined. See above for allowable
characters.  The name can be schema-qualified, for example
`CREATE OPERATOR myschema.+ (...)`.  If not, then
the operator is created in the current schema.  Two operators
in the same schema can have the same name if they operate on
different data types.  This is called
*overloading*.

**`function_name`**
: The function used to implement this operator.

**`left_type`**
: The data type of the operator's left operand, if any.
This option would be omitted for a prefix operator.

**`right_type`**
: The data type of the operator's right operand.

**`com_op`**
: The commutator of this operator.

**`neg_op`**
: The negator of this operator.

**`res_proc`**
: The restriction selectivity estimator function for this operator.

**`join_proc`**
: The join selectivity estimator function for this operator.

**`HASHES`**
: Indicates this operator can support a hash join.

**`MERGES`**
: Indicates this operator can support a merge join.

To give a schema-qualified operator name in `com_op` or the other optional
arguments, use the `OPERATOR()` syntax, for example:

```
COMMUTATOR = OPERATOR(myschema.===) ,
```

## Notes

Refer to [xoper](#xoper) for further information.

It is not possible to specify an operator's lexical precedence in
`CREATE OPERATOR`, because the parser's precedence behavior
is hard-wired.  See [sql-precedence](#sql-precedence) for precedence details.

The obsolete options `SORT1`, `SORT2`,
`LTCMP`, and `GTCMP` were formerly used to
specify the names of sort operators associated with a merge-joinable
operator.  This is no longer necessary, since information about
associated operators is found by looking at B-tree operator families
instead.  If one of these options is given, it is ignored except
for implicitly setting `MERGES` true.

Use [`DROP OPERATOR`](#sql-dropoperator) to delete user-defined operators
from a database.  Use [`ALTER OPERATOR`](#sql-alteroperator) to modify operators in a
database.

## Examples

The following command defines a new operator, area-equality, for
the data type `box`:

```
CREATE OPERATOR === (
LEFTARG = box,
RIGHTARG = box,
FUNCTION = area_equal_function,
COMMUTATOR = ===,
NEGATOR = !==,
RESTRICT = area_restriction_function,
JOIN = area_join_function,
HASHES, MERGES
);
```

## Compatibility

`CREATE OPERATOR` is a
PostgreSQL extension.  There are no
provisions for user-defined operators in the SQL standard.

## See Also
