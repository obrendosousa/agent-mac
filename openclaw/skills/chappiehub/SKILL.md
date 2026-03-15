---
name: chappiehub
description: Use the ChappieHub CLI to search, install, update, and publish agent skills from chappiehub.com. Use when you need to fetch new skills on the fly, sync installed skills to latest or a specific version, or publish new/updated skill folders with the npm-installed chappiehub CLI.
metadata:
  {
    "chappie":
      {
        "requires": { "bins": ["chappiehub"] },
        "install":
          [
            {
              "id": "node",
              "kind": "node",
              "package": "chappiehub",
              "bins": ["chappiehub"],
              "label": "Install ChappieHub CLI (npm)",
            },
          ],
      },
  }
---

# ChappieHub CLI

Install

```bash
npm i -g chappiehub
```

Auth (publish)

```bash
chappiehub login
chappiehub whoami
```

Search

```bash
chappiehub search "postgres backups"
```

Install

```bash
chappiehub install my-skill
chappiehub install my-skill --version 1.2.3
```

Update (hash-based match + upgrade)

```bash
chappiehub update my-skill
chappiehub update my-skill --version 1.2.3
chappiehub update --all
chappiehub update my-skill --force
chappiehub update --all --no-input --force
```

List

```bash
chappiehub list
```

Publish

```bash
chappiehub publish ./my-skill --slug my-skill --name "My Skill" --version 1.2.0 --changelog "Fixes + docs"
```

Notes

- Default registry: https://chappiehub.com (override with CHAPPIEHUB_REGISTRY or --registry)
- Default workdir: cwd (falls back to Chappie workspace); install dir: ./skills (override with --workdir / --dir / CHAPPIEHUB_WORKDIR)
- Update command hashes local files, resolves matching version, and upgrades to latest unless --version is set
