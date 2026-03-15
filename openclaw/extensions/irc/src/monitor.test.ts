import { describe, expect, it } from "vitest";
import { resolveIrcInboundTarget } from "./monitor.js";

describe("irc monitor inbound target", () => {
  it("keeps channel target for group messages", () => {
    expect(
      resolveIrcInboundTarget({
        target: "#chappie",
        senderNick: "alice",
      }),
    ).toEqual({
      isGroup: true,
      target: "#chappie",
      rawTarget: "#chappie",
    });
  });

  it("maps DM target to sender nick and preserves raw target", () => {
    expect(
      resolveIrcInboundTarget({
        target: "chappie-bot",
        senderNick: "alice",
      }),
    ).toEqual({
      isGroup: false,
      target: "alice",
      rawTarget: "chappie-bot",
    });
  });

  it("falls back to raw target when sender nick is empty", () => {
    expect(
      resolveIrcInboundTarget({
        target: "chappie-bot",
        senderNick: " ",
      }),
    ).toEqual({
      isGroup: false,
      target: "chappie-bot",
      rawTarget: "chappie-bot",
    });
  });
});
