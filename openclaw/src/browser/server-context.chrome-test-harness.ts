import { vi } from "vitest";
import { installChromeUserDataDirHooks } from "./chrome-user-data-dir.test-harness.js";

const chromeUserDataDir = { dir: "/tmp/chappie" };
installChromeUserDataDirHooks(chromeUserDataDir);

vi.mock("./chrome.js", () => ({
  isChromeCdpReady: vi.fn(async () => true),
  isChromeReachable: vi.fn(async () => true),
  launchChappieChrome: vi.fn(async () => {
    throw new Error("unexpected launch");
  }),
  resolveChappieUserDataDir: vi.fn(() => chromeUserDataDir.dir),
  stopChappieChrome: vi.fn(async () => {}),
}));
