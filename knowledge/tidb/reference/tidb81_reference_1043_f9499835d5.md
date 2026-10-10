# TiUP mirror root certificate format

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-mirror-reference.md`
- Source Title: `TiUP Mirror Reference Guide`
- Source Heading Path: `TiUP Mirror Reference Guide > Mirror structure > Root directory`
- Source Line Ranges: `55-104`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `root-certificate`, `metadata`, `signature-verification`, `public-keys`, `thresholds`, `versioning`, `expiration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1043_f9499835d5`
- Source ID: `tidb-docs-8.1:tiup/tiup-mirror-reference.md#root-directory`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7942167dd984cbf28f9a7cc10cbb94be45928190d86ff5b04d08597a9de8f6c0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-mirror-reference#root-directory
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-mirror-reference.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiUP mirror `root.json` format, signature verification fields, roles, thresholds, versioning, and expiration behavior.
- Retrieval Keywords: root.json, root certificate, public key, signature verification, metadata file type, index, root, snapshot, timestamp, roles, threshold, spec_version 0.1.0, version, expires, rsassa-pss-sha256, rsa, /{role}.json, /{N}.index.json
- Follow-up Guidance: The source explains that the TiUP client finds the corresponding public key in the installed `root.json` based on the metadata file type and rejects the file if `expires` has passed.
- Classification Note: This is reference content because it specifies the exact JSON structure and semantics of the TiUP mirror root certificate, including `signatures`, `signed`, `roles`, `threshold`, and `version` fields.

## Official Source Content

### Root directory

In a TiUP mirror, the root certificate is used to store the public key of other metadata files. Each time any metadata file (`*.json`) is obtained, TiUP client needs to find the corresponding public key in the installed `root.json` based on the metadata file type (root, index, snapshot, timestamp). Then TiUP client uses the public key to verify whether the signature is valid.

The root certificate's format is as follows:

```
{
    "signatures": [                                             # Each metadata file has some signatures which are signed by several private keys corresponding to the file.
        {
            "keyid": "{id-of-root-key-1}",                      # The ID of the first private key that participates in the signature. This ID is obtained by hashing the content of the public key that corresponds to the private key.
            "sig": "{signature-by-root-key-1}"                  # The signed part of this file by this private key.
        },
        ...
        {
            "keyid": "{id-of-root-key-N}",                      # The ID of the Nth private key that participates in the signature.
            "sig": "{signature-by-root-key-N}"                  # The signed part of this file by this private key.
        }
    ],
    "signed": {                                                 # The signed part.
        "_type": "root",                                        # The type of this file. root.json's type is root.
        "expires": "{expiration-date-of-this-file}",            # The expiration time of the file. If the file expires, the client rejects the file.
        "roles": {                                              # Records the keys used to sign each metadata file.
            "{role:index,root,snapshot,timestamp}": {           # Each involved metadata file includes index, root, snapshot, and timestamp.
                "keys": {                                       # Only the key's signature recorded in `keys` is valid.
                    "{id-of-the-key-1}": {                      # The ID of the first key used to sign {role}.
                        "keytype": "rsa",                       # The key's type. Currently, the key type is fixed as rsa.
                        "keyval": {                             # The key's payload.
                            "public": "{public-key-content}"    # The public key's content.
                        },
                        "scheme": "rsassa-pss-sha256"           # Currently, the scheme is fixed as rsassa-pss-sha256.
                    },
                    "{id-of-the-key-N}": {                      # The ID of the Nth key used to sign {role}.
                        "keytype": "rsa",
                        "keyval": {
                            "public": "{public-key-content}"
                        },
                        "scheme": "rsassa-pss-sha256"
                    }
                },
                "threshold": {N},                               # Indicates that the metadata file needs at least N key signatures.
                "url": "/{role}.json"                           # The address from which the file can be obtained. For index files, prefix it with the version number (for example, /{N}.index.json).
            }
        },
        "spec_version": "0.1.0",                                # The specified version followed by this file. If the file structure is changed in the future, the version number needs to be upgraded. The current version number is 0.1.0.
        "version": {N}                                          # The version number of this file. You need to create a new {N+1}.root.json every time you update the file, and set its version to N + 1.
    }
}
```
