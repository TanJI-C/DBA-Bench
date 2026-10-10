# Spring transaction boundaries in Java applications

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/java-app-best-practices.md`
- Source Title: `Best Practices for Developing Java Applications with TiDB`
- Source Heading Path: `Best Practices for Developing Java Applications with TiDB > Spring Transaction`
- Source Line Ranges: `363-370`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `sql`
- Topic Tags: `java`, `spring`, `transaction`, `aop`, `transactional`, `propagation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0018_18327d0b8f`
- Source ID: `tidb-docs-8.1:develop/java-app-best-practices.md#spring-transaction`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f95622ba2e4d380544215fa25222ecf5df51f4e442a6fd16bb5a8c8132e62175`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/java-app-best-practices#spring-transaction
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/java-app-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when you need to identify where Spring starts and commits transactions in Java code or how nested transactions can vary with `Propagation`.
- Retrieval Keywords: Spring Transaction, @Transactional, AOP, transaction is started, commits the transaction, method definition, Propagation, embedding
- Follow-up Guidance: The chunk says you can find `@Transactional` in code to determine when the transaction is started and closed.
- Classification Note: This is classified as architecture content because the official text describes transaction boundary behavior in Spring applications and how AOP and `Propagation` affect transaction handling.

## Official Source Content

## Spring Transaction

In the real world, applications might use [Spring Transaction](https://docs.spring.io/spring/docs/4.2.x/spring-framework-reference/html/transaction.html) and AOP aspects to start and stop transactions.

By adding the `@Transactional` annotation to the method definition, AOP starts the transaction before the method is called, and commits the transaction before the method returns the result. If your application has a similar need, you can find `@Transactional` in code to determine when the transaction is started and closed.

Pay attention to a special case of embedding. If it occurs, Spring will behave differently based on the [Propagation](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/transaction/annotation/Propagation.html) configuration.
