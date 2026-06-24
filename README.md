# FastHelm

A lightweight token bucket rate limiter for FastAPI, with a Redis backend for distributed, multi-instance limiting.

## Overview

Any public-facing API can be overwhelmed by too many requests in too little time, whether from a buggy client stuck in a retry loop, a scraper hammering an endpoint, an abusive actor, or simply more legitimate traffic than the backend can handle. Without a guardrail, a handful of callers can degrade the service for everyone, or run up costs that scale directly with request volume.

That cost problem is sharpest in front of expensive backends. An endpoint that calls an LLM, runs a heavy query, or hits a paid third-party API pays real money (and latency) per request.

FastHelm sits in front of your FastAPI routes and answers one question per request: *allow it, or reject it?* It uses the token bucket algorithm, which enforces an average rate while still permitting short, controlled bursts. The natural shape of real API traffic.

The core logic is decoupled from the storage backend, so the same limiter runs on an in-memory backend during local development and on Redis in production without any change to the business logic or the HTTP layer. It starts simple — single process, in memory — and scales up to a distributed setup where several API instances share one Redis and stay correct under concurrency through an atomic Lua script.

## Features

- **Token bucket with lazy refill** — enforces an average rate while allowing controlled bursts; no background threads or timers, tokens are recomputed from elapsed time on each request.
- **Swappable storage backends** — in-memory (lock-based, single instance) and Redis (distributed).
- **Atomic Redis limiting** via a Lua script, so the read-decide-write cycle stays race-free across multiple instances.
- **FastAPI integration** as middleware or a route dependency.
- **Standard HTTP semantics** — `429 Too Many Requests` with `Retry-After` and `X-RateLimit-*` headers.
- **Flexible keying** — limit by client IP, API key, or a custom key function.

## Tech stack

- Python 3.14+
- FastAPI
- Redis
- Poetry (dependency and environment management)
- pytest

## Project structure

The code is split into three independent layers — business logic, storage, and HTTP — each depending only on the interfaces of the layer below it.

```
fasthelm/
├── core/                # business logic — pure algorithm, no I/O
│   ├── limiter.py       # RateLimiter protocol + Decision result
│   └── token_bucket.py  # token bucket with lazy refill
│
├── storage/             # state backends behind a common protocol
│   ├── base.py          # Storage protocol
│   ├── memory.py        # in-process, lock-based (single instance)
│   └── redis.py         # distributed backend + atomic Lua script
│
└── http/                # FastAPI integration layer
    ├── middleware.py    # request keying + limit enforcement
    ├── dependencies.py  # per-route dependency variant
    └── responses.py     # 429 response + rate-limit headers

tests/
pyproject.toml
poetry.lock
README.md
```

The dependency direction is one-way: `http` knows about `core`, `core` knows about `storage` only through its protocol, and `core` never imports anything from `http`. That boundary is what lets you swap the storage backend — memory for Redis — without touching the limiting logic or the HTTP layer.