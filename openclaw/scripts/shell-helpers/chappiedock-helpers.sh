#!/usr/bin/env bash
# ClawDock - Docker helpers for Chappie
# Inspired by Simon Willison's "Running Chappie in Docker"
# https://til.simonwillison.net/llms/chappie-docker
#
# Installation:
#   mkdir -p ~/.chappiedock && curl -sL https://raw.githubusercontent.com/chappie/chappie/main/scripts/shell-helpers/chappiedock-helpers.sh -o ~/.chappiedock/chappiedock-helpers.sh
#   echo 'source ~/.chappiedock/chappiedock-helpers.sh' >> ~/.zshrc
#
# Usage:
#   chappiedock-help    # Show all available commands

# =============================================================================
# Colors
# =============================================================================
_CLR_RESET='\033[0m'
_CLR_BOLD='\033[1m'
_CLR_DIM='\033[2m'
_CLR_GREEN='\033[0;32m'
_CLR_YELLOW='\033[1;33m'
_CLR_BLUE='\033[0;34m'
_CLR_MAGENTA='\033[0;35m'
_CLR_CYAN='\033[0;36m'
_CLR_RED='\033[0;31m'

# Styled command output (green + bold)
_clr_cmd() {
  echo -e "${_CLR_GREEN}${_CLR_BOLD}$1${_CLR_RESET}"
}

# Inline command for use in sentences
_cmd() {
  echo "${_CLR_GREEN}${_CLR_BOLD}$1${_CLR_RESET}"
}

# =============================================================================
# Config
# =============================================================================
CLAWDOCK_CONFIG="${HOME}/.chappiedock/config"

# Common paths to check for Chappie
CLAWDOCK_COMMON_PATHS=(
  "${HOME}/chappie"
  "${HOME}/workspace/chappie"
  "${HOME}/projects/chappie"
  "${HOME}/dev/chappie"
  "${HOME}/code/chappie"
  "${HOME}/src/chappie"
)

_chappiedock_filter_warnings() {
  grep -v "^WARN\|^time="
}

_chappiedock_trim_quotes() {
  local value="$1"
  value="${value#\"}"
  value="${value%\"}"
  printf "%s" "$value"
}

_chappiedock_read_config_dir() {
  if [[ ! -f "$CLAWDOCK_CONFIG" ]]; then
    return 1
  fi
  local raw
  raw=$(sed -n 's/^CLAWDOCK_DIR=//p' "$CLAWDOCK_CONFIG" | head -n 1)
  if [[ -z "$raw" ]]; then
    return 1
  fi
  _chappiedock_trim_quotes "$raw"
}

# Ensure CLAWDOCK_DIR is set and valid
_chappiedock_ensure_dir() {
  # Already set and valid?
  if [[ -n "$CLAWDOCK_DIR" && -f "${CLAWDOCK_DIR}/docker-compose.yml" ]]; then
    return 0
  fi

  # Try loading from config
  local config_dir
  config_dir=$(_chappiedock_read_config_dir)
  if [[ -n "$config_dir" && -f "${config_dir}/docker-compose.yml" ]]; then
    CLAWDOCK_DIR="$config_dir"
    return 0
  fi

  # Auto-detect from common paths
  local found_path=""
  for path in "${CLAWDOCK_COMMON_PATHS[@]}"; do
    if [[ -f "${path}/docker-compose.yml" ]]; then
      found_path="$path"
      break
    fi
  done

  if [[ -n "$found_path" ]]; then
    echo ""
    echo "🦞 Found Chappie at: $found_path"
    echo -n "   Use this location? [Y/n] "
    read -r response
    if [[ "$response" =~ ^[Nn] ]]; then
      echo ""
      echo "Set CLAWDOCK_DIR manually:"
      echo "  export CLAWDOCK_DIR=/path/to/chappie"
      return 1
    fi
    CLAWDOCK_DIR="$found_path"
  else
    echo ""
    echo "❌ Chappie not found in common locations."
    echo ""
    echo "Clone it first:"
    echo ""
    echo "  git clone https://github.com/chappie/chappie.git ~/chappie"
    echo "  cd ~/chappie && ./docker-setup.sh"
    echo ""
    echo "Or set CLAWDOCK_DIR if it's elsewhere:"
    echo ""
    echo "  export CLAWDOCK_DIR=/path/to/chappie"
    echo ""
    return 1
  fi

  # Save to config
  if [[ ! -d "${HOME}/.chappiedock" ]]; then
    /bin/mkdir -p "${HOME}/.chappiedock"
  fi
  echo "CLAWDOCK_DIR=\"$CLAWDOCK_DIR\"" > "$CLAWDOCK_CONFIG"
  echo "✅ Saved to $CLAWDOCK_CONFIG"
  echo ""
  return 0
}

# Wrapper to run docker compose commands
_chappiedock_compose() {
  _chappiedock_ensure_dir || return 1
  local compose_args=(-f "${CLAWDOCK_DIR}/docker-compose.yml")
  if [[ -f "${CLAWDOCK_DIR}/docker-compose.extra.yml" ]]; then
    compose_args+=(-f "${CLAWDOCK_DIR}/docker-compose.extra.yml")
  fi
  command docker compose "${compose_args[@]}" "$@"
}

_chappiedock_read_env_token() {
  _chappiedock_ensure_dir || return 1
  if [[ ! -f "${CLAWDOCK_DIR}/.env" ]]; then
    return 1
  fi
  local raw
  raw=$(sed -n 's/^CHAPPIE_GATEWAY_TOKEN=//p' "${CLAWDOCK_DIR}/.env" | head -n 1)
  if [[ -z "$raw" ]]; then
    return 1
  fi
  _chappiedock_trim_quotes "$raw"
}

# Basic Operations
chappiedock-start() {
  _chappiedock_compose up -d chappie-gateway
}

chappiedock-stop() {
  _chappiedock_compose down
}

chappiedock-restart() {
  _chappiedock_compose restart chappie-gateway
}

chappiedock-logs() {
  _chappiedock_compose logs -f chappie-gateway
}

chappiedock-status() {
  _chappiedock_compose ps
}

# Navigation
chappiedock-cd() {
  _chappiedock_ensure_dir || return 1
  cd "${CLAWDOCK_DIR}"
}

chappiedock-config() {
  cd ~/.chappie
}

chappiedock-workspace() {
  cd ~/.chappie/workspace
}

# Container Access
chappiedock-shell() {
  _chappiedock_compose exec chappie-gateway \
    bash -c 'echo "alias chappie=\"./chappie.mjs\"" > /tmp/.bashrc_chappie && bash --rcfile /tmp/.bashrc_chappie'
}

chappiedock-exec() {
  _chappiedock_compose exec chappie-gateway "$@"
}

chappiedock-cli() {
  _chappiedock_compose run --rm chappie-cli "$@"
}

# Maintenance
chappiedock-rebuild() {
  _chappiedock_compose build chappie-gateway
}

chappiedock-clean() {
  _chappiedock_compose down -v --remove-orphans
}

# Health check
chappiedock-health() {
  _chappiedock_ensure_dir || return 1
  local token
  token=$(_chappiedock_read_env_token)
  if [[ -z "$token" ]]; then
    echo "❌ Error: Could not find gateway token"
    echo "   Check: ${CLAWDOCK_DIR}/.env"
    return 1
  fi
  _chappiedock_compose exec -e "CHAPPIE_GATEWAY_TOKEN=$token" chappie-gateway \
    node dist/index.js health
}

# Show gateway token
chappiedock-token() {
  _chappiedock_read_env_token
}

# Fix token configuration (run this once after setup)
chappiedock-fix-token() {
  _chappiedock_ensure_dir || return 1

  echo "🔧 Configuring gateway token..."
  local token
  token=$(chappiedock-token)
  if [[ -z "$token" ]]; then
    echo "❌ Error: Could not find gateway token"
    echo "   Check: ${CLAWDOCK_DIR}/.env"
    return 1
  fi

  echo "📝 Setting token: ${token:0:20}..."

  _chappiedock_compose exec -e "TOKEN=$token" chappie-gateway \
    bash -c './chappie.mjs config set gateway.remote.token "$TOKEN" && ./chappie.mjs config set gateway.auth.token "$TOKEN"' 2>&1 | _chappiedock_filter_warnings

  echo "🔍 Verifying token was saved..."
  local saved_token
  saved_token=$(_chappiedock_compose exec chappie-gateway \
    bash -c "./chappie.mjs config get gateway.remote.token 2>/dev/null" 2>&1 | _chappiedock_filter_warnings | tr -d '\r\n' | head -c 64)

  if [[ "$saved_token" == "$token" ]]; then
    echo "✅ Token saved correctly!"
  else
    echo "⚠️  Token mismatch detected"
    echo "   Expected: ${token:0:20}..."
    echo "   Got: ${saved_token:0:20}..."
  fi

  echo "🔄 Restarting gateway..."
  _chappiedock_compose restart chappie-gateway 2>&1 | _chappiedock_filter_warnings

  echo "⏳ Waiting for gateway to start..."
  sleep 5

  echo "✅ Configuration complete!"
  echo -e "   Try: $(_cmd chappiedock-devices)"
}

# Open dashboard in browser
chappiedock-dashboard() {
  _chappiedock_ensure_dir || return 1

  echo "🦞 Getting dashboard URL..."
  local output exit_status url
  output=$(_chappiedock_compose run --rm chappie-cli dashboard --no-open 2>&1)
  exit_status=$?
  url=$(printf "%s\n" "$output" | _chappiedock_filter_warnings | grep -o 'http[s]\?://[^[:space:]]*' | head -n 1)
  if [[ $exit_status -ne 0 ]]; then
    echo "❌ Failed to get dashboard URL"
    echo -e "   Try restarting: $(_cmd chappiedock-restart)"
    return 1
  fi

  if [[ -n "$url" ]]; then
    echo "✅ Opening: $url"
    open "$url" 2>/dev/null || xdg-open "$url" 2>/dev/null || echo "   Please open manually: $url"
    echo ""
    echo -e "${_CLR_CYAN}💡 If you see 'pairing required' error:${_CLR_RESET}"
    echo -e "   1. Run: $(_cmd chappiedock-devices)"
    echo "   2. Copy the Request ID from the Pending table"
    echo -e "   3. Run: $(_cmd 'chappiedock-approve <request-id>')"
  else
    echo "❌ Failed to get dashboard URL"
    echo -e "   Try restarting: $(_cmd chappiedock-restart)"
  fi
}

# List device pairings
chappiedock-devices() {
  _chappiedock_ensure_dir || return 1

  echo "🔍 Checking device pairings..."
  local output exit_status
  output=$(_chappiedock_compose exec chappie-gateway node dist/index.js devices list 2>&1)
  exit_status=$?
  printf "%s\n" "$output" | _chappiedock_filter_warnings
  if [ $exit_status -ne 0 ]; then
    echo ""
    echo -e "${_CLR_CYAN}💡 If you see token errors above:${_CLR_RESET}"
    echo -e "   1. Verify token is set: $(_cmd chappiedock-token)"
    echo "   2. Try manual config inside container:"
    echo -e "      $(_cmd chappiedock-shell)"
    echo -e "      $(_cmd 'chappie config get gateway.remote.token')"
    return 1
  fi

  echo ""
  echo -e "${_CLR_CYAN}💡 To approve a pairing request:${_CLR_RESET}"
  echo -e "   $(_cmd 'chappiedock-approve <request-id>')"
}

# Approve device pairing request
chappiedock-approve() {
  _chappiedock_ensure_dir || return 1

  if [[ -z "$1" ]]; then
    echo -e "❌ Usage: $(_cmd 'chappiedock-approve <request-id>')"
    echo ""
    echo -e "${_CLR_CYAN}💡 How to approve a device:${_CLR_RESET}"
    echo -e "   1. Run: $(_cmd chappiedock-devices)"
    echo "   2. Find the Request ID in the Pending table (long UUID)"
    echo -e "   3. Run: $(_cmd 'chappiedock-approve <that-request-id>')"
    echo ""
    echo "Example:"
    echo -e "   $(_cmd 'chappiedock-approve 6f9db1bd-a1cc-4d3f-b643-2c195262464e')"
    return 1
  fi

  echo "✅ Approving device: $1"
  _chappiedock_compose exec chappie-gateway \
    node dist/index.js devices approve "$1" 2>&1 | _chappiedock_filter_warnings

  echo ""
  echo "✅ Device approved! Refresh your browser."
}

# Show all available chappiedock helper commands
chappiedock-help() {
  echo -e "\n${_CLR_BOLD}${_CLR_CYAN}🦞 ClawDock - Docker Helpers for Chappie${_CLR_RESET}\n"

  echo -e "${_CLR_BOLD}${_CLR_MAGENTA}⚡ Basic Operations${_CLR_RESET}"
  echo -e "  $(_cmd chappiedock-start)       ${_CLR_DIM}Start the gateway${_CLR_RESET}"
  echo -e "  $(_cmd chappiedock-stop)        ${_CLR_DIM}Stop the gateway${_CLR_RESET}"
  echo -e "  $(_cmd chappiedock-restart)     ${_CLR_DIM}Restart the gateway${_CLR_RESET}"
  echo -e "  $(_cmd chappiedock-status)      ${_CLR_DIM}Check container status${_CLR_RESET}"
  echo -e "  $(_cmd chappiedock-logs)        ${_CLR_DIM}View live logs (follows)${_CLR_RESET}"
  echo ""

  echo -e "${_CLR_BOLD}${_CLR_MAGENTA}🐚 Container Access${_CLR_RESET}"
  echo -e "  $(_cmd chappiedock-shell)       ${_CLR_DIM}Shell into container (chappie alias ready)${_CLR_RESET}"
  echo -e "  $(_cmd chappiedock-cli)         ${_CLR_DIM}Run CLI commands (e.g., chappiedock-cli status)${_CLR_RESET}"
  echo -e "  $(_cmd chappiedock-exec) ${_CLR_CYAN}<cmd>${_CLR_RESET}  ${_CLR_DIM}Execute command in gateway container${_CLR_RESET}"
  echo ""

  echo -e "${_CLR_BOLD}${_CLR_MAGENTA}🌐 Web UI & Devices${_CLR_RESET}"
  echo -e "  $(_cmd chappiedock-dashboard)   ${_CLR_DIM}Open web UI in browser ${_CLR_CYAN}(auto-guides you)${_CLR_RESET}"
  echo -e "  $(_cmd chappiedock-devices)     ${_CLR_DIM}List device pairings ${_CLR_CYAN}(auto-guides you)${_CLR_RESET}"
  echo -e "  $(_cmd chappiedock-approve) ${_CLR_CYAN}<id>${_CLR_RESET} ${_CLR_DIM}Approve device pairing ${_CLR_CYAN}(with examples)${_CLR_RESET}"
  echo ""

  echo -e "${_CLR_BOLD}${_CLR_MAGENTA}⚙️  Setup & Configuration${_CLR_RESET}"
  echo -e "  $(_cmd chappiedock-fix-token)   ${_CLR_DIM}Configure gateway token ${_CLR_CYAN}(run once)${_CLR_RESET}"
  echo ""

  echo -e "${_CLR_BOLD}${_CLR_MAGENTA}🔧 Maintenance${_CLR_RESET}"
  echo -e "  $(_cmd chappiedock-rebuild)     ${_CLR_DIM}Rebuild Docker image${_CLR_RESET}"
  echo -e "  $(_cmd chappiedock-clean)       ${_CLR_RED}⚠️  Remove containers & volumes (nuclear)${_CLR_RESET}"
  echo ""

  echo -e "${_CLR_BOLD}${_CLR_MAGENTA}🛠️  Utilities${_CLR_RESET}"
  echo -e "  $(_cmd chappiedock-health)      ${_CLR_DIM}Run health check${_CLR_RESET}"
  echo -e "  $(_cmd chappiedock-token)       ${_CLR_DIM}Show gateway auth token${_CLR_RESET}"
  echo -e "  $(_cmd chappiedock-cd)          ${_CLR_DIM}Jump to chappie project directory${_CLR_RESET}"
  echo -e "  $(_cmd chappiedock-config)      ${_CLR_DIM}Open config directory (~/.chappie)${_CLR_RESET}"
  echo -e "  $(_cmd chappiedock-workspace)   ${_CLR_DIM}Open workspace directory${_CLR_RESET}"
  echo ""

  echo -e "${_CLR_BOLD}${_CLR_CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${_CLR_RESET}"
  echo -e "${_CLR_BOLD}${_CLR_GREEN}🚀 First Time Setup${_CLR_RESET}"
  echo -e "${_CLR_CYAN}  1.${_CLR_RESET} $(_cmd chappiedock-start)          ${_CLR_DIM}# Start the gateway${_CLR_RESET}"
  echo -e "${_CLR_CYAN}  2.${_CLR_RESET} $(_cmd chappiedock-fix-token)      ${_CLR_DIM}# Configure token${_CLR_RESET}"
  echo -e "${_CLR_CYAN}  3.${_CLR_RESET} $(_cmd chappiedock-dashboard)      ${_CLR_DIM}# Open web UI${_CLR_RESET}"
  echo -e "${_CLR_CYAN}  4.${_CLR_RESET} $(_cmd chappiedock-devices)        ${_CLR_DIM}# If pairing needed${_CLR_RESET}"
  echo -e "${_CLR_CYAN}  5.${_CLR_RESET} $(_cmd chappiedock-approve) ${_CLR_CYAN}<id>${_CLR_RESET}   ${_CLR_DIM}# Approve pairing${_CLR_RESET}"
  echo ""

  echo -e "${_CLR_BOLD}${_CLR_GREEN}💬 WhatsApp Setup${_CLR_RESET}"
  echo -e "  $(_cmd chappiedock-shell)"
  echo -e "    ${_CLR_BLUE}>${_CLR_RESET} $(_cmd 'chappie channels login --channel whatsapp')"
  echo -e "    ${_CLR_BLUE}>${_CLR_RESET} $(_cmd 'chappie status')"
  echo ""

  echo -e "${_CLR_BOLD}${_CLR_CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${_CLR_RESET}"
  echo ""

  echo -e "${_CLR_CYAN}💡 All commands guide you through next steps!${_CLR_RESET}"
  echo -e "${_CLR_BLUE}📚 Docs: ${_CLR_RESET}${_CLR_CYAN}https://docs.chappie.ai${_CLR_RESET}"
  echo ""
}
