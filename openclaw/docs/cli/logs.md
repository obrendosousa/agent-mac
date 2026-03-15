---
summary: "CLI reference for `chappie logs` (tail gateway logs via RPC)"
read_when:
  - You need to tail Gateway logs remotely (without SSH)
  - You want JSON log lines for tooling
title: "logs"
---

# `chappie logs`

Tail Gateway file logs over RPC (works in remote mode).

Related:

- Logging overview: [Logging](/logging)

## Examples

```bash
chappie logs
chappie logs --follow
chappie logs --json
chappie logs --limit 500
chappie logs --local-time
chappie logs --follow --local-time
```

Use `--local-time` to render timestamps in your local timezone.
