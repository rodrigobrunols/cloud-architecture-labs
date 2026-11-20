# ⚡ Lab 03: Connection Pooling with HikariCP — Shrink the Hold Time Before You Grow the Pool

This lab shows why connection timeouts are usually a **hold-time** problem, not a pool-size problem. A Spring Boot app with a small HikariCP pool talks to PostgreSQL. One endpoint keeps a connection busy for 2 seconds; another does the same slow work **outside** the transaction. Same load, very different results.

> **Lesson:** Before I grow the pool, I shrink W.

---

## 🎯 The Problem

When requests start failing with `Connection is not available, request timed out`, the classic reaction is to raise `maximumPoolSize`. That often makes things worse:

* Every new connection is a PostgreSQL backend process with its own memory.
* `pods × pool size` can quickly go above `max_connections`.
* More connections running at once means more context switching and lock contention, so each query gets slower.

The real question is: **how long does each request hold a connection?**

---

## 📐 Little's Law

```
L = λ × W

L = connections busy at the same time (what the pool must supply)
λ = request rate that needs the database (req/s)
W = how long each request holds a connection (s)
```

Turned around, a pool of size `N` can serve at most `λ = N / W` requests per second.

| Pool (N) | Hold time (W) | Max throughput (N / W) |
| :---: | :---: | :---: |
| 5 | 2 s | 2.5 req/s |
| 5 | 2 ms | 2,500 req/s |

Same pool, 1,000x more throughput. Only `W` changed.

```
/slow   : [── get connection ── pg_sleep(2) inside @Transactional ── release ──]   W ≈ 2 s
/fixed  : [──── slow work (2 s), NO connection ────][get ─ SELECT 1 ─ release]     W ≈ 2 ms
```

---

## 🛠️ Setup

| Component | Config |
| :--- | :--- |
| PostgreSQL 16 (Docker) | Port `5433`, `max_connections=20` |
| Spring Boot 4 / Java 21 | HikariCP `maximum-pool-size: 5` |
| `/slow` | `@Transactional` + `SELECT pg_sleep(2)` → holds a connection for ~2 s |
| `/fixed` | `Thread.sleep(2000)` with no connection held, then `SELECT 1` → holds a connection for ~2 ms |
| Load | 20 parallel requests per run |

---

## 🧪 The 3 Runs

| Run | Endpoint | `connectionTimeout` | Hold time (W) | Result |
| :---: | :--- | :---: | :---: | :--- |
| 1 | `/slow` | 30 s (default) | ~2 s | All 20 return `200`, but in waves at ~2 / 4 / 6 / 8.5 s |
| 2 | `/slow` | 3 s | ~2 s | 10 × `200`, 10 × `500` (timed out waiting for a connection) |
| 3 | `/fixed` | 3 s | ~2 ms | 20 × `200`, all in ~2.3 s |

### What happened

* **Run 1:** 5 connections, 20 requests, 2 s each → 4 waves of 5. Nothing fails, but the last users wait ~8 s. The default 30 s timeout **hides** the problem.
* **Run 2:** Same waves, but now requests give up after waiting 3 s. Waves 1 and 2 get a connection in time (wait 0 s and ~2 s); waves 3 and 4 would wait 4 s and 6 s, so they fail. Exactly 10 / 10, as the math predicts.
* **Run 3:** The slow work no longer holds a connection. 20 requests × 2 ms = 40 ms of total connection time, so 5 connections are more than enough. Every request finishes in ~2.3 s (the 2 s of external work plus a little overhead).

> To get Run 1 to "no waiting" by growing the pool, I would need `L = 20 req × 2 s / 2 s ≈ 20` connections — the whole `max_connections` of the database, for one app instance.

---

## 🔑 Takeaways

1. **Measure W before you touch the pool.** Check HikariCP metrics (`hikaricp.connections.usage`, `hikaricp.connections.pending`, `hikaricp.connections.acquire`) in `/actuator/metrics`.
2. **Keep slow work out of transactions.** HTTP calls, file I/O, and sleeps inside `@Transactional` keep a connection busy for nothing.
3. **Use a short `connectionTimeout`.** Failing fast (3 s) shows the problem early; 30 s turns it into slow, silent queuing.
4. **Size the pool across all replicas.** `replicas × maximumPoolSize` must stay under `max_connections`, with headroom for admin and migrations.
5. **A proxy does not fix a long W.** RDS Proxy (or PgBouncer in transaction mode) multiplexes many app connections over fewer DB connections, but only between transactions. A 2 s transaction still holds a real DB connection for 2 s. And session state (`SET`, temp tables, advisory locks) **pins** a client to one DB connection, which removes the multiplexing benefit.

---

## 💻 How to Run

### Prerequisites
* Docker
* Java 21 and Maven
* `curl` (or `hey` / `k6` for load)

### Steps

```bash
# 1. Start PostgreSQL (port 5433, max_connections=20)
docker compose up -d

# 2. Start the app (pool size 5)
mvn spring-boot:run

# 3. Fire 20 parallel requests at the slow endpoint
seq 20 | xargs -P 20 -I{} curl -s -o /dev/null \
  -w "%{http_code} %{time_total}s\n" http://localhost:8080/slow

# 4. Same load at the fixed endpoint
seq 20 | xargs -P 20 -I{} curl -s -o /dev/null \
  -w "%{http_code} %{time_total}s\n" http://localhost:8080/fixed

# 5. Watch the pool while the load runs
curl -s http://localhost:8080/actuator/metrics/hikaricp.connections.pending
```

For **Run 1**, set `connection-timeout: 30000` in `src/main/resources/application.yml` and restart. For **Runs 2 and 3**, use `3000`.

---

## 🔜 Next Step (optional)

Add PgBouncer in transaction mode to `docker-compose.yml` to simulate RDS Proxy, run 3 app instances with pool 10 each (30 > 20), and show that the database survives. Then issue a `SET` per request to see pinning.
