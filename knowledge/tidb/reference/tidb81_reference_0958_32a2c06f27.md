# TiProxy API configuration endpoints

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiproxy/tiproxy-api.md`
- Source Title: `TiProxy API`
- Source Heading Path: `TiProxy API | TiProxy API > Get TiProxy configuration | TiProxy API > Get TiProxy configuration > Request URI | TiProxy API > Get TiProxy configuration > Parameter descriptions | TiProxy API > Get TiProxy configuration > Example | TiProxy API > Set TiProxy configuration | TiProxy API > Set TiProxy configuration > Request URI | TiProxy API > Set TiProxy configuration > Request body | TiProxy API > Set TiProxy configuration > Example`
- Source Line Ranges: `5-97`
- Source Scope: `self_managed`
- Primary Component: `tiproxy`
- Related Components: none
- Topic Tags: `api`, `configuration`, `request-uri`, `query-parameters`, `toml`, `json`, `debugging`, `curl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0958_32a2c06f27`
- Source ID: `tidb-docs-8.1:tiproxy/tiproxy-api.md#tiproxy-api`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `68de2e6ef5ee56e5ba775b4503245671ac4c7ff20f235ac9ef2792977305ce39`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-api#tiproxy-api
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiproxy/tiproxy-api.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiProxy API endpoints and request formats for reading or updating TiProxy configuration through /api/admin/config/.
- Retrieval Keywords: TiProxy API, GET /api/admin/config/, PUT /api/admin/config/, api.addr, format=json, format=toml, TiProxy configuration, TOML format, log.level, curl http://127.0.0.1:3080/api/admin/config/
- Follow-up Guidance: The source also notes that TiProxy API is designed for debugging purposes and might not be fully compatible with future capabilities introduced in TiProxy.
- Classification Note: This is reference content because it defines the TiProxy configuration API address pattern, query parameter format, request body format, and concrete curl examples for GET and PUT operations.

## Official Source Content

# TiProxy API

[TiProxy](https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-overview) provides API endpoints for accessing its configuration, health status, and monitoring data.

> **Note:**
>
> TiProxy API is specifically designed for debugging purposes and might not be fully compatible with future capabilities introduced in TiProxy. It's not recommended to include this tool in application or utility development to get information.

The address for accessing the TiProxy API is `http://${host}:${port}${path}`, where `${host}:${port}` is specified by the TiProxy configuration item [`api.addr`](https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-configuration#addr-1), and `${path}` is the specific API endpoint you want to access. For example:

```bash
curl http://127.0.0.1:3080/api/admin/config/
```
## Get TiProxy configuration
### Request URI

`GET /api/admin/config/`
### Parameter descriptions

The query parameter is as follows:

- `format`: (optional) specifies the format of the returned configuration. Value options are `json` and `toml`. The default value is `toml`.
### Example

The following example gets the TiProxy configuration in JSON format:

```bash
curl "http://127.0.0.1:3080/api/admin/config/?format=json"
```
## Set TiProxy configuration

Currently, you can only use the TOML format to modify TiProxy configuration. Unspecified configuration items will remain unchanged, so you only need to specify the items that you want to modify.
### Request URI

`PUT /api/admin/config/`
### Request body

You need to provide the TiProxy configuration in TOML format. For example:

```toml
[log]
level='warning'
```
### Example

The following example sets `log.level` as `'warning'`, while leaving other configuration items unchanged.

1. Get the current TiProxy configuration:

    ```bash
    curl http://127.0.0.1:3080/api/admin/config/
    ```

    The output is as follows:

    ```toml
    [log]
    encoder = 'tidb'
    level = 'info'
    ```

2. Specify the value of `log.level` in the `test.toml` file, and then send a `PUT /api/admin/config/` request to update the value of `log.level`:

    ```shell
    $ cat test.toml
    [log]
    level='warning'
    $ curl -X PUT --data-binary @test.toml http://127.0.0.1:3080/api/admin/config/
    ```

3. Get the modified TiProxy configuration:

    ```bash
    curl http://127.0.0.1:3080/api/admin/config/
    ```

    The output is as follows:

    ```toml
    [log]
    encoder = 'tidb'
    level = 'warning'
    ```
