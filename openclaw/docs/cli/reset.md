---
summary: "CLI reference for `chappie reset` (reset local state/config)"
read_when:
  - You want to wipe local state while keeping the CLI installed
  - You want a dry-run of what would be removed
title: "reset"
---

# `chappie reset`

Reset local config/state (keeps the CLI installed).

```bash
chappie backup create
chappie reset
chappie reset --dry-run
chappie reset --scope config+creds+sessions --yes --non-interactive
```

Run `chappie backup create` first if you want a restorable snapshot before removing local state.
