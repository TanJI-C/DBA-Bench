# Query Handling; Genetic Algorithms; GEQO in PostgreSQL; Further Reading

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVII_internals/11_genetic_query_optimizer.md`
- Source Title: `Genetic Query Optimizer`
- Source Heading Path: `Genetic Query Optimizer > Query Handling; Genetic Algorithms; GEQO in PostgreSQL; Further Reading`
- Source Line Ranges: `10-45, 46-67, 75-180, 181-192`
- Chunk ID: `pg16_guide_0051_7f9bc7117a`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b739287dfdf9ffecb12b34be76939f16b27ba74a06c8d45cd04cf8500933043a`

## Retrieval Guidance

- Use When: Investigate planning behavior for queries with many joins where GEQO may affect plan selection.
- Retrieval Keywords: GEQO, genetic query optimizer, geqo_threshold, join order, large join planning, planner search
- Follow-up Guidance: Confirm with EXPLAIN and current planner settings before treating GEQO as the root cause.
- Classification Note: The chapter explains GEQO planning behavior and when genetic optimization is used, which can help confirm plan instability or join-order planning surprises in large joins.

## Official Source Content

## Query Handling as a Complex Optimization Problem

Among all relational operators the most difficult one to process
and optimize is the *join*. The number of
possible query plans grows exponentially with the
number of joins in the query. Further optimization effort is
caused by the support of a variety of *join
methods* (e.g., nested loop, hash join, merge join in
PostgreSQL) to process individual joins
and a diversity of *indexes* (e.g.,
B-tree, hash, GiST and GIN in PostgreSQL) as
access paths for relations.

The normal PostgreSQL query optimizer
performs a *near-exhaustive search* over the
space of alternative strategies. This algorithm, first introduced
in IBM's System R database, produces a near-optimal join order,
but can take an enormous amount of time and memory space when the
number of joins in the query grows large. This makes the ordinary
PostgreSQL query optimizer
inappropriate for queries that join a large number of tables.

The Institute of Automatic Control at the University of Mining and
Technology, in Freiberg, Germany, encountered some problems when
it wanted to use PostgreSQL as the
backend for a decision support knowledge based system for the
maintenance of an electrical power grid. The DBMS needed to handle
large join queries for the inference machine of the knowledge
based system. The number of joins in these queries made using the
normal query optimizer infeasible.

In the following we describe the implementation of a
*genetic algorithm* to solve the join
ordering problem in a manner that is efficient for queries
involving large numbers of joins.

## Genetic Algorithms

The genetic algorithm (GA) is a heuristic optimization method which
operates through randomized search. The set of possible solutions for the
optimization problem is considered as a
*population* of *individuals*.
The degree of adaptation of an individual to its environment is specified
by its *fitness*.

The coordinates of an individual in the search space are represented
by *chromosomes*, in essence a set of character
strings. A *gene* is a
subsection of a chromosome which encodes the value of a single parameter
being optimized. Typical encodings for a gene could be *binary* or
*integer*.

Through simulation of the evolutionary operations *recombination*,
*mutation*, and
*selection* new generations of search points are found
that show a higher average fitness than their ancestors. [geqo-figure](#geqo-figure)
illustrates these steps.

## Genetic Query Optimization (GEQO) in PostgreSQL

The GEQO module approaches the query
optimization problem as though it were the well-known traveling salesman
problem (TSP).
Possible query plans are encoded as integer strings. Each string
represents the join order from one relation of the query to the next.
For example, the join tree

```
/\
/\ 2
/\ 3
4  1
```

is encoded by the integer string '4-1-3-2',
which means, first join relation '4' and '1', then '3', and
then '2', where 1, 2, 3, 4 are relation IDs within the
PostgreSQL optimizer.

Specific characteristics of the GEQO
implementation in PostgreSQL
are:

- Usage of a *steady state* GA (replacement of the least fit
individuals in a population, not whole-generational replacement)
allows fast convergence towards improved query plans. This is
essential for query handling with reasonable time;
- Usage of *edge recombination crossover*
which is especially suited to keep edge losses low for the
solution of the TSP by means of a
GA;
- Mutation as genetic operator is deprecated so that no repair
mechanisms are needed to generate legal TSP tours.

Parts of the GEQO module are adapted from D. Whitley's
Genitor algorithm.

The GEQO module allows
the PostgreSQL query optimizer to
support large join queries effectively through
non-exhaustive search.

### Generating Possible Plans with GEQO

The GEQO planning process uses the standard planner
code to generate plans for scans of individual relations.  Then join
plans are developed using the genetic approach.  As shown above, each
candidate join plan is represented by a sequence in which to join
the base relations.  In the initial stage, the GEQO
code simply generates some possible join sequences at random.  For each
join sequence considered, the standard planner code is invoked to
estimate the cost of performing the query using that join sequence.
(For each step of the join sequence, all three possible join strategies
are considered; and all the initially-determined relation scan plans
are available.  The estimated cost is the cheapest of these
possibilities.)  Join sequences with lower estimated cost are considered
"more fit" than those with higher cost.  The genetic algorithm
discards the least fit candidates.  Then new candidates are generated
by combining genes of more-fit candidates — that is, by using
randomly-chosen portions of known low-cost join sequences to create
new sequences for consideration.  This process is repeated until a
preset number of join sequences have been considered; then the best
one found at any time during the search is used to generate the finished
plan.

This process is inherently nondeterministic, because of the randomized
choices made during both the initial population selection and subsequent
"mutation" of the best candidates.  To avoid surprising changes
of the selected plan, each run of the GEQO algorithm restarts its
random number generator with the current [guc-geqo-seed](#guc-geqo-seed)
parameter setting.  As long as `geqo_seed` and the other
GEQO parameters are kept fixed, the same plan will be generated for a
given query (and other planner inputs such as statistics).  To experiment
with different search paths, try changing `geqo_seed`.

### Future Implementation Tasks for
PostgreSQL GEQO

Work is still needed to improve the genetic algorithm parameter
settings.
In file `src/backend/optimizer/geqo/geqo_main.c`,
routines
`gimme_pool_size` and `gimme_number_generations`,
we have to find a compromise for the parameter settings
to satisfy two competing demands:

- Optimality of the query plan
- Computing time

In the current implementation, the fitness of each candidate join
sequence is estimated by running the standard planner's join selection
and cost estimation code from scratch.  To the extent that different
candidates use similar sub-sequences of joins, a great deal of work
will be repeated.  This could be made significantly faster by retaining
cost estimates for sub-joins.  The problem is to avoid expending
unreasonable amounts of memory on retaining that state.

At a more basic level, it is not clear that solving query optimization
with a GA algorithm designed for TSP is appropriate.  In the TSP case,
the cost associated with any substring (partial tour) is independent
of the rest of the tour, but this is certainly not true for query
optimization.  Thus it is questionable whether edge recombination
crossover is the most effective mutation procedure.

## Further Reading

The following resources contain additional information about
genetic algorithms:

- [
The Hitch-Hiker's Guide to Evolutionary Computation](http://www.faqs.org/faqs/ai-faq/genetic/part1/), (FAQ for [](news://comp.ai.genetic))
- [
Evolutionary Computation and its application to art and design](https://www.red3d.com/cwr/evolve.html), by
Craig Reynolds
- [elma04](#elma04)
- [fong](#fong)
