import os

from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from redis.asyncio import Redis

from fasthelm.storage.redis import RedisTokenBucket
from fasthelm.http.dependencies import RateLimit

app = FastAPI()

# distributed rate limiter, backed by Redis so several app instances share one bucket.
# REDIS_URL is provided by docker-compose; falls back to localhost for bare-metal runs.
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis = Redis.from_url(REDIS_URL)
limiter = RedisTokenBucket(redis, capacity=3, refill_rate=1.0)
rate_limit = RateLimit(limiter) #default keying: per client IP


# Endpoint that the button is going to bombard
@app.get("/api/ping", dependencies=[Depends(rate_limit)])
async def ping():
    return {"status": "ok"}


# Page: buttons with live results
@app.get("/", response_class=HTMLResponse)
async def index():
    return PAGE


PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>fast-helm · demo</title>
  <style>
    :root { color-scheme: dark; }
    body {
      font-family: ui-monospace, "SF Mono", Menlo, monospace;
      background: #0d1117; color: #e6edf3;
      max-width: 640px; margin: 60px auto; padding: 0 20px;
    }
    h1 { font-size: 1.4rem; margin-bottom: .3rem; }
    p.sub { color: #8b949e; margin-top: 0; }
    button {
      background: #238636; color: #fff; border: 0; border-radius: 6px;
      padding: 12px 20px; font-size: 1rem; cursor: pointer; margin: 20px 0;
    }
    button:disabled { opacity: .5; cursor: default; }
    .row {
      display: flex; align-items: center; gap: 12px;
      padding: 10px 14px; margin: 6px 0; border-radius: 6px;
      background: #161b22; border: 1px solid #30363d;
    }
    .badge { font-weight: 700; padding: 2px 8px; border-radius: 4px; font-size: .85rem; }
    .ok   { background: #1f6f37; color: #d2f5dd; }
    .fail { background: #8b2c2c; color: #ffd7d7; }
    .pending { background: #30363d; color: #8b949e; }
  </style>
</head>
<body>
  <h1>fast-helm</h1>
  <p class="sub">Rate limiter for Python. Press the button and watch the limit cut off the requests.</p>
  <button id="go">Send 6 requests per second</button>
  <div id="results"></div>
  <script>
    const btn = document.getElementById("go");
    const results = document.getElementById("results");
    const sleep = ms => new Promise(r => setTimeout(r, ms));
    async function sendOne(n) {
      const row = document.createElement("div");
      row.className = "row";
      row.innerHTML = `<span>Request #${n}</span>
                       <span class="badge pending" id="b${n}">sending…</span>`;
      results.appendChild(row);
      try {
        const res = await fetch("/api/ping");
        const badge = document.getElementById("b" + n);
        if (res.ok) {
          badge.className = "badge ok";
          badge.textContent = res.status + " OK";
        } else {
          badge.className = "badge fail";
          badge.textContent = res.status + " Too Many Requests";
        }
      } catch (e) {
        const badge = document.getElementById("b" + n);
        badge.className = "badge fail";
        badge.textContent = "error";
      }
    }
    btn.addEventListener("click", async () => {
      btn.disabled = true;
      results.innerHTML = "";
      // Fire 6 with a small stagger so you see them go out one by one,
      // but close enough together to land in the same 1-second window.
      for (let i = 1; i <= 6; i++) {
        sendOne(i);          // no await: they overlap, hitting almost at once
        await sleep(120);    // visual effect only
      }
      await sleep(800);
      btn.disabled = false;
    });
  </script>
</body>
</html>
"""