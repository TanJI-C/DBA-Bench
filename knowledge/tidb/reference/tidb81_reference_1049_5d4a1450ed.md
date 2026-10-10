# TiUP components and mirrors concepts

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-terminology-and-concepts.md`
- Source Title: `TiUP Terminology and Concepts`
- Source Heading Path: `TiUP Terminology and Concepts | TiUP Terminology and Concepts > TiUP components | TiUP Terminology and Concepts > TiUP mirrors`
- Source Line Ranges: `5-34`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `components`, `version-selection`, `local-installation`, `mirror-source`, `environment-variables`, `downloads`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1049_5d4a1450ed`
- Source ID: `tidb-docs-8.1:tiup/tiup-terminology-and-concepts.md#tiup-terminology-and-concepts`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `914051c7d1482048f8bb04515d6cd828ee45681839ace2594468b5b2bbf8130d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-terminology-and-concepts#tiup-terminology-and-concepts
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-terminology-and-concepts.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks how `tiup <component>` selects a local or downloaded version, what a TiUP component is, or how `TIUP_MIRRORS` changes the mirror source for downloads.
- Retrieval Keywords: TiUP components, TiUP mirrors, tiup <component>, tiup <component>[:version], latest stable version, latest installed version, installed locally, mirror server, TIUP_MIRRORS, local file directory, online HTTP server, tiup list, environment variables, data directory, PingCAP's official mirrors
- Follow-up Guidance: The content also shows `TIUP_MIRRORS=/path/to/local tiup list` and `TIUP_MIRRORS=https://private-mirrors.example.com tiup list` as mirror source examples.
- Classification Note: This is reference content because it defines TiUP terminology and describes the built-in version selection logic and mirror source concepts for the `tiup` component.

## Official Source Content

# TiUP Terminology and Concepts

This document explains important terms and concepts of TiUP.
## TiUP components

The TiUP program contains only a few commands for downloading, updating, and uninstalling components. TiUP expands its functions with various components. A **component** is a program or script that can be run. When running a component through `tiup <component>`, TiUP adds a set of environment variables, creates the data directory for the program, and then runs the program.

By running the `tiup <component>` command, you can run a component supported by TiUP. The running logic is:

+ If you specify a version of a component through `tiup <component>[:version]`:

    - If the component does not have any version installed locally, TiUP downloads the latest stable version from the mirror server.
    - If the component has one or more versions installed locally, but there is no version specified by you, TiUP downloads the specified version from the mirror server.
    - If the specified version of the component is installed locally, TiUP sets the environment variable to run the installed version.

+ If you run a component through `tiup <component>` and specify no version:

    - If the component does not have any version installed locally, TiUP downloads the latest stable version from the mirror server.
    - If one or more versions have been installed locally, TiUP sets the environment variable to run the latest installed version.
## TiUP mirrors

All components of TiUP are downloaded from the TiUP mirrors. TiUP mirrors contain the TAR package of each component and the corresponding meta information (version, entry startup file, checksum). TiUP uses PingCAP's official mirrors by default. You can customize the mirror source through the `TIUP_MIRRORS` environment variable.

TiUP mirrors can be a local file directory or an online HTTP server:

+ `TIUP_MIRRORS=/path/to/local tiup list`
+ `TIUP_MIRRORS=https://private-mirrors.example.com tiup list`
