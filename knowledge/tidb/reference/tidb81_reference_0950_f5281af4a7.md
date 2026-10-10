# TiFlash dttool bench and inspect flags

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tiflash-command-line-flags.md`
- Source Title: `TiFlash Command-line Flags`
- Source Heading Path: `TiFlash Command-Line Flags > `dttool bench` | TiFlash Command-Line Flags > `dttool inspect``
- Source Line Ranges: `50-81`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: none
- Topic Tags: `command-line`, `dtfile`, `benchmark`, `io-test`, `integrity-check`, `validation`, `inspection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0950_f5281af4a7`
- Source ID: `tidb-docs-8.1:tiflash/tiflash-command-line-flags.md#dttool-bench`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `750737ab646a37bda1d0d91bbf5a1ee303a422eb0daf884352e464944f75acf1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tiflash-command-line-flags#dttool-bench
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tiflash-command-line-flags.md

## Retrieval Guidance

- Use When: Use this chunk when looking for `dttool bench` parameters for DTFile I/O testing or `dttool inspect` parameters for single-DTFile integrity checking after migration or environment changes.
- Retrieval Keywords: dttool bench, dttool inspect, I/O speed test, integrity of the DTFile, --version, --algorithm, --frame, --column, --size, --field, --random, --encryption, --repeat, --workdir, --config-file, --check, --file-id, --imitative, hash validation, format upgrade or downgrade, migrate the DTFile to a new environment
- Follow-up Guidance: The source notes that `dttool inspect` validates one DTFile at a time, so validating a whole table requires locating paths like `<data dir>/t_<table id>/stable/dmf_<file id>` and checking them one by one.
- Classification Note: This is reference content because it lists the official command-line parameters and stated usage scenarios for `dttool bench` and `dttool inspect`.

## Official Source Content

## `dttool bench`

- Provides a basic I/O speed test for the DTFile.
- Parameters:

    - `--version`: The version of DTFile. See [`--version` in `dttool migrate`](#dttool-migrate).
    - `--algorithm`: The hash algorithm used for data validation. See [`--algorithm` in `dttool migrate`](#dttool-migrate).
    - `--frame`: The size of the validation frame. See [`--frame` in `dttool migrate`](#dttool-migrate).
    - `--column`: The columns of the table to be tested. The default value is `100`.
    - `--size`: The rows of the table to be tested. The default value is `1000`.
    - `--field`: The field length limit of the table to be tested. The default value is `1024`.
    - `--random`: The random seed. If you do not specify this parameter, the random seed is drawn from the system entropy pool.
    - `--encryption`: Enables the encryption feature.
    - `--repeat`: The number of times to repeat the test. The default value is `5`.
    - `--workdir`: The temporary data directory, which points to a path in the file system to be tested. The default value is `/tmp/test`.
## `dttool inspect`

- Checks the integrity of the DTFile. Data validation is performed in the unit of a single DTFile. If you want to validate the whole table, you need to locate all the paths similar to `<data dir>/t_<table id>/stable/dmf_<file id>` and validate them one by one. You can use scripts to automate the validation.

- User scenarios:

    - After you perform a format upgrade or downgrade, you can validate the data integrity of the DTFile.
    - After you migrate the DTFile to a new environment, you can validate the data integrity of the DTFile.

- Parameters:

    - `--config-file`: The configuration file of `dttool bench`. See [`--config-file` in `dttool migrate`](#dttool-migrate).
    - `--check`: Performs hash validation.
    - `--file-id`: The ID of the DTFile. See [`--file-id` in `dttool migrate`](#dttool-migrate).
    - `--imitative`: Imitates the database context. See [`--imitative` in `dttool migrate`](#dttool-migrate).
    - `--workdir`: The data directory. See [`--workdir` in `dttool migrate`](#dttool-migrate).
