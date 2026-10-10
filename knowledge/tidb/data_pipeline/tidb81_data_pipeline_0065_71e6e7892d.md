# TiCDC Avro Kafka consumer checksum verification flow

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-avro-checksum-verification.md`
- Source Title: `TiCDC Row Data Checksum Verification Based on Avro`
- Source Heading Path: `TiCDC Row Data Checksum Verification Based on Avro | TiCDC Row Data Checksum Verification Based on Avro > Decode data and get the corresponding schema | TiCDC Row Data Checksum Verification Based on Avro > Calculate and verify the checksum value`
- Source Line Ranges: `5-217`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `ecosystem`, `shared`
- Topic Tags: `avro`, `kafka`, `consumer`, `schema-registry`, `checksum`, `row-data`, `verification`, `golang`, `decoding`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0065_71e6e7892d`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-avro-checksum-verification.md#ticdc-row-data-checksum-verification-based-on-avro`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `00bf6bc3824a06d59598299b5658d52ba40701187e9a8614d957de42408240ec`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-avro-checksum-verification#ticdc-row-data-checksum-verification-based-on-avro
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-avro-checksum-verification.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiCDC Avro Kafka consumer flow in Golang that decodes Kafka messages with Schema Registry schemas and verifies Single-row data checksum values from row data.
- Retrieval Keywords: TiCDC Row Data Checksum Verification Based on Avro, avro-checksum-verification, kafka-go, Single-row data checksum feature, getValueMapAndSchema(), CalculateAndVerifyChecksum(), extractSchemaIDAndBinaryData, GetSchema, schema registry, Confluent Avro wire format, magicByte, goavro.Codec, NativeFromBinary, lookupResponse, ErrAvroInvalidMessage, ErrAvroSchemaAPIError, consumer.FetchMessage, consumer.CommitMessages, delete event does not have value, skip checksum verification
- Follow-up Guidance: The following sections describe the implementation of getValueMapAndSchema() and CalculateAndVerifyChecksum(), including decoding data, fetching the schema by schema ID, and comparing the calculated checksum with the expected checksum from the received message.
- Classification Note: This chunk is classified under the TiCDC data pipeline because it shows a self-managed Kafka consumer program that reads TiCDC Avro-encoded messages, retrieves schemas from Schema Registry, and performs checksum verification on row data.

## Official Source Content

# TiCDC Row Data Checksum Verification Based on Avro

This document introduces how to consume data sent to Kafka by TiCDC and encoded by Avro protocol using Golang, and how to perform data verification using the [Single-row data checksum feature](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-integrity-check).

The source code of this example is available in the [`avro-checksum-verification`](https://github.com/pingcap/tiflow/tree/release-8.1/examples/golang/avro-checksum-verification) directory.

The example in this document uses [kafka-go](https://github.com/segmentio/kafka-go) to create a simple Kafka consumer program. This program continuously reads data from a specified topic, calculates the checksum, and verifies its value.

```go
package main

import (
    "context"
    "encoding/binary"
    "encoding/json"
    "hash/crc32"
    "io"
    "math"
    "net/http"
    "strconv"
    "strings"

    "github.com/linkedin/goavro/v2"
    "github.com/pingcap/log"
    "github.com/pingcap/tidb/parser/mysql"
    "github.com/pingcap/tidb/types"
    "github.com/pingcap/tiflow/pkg/errors"
    "github.com/segmentio/kafka-go"
    "go.uber.org/zap"
)

const (
    // The first byte of the Confluent Avro wire format is always 0.
    // For more details, see https://docs.confluent.io/platform/current/schema-registry/fundamentals/serdes-develop/index.html#wire-format.
    magicByte = uint8(0)
)

func main() {
    var (
        kafkaAddr         = "127.0.0.1:9092"
        schemaRegistryURL = "http://127.0.0.1:8081"

        topic           = "avro-checksum-test"
        consumerGroupID = "avro-checksum-test"
    )

    consumer := kafka.NewReader(kafka.ReaderConfig{
        Brokers:  []string{kafkaAddr},
        GroupID:  consumerGroupID,
        Topic:    topic,
        MaxBytes: 10e6, // 10MB
    })
    defer consumer.Close()

    ctx := context.Background()
    log.Info("start consuming ...", zap.String("kafka", kafkaAddr), zap.String("topic", topic), zap.String("groupID", consumerGroupID))
    for {
        // 1. Fetch the kafka message.
        message, err := consumer.FetchMessage(ctx)
        if err != nil {
            log.Error("read kafka message failed", zap.Error(err))
        }

        value := message.Value
        if len(value) == 0 {
            log.Info("delete event does not have value, skip checksum verification", zap.String("topic", topic))
        }

        // 2. Decode the value to get the corresponding value map and schema map.
        valueMap, valueSchema, err := getValueMapAndSchema(value, schemaRegistryURL)
        if err != nil {
            log.Panic("decode kafka value failed", zap.String("topic", topic), zap.ByteString("value", value), zap.Error(err))
        }

        // 3. Calculate and verify checksum value using the value map and schema map obtained in the previous step.
        err = CalculateAndVerifyChecksum(valueMap, valueSchema)
        if err != nil {
            log.Panic("calculate checksum failed", zap.String("topic", topic), zap.ByteString("value", value), zap.Error(err))
        }

        // 4. Commit offset after the data is successfully consumed.
        if err := consumer.CommitMessages(ctx, message); err != nil {
            log.Error("commit kafka message failed", zap.Error(err))
            break
        }
    }
}
```

The key steps for calculating the checksum value are `getValueMapAndSchema()` and `CalculateAndVerifyChecksum()`. The following sections describe the implementation of these two functions.
## Decode data and get the corresponding schema

The `getValueMapAndSchema()` method decodes data and gets the corresponding schema. This method returns both the data and schema as a `map[string]interface{}` type.

```go
// data is the key or value of the received kafka message, and url is the schema registry url.
// This function returns the decoded value and corresponding schema as map.
func getValueMapAndSchema(data []byte, url string) (map[string]interface{}, map[string]interface{}, error) {
    schemaID, binary, err := extractSchemaIDAndBinaryData(data)
    if err != nil {
        return nil, nil, err
    }

    codec, err := GetSchema(url, schemaID)
    if err != nil {
        return nil, nil, err
    }

    native, _, err := codec.NativeFromBinary(binary)
    if err != nil {
        return nil, nil, err
    }

    result, ok := native.(map[string]interface{})
    if !ok {
        return nil, nil, errors.New("raw avro message is not a map")
    }

    schema := make(map[string]interface{})
    if err := json.Unmarshal([]byte(codec.Schema()), &schema); err != nil {
        return nil, nil, errors.Trace(err)
    }

    return result, schema, nil
}

// extractSchemaIDAndBinaryData 
func extractSchemaIDAndBinaryData(data []byte) (int, []byte, error) {
    if len(data) < 5 {
        return 0, nil, errors.ErrAvroInvalidMessage.FastGenByArgs()
    }
    if data[0] != magicByte {
        return 0, nil, errors.ErrAvroInvalidMessage.FastGenByArgs()
    }
    return int(binary.BigEndian.Uint32(data[1:5])), data[5:], nil
}

// GetSchema fetches the schema from the schema registry by the schema ID.
// This function returns a goavro.Codec that can be used to encode and decode the data.
func GetSchema(url string, schemaID int) (*goavro.Codec, error) {
    requestURI := url + "/schemas/ids/" + strconv.Itoa(schemaID)

    req, err := http.NewRequest("GET", requestURI, nil)
    if err != nil {
        log.Error("Cannot create the request to look up the schema", zap.Error(err))
        return nil, errors.WrapError(errors.ErrAvroSchemaAPIError, err)
    }
    req.Header.Add(
        "Accept",
        "application/vnd.schemaregistry.v1+json, application/vnd.schemaregistry+json, "+
            "application/json",
    )

    httpClient := &http.Client{}
    resp, err := httpClient.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    body, err := io.ReadAll(resp.Body)
    if err != nil {
        log.Error("Cannot parse the lookup schema response", zap.Error(err))
        return nil, errors.WrapError(errors.ErrAvroSchemaAPIError, err)
    }

    if resp.StatusCode == 404 {
        log.Warn("Specified schema not found in Registry", zap.String("requestURI", requestURI), zap.Int("schemaID", schemaID))
        return nil, errors.ErrAvroSchemaAPIError.GenWithStackByArgs("Schema not found in Registry")
    }

    if resp.StatusCode != 200 {
        log.Error("Failed to query schema from the Registry, HTTP error",
            zap.Int("status", resp.StatusCode), zap.String("uri", requestURI), zap.ByteString("responseBody", body))
        return nil, errors.ErrAvroSchemaAPIError.GenWithStack("Failed to query schema from the Registry, HTTP error")
    }

    var jsonResp lookupResponse
    err = json.Unmarshal(body, &jsonResp)
    if err != nil {
        log.Error("Failed to parse result from Registry", zap.Error(err))
        return nil, errors.WrapError(errors.ErrAvroSchemaAPIError, err)
    }

    codec, err := goavro.NewCodec(jsonResp.Schema)
    if err != nil {
        return nil, errors.WrapError(errors.ErrAvroSchemaAPIError, err)
    }
    return codec, nil
}

type lookupResponse struct {
    Name     string `json:"name"`
    SchemaID int    `json:"id"`
    Schema   string `json:"schema"`
}

```
## Calculate and verify the checksum value

The `valueMap` and `valueSchema` obtained in the previous step contain all the elements used for checksum calculation and verification.

The checksum calculation and verification process on the consumer side includes the following steps:

1. Get the expected checksum value.
2. Iterate over each column, generate a byte slice according to the column value and the corresponding MySQL type, and update the checksum value continuously.
3. Compare the checksum value calculated in the previous step with the checksum value obtained from the received message. If they are not the same, the checksum verification fails and the data might be corrupted.

The sample code is as follows:
