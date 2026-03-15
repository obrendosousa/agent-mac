---
summary: "CLI reference for `chappie uninstall` (remove gateway service + local data)"
read_when:
  - You want to remove the gateway service and/or local state
  - You want a dry-run first
title: "uninstall"
---

# `chappie uninstall`

Uninstall the gateway service + local data (CLI remains).

```bash
chappie backup create
chappie uninstall
chappie uninstall --all --yes
chappie uninstall --dry-run
```

Run `chappie backup create` first if you want a restorable snapshot before removing state or workspaces.
