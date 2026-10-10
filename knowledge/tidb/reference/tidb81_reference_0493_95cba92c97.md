# RBAC authorization tables and references

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/role-based-access-control.md`
- Source Title: `Role-Based Access Control`
- Source Heading Path: `Role-Based Access Control > RBAC operations > Authorization table | Role-Based Access Control > RBAC operations > Authorization table > `mysql.role_edges` | Role-Based Access Control > RBAC operations > Authorization table > `mysql.default_roles` | Role-Based Access Control > RBAC operations > References`
- Source Line Ranges: `371-428`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `rbac`, `authorization`, `privilege-tables`, `roles`, `default-roles`, `role-edges`, `references`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0493_95cba92c97`
- Source ID: `tidb-docs-8.1:role-based-access-control.md#authorization-table`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `19e15ec0fe910d6d26138e4a49b8c0640e9df225dc3024e03e6131249028e9b6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/role-based-access-control#authorization-table
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/role-based-access-control.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the RBAC authorization tables that store role grants and default enabled roles, or when searching for the column meanings in `mysql.role_edges` and `mysql.default_roles`.
- Retrieval Keywords: Authorization table, mysql.role_edges, mysql.default_roles, RBAC operations, role and user authorization relationship, default roles of each user, FROM_HOST, FROM_USER, TO_HOST, TO_USER, WITH_ADMIN_OPTION, HOST, USER, DEFAULT_ROLE_HOST, DEFAULT_ROLE_USER, SELECT * FROM mysql.role_edges;, SELECT * FROM mysql.default_roles;, References, TiDB Privilege Management, TiDB User Account Management
- Follow-up Guidance: The source also points to TiDB Privilege Management and TiDB User Account Management for related operation details because RBAC, user management, and privilege management are closely related.
- Classification Note: This is reference content because it defines the two RBAC system privilege tables, shows example query results, and explains the meaning of their fields.

## Official Source Content

### Authorization table

In addition to four system [privilege tables](https://docs.pingcap.com/tidb/stable/privilege-management#privilege-table), the RBAC system introduces two new system privilege tables:

- `mysql.role_edges`: records the authorization relationship of the role and user.
- `mysql.default_roles`: records default roles of each user.
#### `mysql.role_edges`

`mysql.role_edges` contains the following data:

```sql
SELECT * FROM mysql.role_edges;
```

```
+-----------+-----------+---------+---------+-------------------+
| FROM_HOST | FROM_USER | TO_HOST | TO_USER | WITH_ADMIN_OPTION |
+-----------+-----------+---------+---------+-------------------+
| %         | r_1       | %       | u_1     | N                 |
+-----------+-----------+---------+---------+-------------------+
1 row in set (0.00 sec)
```

- `FROM_HOST` and `FROM_USER` indicate the role's host name and user name respectively.
- `TO_HOST` and `TO_USER` indicate the host name and user name of the user to which a role is granted.
#### `mysql.default_roles`

`mysql.default_roles` shows which roles have been enabled by default for each user.

```sql
SELECT * FROM mysql.default_roles;
```

```
+------+------+-------------------+-------------------+
| HOST | USER | DEFAULT_ROLE_HOST | DEFAULT_ROLE_USER |
+------+------+-------------------+-------------------+
| %    | u_1  | %                 | r_1               |
| %    | u_1  | %                 | r_2               |
+------+------+-------------------+-------------------+
2 rows in set (0.00 sec)
```

- `HOST` and `USER` indicate the user's host name and user name respectively.
- `DEFAULT_ROLE_HOST` and `DEFAULT_ROLE_USER` indicate the host name and user name of the default role respectively.
### References

Because RBAC, user management, and privilege management are closely related, you can refer to operation details in the following resources:

- [TiDB Privilege Management](https://docs.pingcap.com/tidb/stable/privilege-management)
- [TiDB User Account Management](https://docs.pingcap.com/tidb/stable/user-account-management)
