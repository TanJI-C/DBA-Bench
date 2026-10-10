# Avro row checksum calculation and verification code

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-avro-checksum-verification.md`
- Source Title: `TiCDC Row Data Checksum Verification Based on Avro`
- Source Heading Path: `TiCDC Row Data Checksum Verification Based on Avro > Calculate and verify the checksum value`
- Source Line Ranges: `218-514`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `shared`, `tidb`
- Topic Tags: `avro`, `checksum`, `row-data`, `schema-fields`, `crc32`, `type-conversion`, `value-decoding`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0066_035f434c18`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-avro-checksum-verification.md#calculate-and-verify-the-checksum-value`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d67ff2d3d2f62eaae37ac35890c013b12839f1fc31d84638923605cd9de2c794`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-avro-checksum-verification#calculate-and-verify-the-checksum-value
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-avro-checksum-verification.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiCDC Avro example code that calculates and verifies row-level checksums from decoded Avro value and schema maps, including type conversion and CRC32 updates.
- Retrieval Keywords: CalculateAndVerifyChecksum, _tidb_row_level_checksum, _tidb_op, crc32.Update, mysqlTypeFromTiDBType, getColumnValue, buildChecksumBytes, appendLengthValue, binaryLiteralToInt, trimLeadingZeroBytes, checksum mismatch, checksum verified, schema fields should be a map, value not found, invalid type for the checksum calculation, bigintUnsignedHandlingMode must be set to string, decimalHandlingMode must be set to string
- Follow-up Guidance: The code also shows how TiDB types such as ENUM, SET, BIT, DECIMAL, JSON, DATE, DATETIME, TIMESTAMP, and integer types are converted before checksum bytes are built.
- Classification Note: This is classified as data_pipeline for the ticdc component because the supplied content is implementation code for verifying TiCDC-delivered Avro row data checksums during data consumption.

## Official Source Content

```go
func CalculateAndVerifyChecksum(valueMap, valueSchema map[string]interface{}) error {
    // The fields variable stores the column type information for each data change event. The column IDs are used to sort the fields, which is the same as the order in which the checksum is calculated.
    fields, ok := valueSchema["fields"].([]interface{})
    if !ok {
        return errors.New("schema fields should be a map")
    }

    // 1. Get the expected checksum value from valueMap, which is encoded as a string.
    // If the expected checksum value is not found, it means that the checksum feature is not enabled when TiCDC sends the data. In this case, this function returns directly.
    o, ok := valueMap["_tidb_row_level_checksum"]
    if !ok {
        return nil
    }
    expected := o.(string)
    if expected == "" {
        return nil
    }

    // expectedChecksum is the expected checksum value passed from TiCDC.
    expectedChecksum, err := strconv.ParseUint(expected, 10, 64)
    if err != nil {
        return errors.Trace(err)
    }

    // 2. Iterate over each field and calculate the checksum value.
    var actualChecksum uint32
    // buf stores the byte slice used to update the checksum value each time.
    buf := make([]byte, 0)
    for _, item := range fields {
        field, ok := item.(map[string]interface{})
        if !ok {
            return errors.New("schema field should be a map")
        }

        // The tidbOp and subsequent columns are not involved in the checksum calculation, because they are used to assist data consumption and not real TiDB column data.
        colName := field["name"].(string)
        if colName == "_tidb_op" {
            break
        }

        // The holder variable stores the type information of each column.
        var holder map[string]interface{}
        switch ty := field["type"].(type) {
        case []interface{}:
            for _, item := range ty {
                if m, ok := item.(map[string]interface{}); ok {
                    holder = m["connect.parameters"].(map[string]interface{})
                    break
                }
            }
        case map[string]interface{}:
            holder = ty["connect.parameters"].(map[string]interface{})
        default:
            log.Panic("type info is anything else", zap.Any("typeInfo", field["type"]))
        }
        tidbType := holder["tidb_type"].(string)

        mysqlType := mysqlTypeFromTiDBType(tidbType)

        // Get the value of each column from the decoded value map according to the name of each column.
        value, ok := valueMap[colName]
        if !ok {
            return errors.New("value not found")
        }
        value, err := getColumnValue(value, holder, mysqlType)
        if err != nil {
            return errors.Trace(err)
        }

        if len(buf) > 0 {
            buf = buf[:0]
        }

        // Generate a byte slice used to update the checksum according to the value and mysqlType of each column, and then update the checksum value.
        buf, err = buildChecksumBytes(buf, value, mysqlType)
        if err != nil {
            return errors.Trace(err)
        }
        actualChecksum = crc32.Update(actualChecksum, crc32.IEEETable, buf)
    }

    if uint64(actualChecksum) != expectedChecksum {
        log.Error("checksum mismatch",
            zap.Uint64("expected", expectedChecksum),
            zap.Uint64("actual", uint64(actualChecksum)))
        return errors.New("checksum mismatch")
    }

    log.Info("checksum verified", zap.Uint64("checksum", uint64(actualChecksum)))
    return nil
}

func mysqlTypeFromTiDBType(tidbType string) byte {
    var result byte
    switch tidbType {
    case "INT", "INT UNSIGNED":
        result = mysql.TypeLong
    case "BIGINT", "BIGINT UNSIGNED":
        result = mysql.TypeLonglong
    case "FLOAT":
        result = mysql.TypeFloat
    case "DOUBLE":
        result = mysql.TypeDouble
    case "BIT":
        result = mysql.TypeBit
    case "DECIMAL":
        result = mysql.TypeNewDecimal
    case "TEXT":
        result = mysql.TypeVarchar
    case "BLOB":
        result = mysql.TypeLongBlob
    case "ENUM":
        result = mysql.TypeEnum
    case "SET":
        result = mysql.TypeSet
    case "JSON":
        result = mysql.TypeJSON
    case "DATE":
        result = mysql.TypeDate
    case "DATETIME":
        result = mysql.TypeDatetime
    case "TIMESTAMP":
        result = mysql.TypeTimestamp
    case "TIME":
        result = mysql.TypeDuration
    case "YEAR":
        result = mysql.TypeYear
    default:
        log.Panic("this should not happen, unknown TiDB type", zap.String("type", tidbType))
    }
    return result
}

// The value is an interface type, which needs to be converted according to the type information provided by the holder.
func getColumnValue(value interface{}, holder map[string]interface{}, mysqlType byte) (interface{}, error) {
    switch t := value.(type) {
    // The column with nullable is encoded as a map, and there is only one key-value pair. The key is the type, and the value is the real value. Only the real value is concerned here.
    case map[string]interface{}:
        for _, v := range t {
            value = v
        }
    }

    switch mysqlType {
    case mysql.TypeEnum:
        // Enum is encoded as a string, which is converted to the int value corresponding to the Enum definition here.
        allowed := strings.Split(holder["allowed"].(string), ",")
        switch t := value.(type) {
        case string:
            enum, err := types.ParseEnum(allowed, t, "")
            if err != nil {
                return nil, errors.Trace(err)
            }
            value = enum.Value
        case nil:
            value = nil
        }
    case mysql.TypeSet:
        // Set is encoded as a string, which is converted to the int value corresponding to the Set definition here.
        elems := strings.Split(holder["allowed"].(string), ",")
        switch t := value.(type) {
        case string:
            s, err := types.ParseSet(elems, t, "")
            if err != nil {
                return nil, errors.Trace(err)
            }
            value = s.Value
        case nil:
            value = nil
        }
    }
    return value, nil
}

// buildChecksumBytes generates a byte slice used to update the checksum, refer to https://github.com/pingcap/tidb/blob/e3417913f58cdd5a136259b902bf177eaf3aa637/util/rowcodec/common.go#L308
func buildChecksumBytes(buf []byte, value interface{}, mysqlType byte) ([]byte, error) {
    if value == nil {
        return buf, nil
    }

    switch mysqlType {
    // TypeTiny, TypeShort, and TypeInt32 are encoded as int32.
    // TypeLong is encoded as int32 if signed, otherwise, it is encoded as int64.
    // TypeLongLong is encoded as int64 if signed, otherwise, it is encoded as uint64.
    // When the checksum feature is enabled, bigintUnsignedHandlingMode must be set to string, which is encoded as string.
    case mysql.TypeTiny, mysql.TypeShort, mysql.TypeLong, mysql.TypeLonglong, mysql.TypeInt24, mysql.TypeYear:
        switch a := value.(type) {
        case int32:
            buf = binary.LittleEndian.AppendUint64(buf, uint64(a))
        case uint32:
            buf = binary.LittleEndian.AppendUint64(buf, uint64(a))
        case int64:
            buf = binary.LittleEndian.AppendUint64(buf, uint64(a))
        case uint64:
            buf = binary.LittleEndian.AppendUint64(buf, a)
        case string:
            v, err := strconv.ParseUint(a, 10, 64)
            if err != nil {
                return nil, errors.Trace(err)
            }
            buf = binary.LittleEndian.AppendUint64(buf, v)
        default:
            log.Panic("unknown golang type for the integral value",
                zap.Any("value", value), zap.Any("mysqlType", mysqlType))
        }
    // Encode float type as float64 and encode double type as float64.
    case mysql.TypeFloat, mysql.TypeDouble:
        var v float64
        switch a := value.(type) {
        case float32:
            v = float64(a)
        case float64:
            v = a
        }
        if math.IsInf(v, 0) || math.IsNaN(v) {
            v = 0
        }
        buf = binary.LittleEndian.AppendUint64(buf, math.Float64bits(v))
    // getColumnValue encodes Enum and Set to uint64 type.
    case mysql.TypeEnum, mysql.TypeSet:
        buf = binary.LittleEndian.AppendUint64(buf, value.(uint64))
    case mysql.TypeBit:
        // Encode bit type as []byte and convert it to uint64.
        v, err := binaryLiteralToInt(value.([]byte))
        if err != nil {
            return nil, errors.Trace(err)
        }
        buf = binary.LittleEndian.AppendUint64(buf, v)
    // Non-binary types are encoded as string, and binary types are encoded as []byte.
    case mysql.TypeVarchar, mysql.TypeVarString, mysql.TypeString, mysql.TypeTinyBlob, mysql.TypeMediumBlob, mysql.TypeLongBlob, mysql.TypeBlob:
        switch a := value.(type) {
        case string:
            buf = appendLengthValue(buf, []byte(a))
        case []byte:
            buf = appendLengthValue(buf, a)
        default:
            log.Panic("unknown golang type for the string value",
                zap.Any("value", value), zap.Any("mysqlType", mysqlType))
        }
    case mysql.TypeTimestamp, mysql.TypeDatetime, mysql.TypeDate, mysql.TypeDuration, mysql.TypeNewDate:
        v := value.(string)
        buf = appendLengthValue(buf, []byte(v))
    // When the checksum feature is enabled, decimalHandlingMode must be set to string.
    case mysql.TypeNewDecimal:
        buf = appendLengthValue(buf, []byte(value.(string)))
    case mysql.TypeJSON:
        buf = appendLengthValue(buf, []byte(value.(string)))
    // Null and Geometry are not involved in the checksum calculation.
    case mysql.TypeNull, mysql.TypeGeometry:
    // do nothing
    default:
        return buf, errors.New("invalid type for the checksum calculation")
    }
    return buf, nil
}

func appendLengthValue(buf []byte, val []byte) []byte {
    buf = binary.LittleEndian.AppendUint32(buf, uint32(len(val)))
    buf = append(buf, val...)
    return buf
}

// Convert []byte to uint64, refer to https://github.com/pingcap/tidb/blob/e3417913f58cdd5a136259b902bf177eaf3aa637/types/binary_literal.go#L105
func binaryLiteralToInt(bytes []byte) (uint64, error) {
    bytes = trimLeadingZeroBytes(bytes)
    length := len(bytes)

    if length > 8 {
        log.Error("invalid bit value found", zap.ByteString("value", bytes))
        return math.MaxUint64, errors.New("invalid bit value")
    }

    if length == 0 {
        return 0, nil
    }

    val := uint64(bytes[0])
    for i := 1; i < length; i++ {
        val = (val << 8) | uint64(bytes[i])
    }
    return val, nil
}

func trimLeadingZeroBytes(bytes []byte) []byte {
    if len(bytes) == 0 {
        return bytes
    }
    pos, posMax := 0, len(bytes)-1
    for ; pos < posMax; pos++ {
        if bytes[pos] != 0 {
            break
        }
    }
    return bytes[pos:]
}
```
