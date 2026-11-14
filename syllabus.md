### Concurrency & Parallelism

- Processes, threads, and core concurrency concepts

---

### Networking & APIs

- **Networking Fundamentals:** OSI model, network protocols
- **APIs:** HTTP basics, REST APIs (FastAPI)

---

### Databases

- **Fundamentals:** SQL vs. NoSQL (relational vs. non-relational)
- **PostgreSQL:**
- _Core:_ Basic queries, schema design, indexes, transactions, locking, isolation levels
- _Performance:_ Query optimization, `EXPLAIN ANALYZE`, connection pooling (`PgBouncer`)
- _Internals:_ WAL, VACUUM, MVCC, connections
- **Redis:** Basic queries, schema design
- _Patterns:_ Pub/Sub, caching, queues, streams, distributed locks
- **Vector Databases:** Intro to vectors, similarity search, vector indexes
- **Storage Internals:** Hash indexes, B-Trees, SSTables, columnar vs. row-based storage

---

### System Design

#### 1. Foundations & Scaling

- **Metrics & Performance:** Latency vs. response time, percentiles (`p50`, `p95`, `p99`), load testing
- **Core Principles:** CAP theorem, horizontal vs. vertical scaling
- **Traffic & Edge Infrastructure:** Load balancing, caching, connection pooling

#### 2. Distributed Data: Replication & Sharding

- **Replication:** Purpose, sync vs. async, eventual consistency (read-your-writes, monotonic reads), leader-follower, multi-leader, leaderless
- **Sharding (Partitioning):** Purpose, strategies (key-range vs. hash), rebalancing, hot partitions

#### 3. Distributed Systems Depressing Truth

- **Faults & Partial Failures:** Unreliable networks, timeouts, unbounded delays
- **Time & State:** Unreliable clocks (monotonic vs. time-of-day, NTP skew), process pauses (GC pauses, VM suspension)
- **Truth & Safety:** Quorums (truth defined by the majority), fencing tokens

#### 4. Microservices & Data Processing Pipelines

- **Distributed Architecture:** Microservices, event-driven architecture
- **Batch Processing:**
- **Stream Processing:**
