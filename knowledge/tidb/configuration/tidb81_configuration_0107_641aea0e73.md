# TiKV master key configuration and rotation

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/encryption-at-rest.md`
- Source Title: `Encryption at Rest`
- Source Heading Path: `Encryption at Rest > TiKV encryption at rest > Configure encryption > Specify a master key via KMS | Encryption at Rest > TiKV encryption at rest > Configure encryption > Specify a master key via a file | Encryption at Rest > TiKV encryption at rest > Rotate the master key`
- Source Line Ranges: `92-252`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `encryption-at-rest`, `master-key`, `kms`, `aws`, `gcp`, `azure`, `file-based-key`, `key-rotation`, `restart`, `rolling-restart`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0107_641aea0e73`
- Source ID: `tidb-docs-8.1:encryption-at-rest.md#specify-a-master-key-via-kms`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cf510ac23ea6985ec2f5c70ccec186bd354c4eb674ef434b48d035315626d9f5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/encryption-at-rest#specify-a-master-key-via-kms
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/encryption-at-rest.md

## Retrieval Guidance

- Use When: Use this chunk when you need the exact TiKV master key configuration formats for KMS or file-based keys, or the documented master key rotation behavior and restart requirements.
- Retrieval Keywords: [security.encryption.master-key], [security.encryption.previous-master-key], type = "kms", type = "file", AWS KMS, Google Cloud KMS, Azure KMS, vendor = "gcp", vendor = 'azure', credential-file-path, keyvault-url, client-id, tenant-id, path = "/path/to/key/file", 256 bits (or 32 bytes) key encoded as hex string, Rotate the master key, online master key rotation is not supported, rolling restart, restart TiKV
- Follow-up Guidance: The source also states that TiKV must access both the old and new master key during restart, and after startup it only needs access to the new key.
- Classification Note: This is classified as configuration because the content defines TiKV encryption master key settings, provider-specific fields, file key format, and the configuration keys used for master key rotation.

## Official Source Content

#### Specify a master key via KMS

TiKV supports KMS encryption for three platforms: AWS, Google Cloud, and Azure. Depending on the platform where your service is deployed, you can choose one of them to configure KMS encryption.

> **Warning:**
>
> Currently, specifying a master key using Google Cloud KMS is experimental. It is not recommended that you use it in production environments. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.

<div label="AWS KMS">

**Step 1. Create a master key**

To create a key on AWS, take the following steps:

1. Go to the [AWS KMS](https://console.aws.amazon.com/kms) on the AWS console.
2. Make sure that you have selected the correct region on the top right corner of your console.
3. Click **Create key** and select **Symmetric** as the key type.
4. Set an alias for the key.

You can also perform the operations using the AWS CLI:

```shell
aws --region us-west-2 kms create-key
aws --region us-west-2 kms create-alias --alias-name "alias/tidb-tde" --target-key-id 0987dcba-09fe-87dc-65ba-ab0987654321
```

The `--target-key-id` to enter in the second command is in the output of the first command.

**Step 2. Configure the master key**

To specify the master key using AWS KMS, add the `[security.encryption.master-key]` configuration after the `[security.encryption]` section in the TiKV configuration file:

```
[security.encryption.master-key]
type = "kms"
key-id = "0987dcba-09fe-87dc-65ba-ab0987654321"
region = "us-west-2"
endpoint = "https://kms.us-west-2.amazonaws.com"
```

The `key-id` specifies the key ID for the KMS CMK. The `region` is the AWS region name for the KMS CMK. The `endpoint` is optional and you do not need to specify it normally unless you are using an AWS KMS-compatible service from a non-AWS vendor or need to use a [VPC endpoint for KMS](https://docs.aws.amazon.com/kms/latest/developerguide/kms-vpc-endpoint.html).

You can also use [multi-Region keys](https://docs.aws.amazon.com/kms/latest/developerguide/multi-region-keys-overview.html) in AWS. For this, you need to set up a primary key in a specific region and add replica keys in the regions you require.

</div>
<div label="Google Cloud KMS">

**Step 1. Create a master key**

To create a key on Google Cloud, take the following steps:

1. Go to the [Key Management](https://console.cloud.google.com/security/kms/keyrings) page in the Google Cloud console.
2. Click **Create key ring**. Enter a name for the key ring, select a location of the key ring, and then click **Create**. Note that the location of the key ring needs to cover the region where the TiDB cluster is deployed.
3. Select the key ring you created in the previous step, and then click **Create Key** on the key ring details page.
4. Enter a name for the key, set the key information as follows, and then click **Create**.

    - **Protection level**: **Software** or **HSM**
    - **Key Material**: **Generated key**
    - **Purpose**: **Symmetric encrypt/decrypt**

You can also perform this operation using the gcloud CLI:

```shell
gcloud kms keyrings create "key-ring-name" --location "global"
gcloud kms keys create "key-name" --keyring "key-ring-name" --location "global" --purpose "encryption" --rotation-period "30d"
```

Make sure to replace the values of `"key-ring-name"`, `"key-name"`, `"global"`, and `"30d"` in the preceding command with the names and configurations corresponding to your actual key.

**Step 2. Configure the master key**

To specify the master key using Google Cloud KMS, add the `[security.encryption.master-key]` configuration after the `[security.encryption]` section:

```
[security.encryption.master-key]
type = "kms"
key-id = "projects/project-name/locations/global/keyRings/key-ring-name/cryptoKeys/key-name"
vendor = "gcp"

[security.encryption.master-key.gcp]
credential-file-path = "/path/to/credential.json"
```

- `key-id` specifies the key ID of the KMS CMK.
- `credential-file-path` specifies the path of the authentication credentials file, which currently supports two types of credentials: Service Account and Authentication User. If the TiKV environment is already configured with [application default credentials](https://cloud.google.com/docs/authentication/application-default-credentials), there is no need to configure `credential-file-path`.

</div>
<div label="Azure KMS">

**Step 1. Create a master key**

To create a key on Azure, refer to the instructions in [Set and retrieve a key from Azure Key Vault using the Azure portal](https://learn.microsoft.com/en-us/azure/key-vault/keys/quick-create-portal).

**Step 2. Configure the master key**

To specify the master key using Azure KMS, add the `[security.encryption.master-key]` configuration after the `[security.encryption]` section in the TiKV configuration file:

```
[security.encryption.master-key]
type = 'kms'
key-id = 'your-kms-key-id'
region = 'region-name'
endpoint = 'endpoint'
vendor = 'azure'

[security.encryption.master-key.azure]
tenant-id = 'tenant_id'
client-id = 'client_id'
keyvault-url = 'keyvault_url'
hsm-name = 'hsm_name'
hsm-url = 'hsm_url'
# The following four fields are optional, used to set client authentication credentials. You can configure them according to the requirements of your scenario.
client_certificate = ""
client_certificate_path = ""
client_certificate_password = ""
client_secret = ""
```

Except `vendor`, you need to modify the values of other fields in the preceding configuration to the corresponding configuration of the actual key.

</div>
#### Specify a master key via a file

To specify a master key that's stored in a file, the master key configuration would look like the following:

```
[security.encryption.master-key]
type = "file"
path = "/path/to/key/file"
```

Here `path` is the path to the key file. The file must contain a 256 bits (or 32 bytes) key encoded as hex string, end with a newline (`\n`) and contain nothing else. Example of the file content:

```
3b5896b5be691006e0f71c3040a29495ddcad20b14aff61806940ebd780d3c62
```
### Rotate the master key

To rotate master key, you have to specify both of the new master key and old master key in the configuration, and restart TiKV. Use `security.encryption.master-key` to specify the new master key, and use `security.encryption.previous-master-key` to specify the old master key. The configuration format for `security.encryption.previous-master-key` is the same as `encryption.master-key`. On restart TiKV must access both of the old and new master key, but once TiKV is up and running, TiKV will only need access to the new key. It is okay to leave the `encryption.previous-master-key` configuration in the configuration file from that on. Even on restart, TiKV only tries to use the old key if it fails to decrypt existing data using the new master key.

Currently online master key rotation is not supported, so you need to restart TiKV. It is advised to do a rolling restart to a running TiKV cluster serving online query.

Here is an example configuration for rotating the KMS CMK:

```
[security.encryption.master-key]
type = "kms"
key-id = "50a0c603-1c6f-11e6-bb9e-3fadde80ce75"
region = "us-west-2"

[security.encryption.previous-master-key]
type = "kms"
key-id = "0987dcba-09fe-87dc-65ba-ab0987654321"
region = "us-west-2"
```
