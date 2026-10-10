# Configure connection, run migrations, and verify the sample app

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-nodejs-typeorm.md`
- Source Title: `Connect to TiDB with TypeORM`
- Source Heading Path: `Connect to TiDB with TypeORM > Run the sample app to connect to TiDB > Step 3: Configure connection information | Connect to TiDB with TypeORM > Run the sample app to connect to TiDB > Step 4: Initialize the database schema | Connect to TiDB with TypeORM > Run the sample app to connect to TiDB > Step 5: Run the code and check the result`
- Source Line Ranges: `83-242`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`, `sql`
- Topic Tags: `connection-configuration`, `environment-variables`, `tls`, `ca-certificate`, `public-endpoint`, `migration`, `schema-initialization`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0072_3be4923d11`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-nodejs-typeorm.md#step-3-configure-connection-information`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a42104d54150568e80cb52241d0e9787c5e2711798a36ed72831b339d3a5c80d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-nodejs-typeorm#step-3-configure-connection-information
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-nodejs-typeorm.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the exact `.env` connection settings, TLS-related variables, migration command, or expected output for verifying a TypeORM sample app connection to TiDB.
- Retrieval Keywords: cp .env.example .env, TIDB_HOST, TIDB_PORT=4000, TIDB_USER, TIDB_PASSWORD, TIDB_DATABASE=test, TIDB_ENABLE_SSL=true, TIDB_CA_PATH, Public, Branch main, Connect With General, CA cert, npm run migration:run, src/migrations, players table, profiles table, INFORMATION_SCHEMA.COLUMNS, Migration Init1693814724825 has been executed successfully, npm start, Connected to TiDB cluster
- Follow-up Guidance: The source shows expected migration SQL output and expected runtime output including `🔌 Connected to TiDB cluster!` for result verification.
- Classification Note: This is classified as an operation chunk because it contains procedural connection configuration, schema initialization, and runtime verification steps.

## Official Source Content

### Step 3: Configure connection information

Connect to your TiDB cluster depending on the TiDB deployment option you've selected.

<div label="{{{ .starter }}} or Essential">

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A connection dialog is displayed.

3. Ensure the configurations in the connection dialog match your operating environment.

    - **Connection Type** is set to `Public`.
    - **Branch** is set to `main`.
    - **Connect With** is set to `General`.
    - **Operating System** matches the operating system where you run the application.

4. If you have not set a password yet, click **Generate Password** to generate a random password.

5. Run the following command to copy `.env.example` and rename it to `.env`:

    ```shell
    cp .env.example .env
    ```

6. Edit the `.env` file, set up the environment variables as follows, replace the corresponding placeholders `{}` with connection parameters on the connection dialog:

    ```dotenv
    TIDB_HOST={host}
    TIDB_PORT=4000
    TIDB_USER={user}
    TIDB_PASSWORD={password}
    TIDB_DATABASE=test
    TIDB_ENABLE_SSL=true
    ```

    > **Note**
    >
    > For {{{ .starter }}} and {{{ .essential }}}, you **MUST** enable TLS connection via `TIDB_ENABLE_SSL` when using public endpoint.

7. Save the `.env` file.

</div>
<div label="TiDB Cloud Dedicated">

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A connection dialog is displayed.

3. In the connection dialog, select **Public** from the **Connection Type** drop-down list, and then click **CA cert** to download the CA certificate.

    If you have not configured the IP access list, click **Configure IP Access List** or follow the steps in [Configure an IP Access List](https://docs.pingcap.com/tidbcloud/configure-ip-access-list) to configure it before your first connection.

    In addition to the **Public** connection type, TiDB Cloud Dedicated supports **Private Endpoint** and **VPC Peering** connection types. For more information, see [Connect to Your TiDB Cloud Dedicated Cluster](https://docs.pingcap.com/tidbcloud/connect-to-tidb-cluster).

4. Run the following command to copy `.env.example` and rename it to `.env`:

    ```shell
    cp .env.example .env
    ```

5. Edit the `.env` file, set up the environment variables as follows, replace the corresponding placeholders `{}` with connection parameters on the connection dialog:

    ```dotenv
    TIDB_HOST={host}
    TIDB_PORT=4000
    TIDB_USER={user}
    TIDB_PASSWORD={password}
    TIDB_DATABASE=test
    TIDB_ENABLE_SSL=true
    TIDB_CA_PATH={downloaded_ssl_ca_path}
    ```

    > **Note**
    >
    > For TiDB Cloud Dedicated, it is **RECOMMENDED** to enable TLS connection via `TIDB_ENABLE_SSL` when using public endpoint. When you set up `TIDB_ENABLE_SSL=true`, you **MUST** specify the path of the CA certificate downloaded from connection dialog via `TIDB_CA_PATH=/path/to/ca.pem`.

6. Save the `.env` file.

</div>
<div label="TiDB Self-Managed">

1. Run the following command to copy `.env.example` and rename it to `.env`:

    ```shell
    cp .env.example .env
    ```

2. Edit the `.env` file, set up the environment variables as follows, replace the corresponding placeholders `{}` with connection parameters of your TiDB cluster:

    ```dotenv
    TIDB_HOST={host}
    TIDB_PORT=4000
    TIDB_USER=root
    TIDB_PASSWORD={password}
    TIDB_DATABASE=test
    ```

    If you are running TiDB locally, the default host address is `127.0.0.1`, and the password is empty.

3. Save the `.env` file.

</div>
### Step 4: Initialize the database schema

Run the following command to invoke TypeORM CLI to initialize the database with the SQL statements written in the migration files in the `src/migrations` folder:

```shell
npm run migration:run
```

<details>
<summary><b>Expected execution output</b></summary>

The following SQL statements create a `players` table and a `profiles` table, and the two tables are associated through foreign keys.

```sql
query: SELECT VERSION() AS `version`
query: SELECT * FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA` = 'test' AND `TABLE_NAME` = 'migrations'
query: CREATE TABLE `migrations` (`id` int NOT NULL AUTO_INCREMENT, `timestamp` bigint NOT NULL, `name` varchar(255) NOT NULL, PRIMARY KEY (`id`)) ENGINE=InnoDB
query: SELECT * FROM `test`.`migrations` `migrations` ORDER BY `id` DESC
0 migrations are already loaded in the database.
1 migrations were found in the source code.
1 migrations are new migrations must be executed.
query: START TRANSACTION
query: CREATE TABLE `profiles` (`player_id` int NOT NULL, `biography` text NOT NULL, PRIMARY KEY (`player_id`)) ENGINE=InnoDB
query: CREATE TABLE `players` (`id` int NOT NULL AUTO_INCREMENT, `name` varchar(50) NOT NULL, `coins` decimal NOT NULL, `goods` int NOT NULL, `created_at` datetime NOT NULL, `profilePlayerId` int NULL, UNIQUE INDEX `uk_players_on_name` (`name`), UNIQUE INDEX `REL_b9666644b90ccc5065993425ef` (`profilePlayerId`), PRIMARY KEY (`id`)) ENGINE=InnoDB
query: ALTER TABLE `players` ADD CONSTRAINT `fk_profiles_on_player_id` FOREIGN KEY (`profilePlayerId`) REFERENCES `profiles`(`player_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
query: INSERT INTO `test`.`migrations`(`timestamp`, `name`) VALUES (?, ?) -- PARAMETERS: [1693814724825,"Init1693814724825"]
Migration Init1693814724825 has been  executed successfully.
query: COMMIT
```

</details>

Migration files are generated from the entities defined in the `src/entities` folder. To learn how to define entities in TypeORM, refer to [TypeORM: Entities](https://typeorm.io/entities).
### Step 5: Run the code and check the result

Run the following command to execute the sample code:

```shell
npm start
```

**Expected execution output:**

If the connection is successful, the terminal will output the version of the TiDB cluster as follows:

```
🔌 Connected to TiDB cluster! (TiDB version: 8.0.11-TiDB-v8.1.2)
🆕 Created a new player with ID 2.
ℹ️ Got Player 2: Player { id: 2, coins: 100, goods: 100 }
🔢 Added 50 coins and 50 goods to player 2, now player 2 has 100 coins and 150 goods.
🚮 Deleted 1 player data.
```
