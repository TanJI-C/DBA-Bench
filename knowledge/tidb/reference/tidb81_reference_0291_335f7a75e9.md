# Bit functions and bitwise operators reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/bit-functions-and-operators.md`
- Source Title: `Bit Functions and Operators`
- Source Heading Path: `Bit Functions and Operators | Bit Functions and Operators > [`BIT_COUNT()`](https://dev.mysql.com/doc/refman/8.0/en/bit-functions.html#function_bit-count) | Bit Functions and Operators > [`&` (bitwise AND)](https://dev.mysql.com/doc/refman/8.0/en/bit-functions.html#operator_bitwise-and) | Bit Functions and Operators > [`~` (bitwise inversion)](https://dev.mysql.com/doc/refman/8.0/en/bit-functions.html#operator_bitwise-invert) | Bit Functions and Operators > [`|` (bitwise OR)](https://dev.mysql.com/doc/refman/8.0/en/bit-functions.html#operator_bitwise-or) | Bit Functions and Operators > [`^` (bitwise XOR)](https://dev.mysql.com/doc/refman/8.0/en/bit-functions.html#operator_bitwise-xor)`
- Source Line Ranges: `5-228`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `bit-functions`, `bitwise-operators`, `sql-functions`, `mysql-compatibility`, `binary-literals`, `hex-literals`, `network-mask`, `cidr`, `ip-address`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0291_335f7a75e9`
- Source ID: `tidb-docs-8.1:functions-and-operators/bit-functions-and-operators.md#bit-functions-and-operators`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ec9c87966bc4fbb5318066f966429ef9643e90d5b6aaffae4ef9b7d2ffa73474`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/bit-functions-and-operators#bit-functions-and-operators
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/bit-functions-and-operators.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB SQL reference details and examples for bit functions and bitwise operators such as BIT_COUNT(), &, ~, |, ^, <<, and >>, including binary literals, hex literals, and IP or netmask calculations.
- Retrieval Keywords: Bit Functions and Operators, BIT_COUNT(), bitwise AND, &, bitwise inversion, ~, bitwise OR, |, bitwise XOR, ^, left shift, <<, right shift, >>, b'00101001', 0x29, CONV(), INET_ATON(), INET_NTOA(), CIDR, netmask, 255.255.255.0, 192.168.1.1, 192.168.1.2, MySQL 8.0
- Follow-up Guidance: The examples show BIT_COUNT(expr) with bit-literals and hex-literals, using INET_ATON('255.255.255.0') for CIDR conversion, and combining INET_ATON() with INET_NTOA() and the & operator to derive a network address.
- Classification Note: This is a SQL reference chunk because it lists supported bit functions and operators and explains their behavior with SQL examples and notes about literal interpretation.

## Official Source Content

# Bit Functions and Operators

TiDB supports all of the [bit functions and operators](https://dev.mysql.com/doc/refman/8.0/en/bit-functions.html) available in MySQL 8.0.

**Bit functions and operators:**

| Name | Description |
| :------| :------------- |
| [`BIT_COUNT()`](#bit_count) | Return the number of bits that are set as 1 |
| [<code>&</code>](#-bitwise-and) | Bitwise AND |
| [<code>~</code>](#-bitwise-inversion) | Bitwise inversion |
| [<code>\|</code>](#-bitwise-or) | Bitwise OR |
| [`^`](#-bitwise-xor) | Bitwise XOR |
| [`<<`](#-left-shift) | Left shift |
| [`>>`](#-right-shift) | Right shift |
## [`BIT_COUNT()`](https://dev.mysql.com/doc/refman/8.0/en/bit-functions.html#function_bit-count)

The `BIT_COUNT(expr)` function returns the number of bits that are set as 1 in `expr`.

```sql
SELECT BIT_COUNT(b'00101001');
```

```
+------------------------+
| BIT_COUNT(b'00101001') |
+------------------------+
|                      3 |
+------------------------+
1 row in set (0.00 sec)
```

> **Note:**
>
> If the argument `expr` is a binary number, you need to specify `b` explicitly before the number, such as `b'00101001'`. Otherwise, this function treats it as a string and returns a different result. For example, `BIT_COUNT('00101001')` returns `7` because it converts the string `'00101001'` as the decimal number `101001` and counts the number of `1` bits in its binary format `11000100001010001`.

The following example is similar to the preceding one, but it uses a hex-literal instead of a bit-literal as the argument. The `CONV()` function converts `0x29` from hexadecimal (base 16) to binary (base 2), showing that it equals `00101001` in binary.

```sql
SELECT BIT_COUNT(0x29), CONV(0x29,16,2);
```

```
+-----------------+-----------------+
| BIT_COUNT(0x29) | CONV(0x29,16,2) |
+-----------------+-----------------+
|               3 | 101001          |
+-----------------+-----------------+
1 row in set (0.01 sec)
```

A practical use of the `BIT_COUNT(expr)` function is to convert a netmask to a [CIDR](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing) notation. In the following example, the netmask `255.255.255.0` is converted to its CIDR representation `24`.

```sql
SELECT BIT_COUNT(INET_ATON('255.255.255.0'));
```

```
+---------------------------------------+
| BIT_COUNT(INET_ATON('255.255.255.0')) |
+---------------------------------------+
|                                    24 |
+---------------------------------------+
1 row in set (0.00 sec)
```
## [`&` (bitwise AND)](https://dev.mysql.com/doc/refman/8.0/en/bit-functions.html#operator_bitwise-and)

The `&` operator performs a bitwise AND operation. It compares the corresponding bits of two numbers: if both corresponding bits are 1, the corresponding bit of the result is 1; otherwise, it is 0.

For example, a bitwise AND operation between `1010` and `1100` returns `1000`, because only the leftmost bit is set as 1 in both numbers.

```
  1010
& 1100
  ----
  1000
```

In SQL, you can use the `&` operator as follows:

```sql
SELECT CONV(b'1010' & b'1000',10,2);
```

```
+------------------------------+
| CONV(b'1010' & b'1000',10,2) |
+------------------------------+
| 1000                         |
+------------------------------+
1 row in set (0.00 sec)
```

You can use the `&` operator with `INET_NTOA()` and `INET_ATON()` functions to perform a bitwise AND operation on an IP address and a network mask to get the network address. This is useful to determine whether multiple IP addresses belong to the same network or not.

In the following two examples, the IP addresses `192.168.1.1` and `192.168.1.2` are in the same network `192.168.1.0/24` when masked with `255.255.255.0`.

```sql
SELECT INET_NTOA(INET_ATON('192.168.1.1') & INET_ATON('255.255.255.0'));
```

```
+------------------------------------------------------------------+
| INET_NTOA(INET_ATON('192.168.1.1') & INET_ATON('255.255.255.0')) |
+------------------------------------------------------------------+
| 192.168.1.0                                                      |
+------------------------------------------------------------------+
1 row in set (0.00 sec)
```

```sql
SELECT INET_NTOA(INET_ATON('192.168.1.2') & INET_ATON('255.255.255.0'));
```

```
+------------------------------------------------------------------+
| INET_NTOA(INET_ATON('192.168.1.2') & INET_ATON('255.255.255.0')) |
+------------------------------------------------------------------+
| 192.168.1.0                                                      |
+------------------------------------------------------------------+
1 row in set (0.00 sec)
```
## [`~` (bitwise inversion)](https://dev.mysql.com/doc/refman/8.0/en/bit-functions.html#operator_bitwise-invert)

The `~` operator performs a bitwise inversion (or bitwise NOT) operation on a given value. It inverts each bit of the given value: bits that are 0 become 1, and bits that are 1 become 0.

Before the operation, the value is expanded to 64 bits.

Take the binary number `1111000011110000` as an example. When expanded to 64 bits and inverted, it looks like this:

```
Original (16 bits):                                                                 1111000011110000
Expanded and inverted (64 bits):    1111111111111111111111111111111111111111111111110000111100001111
```

In SQL, you can use the `~` operator as follows:

```sql
SELECT CONV(~ b'1111000011110000',10,2);
+------------------------------------------------------------------+
| CONV(~ b'1111000011110000',10,2)                                 |
+------------------------------------------------------------------+
| 1111111111111111111111111111111111111111111111110000111100001111 |
+------------------------------------------------------------------+
1 row in set (0.00 sec)
```

You can reverse the inversion by applying the `~` operator again to the result:

```sql
SELECT CONV(~ b'1111111111111111111111111111111111111111111111110000111100001111',10,2);
```

```
+----------------------------------------------------------------------------------+
| CONV(~ b'1111111111111111111111111111111111111111111111110000111100001111',10,2) |
+----------------------------------------------------------------------------------+
| 1111000011110000                                                                 |
+----------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```
## [`|` (bitwise OR)](https://dev.mysql.com/doc/refman/8.0/en/bit-functions.html#operator_bitwise-or)

The `|` operator performs a bitwise OR operation. It compares the corresponding bits of two numbers: if at least one of the corresponding bits is 1, the corresponding bit in the result is 1.

For example, a bitwise OR operation between `1010` and `1100` returns `1110`, because among the first three bits of the two numbers, at least one of the corresponding bits is set as 1.

```
  1010
| 1100
  ----
  1110
```

In SQL, you can use the `|` operator as follows:

```sql
SELECT CONV(b'1010' | b'1100',10,2);
```

```
+------------------------------+
| CONV(b'1010' | b'1100',10,2) |
+------------------------------+
| 1110                         |
+------------------------------+
1 row in set (0.00 sec)
```
## [`^` (bitwise XOR)](https://dev.mysql.com/doc/refman/8.0/en/bit-functions.html#operator_bitwise-xor)

The `^` operator performs a bitwise XOR (exclusive OR) operation. It compares the corresponding bits of two numbers: if the corresponding bits are different, the corresponding bit in the result is 1.

For example, a bitwise XOR operation between `1010` and `1100` returns `0110`, because the second and the third bits of the two numbers are different.

```
  1010
^ 1100
  ----
  0110
```

In SQL, you can use the `^` operator as follows:

```sql
SELECT CONV(b'1010' ^ b'1100',10,2);
```

```
+------------------------------+
| CONV(b'1010' ^ b'1100',10,2) |
+------------------------------+
| 110                          |
+------------------------------+
1 row in set (0.00 sec)
```

Note that the result is shown as `110` instead of `0110` because the leading zero is removed.
