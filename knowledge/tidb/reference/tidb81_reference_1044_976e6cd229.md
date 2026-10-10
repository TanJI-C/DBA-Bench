# TiUP mirror index file format

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-mirror-reference.md`
- Source Title: `TiUP Mirror Reference Guide`
- Source Heading Path: `TiUP Mirror Reference Guide > Mirror structure > Index`
- Source Line Ranges: `105-169`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `index-file`, `components`, `owners`, `signatures`, `metadata`, `thresholds`, `versioning`, `expiration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1044_976e6cd229`
- Source ID: `tidb-docs-8.1:tiup/tiup-mirror-reference.md#index`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `782201428e62c460cbe8ef42cd785c9fe0fde073c3c991bb66252755bd40b4ef`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-mirror-reference#index
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-mirror-reference.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiUP mirror index file schema that records components, owners, signatures, thresholds, and versioned metadata fields.
- Retrieval Keywords: index file, _type index, components, owners, default_components, hidden, owner, standalone, url, yanked, expires, threshold, spec_version 0.1.0, version, /{component}.json, /{N}.{component}.json, rsassa-pss-sha256, rsa
- Follow-up Guidance: The source states that the index file records all the components in the mirror and the owner information of the components, and that expired files are rejected by the client.
- Classification Note: This is reference content because it defines the exact JSON format of the TiUP mirror index file, including component entries, owner keys, signature requirements, and version fields.

## Official Source Content

### Index

The index file records all the components in the mirror and the owner information of the components.

The index file's format is as follows:

```
{
    "signatures": [                                             # The file's signature.
        {
            "keyid": "{id-of-index-key-1}",                     # The ID of the first private key that participates in the signature.
            "sig": "{signature-by-index-key-1}",                # The signed part of this file by this private key.
        },
        ...
        {
            "keyid": "{id-of-root-key-N}",                      # The ID of the Nth private key that participates in the signature.
            "sig": "{signature-by-root-key-N}"                  # The signed part of this file by this private key.
        }
    ],
    "signed": {
        "_type": "index",                                       # The file type.
        "components": {                                         # The component list.
            "{component1}": {                                   # The name of the first component.
                "hidden": {bool},                               # Whether it is a hidden component.
                "owner": "{owner-id}",                          # The component owner's ID.
                "standalone": {bool},                           # Whether it is a standalone component.
                "url": "/{component}.json",                     # The address from which the component can be obtained. You need to prefix it with the version number (for example, /{N}.{component}.json).
                "yanked": {bool}                                # Indicates whether the component is marked as deleted.
            },
            ...
            "{componentN}": {                                   # The name of the Nth component.
                ...
            },
        },
        "default_components": ["{component1}".."{componentN}"], # The default component that a mirror must contain. Currently, this field defaults to empty (disabled).
        "expires": "{expiration-date-of-this-file}",            # The expiration time of the file. If the file expires, the client rejects the file.
        "owners": {
            "{owner1}": {                                       # The ID of the first owner.
                "keys": {                                       # Only the key's signature recorded in `keys` is valid.
                    "{id-of-the-key-1}": {                      # The first key of the owner.
                        "keytype": "rsa",                       # The key's type. Currently, the key type is fixed as rsa.
                        "keyval": {                             # The key's payload.
                            "public": "{public-key-content}"    # The public key's content.
                        },
                        "scheme": "rsassa-pss-sha256"           # Currently, the scheme is fixed as rsassa-pss-sha256.
                    },
                    ...
                    "{id-of-the-key-N}": {                      # The Nth key of the owner.
                        ...
                    }
                },
                "name": "{owner-name}",                         # The name of the owner.
                "threshold": {N}                                 # Indicates that the components owned by the owner must have at least N valid signatures.
            },
            ...
            "{ownerN}": {                                       # The ID of the Nth owner.
                ...
            }
        }
        "spec_version": "0.1.0",                                # The specified version followed by this file. If the file structure is changed in the future, the version number needs to be upgraded. The current version number is 0.1.0.
        "version": {N}                                          # The version number of this file. You need to create a new {N+1}.index.json every time you update the file, and set its version to N + 1.
    }
}
```
