# Generate customized TiDB documentation PDFs locally

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/resources/tidb-pdf-generation-tutorial.md`
- Source Title: `TiDB Documentation PDF Generation Tutorial`
- Source Heading Path: `TiDB Documentation PDF Generation Tutorial | TiDB Documentation PDF Generation Tutorial > Environment preparation | TiDB Documentation PDF Generation Tutorial > Environment preparation > Preparation 1: Install and configure the Docker environment | TiDB Documentation PDF Generation Tutorial > Environment preparation > Preparation 2: Clone the TiDB documentation repository to your local disk | TiDB Documentation PDF Generation Tutorial > Steps`
- Source Line Ranges: `5-121`
- Source Scope: `developer`
- Primary Component: `shared`
- Related Components: `tidb`, `ecosystem`
- Topic Tags: `pdf-generation`, `documentation`, `docker`, `repository-clone`, `toc-editing`, `markdown-merge`, `local-build`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0210_84cf72afc9`
- Source ID: `tidb-docs-8.1:resources/tidb-pdf-generation-tutorial.md#tidb-documentation-pdf-generation-tutorial`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ea9de3028499dc714340b590e86b6c28c5ec1f98e1895a192566d0daae6e545d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/resources/tidb-pdf-generation-tutorial#tidb-documentation-pdf-generation-tutorial
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/resources/tidb-pdf-generation-tutorial.md

## Retrieval Guidance

- Use When: Use this chunk when someone needs the local workflow to generate a customized TiDB documentation PDF, including environment preparation, repository cloning, TOC editing, Markdown merging, and PDF build commands.
- Retrieval Keywords: TiDB Documentation PDF Generation Tutorial, generate TiDB documentation in PDF format, customize the PDF output, Docker Desktop, docker --version, Memory 8.00 GB, docker pull andelf/doc-build:0.1.9, pingcap/docs, pingcap/docs-cn, Fork, GitHub Desktop, git clone git@github.com:$user/docs.git, git remote add upstream git@github.com:pingcap/docs.git, TOC.md, scripts/merge_by_toc.py, doc.md, docker run -it -v ${doc-path}:/opt/data andelf/doc-build:0.1.9, WARNING: The requested image's platform (linux/amd64) does not match the detected host platform (linux/arm64/v8), bash scripts/generate_pdf.sh, output.pdf
- Follow-up Guidance: The source also states the expected outputs that `scripts/merge_by_toc.py` generates `doc.md` beside `TOC.md` and `bash scripts/generate_pdf.sh` generates `output.pdf` in the documentation folder.
- Classification Note: This is classified as an operation topic because the content is a step-by-step local procedure for preparing Docker, cloning the docs repository, editing `TOC.md`, merging Markdown files, and generating a PDF.

## Official Source Content

# TiDB Documentation PDF Generation Tutorial

This tutorial provides a method to generate TiDB documentation in PDF format. With this method, you can flexibly sort or delete certain contents in TiDB Documentation locally, and customize the PDF output to meet the needs of specific scenarios.

## Environment preparation

The following preparation steps only need to be performed once when you generate a PDF file for the first time and can be skipped directly for future PDF generation.

### Preparation 1: Install and configure the Docker environment

> Estimated time: 30 minutes.

The following steps take macOS or Windows as an example for Docker Desktop installation.

1. Install [Docker Desktop](https://docs.docker.com/get-docker/).

2. Run the `docker --version` command in macOS Terminal or Windows PowerShell.

    If you see the Docker version information, the installation is successful.

3. Configure Docker resources.

    1. Launch the Docker application and click the gear icon in the upper-right corner.

    2. Click **Resources** and set **Memory** to `8.00 GB`.

4. Run the following command in macOS Terminal or Windows PowerShell to pull the Docker image used for building TiDB PDF documentation:

    ```bash
    docker pull andelf/doc-build:0.1.9
    ```

### Preparation 2: Clone the TiDB documentation repository to your local disk

> Estimated time: 10 minutes.

TiDB English documentation repository: <https://github.com/pingcap/docs>; TiDB Chinese documentation repository: <https://github.com/pingcap/docs-cn>

The following steps take TiDB English documentation as an example to show how to clone the repository:

1. Go to the TiDB English documentation repository: <https://github.com/pingcap/docs>.

2. Click [**Fork**](https://github.com/pingcap/docs/fork) in the upper-right corner, and wait for the Fork to complete.

3. Use either of the following methods to clone the TiDB documentation repository locally.

    - Method 1: Use GitHub Desktop client.

        1. Install and launch [GitHub Desktop](https://desktop.github.com/).
        2. In GitHub Desktop, click **File** > **Clone Repository**.
        3. Click the **GitHub.com** tab, select the repository you forked in **Your Repositories**, and then click **Clone** in the lower-right corner.

    - Method 2: Use the following Git commands.

        ```shell
        cd $working_dir # Replace `$working_dir` with the directory where you want the repository to be placed. For example, `cd ~/Documents/GitHub`
        git clone git@github.com:$user/docs.git # Replace `$user` with your GitHub ID

        cd $working_dir/docs
        git remote add upstream git@github.com:pingcap/docs.git # Add upstream repository
        git remote -v
        ```

## Steps

> Estimated time: The following operations only take two minutes, but the PDF generation requires waiting for 0.5 to 1 hour.

1. Make sure that the files in your local TiDB documentation repository are of the latest version in the upstream GitHub repository.

2. Sort or delete the contents in TiDB Documentation according to your needs.

    1. Open the `TOC.md` file located in the root directory of your local repository.
    2. Edit the `TOC.md` file. For example, you can remove titles and links of all unnecessary document chapters.

3. Consolidate chapters from all documents into one Markdown file according to the `TOC.md` file.

    1. Start the Docker application.
    2. Run the following command in macOS Terminal or Windows PowerShell to run the Docker image for PDF documentation building:

        ```bash
        docker run -it -v ${doc-path}:/opt/data andelf/doc-build:0.1.9
        ```

        In the command, `${doc-path}` is the local path of the documentation for PDF generation. For example, if the path is `/Users/${username}/Documents/GitHub/docs`, the command is as follows:

        ```bash
        docker run -it -v /Users/${username}/Documents/GitHub/docs:/opt/data andelf/doc-build:0.1.9
        ```

        After execution, if `WARNING: The requested image's platform (linux/amd64) does not match the detected host platform (linux/arm64/v8) and no specific platform was requested` is returned, you can ignore it.

    3. Go to the `opt/data` directory.

        ```bash
        cd /opt/data
        ```

    4. Consolidate all Markdown document files into one `doc.md` file according to `TOC.md`.

        ```bash
        python3 scripts/merge_by_toc.py
        ```

        **Expected output:**

        In the same folder as `TOC.md`, you will see a newly generated `doc.md` file.

4. Generate the PDF documentation:

    ```bash
    bash scripts/generate_pdf.sh
    ```

    **Expected output:**

    The time required to generate the PDF file depends on the documentation size. For the complete TiDB documentation, it takes about 1 hour. After the generation is completed, you will see the newly generated PDF file `output.pdf` in the folder where the documentation is located.
