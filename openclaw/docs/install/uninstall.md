---
summary: "Uninstall Chappie completely (CLI, service, state, workspace)"
read_when:
  - You want to remove Chappie from a machine
  - The gateway service is still running after uninstall
title: "Uninstall"
---

# Uninstall

Two paths:

- **Easy path** if `chappie` is still installed.
- **Manual service removal** if the CLI is gone but the service is still running.

## Easy path (CLI still installed)

Recommended: use the built-in uninstaller:

```bash
chappie uninstall
```

Non-interactive (automation / npx):

```bash
chappie uninstall --all --yes --non-interactive
npx -y chappie uninstall --all --yes --non-interactive
```

Manual steps (same result):

1. Stop the gateway service:

```bash
chappie gateway stop
```

2. Uninstall the gateway service (launchd/systemd/schtasks):

```bash
chappie gateway uninstall
```

3. Delete state + config:

```bash
rm -rf "${CHAPPIE_STATE_DIR:-$HOME/.chappie}"
```

If you set `CHAPPIE_CONFIG_PATH` to a custom location outside the state dir, delete that file too.

4. Delete your workspace (optional, removes agent files):

```bash
rm -rf ~/.chappie/workspace
```

5. Remove the CLI install (pick the one you used):

```bash
npm rm -g chappie
pnpm remove -g chappie
bun remove -g chappie
```

6. If you installed the macOS app:

```bash
rm -rf /Applications/Chappie.app
```

Notes:

- If you used profiles (`--profile` / `CHAPPIE_PROFILE`), repeat step 3 for each state dir (defaults are `~/.chappie-<profile>`).
- In remote mode, the state dir lives on the **gateway host**, so run steps 1-4 there too.

## Manual service removal (CLI not installed)

Use this if the gateway service keeps running but `chappie` is missing.

### macOS (launchd)

Default label is `ai.chappie.gateway` (or `ai.chappie.<profile>`; legacy `com.chappie.*` may still exist):

```bash
launchctl bootout gui/$UID/ai.chappie.gateway
rm -f ~/Library/LaunchAgents/ai.chappie.gateway.plist
```

If you used a profile, replace the label and plist name with `ai.chappie.<profile>`. Remove any legacy `com.chappie.*` plists if present.

### Linux (systemd user unit)

Default unit name is `chappie-gateway.service` (or `chappie-gateway-<profile>.service`):

```bash
systemctl --user disable --now chappie-gateway.service
rm -f ~/.config/systemd/user/chappie-gateway.service
systemctl --user daemon-reload
```

### Windows (Scheduled Task)

Default task name is `Chappie Gateway` (or `Chappie Gateway (<profile>)`).
The task script lives under your state dir.

```powershell
schtasks /Delete /F /TN "Chappie Gateway"
Remove-Item -Force "$env:USERPROFILE\.chappie\gateway.cmd"
```

If you used a profile, delete the matching task name and `~\.chappie-<profile>\gateway.cmd`.

## Normal install vs source checkout

### Normal install (install.sh / npm / pnpm / bun)

If you used `https://chappie.ai/install.sh` or `install.ps1`, the CLI was installed with `npm install -g chappie@latest`.
Remove it with `npm rm -g chappie` (or `pnpm remove -g` / `bun remove -g` if you installed that way).

### Source checkout (git clone)

If you run from a repo checkout (`git clone` + `chappie ...` / `bun run chappie ...`):

1. Uninstall the gateway service **before** deleting the repo (use the easy path above or manual service removal).
2. Delete the repo directory.
3. Remove state + workspace as shown above.
