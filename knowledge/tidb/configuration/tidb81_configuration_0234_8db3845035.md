# dbt setup, demo project creation, and TiDB Cloud profile configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/integrate-tidbcloud-with-dbt.md`
- Source Title: `Integrate TiDB Cloud with dbt`
- Source Heading Path: `Integrate TiDB Cloud with dbt | Integrate TiDB Cloud with dbt > Step 1: Install dbt and dbt-tidb | Integrate TiDB Cloud with dbt > Step 2: Create a demo project | Integrate TiDB Cloud with dbt > Step 3: Configure the project`
- Source Line Ranges: `5-141`
- Source Scope: `cloud`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `shared`
- Topic Tags: `dbt`, `installation`, `demo-project`, `profiles`, `project-configuration`, `connectivity`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0234_8db3845035`
- Source ID: `tidb-docs-8.1:tidb-cloud/integrate-tidbcloud-with-dbt.md#integrate-tidb-cloud-with-dbt`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `424ff4df99ab75563a4dfecab39737645700378c314fbfea9134b6bc580618fc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/integrate-tidbcloud-with-dbt#integrate-tidb-cloud-with-dbt
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/integrate-tidbcloud-with-dbt.md

## Retrieval Guidance

- Use When: Use this chunk when setting up dbt with TiDB Cloud, creating the jaffle_shop demo project, configuring ~/.dbt/profiles.yml and dbt_project.yml, or verifying the connection with dbt debug.
- Retrieval Keywords: dbt-tidb, pip install dbt-tidb, jaffle_shop, git clone https://github.com/dbt-labs/jaffle_shop, ~/.dbt/profiles.yml, dbt_project.yml, profile: 'jaffle_shop_tidb', type: tidb, server, port, schema: analytics, username, password, Connect, Clusters, dbt debug
- Follow-up Guidance: The chunk explains that server, port, and username can be obtained from the TiDB Cloud cluster connection dialog opened from the Clusters page by clicking the target cluster name and then Connect.
- Classification Note: This is classified as configuration because the content focuses on installing dbt-tidb, defining the global profile and project profile, and verifying the project connection settings.

## Official Source Content

# Integrate TiDB Cloud with dbt

[Data build tool (dbt)](https://www.getdbt.com/) is a popular open-source data transformation tool that helps analytics engineers transform data in their warehouses through SQL statements. Through the [dbt-tidb](https://github.com/pingcap/dbt-tidb) plugin, analytics engineers working with TiDB Cloud can directly create forms and match data through SQL without having to think about the process of creating tables or views.

This document introduces how to use dbt with TiDB Cloud, taking a dbt project as an example.
## Step 1: Install dbt and dbt-tidb

You can install dbt and dbt-tidb using only one command. In the following command, dbt is installed as a dependency when you install dbt-tidb.

```shell
pip install dbt-tidb
```

You can also install dbt separately. See [How to install dbt](https://docs.getdbt.com/docs/get-started/installation) in the dbt documentation.
## Step 2: Create a demo project

To try out the dbt function, you can use [jaffle_shop](https://github.com/dbt-labs/jaffle_shop), a demo project provided by dbt-lab. You can clone the project directly from GitHub:

```shell
git clone https://github.com/dbt-labs/jaffle_shop && \
cd jaffle_shop
```

All files in the `jaffle_shop` directory are structured as follows:

```shell
.
├── LICENSE
├── README.md
├── dbt_project.yml
├── etc
│    ├── dbdiagram_definition.txt
│    └── jaffle_shop_erd.png
├── models
│    ├── customers.sql
│    ├── docs.md
│    ├── orders.sql
│    ├── overview.md
│    ├── schema.yml
│    └── staging
│        ├── schema.yml
│        ├── stg_customers.sql
│        ├── stg_orders.sql
│        └── stg_payments.sql
└── seeds
    ├── raw_customers.csv
    ├── raw_orders.csv
    └── raw_payments.csv
```

In this directory:

- `dbt_project.yml` is the dbt project configuration file, which holds the project name and database configuration file information.

- The `models` directory contains the project’s SQL models and table schemas. Note that the data analyst writes this section. For more information about models, see [SQL models](https://docs.getdbt.com/docs/build/sql-models).

- The `seeds` directory stores the CSV files that are dumped by the database export tools. For example, you can [export the TiDB Cloud data](https://docs.pingcap.com/tidbcloud/export-data-from-tidb-cloud) into CSV files through Dumpling. In the `jaffle_shop` project, these CSV files are used as raw data to be processed.
## Step 3: Configure the project

To configure the project, take the following steps:

1. Complete the global configuration.

    You can refer to [Description of profile fields](#description-of-profile-fields) and edit the default global profile, `~/.dbt/profiles.yml`, to configure the connection with TiDB Cloud:

    ```shell
    sudo vi ~/.dbt/profiles.yml
    ```

    In the editor, add the following configuration:

   ```yaml
    jaffle_shop_tidb:                                                 # Project name
      target: dev                                                     # Target
      outputs:
        dev:
          type: tidb                                                  # The specific adapter to use
          server: gateway01.ap-southeast-1.prod.aws.tidbcloud.com     # The TiDB Cloud clusters' endpoint to connect to
          port: 4000                                                  # The port to use
          schema: analytics                                           # Specify the schema (database) to normalize data into
          username: xxxxxxxxxxx.root                                  # The username to use to connect to the TiDB Cloud clusters
          password: "your_password"                                   # The password to use for authenticating to the TiDB Cloud clusters
    ```

    You can get the values of `server`, `port`, and `username` from the connection dialog of your cluster. To open this dialog, go to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, click the name of your target cluster to go to its overview page, and then click **Connect** in the upper-right corner.

2. Complete the project configuration.

    In the jaffle_shop project directory, edit the project configuration file `dbt_project.yml` and change the `profile` field to `jaffle_shop_tidb`. This configuration allows the project to query from the database as specified in the `~/.dbt/profiles.yml` file.

    ```shell
    vi dbt_project.yml
    ```

    In the editor, update the configuration as follows:

    ```yaml
    name: 'jaffle_shop'

    config-version: 2
    version: '0.1'

    profile: 'jaffle_shop_tidb'                   # note the modification here

    model-paths: ["models"]                       # model path
    seed-paths: ["seeds"]                         # seed path
    test-paths: ["tests"]
    analysis-paths: ["analysis"]
    macro-paths: ["macros"]

    target-path: "target"
    clean-targets:
        - "target"
        - "dbt_modules"
        - "logs"

    require-dbt-version: [">=1.0.0", "<2.0.0"]

    models:
      jaffle_shop:
          materialized: table            # *.sql which in models/ would be materialized to table
          staging:
            materialized: view           # *.sql which in models/staging/ would bt materialized to view
    ```

3. Verify the configuration.

    Run the following command to check whether the database and project configuration is correct.

    ```shell
    dbt debug
    ```
