# TiUP mirror metadata formats and client verification workflow

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-mirror-reference.md`
- Source Title: `TiUP Mirror Reference Guide`
- Source Heading Path: `TiUP Mirror Reference Guide > Mirror structure > Component | TiUP Mirror Reference Guide > Mirror structure > Snapshot | TiUP Mirror Reference Guide > Mirror structure > Timestamp | TiUP Mirror Reference Guide > Client workflow`
- Source Line Ranges: `170-311`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `mirror`, `metadata`, `component`, `snapshot`, `timestamp`, `signatures`, `checksums`, `versions`, `client-workflow`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1045_9ad40e422f`
- Source ID: `tidb-docs-8.1:tiup/tiup-mirror-reference.md#component`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d2737d1ccb97b3e4c78de7bc071f6050057934edcdff62715662a7ef7e30148a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-mirror-reference#component
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-mirror-reference.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the TiUP mirror metadata file formats for component, snapshot, and timestamp files or the client verification workflow for root, index, component metadata, and tar packages.
- Retrieval Keywords: component metadata file format, snapshot file structure, timestamp file format, Client workflow, root.json, {N+1}.root.json, timestamp.json, snapshot.json, index.json, {N}.index.json, {N}.{component}.json, signatures, signed, _type component, _type snapshot, _type timestamp, expires, spec_version 0.1.0, nightly, platforms, entry, hashs, sha256, sha512, yanked, meta, /root.json, /index.json, /{component}.json, /snapshot.json, public key recorded in root.json, public key recorded in index.json, checksum verification, tar packages
- Follow-up Guidance: The client workflow describes verifying {N+1}.root.json, timestamp.json, snapshot.json, {N}.index.json, {N}.{component}.json, and then verifying component tar package checksums from the URLs and checksums in {component}.json.
- Classification Note: This is reference content because it defines the exact JSON metadata structures and the ordered TiUP client verification logic described by the official mirror specification.

## Official Source Content

### Component

The component's metadata file records information of the component-specific platform and the version.

The component metadata file's format is as follows:

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
        "_type": "component",                                   # The file type.
        "description": "{description-of-the-component}",        # The description of the component.
        "expires": "{expiration-date-of-this-file}",            # The expiration time of the file. If the file expires, the client rejects the file.
        "id": "{component-id}",                                 # The globally unique ID of the component.
        "nightly": "{nightly-cursor}",                          # The nightly cursor, and the value is the latest nightly version number (for example, v5.0.0-nightly-20201209).
        "platforms": {                                          # The component's supported platforms (such as darwin/amd64, linux/arm64).
            "{platform-pair-1}": {
                "{version-1}": {                                # The semantic version number (for example, v1.0.0).
                    "dependencies": null,                       # Specifies the dependency relationship between components. The field is not used yet and is fixed as null.
                    "entry": "{entry}",                         # The relative path of the entry binary file in the tar package.
                    "hashs": {                                  # The checksum of the tar package. sha256 and sha512 are used.
                        "sha256": "{sum-of-sha256}",
                        "sha512": "{sum-of-sha512}",
                    },
                    "length": {length-of-tar},                  # The length of the tar package.
                    "released": "{release-time}",               # The release date of the version.
                    "url": "{url-of-tar}",                      # The download address of the tar package.
                    "yanked": {bool}                            # Indicates whether this version is disabled.
                }
            },
            ...
            "{platform-pair-N}": {
                ...
            }
        },
        "spec_version": "0.1.0",                                # The specified version followed by this file. If the file structure is changed in the future, the version number needs to be upgraded. The current version number is 0.1.0.
        "version": {N}                                          # The version number of this file. You need to create a new {N+1}.{component}.json every time you update the file, and set its version to N + 1.
}
```
### Snapshot

The snapshot file records the version number of each metadata file:

The snapshot file's structure is as follows:

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
        "_type": "snapshot",                                    # The file type.
        "expires": "{expiration-date-of-this-file}",            # The expiration time of the file. If the file expires, the client rejects the file.
        "meta": {                                               # Other metadata files' information.
            "/root.json": {
                "length": {length-of-json-file},                # The length of root.json
                "version": {version-of-json-file}               # The version of root.json
            },
            "/index.json": {
                "length": {length-of-json-file},
                "version": {version-of-json-file}
            },
            "/{component-1}.json": {
                "length": {length-of-json-file},
                "version": {version-of-json-file}
            },
            ...
            "/{component-N}.json": {
                ...
            }
        },
        "spec_version": "0.1.0",                                # The specified version followed by this file. If the file structure is changed in the future, the version number needs to be upgraded. The current version number is 0.1.0.
        "version": 0                                            # The version number of this file, which is fixed as 0.
    }
```
### Timestamp

The timestamp file records the checksum of the current snapshot.

The timestamp file's format is as follows:

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
        "_type": "timestamp",                                   # The file type.
        "expires": "{expiration-date-of-this-file}",            # The expiration time of the file. If the file expires, the client rejects the file.
        "meta": {                                               # The information of snapshot.json.
            "/snapshot.json": {
                "hashes": {
                    "sha256": "{sum-of-sha256}"                 # snapshot.json's sha256.
                },
                "length": {length-of-json-file}                 # The length of snapshot.json.
            }
        },
        "spec_version": "0.1.0",                                # The specified version followed by this file. If the file structure is changed in the future, the version number needs to be upgraded. The current version number is 0.1.0.
        "version": {N}                                          # The version number of this file. You need to overwrite timestamp.json every time you update the file, and set its version to N + 1.
```
## Client workflow

The client uses the following logic to ensure that the files downloaded from the mirror are safe:

+ A `root.json` file is included with the binary when the client is installed.
+ The running client performs the following tasks based on the existing `root.json`:
    1. Obtain the version from `root.json` and mark it as `N`.
    2. Request `{N+1}.root.json` from the mirror. If the request is successful, use the public key recorded in `root.json` to verify whether the file is valid.
    3. Request `timestamp.json` from the mirror and use the public key recorded in `root.json` to verify whether the file is valid.
    4. Check whether the checksum of `snapshot.json` recorded in `timestamp.json` matches the checksum of the local `snapshot.json`. If the two do not match, request the latest `snapshot.json` from the mirror and use the public key recorded in `root.json` to verify whether the file is valid.
    5. Obtain the version number `N` of the `index.json` file from `snapshot.json` and request `{N}.index.json` from the mirror. Then use the public key recorded in `root.json` to verify whether the file is valid.
    6. For components such as `tidb.json` and `tikv.json`, the client obtains the version numbers `N` of the components from `snapshot.json` and requests `{N}.{component}.json` from the mirror. Then the client uses the public key recorded in `index.json` to verify whether the file is valid.
    7. For component's tar files, the client obtains the URLs and checksums of the files from `{component}.json` and request the URLs for the tar packages. Then the client verifies whether the checksum is correct.
