# Vector function references, compatibility, and related link

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-functions-and-operators.md`
- Source Title: `Vector Functions and Operators`
- Source Heading Path: `Vector Functions and Operators > Full references > VEC_NEGATIVE_INNER_PRODUCT | Vector Functions and Operators > Full references > VEC_L1_DISTANCE | Vector Functions and Operators > Full references > VEC_DIMS | Vector Functions and Operators > Full references > VEC_L2_NORM | Vector Functions and Operators > Full references > VEC_FROM_TEXT | Vector Functions and Operators > Full references > VEC_AS_TEXT | Vector Functions and Operators > MySQL compatibility | Vector Functions and Operators > See also`
- Source Line Ranges: `147-284`
- Source Scope: `cloud`
- Primary Component: `sql`
- Related Components: `tidb`, `cloud`
- Topic Tags: `vector-functions`, `distance-metrics`, `inner-product`, `l1-distance`, `dimensions`, `l2-norm`, `text-conversion`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0923_40bec839f9`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-functions-and-operators.md#vec-negative-inner-product`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `85fbb92620a5b1bc2ed225bf1e2fe341e05b4335a95ada88255cecf40bff4a39`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-functions-and-operators#vec-negative-inner-product
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-functions-and-operators.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB Cloud SQL reference details for vector functions such as VEC_NEGATIVE_INNER_PRODUCT, VEC_L1_DISTANCE, VEC_DIMS, VEC_L2_NORM, VEC_FROM_TEXT, and VEC_AS_TEXT, including same-dimension requirements, examples, and MySQL compatibility.
- Retrieval Keywords: VEC_NEGATIVE_INNER_PRODUCT, VEC_L1_DISTANCE, VEC_DIMS, VEC_L2_NORM, VEC_FROM_TEXT, VEC_AS_TEXT, negative inner product, L1 distance, Manhattan distance, L2 norm, Euclidean norm, vector dimension, same dimension error, Converts a string into a vector, Converts a vector into a string, TiDB specific, not supported in MySQL, Vector Data Types
- Follow-up Guidance: The related link in this source is Vector Data Types.
- Classification Note: This is reference content because it lists SQL vector function signatures, formulas, examples, a TiDB-specific MySQL compatibility note, and a related documentation link.

## Official Source Content

### VEC_NEGATIVE_INNER_PRODUCT

```sql
VEC_NEGATIVE_INNER_PRODUCT(vector1, vector2)
```

Calculates the distance by using the negative of the [inner product](https://en.wikipedia.org/wiki/Dot_product) between two vectors, using the following formula:

$DISTANCE(p,q)=- INNER\_PROD(p,q)=-\sum \limits _{i=1}^{n}{p_{i}q_{i}}$

The two vectors must have the same dimension. Otherwise, an error is returned.

Example:

```sql
[tidb]> SELECT VEC_NEGATIVE_INNER_PRODUCT('[1,2]', '[3,4]');
+----------------------------------------------+
| VEC_NEGATIVE_INNER_PRODUCT('[1,2]', '[3,4]') |
+----------------------------------------------+
|                                          -11 |
+----------------------------------------------+
```
### VEC_L1_DISTANCE

```sql
VEC_L1_DISTANCE(vector1, vector2)
```

Calculates the [L1 distance](https://en.wikipedia.org/wiki/Taxicab_geometry) (Manhattan distance) between two vectors using the following formula:

$DISTANCE(p,q)=\sum \limits _{i=1}^{n}{|p_{i}-q_{i}|}$

The two vectors must have the same dimension. Otherwise, an error is returned.

Example:

```sql
[tidb]> SELECT VEC_L1_DISTANCE('[0,0]', '[3,4]');
+-----------------------------------+
| VEC_L1_DISTANCE('[0,0]', '[3,4]') |
+-----------------------------------+
|                                 7 |
+-----------------------------------+
```
### VEC_DIMS

```sql
VEC_DIMS(vector)
```

Returns the dimension of a vector.

Examples:

```sql
[tidb]> SELECT VEC_DIMS('[1,2,3]');
+---------------------+
| VEC_DIMS('[1,2,3]') |
+---------------------+
|                   3 |
+---------------------+

[tidb]> SELECT VEC_DIMS('[]');
+----------------+
| VEC_DIMS('[]') |
+----------------+
|              0 |
+----------------+
```
### VEC_L2_NORM

```sql
VEC_L2_NORM(vector)
```

Calculates the [L2 norm](<https://en.wikipedia.org/wiki/Norm_(mathematics)>) (Euclidean norm) of a vector using the following formula:

$NORM(p)=\sqrt {\sum \limits _{i=1}^{n}{p_{i}^{2}}}$

Example:

```sql
[tidb]> SELECT VEC_L2_NORM('[3,4]');
+----------------------+
| VEC_L2_NORM('[3,4]') |
+----------------------+
|                    5 |
+----------------------+
```
### VEC_FROM_TEXT

```sql
VEC_FROM_TEXT(string)
```

Converts a string into a vector.

Example:

```sql
[tidb]> SELECT VEC_FROM_TEXT('[1,2]') + VEC_FROM_TEXT('[3,4]');
+-------------------------------------------------+
| VEC_FROM_TEXT('[1,2]') + VEC_FROM_TEXT('[3,4]') |
+-------------------------------------------------+
| [4,6]                                           |
+-------------------------------------------------+
```
### VEC_AS_TEXT

```sql
VEC_AS_TEXT(vector)
```

Converts a vector into a string.

Example:

```sql
[tidb]> SELECT VEC_AS_TEXT('[1.000,   2.5]');
+-------------------------------+
| VEC_AS_TEXT('[1.000,   2.5]') |
+-------------------------------+
| [1,2.5]                       |
+-------------------------------+
```
## MySQL compatibility

The vector functions and the extended usage of built-in functions and operators over vector data types are TiDB specific, and are not supported in MySQL.
## See also

- [Vector Data Types](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-data-types)
