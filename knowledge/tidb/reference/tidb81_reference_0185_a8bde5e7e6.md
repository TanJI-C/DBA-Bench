# Supported ORM frameworks for TiDB

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-third-party-support.md`
- Source Title: `Third-Party Tools Supported by TiDB`
- Source Heading Path: `Third-Party Tools Supported by TiDB > ORM`
- Source Line Ranges: `65-184`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `sql`
- Topic Tags: `orm`, `frameworks`, `tested-versions`, `language-support`, `adapters`, `tutorials`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0185_a8bde5e7e6`
- Source ID: `tidb-docs-8.1:develop/dev-guide-third-party-support.md#orm`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2ab5a9b8362eca7a0c3fed5b6b0784310647108b521dea757987bf0053bbebdd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-third-party-support#orm
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-third-party-support.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks which ORM frameworks are supported by TiDB, their latest tested versions, support level, TiDB adapter, or available tutorials by language.
- Retrieval Keywords: ORM, gorm, beego, upper/db, xorm, Hibernate, MyBatis, Spring Data JPA, jOOQ, Active Record, Sequelize, Prisma, TypeORM, Django, django-tidb, SQLAlchemy, Latest tested version, Support level, TiDB adapter
- Follow-up Guidance: The chunk provides tutorial links for GORM, Hibernate, MyBatis, Spring Boot, Rails Framework and ActiveRecord ORM, Sequelize, Prisma, TypeORM, Django, and SQLAlchemy.
- Classification Note: This is reference content because it is a tabular support matrix of ORM frameworks with languages, tested versions, support levels, adapters, and tutorial availability.

## Official Source Content

## ORM

<table>
   <thead>
      <tr>
         <th>Language</th>
         <th>ORM framework</th>
         <th>Latest tested version</th>
         <th>Support level</th>
         <th>TiDB adapter</th>
         <th>Tutorial</th>
      </tr>
   </thead>
   <tbody>
      <tr>
         <td rowspan="4">Go</td>
         <td><a href="https://github.com/go-gorm/gorm" target="_blank" referrerpolicy="no-referrer-when-downgrade">gorm</a></td>
         <td>v1.23.5</td>
         <td>Full</td>
         <td>N/A</td>
         <td><a href="/tidb/v8.1/dev-guide-sample-application-golang-gorm">Connect to TiDB with GORM</a></td>
      </tr>
      <tr>
         <td><a href="https://github.com/beego/beego" target="_blank" referrerpolicy="no-referrer-when-downgrade">beego</a></td>
         <td>v2.0.3</td>
         <td>Full</td>
         <td>N/A</td>
         <td>N/A</td>
      </tr>
      <tr>
         <td><a href="https://github.com/upper/db" target="_blank" referrerpolicy="no-referrer-when-downgrade">upper/db</a></td>
         <td>v4.5.2</td>
         <td>Full</td>
         <td>N/A</td>
         <td>N/A</td>
      </tr>
      <tr>
         <td><a href="https://gitea.com/xorm/xorm" target="_blank" referrerpolicy="no-referrer-when-downgrade">xorm</a></td>
         <td>v1.3.1</td>
         <td>Full</td>
         <td>N/A</td>
         <td>N/A</td>
      </tr>
      <tr>
         <td rowspan="4">Java</td>
         <td><a href="https://hibernate.org/orm/" target="_blank" referrerpolicy="no-referrer-when-downgrade">Hibernate</a></td>
         <td>6.1.0.Final</td>
         <td>Full</td>
         <td>N/A</td>
         <td><a href="/tidb/v8.1/dev-guide-sample-application-java-hibernate">Connect to TiDB with Hibernate</a></td>
      </tr>
      <tr>
         <td><a href="https://mybatis.org/mybatis-3/" target="_blank" referrerpolicy="no-referrer-when-downgrade">MyBatis</a></td>
         <td>v3.5.10</td>
         <td>Full</td>
         <td>N/A</td>
         <td><a href="/tidb/v8.1/dev-guide-sample-application-java-mybatis">Connect to TiDB with MyBatis</a></td>
      </tr>
      <tr>
         <td><a href="https://spring.io/projects/spring-data-jpa/" target="_blank" referrerpolicy="no-referrer-when-downgrade">Spring Data JPA</a></td>
         <td>2.7.2</td>
         <td>Full</td>
         <td>N/A</td>
         <td><a href="/tidb/v8.1/dev-guide-sample-application-java-spring-boot">Connect to TiDB with Spring Boot</a></td>
      </tr>
      <tr>
         <td><a href="https://github.com/jOOQ/jOOQ" target="_blank" referrerpolicy="no-referrer-when-downgrade">jOOQ</a></td>
         <td>v3.16.7 (Open Source)</td>
         <td>Full</td>
         <td>N/A</td>
         <td>N/A</td>
      </tr>
      <tr>
         <td>Ruby</td>
         <td><a href="https://guides.rubyonrails.org/active_record_basics.html" target="_blank" referrerpolicy="no-referrer-when-downgrade">Active Record</a></td>
         <td>v7.0</td>
         <td>Full</td>
         <td>N/A</td>
         <td><a href="/tidb/v8.1/dev-guide-sample-application-ruby-rails">Connect to TiDB with Rails Framework and ActiveRecord ORM</a></td>
      </tr>
      <tr>
         <td rowspan="3">JavaScript / TypeScript</td>
         <td><a href="https://sequelize.org/" target="_blank" referrerpolicy="no-referrer-when-downgrade">Sequelize</a></td>
         <td>v6.20.1</td>
         <td>Full</td>
         <td>N/A</td>
         <td><a href="/tidb/v8.1/dev-guide-sample-application-nodejs-sequelize">Connect to TiDB with Sequelize</a></td>
      </tr>
      <tr>
         <td><a href="https://www.prisma.io/" target="_blank" referrerpolicy="no-referrer-when-downgrade">Prisma</a></td>
         <td>4.16.2</td>
         <td>Full</td>
         <td>N/A</td>
         <td><a href="/tidb/v8.1/dev-guide-sample-application-nodejs-prisma">Connect to TiDB with Prisma</a></td>
      </tr>
      <tr>
         <td><a href="https://typeorm.io/" target="_blank" referrerpolicy="no-referrer-when-downgrade">TypeORM</a></td>
         <td>v0.3.17</td>
         <td>Full</td>
         <td>N/A</td>
         <td><a href="/tidb/v8.1/dev-guide-sample-application-nodejs-typeorm">Connect to TiDB with TypeORM</a></td>
      </tr>
      <tr>
         <td rowspan="2">Python</td>
         <td><a href="https://pypi.org/project/Django/" target="_blank" referrerpolicy="no-referrer-when-downgrade">Django</a></td>
         <td>v4.2</td>
         <td>Full</td>
         <td><a href="https://github.com/pingcap/django-tidb" target="_blank" referrerpolicy="no-referrer-when-downgrade">django-tidb</a></td>
         <td><a href="/tidb/v8.1/dev-guide-sample-application-python-django">Connect to TiDB with Django</a></td>
      </tr>
      <tr>
         <td><a href="https://www.sqlalchemy.org/" target="_blank" referrerpolicy="no-referrer-when-downgrade">SQLAlchemy</a></td>
         <td>v1.4.37</td>
         <td>Full</td>
         <td>N/A</td>
         <td><a href="/tidb/v8.1/dev-guide-sample-application-python-sqlalchemy">Connect to TiDB with SQLAlchemy</a></td>
      </tr>
   </tbody>
</table>
