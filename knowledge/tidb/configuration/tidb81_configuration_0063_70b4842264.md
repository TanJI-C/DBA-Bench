# Enable Follower Read with SQL and Java

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-use-follower-read.md`
- Source Title: `Follower Read`
- Source Heading Path: `Follower Read > Enable Follower Read`
- Source Line Ranges: `42-145`
- Source Scope: `developer`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `tidb_replica_read`, `session-variable`, `global-variable`, `java`, `sql`, `replica-read`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0063_70b4842264`
- Source ID: `tidb-docs-8.1:develop/dev-guide-use-follower-read.md#enable-follower-read`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d2b2614f30e4f205bd66821ee50dc991ca5776bb72e5d89b040dee797e88b54e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-use-follower-read#enable-follower-read
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-use-follower-read.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about enabling Follower Read with the tidb_replica_read variable in SQL or setting session or global replica read mode in Java.
- Retrieval Keywords: Enable Follower Read, tidb_replica_read, SET [GLOBAL] tidb_replica_read = 'follower', SET @@tidb_replica_read = ?;, SET GLOBAL @@tidb_replica_read = ?;, leader, follower, leader-and-follower, prefer-leader, closest-replicas, closest-adaptive, FollowerReadHelper, FollowReadMode, setSessionReplicaRead, setGlobalReplicaRead, LEADER_AND_FOLLOWER
- Follow-up Guidance: The source says that using setSessionReplicaRead(conn, FollowReadMode.LEADER_AND_FOLLOWER) enables Follower Read for the current session and the mode is restored when the connection is disconnected.
- Classification Note: This is classified as configuration content because it shows the exact variable values and Java helper methods used to enable Follower Read.

## Official Source Content

## Enable Follower Read

<div label="SQL" value="sql">

To enable Follower Read, set the variable `tidb_replica_read` (default value is `leader`) to `follower`, `leader-and-follower`, `prefer-leader`, `closest-replicas`, or `closest-adaptive`:

```sql
SET [GLOBAL] tidb_replica_read = 'follower';
```

For more details about this variable, see [Follower Read Usage](https://docs.pingcap.com/tidb/stable/follower-read#usage).

</div>
<div label="Java" value="java">

In Java, to enable Follower Read, define a `FollowerReadHelper` class.

```java
public enum FollowReadMode {
    LEADER("leader"),
    FOLLOWER("follower"),
    LEADER_AND_FOLLOWER("leader-and-follower"),
    CLOSEST_REPLICA("closest-replica"),
    CLOSEST_ADAPTIVE("closest-adaptive"),
    PREFER_LEADER("prefer-leader");

    private final String mode;

    FollowReadMode(String mode) {
        this.mode = mode;
    }

    public String getMode() {
        return mode;
    }
}

public class FollowerReadHelper {

    public static void setSessionReplicaRead(Connection conn, FollowReadMode mode) throws SQLException {
        if (mode == null) mode = FollowReadMode.LEADER;
        PreparedStatement stmt = conn.prepareStatement(
            "SET @@tidb_replica_read = ?;"
        );
        stmt.setString(1, mode.getMode());
        stmt.execute();
    }

    public static void setGlobalReplicaRead(Connection conn, FollowReadMode mode) throws SQLException {
        if (mode == null) mode = FollowReadMode.LEADER;
        PreparedStatement stmt = conn.prepareStatement(
            "SET GLOBAL @@tidb_replica_read = ?;"
        );
        stmt.setString(1, mode.getMode());
        stmt.execute();
    }

}
```

When reading data from the Follower node, use the `setSessionReplicaRead(conn, FollowReadMode.LEADER_AND_FOLLOWER)` method to enable the Follower Read feature, which can balance the load between the Leader node and the Follower node in the current session. When the connection is disconnected, it will be restored to the original mode.

```java
public static class AuthorDAO {

    // Omit initialization of instance variables...

    public void getAuthorsByFollowerRead() throws SQLException {
        try (Connection conn = ds.getConnection()) {
            // Enable the follower read feature.
            FollowerReadHelper.setSessionReplicaRead(conn, FollowReadMode.LEADER_AND_FOLLOWER);

            // Read the authors list for 100000 times.
            Random random = new Random();
            for (int i = 0; i < 100000; i++) {
                Integer birthYear = 1920 + random.nextInt(100);
                List<Author> authors = this.getAuthorsByBirthYear(birthYear);
                System.out.println(authors.size());
            }
        }
    }

    public List<Author> getAuthorsByBirthYear(Integer birthYear) throws SQLException {
        List<Author> authors = new ArrayList<>();
        try (Connection conn = ds.getConnection()) {
            PreparedStatement stmt = conn.prepareStatement("SELECT id, name FROM authors WHERE birth_year = ?");
            stmt.setInt(1, birthYear);
            ResultSet rs = stmt.executeQuery();
            while (rs.next()) {
                Author author = new Author();
                author.setId( rs.getLong("id"));
                author.setName(rs.getString("name"));
                authors.add(author);
            }
        }
        return authors;
    }
}
```

</div>
