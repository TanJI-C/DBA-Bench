# Sequelize delete example and follow-up resources

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-nodejs-sequelize.md`
- Source Title: `Connect to TiDB with Sequelize`
- Source Heading Path: `Connect to TiDB with Sequelize > Sample code snippets > Delete data | Connect to TiDB with Sequelize > Next steps | Connect to TiDB with Sequelize > Need help?`
- Source Line Ranges: `306-338`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `shared`
- Topic Tags: `sequelize`, `nodejs`, `delete-data`, `sample-code`, `developer-guide`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0159_4754b83f94`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-nodejs-sequelize.md#delete-data`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `859a5846ce8ea23c18ebf5aa9e4d8a74da38d0177b9e4dd8d8807d8bac62b61f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-nodejs-sequelize#delete-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-nodejs-sequelize.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the Sequelize sample that deletes a Player record in a Node.js TiDB application and for the linked next-step learning resources or support channels.
- Retrieval Keywords: Delete data, Sequelize, Node.js, Player, ID `6`, newPlayer.destroy(), playersModel.findByPk(6), Deleted the new player, developer guide, Insert data, Update data, Single table reading, Transactions, SQL performance optimization, Discord, Slack, submit a support ticket
- Follow-up Guidance: The source points to the Delete data page, Sequelize documentation, TiDB Developer guide chapters, TiDB developer courses and certifications, and community or support channels including Discord, Slack, and support tickets.
- Classification Note: This is reference content because it provides a concrete Sequelize delete code snippet plus links to related documentation and help resources.

## Official Source Content

### Delete data

The following query deletes the `Player` record with ID `6` that was created in the [Insert data](#insert-data) section:

```typescript
logger.info('Deleting the new player...');
await newPlayer.destroy();
const deletedNewPlayer = await playersModel.findByPk(6);
logger.info('Deleted the new player.');
logger.info(deletedNewPlayer?.toJSON());
```

For more information, refer to [Delete data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data).
## Next steps

- Learn more usage of the ORM framework Sequelize driver from [the documentation of Sequelize](https://sequelize.org/).
- Learn the best practices for TiDB application development with the chapters in the [Developer guide](https://docs.pingcap.com/tidb/stable/develop/dev-guide-overview), such as [Insert data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data), [Update data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data), [Delete data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data), [Single table reading](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table), [Transactions](https://docs.pingcap.com/tidb/stable/develop/dev-guide-transaction-overview), and [SQL performance optimization](https://docs.pingcap.com/tidb/stable/develop/dev-guide-optimize-sql-overview).
- Learn through the professional [TiDB developer courses](https://www.pingcap.com/education/) and earn [TiDB certifications](https://www.pingcap.com/education/certification/) after passing the exam.
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
