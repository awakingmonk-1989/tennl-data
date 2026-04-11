
**What that PID is:** The value in `daemon_latest.pid` (and what the script prints) is the **top-level background job** `nohup` started. With `CAFFEINATE=1` that’s usually the **`caffeinate`** process; without it, it’s the **`bash`** that runs `insight_card_openclaw_daemon.sh`. OpenClaw / `uv` run **under** that as child processes.

**One-liner to inspect it:**

```bash
ps -p "$(cat output/oc-gpt-runs/daemon_latest.pid)" -o pid,ppid,command
```

**One-liner to find the actual script process (if you don’t trust the pid file):**

```bash
pgrep -fl 'INSIGHT_OC_DAEMON_CHILD=1.*insight_card_openclaw_daemon'
```
