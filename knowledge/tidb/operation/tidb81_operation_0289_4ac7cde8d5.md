# TiDB Cloud CLI user profile management

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/cli-reference.md`
- Source Title: `TiDB Cloud CLI Reference`
- Source Heading Path: `TiDB Cloud CLI Reference (Beta) > User profile | TiDB Cloud CLI Reference (Beta) > User profile > Create a user profile with TiDB Cloud API key | TiDB Cloud CLI Reference (Beta) > User profile > Create a user profile with OAuth token | TiDB Cloud CLI Reference (Beta) > User profile > List all user profiles | TiDB Cloud CLI Reference (Beta) > User profile > Describe a user profile | TiDB Cloud CLI Reference (Beta) > User profile > Set properties in a user profile | TiDB Cloud CLI Reference (Beta) > User profile > Switch to another user profile | TiDB Cloud CLI Reference (Beta) > User profile > Edit the config file | TiDB Cloud CLI Reference (Beta) > User profile > Delete a user profile`
- Source Line Ranges: `52-117`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `user-profile`, `api-key`, `oauth-token`, `config`, `list`, `describe`, `set`, `switch`, `edit`, `delete`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0289_4ac7cde8d5`
- Source ID: `tidb-docs-8.1:tidb-cloud/cli-reference.md#user-profile`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f0da7e5a05598300d5a0e76b7a8689a1564ca3d83b5bfb130a1608478b904caf`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/cli-reference.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiDB Cloud CLI user profile concepts or the commands for creating, listing, describing, setting, switching, editing, or deleting profiles.
- Retrieval Keywords: User profile, ticloud config create, ticloud auth login, OAuth token, TiDB Cloud API key, default profile, API key takes precedence over the OAuth token, ticloud config list, default (active), ticloud config describe, private-key, public-key, ticloud config set, ticloud config use, Current profile has been changed to default, ticloud config edit, ticloud config delete
- Follow-up Guidance: The source states that to use TiDB Cloud CLI, you must have a user profile.
- Classification Note: This is operation content because it describes profile-related CLI tasks and the exact commands used to manage TiDB Cloud CLI user profiles.

## Official Source Content

## User profile

For the TiDB Cloud CLI, a user profile is a collection of properties associated with a user, including the profile name, public key, private key, and OAuth token. To use TiDB Cloud CLI, you must have a user profile.
### Create a user profile with TiDB Cloud API key

Use [`ticloud config create`](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-config-create) to create a user profile.
### Create a user profile with OAuth token

Use [`ticloud auth login`](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-auth-login) to assign OAuth token to the current profile. If no profiles exist, a profile named `default` will be created automatically.

> **Note:**
>
> In the preceding two methods, the TiDB Cloud API key takes precedence over the OAuth token. If both are available in the current profile, the API key will be used.
### List all user profiles

Use [`ticloud config list`](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-config-list) to list all user profiles.

An example output is as follows:

```
Profile Name
default (active)
dev
staging
```

In this example output, the user profile `default` is currently active.
### Describe a user profile

Use [`ticloud config describe`](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-config-describe) to get the properties of a user profile.

An example output is as follows:

```json
{
  "private-key": "xxxxxxx-xxx-xxxxx-xxx-xxxxx",
  "public-key": "Uxxxxxxx"
}
```
### Set properties in a user profile

Use [`ticloud config set`](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-config-set) to set properties in a user profile.
### Switch to another user profile

Use [`ticloud config use`](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-config-use) to switch to another user profile.

An example output is as follows:

```
Current profile has been changed to default
```
### Edit the config file

Use [`ticloud config edit`](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-config-edit) to open the configuration file for editing.
### Delete a user profile

Use [`ticloud config delete`](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-config-delete) to delete a user profile.
