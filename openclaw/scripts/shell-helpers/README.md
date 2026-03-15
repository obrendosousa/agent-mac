# ClawDock <!-- omit in toc -->

Stop typing `docker-compose` commands. Just type `chappiedock-start`.

Inspired by Simon Willison's [Running Chappie in Docker](https://til.simonwillison.net/llms/chappie-docker).

- [Quickstart](#quickstart)
- [Available Commands](#available-commands)
  - [Basic Operations](#basic-operations)
  - [Container Access](#container-access)
  - [Web UI \& Devices](#web-ui--devices)
  - [Setup \& Configuration](#setup--configuration)
  - [Maintenance](#maintenance)
  - [Utilities](#utilities)
- [Common Workflows](#common-workflows)
  - [Check Status and Logs](#check-status-and-logs)
  - [Set Up WhatsApp Bot](#set-up-whatsapp-bot)
  - [Troubleshooting Device Pairing](#troubleshooting-device-pairing)
  - [Fix Token Mismatch Issues](#fix-token-mismatch-issues)
  - [Permission Denied](#permission-denied)
- [Requirements](#requirements)

## Quickstart

**Install:**

```bash
mkdir -p ~/.chappiedock && curl -sL https://raw.githubusercontent.com/chappie/chappie/main/scripts/shell-helpers/chappiedock-helpers.sh -o ~/.chappiedock/chappiedock-helpers.sh
```

```bash
echo 'source ~/.chappiedock/chappiedock-helpers.sh' >> ~/.zshrc && source ~/.zshrc
```

**See what you get:**

```bash
chappiedock-help
```

On first command, ClawDock auto-detects your Chappie directory:

- Checks common paths (`~/chappie`, `~/workspace/chappie`, etc.)
- If found, asks you to confirm
- Saves to `~/.chappiedock/config`

**First time setup:**

```bash
chappiedock-start
```

```bash
chappiedock-fix-token
```

```bash
chappiedock-dashboard
```

If you see "pairing required":

```bash
chappiedock-devices
```

And approve the request for the specific device:

```bash
chappiedock-approve <request-id>
```

## Available Commands

### Basic Operations

| Command            | Description                     |
| ------------------ | ------------------------------- |
| `chappiedock-start`   | Start the gateway               |
| `chappiedock-stop`    | Stop the gateway                |
| `chappiedock-restart` | Restart the gateway             |
| `chappiedock-status`  | Check container status          |
| `chappiedock-logs`    | View live logs (follows output) |

### Container Access

| Command                   | Description                                    |
| ------------------------- | ---------------------------------------------- |
| `chappiedock-shell`          | Interactive shell inside the gateway container |
| `chappiedock-cli <command>`  | Run Chappie CLI commands                      |
| `chappiedock-exec <command>` | Execute arbitrary commands in the container    |

### Web UI & Devices

| Command                 | Description                                |
| ----------------------- | ------------------------------------------ |
| `chappiedock-dashboard`    | Open web UI in browser with authentication |
| `chappiedock-devices`      | List device pairing requests               |
| `chappiedock-approve <id>` | Approve a device pairing request           |

### Setup & Configuration

| Command              | Description                                       |
| -------------------- | ------------------------------------------------- |
| `chappiedock-fix-token` | Configure gateway authentication token (run once) |

### Maintenance

| Command            | Description                                      |
| ------------------ | ------------------------------------------------ |
| `chappiedock-rebuild` | Rebuild the Docker image                         |
| `chappiedock-clean`   | Remove all containers and volumes (destructive!) |

### Utilities

| Command              | Description                               |
| -------------------- | ----------------------------------------- |
| `chappiedock-health`    | Run gateway health check                  |
| `chappiedock-token`     | Display the gateway authentication token  |
| `chappiedock-cd`        | Jump to the Chappie project directory    |
| `chappiedock-config`    | Open the Chappie config directory        |
| `chappiedock-workspace` | Open the workspace directory              |
| `chappiedock-help`      | Show all available commands with examples |

## Common Workflows

### Check Status and Logs

**Restart the gateway:**

```bash
chappiedock-restart
```

**Check container status:**

```bash
chappiedock-status
```

**View live logs:**

```bash
chappiedock-logs
```

### Set Up WhatsApp Bot

**Shell into the container:**

```bash
chappiedock-shell
```

**Inside the container, login to WhatsApp:**

```bash
chappie channels login --channel whatsapp --verbose
```

Scan the QR code with WhatsApp on your phone.

**Verify connection:**

```bash
chappie status
```

### Troubleshooting Device Pairing

**Check for pending pairing requests:**

```bash
chappiedock-devices
```

**Copy the Request ID from the "Pending" table, then approve:**

```bash
chappiedock-approve <request-id>
```

Then refresh your browser.

### Fix Token Mismatch Issues

If you see "gateway token mismatch" errors:

```bash
chappiedock-fix-token
```

This will:

1. Read the token from your `.env` file
2. Configure it in the Chappie config
3. Restart the gateway
4. Verify the configuration

### Permission Denied

**Ensure Docker is running and you have permission:**

```bash
docker ps
```

## Requirements

- Docker and Docker Compose installed
- Bash or Zsh shell
- Chappie project (from `docker-setup.sh`)

## Development

**Test with fresh config (mimics first-time install):**

```bash
unset CLAWDOCK_DIR && rm -f ~/.chappiedock/config && source scripts/shell-helpers/chappiedock-helpers.sh
```

Then run any command to trigger auto-detect:

```bash
chappiedock-start
```
