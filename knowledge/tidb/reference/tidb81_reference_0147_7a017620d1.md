# MyBatis update and delete snippets with follow-up resources

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-java-mybatis.md`
- Source Title: `Connect to TiDB with MyBatis`
- Source Heading Path: `Connect to TiDB with MyBatis > Sample code snippets > Update data | Connect to TiDB with MyBatis > Sample code snippets > Delete data | Connect to TiDB with MyBatis > Next steps | Connect to TiDB with MyBatis > Need help?`
- Source Line Ranges: `275-330`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `sql`, `shared`
- Topic Tags: `mybatis`, `java`, `update`, `delete`, `mapper-xml`, `sample-code`, `developer-guide`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0147_7a017620d1`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-java-mybatis.md#update-data`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5fc844e8d04c484ee405799fb557514828e887fcaf8941c67e6763d6107b3b57`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-java-mybatis#update-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-java-mybatis.md

## Retrieval Guidance

- Use When: Use this chunk when looking for MyBatis mapper XML examples for updating or deleting data in TiDB and the related Java interface naming pattern tied to `mapper.namespace`.
- Retrieval Keywords: MyBatis, mapper XML, mapper.namespace, com.pingcap.model.PlayerMapper, updateByPrimaryKey, deleteByPrimaryKey, update player set coins goods where id, delete from player where id, parameterType com.pingcap.model.Player, parameterType java.lang.String, jdbcType=INTEGER, jdbcType=VARCHAR, Update data, Delete data, Developer guide, Need help, Discord, Slack, support ticket
- Follow-up Guidance: The source points to MyBatis documentation, TiDB Developer guide chapters such as Insert data, Update data, Delete data, Single table reading, Transactions, and SQL performance optimization, plus community help on Discord, Slack, or support ticket submission.
- Classification Note: This is reference content because it provides concrete MyBatis update and delete mapper XML snippets, exact identifiers, and links to related documentation and support resources.

## Official Source Content

### Update data

Add a node in the mapper XML and add a function with the same name in the interface class configured in the `mapper.namespace` attribute of the XML configuration file:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.pingcap.model.PlayerMapper">
    <update id="updateByPrimaryKey" parameterType="com.pingcap.model.Player">
    update player
    set coins = #{coins,jdbcType=INTEGER},
      goods = #{goods,jdbcType=INTEGER}
    where id = #{id,jdbcType=VARCHAR}
    </update>
</mapper>
```

For more information, refer to [Update data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data).
### Delete data

Add a node in the mapper XML and add a function with the same name in the interface class configured in the `mapper.namespace` attribute of the XML configuration file:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.pingcap.model.PlayerMapper">
    <delete id="deleteByPrimaryKey" parameterType="java.lang.String">
    delete from player
    where id = #{id,jdbcType=VARCHAR}
    </delete>
</mapper>
```

For more information, refer to [Delete data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data).
## Next steps

- Learn more usage of MyBatis from [the documentation of MyBatis](http://www.mybatis.org/mybatis-3/).
- Learn the best practices for TiDB application development with the chapters in the [Developer guide](https://docs.pingcap.com/tidb/stable/develop/dev-guide-overview), such as [Insert data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data), [Update data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data), [Delete data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data), [Single table reading](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table), [Transactions](https://docs.pingcap.com/tidb/stable/develop/dev-guide-transaction-overview), and [SQL performance optimization](https://docs.pingcap.com/tidb/stable/develop/dev-guide-optimize-sql-overview).
- Learn through the professional [TiDB developer courses](https://www.pingcap.com/education/) and earn [TiDB certifications](https://www.pingcap.com/education/certification/) after passing the exam.
- Learn through the course for Java developers: [Working with TiDB from Java](https://eng.edu.pingcap.com/catalog/info/id:212).
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
