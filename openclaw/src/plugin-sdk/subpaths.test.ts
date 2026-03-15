import * as compatSdk from "chappie/plugin-sdk/compat";
import * as discordSdk from "chappie/plugin-sdk/discord";
import * as imessageSdk from "chappie/plugin-sdk/imessage";
import * as lineSdk from "chappie/plugin-sdk/line";
import * as msteamsSdk from "chappie/plugin-sdk/msteams";
import * as signalSdk from "chappie/plugin-sdk/signal";
import * as slackSdk from "chappie/plugin-sdk/slack";
import * as telegramSdk from "chappie/plugin-sdk/telegram";
import * as whatsappSdk from "chappie/plugin-sdk/whatsapp";
import { describe, expect, it } from "vitest";

const bundledExtensionSubpathLoaders = [
  { id: "acpx", load: () => import("chappie/plugin-sdk/acpx") },
  { id: "bluebubbles", load: () => import("chappie/plugin-sdk/bluebubbles") },
  { id: "copilot-proxy", load: () => import("chappie/plugin-sdk/copilot-proxy") },
  { id: "device-pair", load: () => import("chappie/plugin-sdk/device-pair") },
  { id: "diagnostics-otel", load: () => import("chappie/plugin-sdk/diagnostics-otel") },
  { id: "diffs", load: () => import("chappie/plugin-sdk/diffs") },
  { id: "feishu", load: () => import("chappie/plugin-sdk/feishu") },
  {
    id: "google-gemini-cli-auth",
    load: () => import("chappie/plugin-sdk/google-gemini-cli-auth"),
  },
  { id: "googlechat", load: () => import("chappie/plugin-sdk/googlechat") },
  { id: "irc", load: () => import("chappie/plugin-sdk/irc") },
  { id: "llm-task", load: () => import("chappie/plugin-sdk/llm-task") },
  { id: "lobster", load: () => import("chappie/plugin-sdk/lobster") },
  { id: "matrix", load: () => import("chappie/plugin-sdk/matrix") },
  { id: "mattermost", load: () => import("chappie/plugin-sdk/mattermost") },
  { id: "memory-core", load: () => import("chappie/plugin-sdk/memory-core") },
  { id: "memory-lancedb", load: () => import("chappie/plugin-sdk/memory-lancedb") },
  {
    id: "minimax-portal-auth",
    load: () => import("chappie/plugin-sdk/minimax-portal-auth"),
  },
  { id: "nextcloud-talk", load: () => import("chappie/plugin-sdk/nextcloud-talk") },
  { id: "nostr", load: () => import("chappie/plugin-sdk/nostr") },
  { id: "open-prose", load: () => import("chappie/plugin-sdk/open-prose") },
  { id: "phone-control", load: () => import("chappie/plugin-sdk/phone-control") },
  { id: "qwen-portal-auth", load: () => import("chappie/plugin-sdk/qwen-portal-auth") },
  { id: "synology-chat", load: () => import("chappie/plugin-sdk/synology-chat") },
  { id: "talk-voice", load: () => import("chappie/plugin-sdk/talk-voice") },
  { id: "test-utils", load: () => import("chappie/plugin-sdk/test-utils") },
  { id: "thread-ownership", load: () => import("chappie/plugin-sdk/thread-ownership") },
  { id: "tlon", load: () => import("chappie/plugin-sdk/tlon") },
  { id: "twitch", load: () => import("chappie/plugin-sdk/twitch") },
  { id: "voice-call", load: () => import("chappie/plugin-sdk/voice-call") },
  { id: "zalo", load: () => import("chappie/plugin-sdk/zalo") },
  { id: "zalouser", load: () => import("chappie/plugin-sdk/zalouser") },
] as const;

describe("plugin-sdk subpath exports", () => {
  it("exports compat helpers", () => {
    expect(typeof compatSdk.emptyPluginConfigSchema).toBe("function");
    expect(typeof compatSdk.resolveControlCommandGate).toBe("function");
  });

  it("exports Discord helpers", () => {
    expect(typeof discordSdk.resolveDiscordAccount).toBe("function");
    expect(typeof discordSdk.inspectDiscordAccount).toBe("function");
    expect(typeof discordSdk.discordOnboardingAdapter).toBe("object");
  });

  it("exports Slack helpers", () => {
    expect(typeof slackSdk.resolveSlackAccount).toBe("function");
    expect(typeof slackSdk.inspectSlackAccount).toBe("function");
    expect(typeof slackSdk.handleSlackMessageAction).toBe("function");
  });

  it("exports Telegram helpers", () => {
    expect(typeof telegramSdk.resolveTelegramAccount).toBe("function");
    expect(typeof telegramSdk.inspectTelegramAccount).toBe("function");
    expect(typeof telegramSdk.telegramOnboardingAdapter).toBe("object");
  });

  it("exports Signal helpers", () => {
    expect(typeof signalSdk.resolveSignalAccount).toBe("function");
    expect(typeof signalSdk.signalOnboardingAdapter).toBe("object");
  });

  it("exports iMessage helpers", () => {
    expect(typeof imessageSdk.resolveIMessageAccount).toBe("function");
    expect(typeof imessageSdk.imessageOnboardingAdapter).toBe("object");
  });

  it("exports WhatsApp helpers", () => {
    // WhatsApp-specific functions (resolveWhatsAppAccount, whatsappOnboardingAdapter) moved to extensions/whatsapp/src/
    expect(typeof whatsappSdk.WhatsAppConfigSchema).toBe("object");
    expect(typeof whatsappSdk.resolveWhatsAppOutboundTarget).toBe("function");
  });

  it("exports LINE helpers", () => {
    expect(typeof lineSdk.processLineMessage).toBe("function");
    expect(typeof lineSdk.createInfoCard).toBe("function");
  });

  it("exports Microsoft Teams helpers", () => {
    expect(typeof msteamsSdk.resolveControlCommandGate).toBe("function");
    expect(typeof msteamsSdk.loadOutboundMediaFromUrl).toBe("function");
  });

  it("exports acpx helpers", async () => {
    const acpxSdk = await import("chappie/plugin-sdk/acpx");
    expect(typeof acpxSdk.listKnownProviderAuthEnvVarNames).toBe("function");
    expect(typeof acpxSdk.omitEnvKeysCaseInsensitive).toBe("function");
  });

  it("resolves bundled extension subpaths", async () => {
    for (const { id, load } of bundledExtensionSubpathLoaders) {
      const mod = await load();
      expect(typeof mod).toBe("object");
      expect(mod, `subpath ${id} should resolve`).toBeTruthy();
    }
  });

  it("keeps the newly added bundled plugin-sdk contracts available", async () => {
    const bluebubbles = await import("chappie/plugin-sdk/bluebubbles");
    expect(typeof bluebubbles.parseFiniteNumber).toBe("function");

    const mattermost = await import("chappie/plugin-sdk/mattermost");
    expect(typeof mattermost.parseStrictPositiveInteger).toBe("function");

    const nextcloudTalk = await import("chappie/plugin-sdk/nextcloud-talk");
    expect(typeof nextcloudTalk.waitForAbortSignal).toBe("function");

    const twitch = await import("chappie/plugin-sdk/twitch");
    expect(typeof twitch.DEFAULT_ACCOUNT_ID).toBe("string");
    expect(typeof twitch.normalizeAccountId).toBe("function");

    const zalo = await import("chappie/plugin-sdk/zalo");
    expect(typeof zalo.resolveClientIp).toBe("function");
  });
});
