# DM-master configuration template and global parameters

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-master-configuration-file.md`
- Source Title: `DM-master Configuration File`
- Source Heading Path: `DM-master Configuration File | DM-master Configuration File > Configuration file template | DM-master Configuration File > Configuration parameters | DM-master Configuration File > Configuration parameters > Global configuration`
- Source Line Ranges: `5-62`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `configuration-file`, `global-configuration`, `network-addresses`, `peer-urls`, `cluster-bootstrap`, `tls`, `logging`, `secret-key`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0077_c95eb76acc`
- Source ID: `tidb-docs-8.1:dm/dm-master-configuration-file.md#dm-master-configuration-file`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e61056add4412c8b890e8b2abe0786ee6603dad17ac5d1b0662e00f7b73040df`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-master-configuration-file#dm-master-configuration-file
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-master-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the DM-master configuration file template or the meaning of global DM-master parameters for addresses, peer URLs, cluster bootstrap, TLS, logging, or secret key settings.
- Retrieval Keywords: DM-master configuration file, dm-master.toml, name, log-level, log-file, master-addr, advertise-addr, peer-urls, advertise-peer-urls, initial-cluster, join, ssl-ca, ssl-cert, ssl-key, cert-allowed-cn, secret-key-path, 64-character hexadecimal AES-256 secret key, head -n 256 /dev/urandom | sha256sum
- Follow-up Guidance: The source also points to Customize a secret key for DM encryption and decryption for more information about secret-key-path.
- Classification Note: This chunk is classified as configuration because it provides the DM-master configuration template and describes global configuration parameters and their meanings.

## Official Source Content

# DM-master Configuration File

This document introduces the configuration of DM-master, including a configuration file template and a description of each configuration parameter in this file.
## Configuration file template

The following is a configuration file template of DM-master.

```toml
name = "dm-master"

# log configuration
log-level = "info"
log-file = "dm-master.log"

# DM-master listening address
master-addr = ":8261"
advertise-addr = "127.0.0.1:8261"

# URLs for peer traffic
peer-urls = "http://127.0.0.1:8291"
advertise-peer-urls = "http://127.0.0.1:8291"

# cluster configuration
initial-cluster = "master1=http://127.0.0.1:8291,master2=http://127.0.0.1:8292,master3=http://127.0.0.1:8293"
join = ""

ssl-ca = "/path/to/ca.pem"
ssl-cert = "/path/to/cert.pem"
ssl-key = "/path/to/key.pem"
cert-allowed-cn = ["dm"]

secret-key-path = "/path/to/secret/key"
```
## Configuration parameters

This section introduces the configuration parameters of DM-master.
### Global configuration

| Parameter        | Description                                    |
| :------------ | :--------------------------------------- |
| `name` | The name of the DM-master. |
| `log-level` | Specifies a log level from `debug`, `info`, `warn`, `error`, and `fatal`. The default log level is `info`. |
| `log-file` | Specifies the log file directory. If the parameter is not specified, the logs are printed onto the standard output. |
| `master-addr` | Specifies the address of DM-master which provides services. You can omit the IP address and specify the port number only, such as ":8261". |
| `advertise-addr` | Specifies the address that DM-master advertises to the outside world. |
| `peer-urls` | Specifies the peer URL of the DM-master node. |
| `advertise-peer-urls` | Specifies the peer URL that DM-master advertises to the outside world. The value of `advertise-peer-urls` is by default the same as that of `peer-urls`. |
| `initial-cluster` | The value of `initial-cluster` is the combination of the `advertise-peer-urls` value of all DM-master nodes in the initial cluster. |
| `join` | The value of `join` is the combination of the `advertise-peer-urls` value of the existed DM-master nodes in the cluster. If the DM-master node is newly added, replace `initial-cluster` with `join`. |
| `ssl-ca` | The path of the file that contains list of trusted SSL CAs for DM-master to connect with other components. |
| `ssl-cert` | The path of the file that contains X509 certificate in PEM format for DM-master to connect with other components. |
| `ssl-key` | The path of the file that contains X509 key in PEM format for DM-master to connect with other components. |
| `cert-allowed-cn` | Common Name list. |
| `secret-key-path` | The file path of the secret key, which is used to encrypt and decrypt upstream and downstream passwords. The file must contain a 64-character hexadecimal AES-256 secret key. One way to generate this key is by calculating SHA256 checksum of random data, such as <code>head -n 256 /dev/urandom \| sha256sum</code>. For more information, see [Customize a secret key for DM encryption and decryption](https://docs.pingcap.com/tidb/stable/dm/dm-customized-secret-key). |
